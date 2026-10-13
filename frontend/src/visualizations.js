import { h } from "./dom.js";
import { formatValue } from "./format.js";

export function renderBar(col, value, formatted, range) {
  const opts = col.bar_options || {};
  const num = Number(value);
  const min = opts.fit_to_data ? (range?.min ?? 0) : Math.min(0, range?.min ?? 0);
  const max = opts.fit_to_data ? (range?.max ?? 0) : Math.max(0, range?.max ?? 0);
  const span = max - min || 1;
  const pct = Math.max(0, Math.min(100, ((num - min) / span) * 100));
  const negative = num < 0;
  const color = negative
    ? (opts.bar_color_negative || opts.bar_color || "var(--et-negative, #dc2626)")
    : (opts.bar_color || "var(--et-accent, #2563eb)");
  const bar = h("div", { class: "et-bar", style: { width: `${pct}%`, backgroundColor: color } });
  const wrap = h("div", { class: `et-bar-wrap${negative ? " et-bar-negative" : ""}` }, bar);
  const label = h("span", { class: `et-bar-label${opts.hide_labels ? " et-hidden" : ""}` }, formatted);
  const cell = h("div", {
    class: "et-bar-cell",
    style: opts.background_color ? { backgroundColor: opts.background_color } : {},
  }, [wrap, label]);
  return cell;
}

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

export function renderSparkline(col, value) {
  const opts = col.sparkline_options || {};
  const points = sparklinePoints(value, opts);
  if (!points.length) return h("span", { class: "et-null" }, "–");

  const width = opts.width || 64;
  const height = opts.height || 18;
  const pad = 1.5;
  const ys = points.map((point) => point[1]);
  let min = Math.min(...ys);
  let max = Math.max(...ys);
  if (!opts.fit_to_data) {
    min = Math.min(0, min);
    max = Math.max(0, max);
  }
  const span = max - min || 1;
  const step = points.length > 1 ? (width - pad * 2) / (points.length - 1) : 0;
  const baseline = pad + (height - pad * 2) * (1 - (Math.max(0, min) - min) / span);
  const scaled = points.map(([x, y], index) => ({
    x: points.length > 1 ? pad + index * step : width / 2,
    y: pad + (height - pad * 2) * (1 - (y - min) / span),
    raw: [x, y],
  }));

  const color = opts.color || "var(--et-accent, #2563eb)";
  const svgNS = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(svgNS, "svg");
  svg.setAttribute("class", "et-sparkline");
  svg.setAttribute("width", String(width));
  svg.setAttribute("height", String(height));
  svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

  const tooltip = ([x, y]) => {
    const title = document.createElementNS(svgNS, "title");
    const yText = formatValue(y, opts.y_fmt, { type: "number", fallback: String(y) });
    title.textContent = x === undefined || x === null || x === "" ? yText : `${x}: ${yText}`;
    return title;
  };

  // Zero baseline when the scale crosses zero (matching Evidence's defaults).
  if (!opts.fit_to_data && min < 0 && max > 0) {
    const zero = document.createElementNS(svgNS, "line");
    zero.setAttribute("x1", "0");
    zero.setAttribute("x2", String(width));
    zero.setAttribute("y1", String(baseline));
    zero.setAttribute("y2", String(baseline));
    zero.setAttribute("stroke", "color-mix(in srgb, CanvasText 20%, transparent)");
    zero.setAttribute("stroke-width", "1");
    svg.append(zero);
  }

  const type = opts.type || "line";
  if (type === "bar") {
    const slot = width / scaled.length;
    const barWidth = Math.max(1, slot * 0.7);
    scaled.forEach((point) => {
      const top = Math.min(point.y, baseline);
      const rect = document.createElementNS(svgNS, "rect");
      rect.setAttribute("x", String(Math.max(0, point.x - barWidth / 2)));
      rect.setAttribute("y", String(top));
      rect.setAttribute("width", String(barWidth));
      rect.setAttribute("height", String(Math.max(1, Math.abs(baseline - point.y))));
      rect.setAttribute("rx", "0.5");
      rect.setAttribute("fill", color);
      rect.append(tooltip(point.raw));
      svg.append(rect);
    });
  } else {
    const linePoints = scaled.map((point) => `${point.x},${point.y}`).join(" ");
    if (type === "area") {
      const area = document.createElementNS(svgNS, "polygon");
      area.setAttribute(
        "points",
        `${linePoints} ${scaled[scaled.length - 1].x},${baseline} ${scaled[0].x},${baseline}`,
      );
      area.setAttribute("fill", color);
      area.setAttribute("opacity", "0.18");
      svg.append(area);
    }
    const poly = document.createElementNS(svgNS, "polyline");
    poly.setAttribute("points", linePoints);
    poly.setAttribute("fill", "none");
    poly.setAttribute("stroke", color);
    poly.setAttribute("stroke-width", "1.25");
    poly.setAttribute("stroke-linejoin", "round");
    poly.setAttribute("stroke-linecap", "round");
    svg.append(poly);
    scaled.forEach((point) => {
      const dot = document.createElementNS(svgNS, "circle");
      dot.setAttribute("cx", String(point.x));
      dot.setAttribute("cy", String(point.y));
      dot.setAttribute("r", "2.5");
      dot.setAttribute("fill", "transparent");
      dot.append(tooltip(point.raw));
      svg.append(dot);
    });
  }
  return svg;
}

export function sparklinePoints(value, opts) {
  if (!Array.isArray(value)) return [];
  const xKey = opts.x;
  const yKey = opts.y;
  const points = [];
  value.forEach((item, index) => {
    if (item === null || item === undefined) return;
    let x = index;
    let y;
    if (Array.isArray(item)) {
      x = item[0];
      y = Number(item[1]);
    } else if (typeof item === "object") {
      const keys = Object.keys(item);
      const yField = yKey && yKey in item ? yKey : keys.find((key) => _isNumeric(item[key]));
      const xField =
        xKey && xKey in item ? xKey : keys.find((key) => key !== yField && !_isNumeric(item[key]));
      x = xField ? item[xField] : index;
      y = Number(yField ? item[yField] : NaN);
    } else {
      y = Number(item);
    }
    if (y !== null && !isNaN(y)) points.push([x, y]);
  });
  return points;
}

function _isNumeric(value) {
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value === "string") return value.trim() !== "" && !isNaN(Number(value));
  return false;
}
