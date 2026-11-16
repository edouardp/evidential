// Per-widget theme resolution. Never mutate the model or a global colour mode.
import chroma from "chroma-js";
import {COLOR_SCALES, FALLBACK_COLOR_SCALE, bindColorResolver, resolveColor, seriesColors} from "./color.js";
import {paintResolver} from "./contrast.js";

export const SCHEMES = {
  light: {surface: "#ffffff", text: "#172033", muted: "#64748b", accent: "#2563eb",
    positive: "#15803d", negative: "#dc2626", reference: "#0f766e", selection: "#8b1e2d"},
  dark: {surface: "#171b24", text: "#e5e7eb", muted: "#a6b0c0", accent: "#7da8ff",
    positive: "#4ade80", negative: "#fb7185", reference: "#5eead4", selection: "#fb7185"},
};

/** A monotone lightness transform, preserving hue, opacity and palette order.
 * Reduce chroma only to bring the new lightness into the sRGB gamut.
 */
export function adaptColor(value) {
  if (!chroma.valid(value)) return value;
  const original = chroma(value), [lightness, chromaValue, hue] = original.lch();
  const light = 28 + lightness * 0.72;
  let low = 0, high = chromaValue;
  for (let step = 0; step < 12; step++) {
    const mid = (low + high) / 2;
    if (chroma.lch(light, mid, hue).clipped()) high = mid;
    else low = mid;
  }
  return chroma.lch(light, low, hue).alpha(original.alpha()).hex();
}

const colorKeys = new Set(["color", "background", "backgroundColor", "background-color", "font_color",
  "negative_color", "highlight", "outline", "empty_color", "marker_color", "reference_color", "color_negative",
  "bar_color", "bar_color_negative", "background_color"]);
// These maps contain user labels or data, never presentation colours. Keep
// their references (especially large group membership arrays) unchanged.
const dataKeys = new Set(["members", "cells", "names", "legend", "legacy", "rows", "values", "icon_map", "template_fmt"]);
const paletteKeys = new Set(["color_scale", "palette"]);
const themeKeys = {background: "bg", surface: "surface", text: "text", muted: "muted", border: "border",
  row_border: "row-border", header_bg: "header-bg", header_border: "header-border", header_text: "header-text",
  hover: "hover", shading: "shading", total_bg: "total-bg", total_text: "total-text", subtotal_bg: "subtotal-bg",
  pivot_bg: "pivot-bg", link: "link", negative: "negative", positive: "positive", accent: "accent", font: "font", font_size: "font-size"};

export function themeColors(scheme, options = {}, native = value => value) {
  const overrides = options.theme || {}, base = SCHEMES[scheme];
  const tokens = {...base, ...Object.fromEntries(Object.entries(overrides).filter(([, value]) => value != null))};
  tokens.surface = overrides.surface || overrides.dialog_background || overrides.background || options.background_color || base.surface;
  tokens.neutral = tokens.surface;
  for (const role of ["surface", "neutral", "text", "muted", "accent", "positive", "negative"]) {
    const value = resolveColor(tokens[role]);
    tokens[role] = chroma.valid(value) ? value : native(value);
  }
  const cache = new Map();
  function resolve(value, adapt = options.adapt_colors) {
    if (typeof value !== "string") return value;
    const key = `${!!adapt}:${value}`;
    if (cache.has(key)) return cache.get(key);
    let result;
    if (value.startsWith("fixed:")) result = resolveColor(value.slice(6));
    else if (value.startsWith("theme:")) {
      const [role, alpha = "1"] = value.slice(6).split("/");
      const token = resolveColor(tokens[role]);
      result = chroma.valid(token) ? chroma(token).alpha(Number(alpha)).hex() : token || value;
    } else {
      const literal = resolveColor(value);
      result = scheme === "dark" && adapt ? adaptColor(literal) : literal;
    }
    cache.set(key, result);
    return result;
  }
  function palette(value) {
    if (Array.isArray(value)) return value.map(item => resolve(item));
    const name = typeof value === "string" ? value.toLowerCase() : "";
    const named = name === "tab10" ? seriesColors(10) : COLOR_SCALES[name];
    if (!named) return value;
    if (scheme !== "dark") return named;
    // Sequential light-to-dark scales become surface-to-bright. Diverging and
    // perceptual maps retain their existing lightness ordering and hue sequence.
    if (/^(green|blue|red|orange|purple|grey|gray|blues|reds|greens|greys|oranges|purples|bugn|bupu|gnbu|orrd|pubu|rdpu|ylgn|ylgnbu|ylorbr|ylorrd)$/.test(name)) {
      return chroma.scale([tokens.surface, adaptColor(named.at(-1))]).mode("lab").colors(named.length);
    }
    return named.map(item => resolve(item, true));
  }
  function compile(value, key = "") {
    if (dataKeys.has(key)) return value;
    if (paletteKeys.has(key)) return palette(value);
    if (colorKeys.has(key)) return resolve(value);
    if (!value || typeof value !== "object") return value;
    if (Array.isArray(value)) return value.map(item => compile(item));
    // Theme overrides are exact UI settings, not encoded data colours.
    if (key === "theme") return value;
    const result = Object.fromEntries(Object.entries(value).map(([name, item]) => [name,
      key === "colors" ? resolve(item) : compile(item, name)]));
    if (["gradient", "color_options"].includes(key) && !value.color_scale && !value.color_stops) result.color_scale = defaultPalette;
    if (value.sources && !value.palette) result.palette = palette("tab10");
    bindColorResolver(result, resolve);
    return result;
  }
  const defaultPalette = scheme === "dark" ? [tokens.surface, base.accent] : FALLBACK_COLOR_SCALE;
  return {tokens, resolve, compile, defaultPalette};
}

