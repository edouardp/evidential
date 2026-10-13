import { test } from "node:test";
import assert from "node:assert/strict";
import {
  createColorScale,
  getColorForValue,
  colorStylesFromHex,
  calculateVizRanges,
  calculateColorStyles,
  buildColorVizScale,
  COLOR_SCALES,
  COLORMAPS,
  resolveColor,
} from "./src/color.js";

test("named colour scales: presets, matplotlib colormaps and names", () => {
  assert.deepEqual(COLOR_SCALES.viridis, [
    "#440154",
    "#472d7b",
    "#3b528b",
    "#2c728e",
    "#21918c",
    "#28ae80",
    "#5ec962",
    "#addc30",
    "#fde725",
  ]);
  assert.equal(COLOR_SCALES.rdbu.length, 9);
  assert.ok(Object.keys(COLORMAPS).length >= 30);
  // Lookup is case-insensitive (`resolvePalette`).
  const scale = buildColorVizScale({ color_options: { color_scale: "Viridis" } }, { min: 0, max: 100 }, null);
  assert.equal(scale.colorPalette.length, 9);
  // matplotlib colour names resolve to hex.
  assert.equal(resolveColor("tab:blue"), "#1f77b4");
  assert.equal(resolveColor("C0"), "#1f77b4");
  assert.equal(resolveColor("k"), "#000000");
  assert.equal(resolveColor("#abc"), "#abc");
});

test("an unknown colour scale raises instead of falling back", () => {
  assert.throws(
    () => buildColorVizScale({ color_options: { color_scale: "viridis2" } }, { min: 0, max: 1 }, null),
    /Unknown colour scale/,
  );
});

test("linear color scale", () => {
  const scale = createColorScale([0, 100], {
    colorPalette: ["#ffffff", "#0000ff"],
    min: 0,
    max: 100,
  });
  assert.equal(scale.kind, "linear");
  assert.equal(getColorForValue(0, scale), "#ffffff");
  assert.equal(getColorForValue(100, scale), "#0000ff");
});

test("diverging scale anchors the midpoint", () => {
  const scale = createColorScale([-100, 100], {
    colorPalette: ["#ff0000", "#ffffff", "#00ff00"],
    midpoint: 0,
  });
  assert.equal(scale.kind, "diverging");
  assert.equal(getColorForValue(0, scale), "#ffffff");
});

test("contrast-aware cell styles", () => {
  const dark = colorStylesFromHex("#111827");
  assert.equal(dark.color, "#ffffff");
  const light = colorStylesFromHex("#fef9c3");
  assert.equal(light.color, "#000000");
});

test("viz ranges skip totals", () => {
  const columns = [{ name: "x", viz: "bar" }];
  const rows = [{ x: 1 }, { x: 5 }, { x: 100, render_type: "row_total" }];
  const ranges = calculateVizRanges(columns, rows);
  assert.deepEqual(ranges.get("x"), { min: 1, max: 5 });
});

test("named colour-scale presets resolve to palettes", () => {
  const scale = createColorScale([], {
    colorPalette: "green",
    min: 0,
    max: 1,
  });
  assert.ok(scale);
  assert.match(getColorForValue(1, scale), /^#[0-9a-f]{6}$/i);
});

test("calculateColorStyles uses conditional color column", () => {
  const col = { name: "x", viz: "color", color_options: { conditional_colors: "color" } };
  const row = { x: 5, color: "#ff0000" };
  const styles = calculateColorStyles(col, row, { min: 0, max: 10 }, null);
  assert.equal(styles.backgroundColor, "#ff0000");
});

test("color scale uses inferred bounds and requested interpolation mode", () => {
  const scale = buildColorVizScale(
    { color_options: { color_scale: ["#000000", "#ffffff"], scale_mode: "rgb" } },
    { min: 10, max: 20 },
  );
  assert.equal(getColorForValue(15, scale), "#808080");
  const named = buildColorVizScale({}, { min: 0, max: 1 }, "green");
  assert.equal(getColorForValue(1, named), "#16a34a");
  assert.ok(createColorScale([0, 1], { colorPalette: "unknown" }));
});
