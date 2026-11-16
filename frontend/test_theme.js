import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import chroma from "chroma-js";
import {adaptColor, SCHEMES, ThemeController, themeColors} from "./src/theme.js";
import {dataColor, calculateColorStyles} from "./src/color.js";
import {pointSeries, markColor} from "./src/mark-series.js";

test("custom colours are exact by default; adaptation preserves hue, alpha and lightness ordering", () => {
  const original = "#14385a80";
  assert.equal(themeColors("dark").resolve(original), original);
  const light = themeColors("light", {adapt_colors: true}), dark = themeColors("dark", {adapt_colors: true});
  assert.equal(light.resolve(original), original);
  assert.equal(dark.resolve(original), dark.resolve(original)); // cache
  const result = chroma(dark.resolve(original)), source = chroma(original);
  assert.ok(result.get("lab.l") > source.get("lab.l"));
  assert.ok(Math.abs(result.get("lch.h") - source.get("lch.h")) < 1);
  assert.equal(result.alpha(), source.alpha());
  assert.equal(dark.resolve("fixed:tab:blue"), "#1f77b4");
  assert.equal(dark.resolve("var(--custom)"), "var(--custom)");
  assert.equal(dark.resolve(false), false);
  assert.equal(adaptColor("transparent"), "transparent");
  const values = ["#111", "#555", "#999", "#ddd"].map(value => chroma(adaptColor(value)).get("lab.l"));
  assert.ok(values.every((value, index) => !index || value > values[index - 1]));
});

test("semantic neutrals follow surface and alpha, while builtin palettes adapt without opt-in", () => {
  for (const scheme of ["light", "dark"]) {
    const colors = themeColors(scheme);
    assert.equal(colors.resolve("theme:neutral"), SCHEMES[scheme].surface);
    assert.equal(chroma(colors.resolve("theme:negative/0.2")).alpha(), 0.2);
    assert.equal(colors.resolve("theme:unknown"), "theme:unknown");
    for (const name of ["blue", "viridis", "tab10"]) {
      const palette = colors.compile({palette: name}).palette;
      assert.ok(palette.length > 1);
      if (scheme === "dark") assert.notDeepEqual(palette, themeColors("light").compile({palette: name}).palette);
    }
    assert.equal(colors.compile({palette: "unknown"}).palette, "unknown");
  }
  assert.equal(themeColors("dark", {theme: {surface: "#222222"}}).resolve("theme:neutral"), "#222222");
  assert.equal(themeColors("dark", {theme: {text: "var(--ink)"}}).resolve("theme:text"), "var(--ink)");
});

test("presentation compilation covers maps, gradients, labels and dynamic data without rewriting rows", () => {
  const colors = themeColors("dark", {adapt_colors: true});
  const input = {name: "red", title: "blue", domain: {palette: ["red", "theme:neutral", "fixed:blue"]},
    encodings: [{kind: "points", sources: ["a", "b"], color_column: "fill"},
      {kind: "bar", color: "#123456", label: {color: "fixed:white"}, gradient: {}},
      {kind: "strip", colors: {yes: "green", no: "fixed:red"}}],
    color_options: {conditional_colors: "fill"}, cell_style: {background: "theme:surface"},
    theme: {background: "#123456"}};
  const original = structuredClone(input), compiled = colors.compile(input);
  assert.deepEqual(input, original);
  assert.equal(compiled.name, "red"); assert.equal(compiled.title, "blue");
  assert.equal(compiled.domain.palette[1], SCHEMES.dark.surface);
  assert.equal(compiled.domain.palette[2], "blue");
  assert.equal(compiled.encodings[1].label.color, "white");
  assert.equal(compiled.encodings[2].colors.no, "red");
  assert.deepEqual(compiled.encodings[1].gradient.color_scale, colors.defaultPalette);
  assert.deepEqual(compiled.color_options.color_scale, colors.defaultPalette);
  assert.deepEqual(compiled.theme, input.theme);
  const row = {a: 1, fill: "#123456"};
  assert.equal(dataColor(row.fill, compiled), colors.resolve(row.fill));
  assert.equal(markColor(pointSeries(compiled.encodings[0])[0], row), colors.resolve(row.fill));
  assert.equal(calculateColorStyles(compiled, row).backgroundColor, colors.resolve(row.fill));
  assert.deepEqual(row, {a: 1, fill: "#123456"});
  for (const key of ["legend", "names", "members", "cells", "icon_map", "template_fmt", "legacy", "rows", "values"]) {
    const data = {color: "red", palette: "blue"};
    assert.equal(colors.compile({[key]: data})[key], data);
  }
});