function parent(node) { return node.parentElement || node.getRootNode()?.host || null; }
function hostScheme(host, view, attributesFirst = false) {
  if (attributesFirst) {
    for (let node = host; node; node = parent(node)) {
      for (const attr of ["data-color-scheme", "data-theme"]) {
        const value = node.getAttribute(attr);
        if (value === "light" || value === "dark") return value;
      }
    }
    // Prefer explicit site signals over an island host's computed light
    // scheme, which marimo may set as a runtime default.
    for (let node = host; node; node = parent(node)) {
      if (node.classList.contains("dark")) return "dark";
      if (node.classList.contains("light")) return "light";
      const scheme = node.style.colorScheme?.replace(/\bonly\b/g, "").trim();
      if (scheme === "light" || scheme === "dark") return scheme;
    }
  }
  const computed = new Map();
  const cssScheme = node => {
    if (!node) return null;
    if (!computed.has(node)) computed.set(node, view.getComputedStyle(node).colorScheme?.replace(/\bonly\b/g, "").trim());
    return computed.get(node);
  };
  for (let node = host; node; node = parent(node)) {
    for (const attr of ["data-color-scheme", "data-theme"]) {
      const value = node.getAttribute(attr);
      if (value === "light" || value === "dark") return value;
    }
    if (node.classList.contains("dark")) return "dark";
    if (node.classList.contains("light")) return "light";
    const scheme = node.style.colorScheme?.replace(/\bonly\b/g, "").trim();
    if (scheme === "light" || scheme === "dark") return scheme;
    const local = cssScheme(node);
    if ((local === "light" || local === "dark") && local !== cssScheme(parent(node))) return local;
  }
  return null;
}

