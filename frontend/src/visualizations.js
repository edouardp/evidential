import {renderGlyph} from "./mark-glyphs.js";
import {marksDomain, niceTicks, scalePosition} from "./mark-scales.js";
import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { resolveColor } from "./color.js";
import { inspectable, inspectionData } from "./tooltips.js";
import { markTooltip, tooltipText } from "./tooltip-data.js";
import { renderMarkLabel } from "./mark-labels.js";

export function renderMarks(col, row, range, format, context = {}) {
  const labelFor = (column, enc, record, geometry, formatter) => inspectable(
    renderMarkLabel(column, enc, record, geometry, formatter), markTooltip(column, enc, record, {context}),
    {priority: 1, navigate: false});
  const encodings = col.encodings || [];
  const scale = col.scale || {};
  const {lo, hi, span} = marksDomain(col, range);
  const reverse = encodings.some(enc => enc.kind === "bar" && enc.direction === "left");
  const pos = scalePosition(lo, hi, scale.transform, reverse);
  const clampPos = (value) => {
    const pct = pos(value);
    return pct == null ? null : Math.max(0, Math.min(100, pct));
  };
  const track = h("div", { class: "et-marks" });
  track.setAttribute("role", "img");
  if (encodings.some(enc => ["above", "below"].includes(enc.label?.position))) track.classList.add("et-marks-tall");

  // Faint vertical lines at round values help read a mark against the scale.
  if (scale.gridlines) {
    for (const tick of niceTicks(lo, hi, 4, scale.transform)) {
      const pct = pos(tick);
      if (pct == null) continue;
      track.append(
        h("div", { class: "et-mark-gridline", style: { left: `${Math.max(0, Math.min(100, pct))}%` } }),
      );
    }
  }

  // Column-wide reference rules paint behind the marks.
  const barReferences = encodings.filter(enc => enc.kind === "bar" && enc.reference != null)
    .map(enc => ({value: enc.reference, color: enc.reference_color, label: enc.reference_label}));
  const hasCenter = encodings.some(enc => enc.center);
  const references = [...(hasCenter ? [{value: 0}] : []), ...(col.references || []), ...barReferences];
  const referenceBands = document.createDocumentFragment();
  for (const ref of references) {
    if (ref.value == null || !isFinite(Number(ref.value))) continue;
    const raw = pos(Number(ref.value));
    if (raw == null) continue;
    const pct = raw;
    if (ref.high != null && isFinite(Number(ref.high))) {
      const rawHigh = pos(Number(ref.high));
      if (rawHigh == null) continue;
      const left = Math.max(0, Math.min(100, Math.min(pct, rawHigh)));
      const right = Math.max(0, Math.min(100, Math.max(pct, rawHigh)));
      if (right <= left) continue;
      referenceBands.append(
        h("div", {
          class: "et-mark-band",
          style: {
            left: `${left}%`,
            width: `${right - left}%`,
            backgroundColor: resolveColor(ref.color),
          },
        }),
      );
      if (ref.label) {
        track.append(
          h("span", { class: "et-mark-reference-label", style: { left: `${left}%` } }, String(ref.label)),
        );
      }
      continue;
    }
    if (pct < 0 || pct > 100) continue;
    track.append(
      h("div", {
        class: "et-mark-reference",
        style: {
          left: `${pct}%`,
          backgroundColor: resolveColor(ref.color) || "var(--et-reference, #0f766e)",
        },
      }),
    );
    if (ref.label) {
      track.append(
        h("span", { class: "et-mark-reference-label", style: { left: `${pct}%` } }, String(ref.label)),
      );
    }
  }

  // Bands form the background; even opaque fills must leave guides visible.
  track.prepend(referenceBands);
  const view = {col, row, track, pos, clampPos, lo, hi, span, reverse, format, labelFor, context,
    barCount: encodings.filter(enc => enc.kind === "bar").length, barIndex: 0,
    stack: encodings.filter(enc => enc.kind === "stacked_bar")};
  for (const encoding of encodings) renderGlyph(encoding, view);
  if (!track.querySelector(".et-mark, .et-mark-strip, .et-density-band")) {
    track.append(h("span", {class: "et-null"}, String(col.null_text ?? (format ? format(null) : "–"))));
  }
  const description = [...new Set([...track.querySelectorAll("[data-et-tooltip]:not([data-mark-label])")]
    .map(node => tooltipText(inspectionData(node))))].join("\n");
  track.setAttribute("aria-label", description || "No observations");
  return track;
}