function fixture() {
  const dom = new JSDOM('<body><div id="host"><section></section><dialog></dialog></div></body>');
  const view = dom.window, document = view.document, host = document.querySelector("#host");
  const media = new view.EventTarget(); media.matches = true;
  view.matchMedia = () => media;
  let options = {}, changes = 0;
  const roots = [...host.children];
  const controller = new ThemeController(host, roots, () => options, () => changes++);
  return {view, document, host, roots, controller, media, setOptions: value => {options = value;}, get changes() {return changes;}};
}

test("scheme precedence follows explicit, nearest host, inherited CSS then OS; cache does not leak", async () => {
  const f = fixture(), {controller, host, document, media, roots} = f;
  assert.equal(controller.scheme(), "dark");
  document.body.className = "light";
  assert.equal(controller.scheme(), "light");
  host.dataset.theme = "dark";
  assert.equal(controller.scheme(), "dark");
  host.dataset.colorScheme = "light";
  assert.equal(controller.scheme(), "light");
  f.setOptions({color_scheme: "dark"}); assert.equal(controller.scheme(), "dark");
  f.setOptions({color_scheme: "auto"});
  delete host.dataset.colorScheme; delete host.dataset.theme;
  document.body.className = ""; host.style.colorScheme = "only light";
  assert.equal(controller.scheme(), "light");
  host.style.colorScheme = "light only";
  assert.equal(controller.scheme(), "light");
  host.style.colorScheme = "";
  document.body.className = "dark";
  assert.equal(controller.scheme(), "dark");
  document.body.className = ""; media.matches = false;
  assert.equal(controller.scheme(), "light");
  const cols = [{name: "a"}], options = {font_size: "13px", theme: {font: "serif"}};
  const a = controller.prepare(cols, options);
  assert.equal(controller.prepare(cols, options), a);
  assert.equal(roots[0].dataset.colorScheme, "light");
  assert.equal(roots[1].style.getPropertyValue("--et-surface"), "#ffffff");
  document.body.className = "dark";
  await new Promise(resolve => setTimeout(resolve, 0));
  assert.equal(f.changes, 1);
  const b = controller.prepare(cols, options);
  assert.notEqual(a, b); assert.equal(roots[0].dataset.colorScheme, "dark");
  assert.notEqual(controller.prepare(cols, options, {}), b);
  media.dispatchEvent(new f.view.Event("change")); assert.equal(f.changes, 1);
  f.view.dispatchEvent(new f.view.Event("beforeprint")); assert.equal(controller.scheme(), "light");
  f.view.dispatchEvent(new f.view.Event("afterprint")); assert.equal(controller.scheme(), "dark");
  controller.prepare(cols, {});
  assert.equal(roots[0].style.getPropertyValue("--et-font"), "");
  controller.destroy();
  const before = f.changes;
  controller.refresh(); media.dispatchEvent(new f.view.Event("change"));
  f.view.dispatchEvent(new f.view.Event("beforeprint"));
  assert.equal(f.changes, before);
});

test("native CSS scheme, shadow hosts, absent matchMedia and exact UI overrides", () => {
  const {view, host, roots, controller} = fixture();
  controller.destroy();
  const shadow = host.attachShadow({mode: "open"}), child = view.document.createElement("div");
  shadow.append(child); host.className = "dark";
  view.matchMedia = undefined;
  const nested = new ThemeController(child, [child], () => ({}), () => {});
  assert.equal(nested.scheme(), "dark");
  host.className = "light"; assert.equal(nested.scheme(), "light");
  host.className = "";
  view.getComputedStyle = () => ({colorScheme: "only dark"});
  assert.equal(nested.scheme(), "dark");
  nested.destroy();
  controller.apply("dark", SCHEMES.dark, {background_color: "pink", row_lines: "red", header_color: "orange",
    header_font_color: "black", total_row_color: "green", total_font_color: "white", theme: {font_size: "14px"}});
  assert.equal(roots[0].style.getPropertyValue("--et-header-bg"), "orange");
  assert.equal(roots[0].style.getPropertyValue("--et-total-text"), "white");
  assert.equal(roots[0].style.getPropertyValue("--et-row-border"), "red");
});