/** Listen outside the widget, including shadow hosts; own paints never trigger loops. */
export class ThemeController {
  constructor(host, roots, getOptions, onChange) {
    this.host = host;
    this.roots = roots;
    this.getOptions = getOptions;
    this.view = host.ownerDocument.defaultView;
    this.media = this.view.matchMedia?.("(prefers-color-scheme: dark)");
    this.refresh = () => {
      if (this.destroyed) return;
      const scheme = this.scheme();
      if (scheme !== this.current || this.paintKey() !== this.lastPaint) {
        this.current = scheme; this.cache = null; onChange();
      }
    };
    this.observer = new this.view.MutationObserver(this.refresh);
    for (let node = host; node; node = parent(node)) {
      this.observer.observe(node, {attributes: true, attributeFilter: ["class", "style", "data-theme", "data-color-scheme"]});
    }
    this.media?.addEventListener("change", this.refresh);
    this.beforePrint = () => { this.printing = true; this.refresh(); };
    this.afterPrint = () => { this.printing = false; this.refresh(); };
    this.view.addEventListener("beforeprint", this.beforePrint);
    this.view.addEventListener("afterprint", this.afterPrint);
  }
  scheme() {
    if (this.printing) return "light";
    const explicit = this.getOptions().color_scheme;
    let host = this.host;
    const source = this.getOptions().theme_source || "auto";
    let island = false;
    for (let node = host; node; node = parent(node)) {
      if (node.tagName === "MARIMO-ISLAND") { island = true; break; }
    }
    const hostContext = source === "host" || (source === "auto" && island);
    if (hostContext) {
      // Page preference is independent of the embed card: sites can force a
      // light color-scheme on that card for other marimo outputs. Starting at
      // the page body also avoids inherited runtime defaults on shadow hosts.
      host = host.ownerDocument.body || host.ownerDocument.documentElement;
    }
    return explicit && explicit !== "auto" ? explicit
      : hostScheme(host, this.view, hostContext) || (this.media?.matches ? "dark" : "light");
  }
  paintKey() {
    const style = this.view.getComputedStyle(this.roots[0]);
    return ["surface", "text", "muted", "accent", "positive", "negative"]
      .map(role => style.getPropertyValue?.(`--et-${role}`)).join("|");
  }
  prepare(columns, options, rowLayout = null) {
    const scheme = this.scheme();
    this.current = scheme;
    if (this.cache?.columns === columns && this.cache.options === options && this.cache.rowLayout === rowLayout && this.cache.scheme === scheme) return this.cache.result;
    this.apply(scheme, themeColors(scheme, options).tokens, options);
    const paint = paintResolver(this.roots[0]);
    let colors;
    try { colors = themeColors(scheme, options, value => paint.color(value).hex()); }
    finally { paint.destroy(); }
    const compiledOptions = colors.compile(options);
    compiledOptions.color_scale ||= colors.defaultPalette;
    const result = {columns: colors.compile(columns), options: compiledOptions, rowLayout: colors.compile(rowLayout), colors};
    this.cache = {columns, options, rowLayout, scheme, result};
    this.lastPaint = this.paintKey();
    return result;
  }
  apply(scheme, tokens, options) {
    const mix = (value, alpha) => `color-mix(in srgb, ${value} ${alpha * 100}%, transparent)`;
    const vars = {
      bg: SCHEMES[scheme].surface, surface: tokens.surface, text: tokens.text, muted: tokens.muted,
      border: mix(tokens.muted, 0.3), "row-border": mix(tokens.muted, 0.22),
      "header-bg": tokens.surface, "header-border": mix(tokens.text, 0.4), "header-text": tokens.text,
      hover: mix(tokens.text, 0.08), shading: mix(tokens.text, 0.04),
      "total-bg": mix(tokens.muted, 0.16), "subtotal-bg": mix(tokens.muted, 0.1), "pivot-bg": mix(tokens.muted, 0.1),
      "total-text": tokens.text, link: tokens.accent, negative: tokens.negative, positive: tokens.positive,
      accent: tokens.accent, reference: tokens.reference, selection: tokens.selection,
      "axis-text": scheme === "light" ? "#000000" : tokens.text,
    };
    const theme = {...options.theme};
    theme.background ||= options.background_color;
    theme.header_bg ||= options.header_color;
    theme.header_text ||= options.header_font_color;
    theme.total_bg ||= options.total_row_color;
    theme.total_text ||= options.total_font_color;
    theme.row_border ||= typeof options.row_lines === "string" ? options.row_lines : null;
    for (const [key, css] of Object.entries(themeKeys)) {
      if (theme[key]) vars[css] = resolveColor(theme[key]);
    }
    for (const root of this.roots) {
      root.dataset.colorScheme = scheme;
      root.style.colorScheme = scheme;
      for (const [key, value] of Object.entries(vars)) root.style.setProperty(`--et-${key}`, value);
      for (const key of ["font", "font-size"]) if (!vars[key]) root.style.removeProperty(`--et-${key}`);
    }
  }
  destroy() {
    this.destroyed = true;
    this.observer.disconnect();
    this.media?.removeEventListener("change", this.refresh);
    this.view.removeEventListener("beforeprint", this.beforePrint);
    this.view.removeEventListener("afterprint", this.afterPrint);
    this.cache = null;
  }
}