export function renderBar(col, value, formatted, range, row) {
  const opts = col.bar_options || {};
  const num = Number(value);
  const min = range?.shared || opts.fit_to_data ? (range?.min ?? 0) : Math.min(0, range?.min ?? 0);
  const max = range?.shared || opts.fit_to_data ? (range?.max ?? 0) : Math.max(0, range?.max ?? 0);
  const negative = num < 0;
  // A leftward bar fills from the right edge — the mirror of the default, for a
  // back-to-back ("tornado") league table.
  const leftward = opts.direction === "left";
  // A per-row colour column (`bar(color="@column")`) wins over a fixed colour.
  const rowColor =
    opts.bar_color_column && row ? resolveColor(row[opts.bar_color_column]) : null;
  const color = negative
    ? (resolveColor(row?.[opts.bar_color_negative_column]) || rowColor || resolveColor(opts.bar_color_negative) || resolveColor(opts.bar_color) || "var(--et-negative, #dc2626)")
    : (rowColor || resolveColor(opts.bar_color) || "var(--et-accent, #2563eb)");
  const label = h(
    "span",
    { class: `et-bar-label${opts.hide_labels ? " et-hidden" : ""}` },
    formattedText(formatted),
  );
  const background = opts.background_color ? { backgroundColor: opts.background_color } : {};
  // `pad` insets the bar — and, in centred mode, the centre line's ends on the
  // first/last row — from the top and bottom (a px number or a CSS length).
  const pad =
    opts.pad == null ? null : typeof opts.pad === "number" ? `${opts.pad}px` : String(opts.pad);

  let cell;
  if (opts.center) {
    // A zero-centred "diverging" bar: the bar grows left (negative) or right
    // (positive) from a centre line by its magnitude, and the value sits on the
    // opposite side of the line.
    const maxAbs = Math.max(Math.abs(min), Math.abs(max), 1e-9);
    const width = Math.max(0, Math.min(100, (Math.abs(num) / maxAbs) * 100)) / 2;
    const bar = h("div", {
      class: `et-bar et-bar-${negative ? "left" : "right"}`,
      style: { width: `${width}%`, backgroundColor: color },
    });
    const axis = h("div", { class: "et-bar-axis" });
    const wrap = h("div", { class: "et-bar-wrap" }, [axis, bar]);
    label.classList.add(negative ? "et-bar-label-right" : "et-bar-label-left");
    cell = h("div", { class: "et-bar-cell et-bar-center", style: background }, [wrap, label]);
  } else {
    const span = max - min || 1;
    const pct = Math.max(0, Math.min(100, ((num - min) / span) * 100));
    const bar = h("div", {
      class: `et-bar${leftward ? " et-bar-fill-left" : ""}`,
      style: { width: `${pct}%`, backgroundColor: color },
    });
    const marks = referenceMarks(opts, min, span, leftward);
    const wrap = h("div", { class: `et-bar-wrap${negative ? " et-bar-negative" : ""}` }, [bar, ...marks]);
    cell = h("div", { class: "et-bar-cell", style: background }, [wrap, label]);
  }
  if (pad) cell.style.setProperty("--et-bar-pad", pad);
  return cell;
}

/** A vertical benchmark rule (and its caption) for a bar column. */
function referenceMarks(opts, min, span, leftward) {
  if (opts.reference == null || !isFinite(Number(opts.reference))) return [];
  const pct = Math.max(0, Math.min(100, ((Number(opts.reference) - min) / span) * 100));
  // A leftward bar mirrors the scale, so its rule mirrors with it.
  const left = leftward ? 100 - pct : pct;
  const color = resolveColor(opts.reference_color) || "var(--et-reference, #0f766e)";
  const marks = [
    h("div", { class: "et-bar-reference", style: { left: `${left}%`, backgroundColor: color } }),
  ];
  if (opts.reference_label) {
    // Keep the caption inside the column: centre it on the rule, but anchor it
    // to the nearer edge when the rule sits near one end.
    const anchor =
      left > 60 ? "translateX(-100%)" : left < 40 ? "translateX(0)" : "translateX(-50%)";
    marks.push(
      h(
        "span",
        { class: "et-bar-reference-label", style: { left: `${left}%`, color, transform: anchor } },
        String(opts.reference_label),
      ),
    );
  }
  return marks;
}

