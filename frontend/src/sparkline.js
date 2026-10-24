import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { numeric } from "./mark-data.js";
import { sparklinePoints } from "./sparkline-data.js";
import { renderChangeSparkline } from "./change-sparkline.js";

export { sparklinePoints } from "./sparkline-data.js";

export function renderSparkline(col, value, changeColor) {
  const opts = col.sparkline_options || {};
  const points = sparklinePoints(value, opts);
  const present = points.filter(point => point[1] != null);
  if (!present.length) return h("span", { class: "et-null" }, "–");

  if (opts.type === "change") return renderChangeSparkline(points, opts, changeColor);

  const width = opts.width || 64;
  const height = opts.height || 18;
  const pad = 1.5;
  const ys = present.map((point) => point[1]);
  let min = Math.min(...ys);
  let max = Math.max(...ys);
  if (!opts.fit_to_data) {
    min = Math.min(0, min);
    max = Math.max(0, max);
  }
  const span = max - min || 1;
  // Numeric/date x coordinates preserve elapsed distance. Categorical labels
  // retain ordinal spacing, including the slots occupied by missing values.
  const xNumber = x => numeric(x) ?? (typeof x === "string" && /^\d{4}-\d\d-\d\d/.test(x) ? Date.parse(x) : NaN);
  const xs = points.map(point => xNumber(point[0]));
  const quantitativeX = xs.every(Number.isFinite);
  const xmin = quantitativeX ? Math.min(...xs) : 0;
  const xmax = quantitativeX ? Math.max(...xs) : points.length - 1;
  const baseline = pad + (height - pad * 2) * (1 - (Math.max(0, min) - min) / span);
  const scaled = points.map(([x, y, source], index) => ({
    x: xmax > xmin ? pad + ((quantitativeX ? xs[index] : index) - xmin) / (xmax - xmin) * (width - pad * 2) : width / 2,
    y: y == null ? null : pad + (height - pad * 2) * (1 - (y - min) / span),
    raw: [x, y],
    source,
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
  const showMarkers = !!opts.markers || type === "points";
  const endsOnly = opts.markers === "ends";
  if (type === "bar") {
    const slot = width / scaled.length;
    const barWidth = Math.max(1, slot * 0.7);
    scaled.forEach((point) => {
      if (point.y == null) return;
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
  } else if (type !== "points") {
    const segments = [];
    let segment = [];
    for (const point of scaled) {
      if (point.y == null) {
        if (segment.length) segments.push(segment);
        segment = [];
      } else segment.push(point);
    }
    if (segment.length) segments.push(segment);
    for (const run of segments) {
      const linePoints = run.map((point) => `${point.x},${point.y}`).join(" ");
      if (type === "area") {
        if (opts.signed) {
          // Split the fill at the zero baseline: up and down get their own colour.
          addArea(svgNS, svg, run, baseline, (point) => Math.min(point.y, baseline), color);
          addArea(svgNS, svg, run, baseline, (point) => Math.max(point.y, baseline), "var(--et-negative, #dc2626)");
        } else {
          addArea(svgNS, svg, run, baseline, (point) => point.y, color);
        }
      }
      const poly = document.createElementNS(svgNS, "polyline");
      poly.setAttribute("points", linePoints);
      poly.setAttribute("fill", "none");
      poly.setAttribute("stroke", color);
      poly.setAttribute("stroke-width", "1.25");
      poly.setAttribute("stroke-linejoin", "round");
      poly.setAttribute("stroke-linecap", "round");
      svg.append(poly);
    }
  }
  scaled.forEach((point, index) => {
    if (point.y == null) return;
    const isEnd = index === 0 || index === scaled.length - 1;
    const visible = showMarkers && (!endsOnly || isEnd);
    const perPoint = point.source && typeof point.source === "object" ? point.source.color : null;
    const dot = document.createElementNS(svgNS, "circle");
    dot.setAttribute("cx", String(point.x));
    dot.setAttribute("cy", String(point.y));
    dot.setAttribute("r", visible ? "2.2" : "2.5");
    dot.setAttribute("fill", visible ? (perPoint || opts.marker_color || color) : "transparent");
    dot.append(tooltip(point.raw));
    svg.append(dot);
  });
  return svg;
}

/** Add an area polygon under a sparkline, following a per-point baseline clip. */
function addArea(svgNS, svg, scaled, baseline, clip, fill) {
  const area = document.createElementNS(svgNS, "polygon");
  const points = scaled.map((point) => `${point.x},${clip(point)}`).join(" ");
  area.setAttribute(
    "points",
    `${points} ${scaled[scaled.length - 1].x},${baseline} ${scaled[0].x},${baseline}`,
  );
  area.setAttribute("fill", fill);
  area.setAttribute("opacity", "0.22");
  svg.append(area);
}
