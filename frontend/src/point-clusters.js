// Pixel-space aggregation is presentation only: every source point survives.
import chroma from "chroma-js";
import { h } from "./dom.js";

const visuals = new WeakMap();
export function pointVisual(node) { return visuals.get(node) || node; }

/** A sorted sweep, bounded by the WHOLE cluster, rather than its last member.
 * Sorting is O(n log n); the sweep is O(n). The bounding-box diagonal is a
 * conservative distance bound, so a chain can never stretch beyond tolerance.
 */
export function pointClusters(points, tolerance = 1) {
  const sorted = [...points].sort((a, b) => a.x - b.x || a.y - b.y);
  const result = [];
  let group = [], minX, minY, maxY;
  const flush = () => {
    if (group.length > 1 && new Set(group.map(point => point.color)).size > 1) result.push(group);
  };
  for (const point of sorted) {
    const first = group[0];
    if (!point.opaque || !first || Math.abs(point.width - first.width) > 0.01 || Math.abs(point.height - first.height) > 0.01 ||
        Math.hypot(point.x - minX, Math.max(maxY, point.y) - Math.min(minY, point.y)) > tolerance) {
      flush();
      group = []; minX = point.x; minY = point.y; maxY = point.y;
    }
    if (!point.opaque) continue;
    group.push(point); minY = Math.min(minY, point.y); maxY = Math.max(maxY, point.y);
  }
  flush();
  return result;
}

const namespace = "http://www.w3.org/2000/svg";
function path(svg, d, attributes) {
  const node = document.createElementNS(namespace, "path");
  node.setAttribute("d", d);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, value);
  svg.append(node);
}

/** Start at twelve o'clock: halves split vertically, thirds meet at the centre. */
function sectorCircle(group, size) {
  const svg = document.createElementNS(namespace, "svg");
  svg.setAttribute("viewBox", `0 0 ${size} ${size}`);
  svg.setAttribute("aria-hidden", "true");
  const center = size / 2;
  const at = (angle, radius) => `${center + Math.sin(angle) * radius},${center - Math.cos(angle) * radius}`;
  group.forEach((point, index) => {
    const start = index / group.length * 2 * Math.PI, end = (index + 1) / group.length * 2 * Math.PI;
    const arc = radius => `M${at(start, radius)} A${radius},${radius} 0 0 1 ${at(end, radius)}`;
    path(svg, `M${center},${center} L${at(start, center)} A${center},${center} 0 0 1 ${at(end, center)} Z`, {fill: point.color});
    if (point.outline) path(svg, arc(center + 0.5), {fill: "none", stroke: point.outline, "stroke-width": "1"});
  });
  return svg;
}

/** Recompute on layout and resize; read all geometry before writing any glyphs. */
export function combinePoints(root) {
  const tracks = [...root.querySelectorAll(".et-marks")];
  for (const track of tracks) {
    for (const composite of track.querySelectorAll(".et-point-composite")) composite.remove();
    for (const point of track.querySelectorAll(".et-mark-point")) {
      point.classList.remove("et-point-combined-member"); visuals.delete(point);
    }
  }
  const view = root.ownerDocument.defaultView;
  const plans = tracks.map(track => {
    const points = [...track.querySelectorAll(".et-mark-point")].map(node => {
      const rect = node.getBoundingClientRect(), style = view.getComputedStyle(node);
      const color = style.backgroundColor;
      const opaque = rect.width > 0 && rect.height > 0 && Number(style.opacity || 1) === 1 &&
        style.visibility !== "hidden" && chroma.valid(color) && chroma(color).alpha() === 1;
      return {node, x: rect.left + rect.width / 2, y: rect.top + rect.height / 2,
        width: rect.width, height: rect.height, color: opaque ? chroma(color).hex() : color, opaque,
        outline: style.boxShadow === "none" ? null : style.boxShadow.match(/(?:rgba?|color)\([^)]*\)/)?.[0]};
    });
    return {track, clusters: pointClusters(points)};
  });
  for (const {track, clusters} of plans) for (const group of clusters) {
    // Use declaration order for sectors, names and legend keys, regardless of x.
    group.sort((a, b) => a.node.compareDocumentPosition(b.node) & 4 ? -1 : 1);
    const first = group[0].node;
    const composite = h("div", {class: "et-mark et-point-composite", "aria-hidden": "true",
      "data-point-count": group.length, style: {
        top: first.style.top, bottom: first.style.bottom, transform: first.style.transform,
        left: `${group.reduce((sum, point) => sum + parseFloat(point.node.style.left), 0) / group.length}%`,
        width: first.style.width, height: first.style.height,
      }}, sectorCircle(group, parseFloat(first.style.width)));
    for (const point of group) { point.node.classList.add("et-point-combined-member"); visuals.set(point.node, composite); }
    track.append(composite);
  }
}
