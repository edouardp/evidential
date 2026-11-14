// Pixel-space aggregation is presentation only: every source point survives.
import chroma from "chroma-js";
import { h } from "./dom.js";
import {markerPath, svgNode} from "./marker-shapes.js";

const visuals = new WeakMap();
export function pointVisual(node) { return visuals.get(node) || node; }

/** A sorted sweep, bounded by the WHOLE cluster, rather than its last member.
 * Sorting is O(n log n); the sweep is O(n). The bounding-box diagonal is a
 * conservative distance bound, so a chain can never stretch beyond tolerance.
 */
export function pointClusters(points, tolerance = 1) {
  const geometry = point => `${point.shape || "circle"}:${point.angle || 0}`;
  const sorted = [...points].sort((a, b) => geometry(a).localeCompare(geometry(b)) || a.x - b.x || a.y - b.y);
  const result = [];
  let group = [], minX, minY, maxY;
  const flush = () => {
    if (group.length > 1 && new Set(group.map(point => point.color)).size > 1) result.push(group);
  };
  for (const point of sorted) {
    const first = group[0];
    if (!point.opaque || !first || geometry(point) !== geometry(first) || Math.abs(point.width - first.width) > 0.01 || Math.abs(point.height - first.height) > 0.01 ||
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

/** Clip the same marker geometry into colored sectors; keep its own outline. */
function sectorShape(group, size) {
  if (!group[0].shape || group[0].shape === "circle") return sectorCircle(group, size);
  const svg = svgNode("svg", {viewBox: "-50 -50 100 100", "aria-hidden": "true"});
  const defs = svgNode("defs");
  const counter = Symbol.for("evidential.markerClusterCounter");
  const id = `et-marker-cluster-${document[counter] = (document[counter] || 0) + 1}`;
  const shape = group[0].shape;
  const shapeClip = svgNode("clipPath", {id});
  shapeClip.append(svgNode("path", {d: markerPath(shape), transform: `rotate(${group[0].angle || 0})`}));
  defs.append(shapeClip); svg.append(defs);
  group.forEach((point, index) => {
    const start = index / group.length * 2 * Math.PI, end = (index + 1) / group.length * 2 * Math.PI;
    const at = angle => `${Math.sin(angle) * 150},${-Math.cos(angle) * 150}`;
    const sector = `M0,0 L${at(start)} A150,150 0 ${end - start > Math.PI ? 1 : 0},1 ${at(end)} Z`;
    const sectorClip = svgNode("clipPath", {id: `${id}-${index}`});
    sectorClip.append(svgNode("path", {d: sector})); defs.append(sectorClip);
    const fill = svgNode("g", {"clip-path": `url(#${id})`});
    fill.append(svgNode("path", {d: sector, fill: point.color})); svg.append(fill);
    if (point.outline) {
      const edge = svgNode("g", {"clip-path": `url(#${id}-${index})`});
      edge.append(svgNode("path", {d: markerPath(shape), fill: "none", stroke: point.outline,
        "stroke-width": 1, "vector-effect": "non-scaling-stroke", "stroke-linejoin": "round",
        transform: `rotate(${group[0].angle || 0})`}));
      svg.append(edge);
    }
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
      const shape = node.dataset.shape || "circle";
      const color = shape === "circle" ? style.backgroundColor : style.color;
      const outline = node.querySelector(".et-marker-svg path");
      const opaque = rect.width > 0 && rect.height > 0 && Number(style.opacity || 1) === 1 &&
        style.visibility !== "hidden" && chroma.valid(color) && chroma(color).alpha() === 1;
      return {node, x: rect.left + rect.width / 2, y: rect.top + rect.height / 2,
        shape, angle: Number(node.dataset.angle || 0),
        width: rect.width, height: rect.height, color: opaque ? chroma(color).hex() : color, opaque,
        outline: outline ? (view.getComputedStyle(outline).stroke || outline.getAttribute("stroke")) === "none" ? null
          : view.getComputedStyle(outline).stroke || outline.getAttribute("stroke")
          : style.boxShadow === "none" ? null : style.boxShadow.match(/(?:rgba?|color)\([^)]*\)/)?.[0]};
    });
    return pointClusters(points);
  });
  for (const clusters of plans) for (const group of clusters) {
    // Use declaration order for sectors, names and legend keys, regardless of x.
    group.sort((a, b) => a.node.compareDocumentPosition(b.node) & 4 ? -1 : 1);
    const first = group[0].node;
    const composite = h("div", {class: "et-mark et-point-composite", "aria-hidden": "true",
      "data-point-count": group.length, style: {
        top: first.style.top, bottom: first.style.bottom, transform: first.style.transform.replace(/ rotate\([^)]*\)/g, ""),
        left: `${group.reduce((sum, point) => sum + parseFloat(point.node.style.left), 0) / group.length}%`,
        width: first.style.width, height: first.style.height,
      }}, sectorShape(group, parseFloat(first.style.width)));
    for (const point of group) { point.node.classList.add("et-point-combined-member"); visuals.set(point.node, composite); }
    group.at(-1).node.after(composite);
  }
}
