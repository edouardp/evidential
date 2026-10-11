import { test } from "node:test";
import assert from "node:assert/strict";
import {
  createColorScale,
  getColorForValue,
  colorStylesFromHex,
  calculateVizRanges,
  calculateColorStyles,
} from "./src/color.js";

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

test("calculateColorStyles uses conditional color column", () => {
  const col = { name: "x", viz: "color", color_options: { conditional_colors: "color" } };
  const row = { x: 5, color: "#ff0000" };
  const styles = calculateColorStyles(col, row, { min: 0, max: 10 }, null);
  assert.equal(styles.backgroundColor, "#ff0000");
});
