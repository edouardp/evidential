import { createColorScale, getColorForValue, resolveColor } from "./color.js";
import { formatValue } from "./format.js";
import { sparklinePoints } from "./sparkline-data.js";

/** The inclusive steady interval is categorical; magnitude only determines color. */
export function changeState(value, steady = [0, 0]) {
  return value < steady[0] ? "down" : value > steady[1] ? "up" : "steady";
}

/** Anchor the entire neutral interval at 0.5, with independent ramps either side. */
export function changeColorScale(opts, values) {
  const steady = opts.steady || [0, 0];
  if (!opts.color_scale) {
    const colors = {down: "var(--et-negative, #dc2626)", steady: "#b8bcc2", up: "var(--et-accent, #2563eb)"};
    return value => resolveColor(opts.color) || colors[changeState(value, steady)];
  }
  let [min, max] = steady;
  for (const value of values) {
    if (value != null && Number.isFinite(value)) {
      min = Math.min(min, value);
      max = Math.max(max, value);
    }
  }
  [min, max] = opts.color_domain || [min, max];
  const palette = Array.isArray(opts.color_scale) ? opts.color_scale.map(resolveColor) : opts.color_scale;
  const scale = createColorScale([], {colorPalette: palette, min: 0, max: 1});
  return value => {
    let at = 0.5;
    if (value < steady[0]) at = min < steady[0] ? 0.5 * (value - min) / (steady[0] - min) : 0;
    else if (value > steady[1]) at = max > steady[1] ? 0.5 + 0.5 * (value - steady[1]) / (max - steady[1]) : 1;
    return getColorForValue(Math.max(0, Math.min(1, at)), scale);
  };
}

/** Build once per matching dataset, before pagination; each physical column has its own scale. */
export function prepareChangeScales(columns, rows) {
  const scales = new Map();
  for (const column of columns) {
    const opts = column.sparkline_options || {};
    if (column.viz !== "sparkline" || opts.type !== "change") continue;
    const values = [];
    if (opts.color_scale && !opts.color_domain) {
      for (const row of rows) {
        if (row.render_type && row.render_type !== "cell_data") continue;
        for (const [, value] of sparklinePoints(row[column.name], opts)) {
          if (value != null) values.push(value);
        }
      }
    }
    scales.set(column, changeColorScale(opts, values));
  }
  return scales;
}

/** Equal rectangles: steady is centered; up/down shift by half a rectangle height. */
export function renderChangeSparkline(points, opts, colorForValue) {
  const width = opts.width || 64;
  const height = opts.height || 18;
  const pad = Math.min(1.5, height / 8);
  const rectHeight = (height - 2 * pad) / 2;
  const slot = width / points.length;
  const colors = colorForValue || changeColorScale(opts, points.map(point => point[1]));
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("class", "et-sparkline et-sparkline-change");
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
  svg.setAttribute("role", "img");
  const counts = {up: 0, steady: 0, down: 0, missing: 0};
  points.forEach(([, value]) => {
    if (value == null) counts.missing++;
    else counts[changeState(value, opts.steady)]++;
  });
  svg.setAttribute("aria-label", `Changes: ${counts.up} up, ${counts.steady} steady, ${counts.down} down, ${counts.missing} missing`);
  points.forEach(([x, value], index) => {
    if (value == null) return;
    const state = changeState(value, opts.steady);
    const rect = document.createElementNS(ns, "rect");
    const y = pad + (state === "up" ? 0 : state === "steady" ? rectHeight / 2 : rectHeight);
    rect.setAttribute("x", String((index + 0.15) * slot));
    rect.setAttribute("y", String(y));
    rect.setAttribute("width", String(slot * 0.7));
    rect.setAttribute("height", String(rectHeight));
    rect.setAttribute("rx", String(Math.min(0.6, slot * 0.35)));
    rect.setAttribute("fill", colors(value));
    rect.setAttribute("data-state", state);
    const title = document.createElementNS(ns, "title");
    const formatted = formatValue(value, opts.y_fmt, {type: "number", fallback: String(value)});
    const text = x === undefined || x === null || x === "" ? formatted : `${x}: ${formatted}`;
    title.textContent = `${text} (${state})`;
    rect.append(title);
    svg.append(rect);
  });
  return svg;
}