/** A numeric value as that many repeated symbols — glyphs, emoji or images. */
export function renderSymbols(col, value, formatted) {
  const opts = col.symbol_options || {};
  const num = Number(value);
  if (value === null || value === undefined || value === "" || Number.isNaN(num)) {
    return h("span", { class: "et-null" }, formatted ?? "–");
  }
  const filled = Math.max(0, Math.round(num));
  const total = opts.max != null ? Math.max(filled, Math.round(Number(opts.max))) : filled;
  const wrap = h("span", { class: "et-symbols" });
  if (opts.size != null) wrap.style.fontSize = `${opts.size}em`;
  if (opts.gap != null) wrap.style.gap = `${opts.gap}em`;
  for (let i = 0; i < total; i++) {
    const on = i < filled;
    if (opts.image) {
      wrap.append(
        h("img", {
          class: `et-symbol-image${on ? "" : " et-symbol-empty"}`,
          src: String(opts.image),
          alt: "",
          loading: "lazy",
        }),
      );
      continue;
    }
    if (opts.shape) {
      // A CSS-drawn box: pixel-exact and font-independent (unlike a glyph).
      const box = h("span", {
        class: `et-symbol-box et-symbol-box-${opts.shape}${on ? "" : " et-symbol-empty"}`,
      });
      const side = opts.size != null ? `${opts.size}em` : null;
      if (side) box.style.width = box.style.height = side;
      const fill = on ? opts.color : opts.empty_color;
      if (fill) box.style.backgroundColor = resolveColor(fill);
      wrap.append(box);
      continue;
    }
    const node = h(
      "span",
      { class: `et-symbol${on ? "" : " et-symbol-empty"}` },
      on ? (opts.symbol || "●") : (opts.empty || opts.symbol || "●"),
    );
    const colour = on ? opts.color : opts.empty_color;
    if (colour) node.style.color = resolveColor(colour);
    wrap.append(node);
  }
  return wrap;
}

/** Resolve a neutral band from a string, pair, symmetric bound or explicit min/max. */
export function neutralBounds(opts) {
  const range = opts.neutral_range;
  if (typeof range === "string") {
    const match = range.match(/^\s*(-?\d+(?:\.\d+)?)\s*(?::|\.\.)\s*(-?\d+(?:\.\d+)?)\s*$/);
    if (match) return [Number(match[1]), Number(match[2])];
  }
  if (Array.isArray(range) && range.length === 2) return [Number(range[0]), Number(range[1])];
  if (typeof range === "number" && isFinite(range)) return [-Math.abs(range), Math.abs(range)];
  return [opts.neutral_min ?? 0, opts.neutral_max ?? 0];
}

export function renderDelta(col, value) {
  const opts = col.delta_options || {};
  const isMissing = value === null || value === undefined;
  const num = isMissing ? 0 : Number(value);
  const [lo, hi] = neutralBounds(opts);
  const isNeutral =
    isMissing || ((lo == null || num >= lo) && (hi == null || num <= hi));
  const positive = num > 0;
  const good = isNeutral ? false : opts.down_is_good ? !positive : positive;
  const cls = isNeutral ? "et-delta-neutral" : good ? "et-delta-good" : "et-delta-bad";
  // The indicator is a dash for a neutral value, otherwise an up/down arrow.
  const indicator =
    opts.show_symbol === false ? "" : isNeutral ? "–" : positive ? "▲" : num < 0 ? "▼" : "–";
  // A `pct`-formatted delta holds a fraction, so always show it as a
  // percentage — even above 100% (e.g. a 307% change) — rather than falling
  // back to a bare number.
  const pct =
    col.fmt && col.fmt.startsWith("pct")
      ? formatValue(Math.abs(num), col.fmt, {
          type: "number",
          fallback: String(Math.abs(num)),
        })
      : Math.abs(num).toLocaleString(undefined, { maximumFractionDigits: 1 });
  const valueText = opts.show_value === false || isMissing ? "" : pct;
  const valueNode = valueText ? h("span", { class: "et-delta-value" }, valueText) : null;
  const indicatorNode = indicator
    ? h("span", { class: "et-delta-indicator" }, indicator)
    : null;
  // The indicator follows the value by default (e.g. "12.0% ▲").
  const ordered =
    opts.symbol_position === "left" ? [indicatorNode, valueNode] : [valueNode, indicatorNode];
  const content = [];
  for (const node of ordered) {
    if (!node) continue;
    if (content.length) content.push(" ");
    content.push(node);
  }
  const classes = ["et-delta", cls, opts.chip ? "et-delta-chip" : ""].filter(Boolean).join(" ");
  return h("span", { class: classes }, content.length ? content : "–");
}

export { renderSparkline, sparklinePoints } from "./sparkline.js";
