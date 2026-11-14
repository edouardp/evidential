// Shared, font-independent marker geometry. Size is the unrotated bounding box.
import {resolveColor} from "./color.js";

export const SVG_NS = "http://www.w3.org/2000/svg";
const paths = {
  circle: "M0,-50 A50,50 0 1,1 0,50 A50,50 0 1,1 0,-50 Z",
  square: "M-50,-50 H50 V50 H-50 Z",
  rounded: "M-30,-50 H30 Q50,-50 50,-30 V30 Q50,50 30,50 H-30 Q-50,50 -50,30 V-30 Q-50,-50 -30,-50 Z",
  triangle: "M0,-50 L43.3012701892,25 H-43.3012701892 Z",
  diamond: "M0,-50 L37.5,0 0,50 -37.5,0 Z",
  cross: "M-17,-50 H17 V-17 H50 V17 H17 V50 H-17 V17 H-50 V-17 H-17 Z",
  star: "M0,-50 L11.8,-16.2 47.6,-15.5 19,6.2 29.4,40.5 0,20 -29.4,40.5 -19,6.2 -47.6,-15.5 -11.8,-16.2 Z",
  bar: "M-10,-50 H10 V50 H-10 Z",
};

export const MARKER_SHAPES = Object.keys(paths);
export const markerPath = (shape = "circle") => Object.hasOwn(paths, shape) ? paths[shape] : paths.circle;
export const markerAngle = (shape, angle = 0) => shape === "circle" ? 0 : ((angle % 360) + 360) % 360;

export function svgNode(tag, attributes = {}) {
  const node = document.createElementNS(SVG_NS, tag);
  for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, String(value));
  return node;
}

export function markerOutline(outline) {
  return outline === false ? "none" : typeof outline === "string" ? resolveColor(outline) || outline
    : "var(--et-marker-outline, color-mix(in srgb, Canvas 60%, transparent))";
}

export function markerGraphic({shape = "circle", angle = 0, color = "currentColor", outline, hollow = false} = {}) {
  const svg = svgNode("svg", {viewBox: "-50 -50 100 100", "aria-hidden": "true", class: "et-marker-svg"});
  svg.append(svgNode("path", {d: markerPath(shape), fill: hollow ? "none" : color,
    stroke: hollow && outline !== false && typeof outline !== "string" ? color : markerOutline(outline),
    "stroke-width": 1, "vector-effect": "non-scaling-stroke", "stroke-linejoin": "round",
    transform: `rotate(${markerAngle(shape, angle)})`}));
  return svg;
}

/** Keep native circles cheap; other shapes use the very same SVG paths as symbols. */
export function decorateMarker(node, {shape = "circle", angle = 0, color, outline} = {}) {
  const rotation = markerAngle(shape, angle);
  node.dataset.shape = shape;
  node.dataset.angle = String(rotation);
  node.style.backgroundColor = color;
  if (outline === false) node.style.boxShadow = "none";
  else if (typeof outline === "string") node.style.boxShadow = `0 0 0 1px ${resolveColor(outline) || outline}`;
  if (rotation) node.style.transform = `${node.style.transform} rotate(${rotation}deg)`;
  if (shape !== "circle") {
    node.classList.add("et-shaped-marker");
    node.style.backgroundColor = "transparent";
    node.style.color = color;
    node.style.boxShadow = "none";
    node.style.borderRadius = "0";
    node.append(markerGraphic({shape, color: "currentColor", outline}));
  }
  return node;
}

const glyphs = {
  "●": ["circle", false], "○": ["circle", true], "■": ["square", false], "□": ["square", true],
  "▲": ["triangle", false], "△": ["triangle", true], "▼": ["triangle", false, 180],
  "◆": ["diamond", false], "◇": ["diamond", true], "★": ["star", false], "☆": ["star", true],
  "+": ["cross", false], "✚": ["cross", false], "×": ["cross", false, 45], "✕": ["cross", false, 45],
};

/** Recognize familiar geometric glyphs while leaving arbitrary text/emoji intact. */
export function symbolGeometry(options, on) {
  const glyph = on ? options.symbol || "●" : options.empty ?? options.symbol ?? "●";
  const known = Object.hasOwn(glyphs, glyph) ? glyphs[glyph] : null;
  if (options.shape) return {shape: options.shape, angle: options.angle || 0, hollow: !on && Boolean(options.empty && known?.[1])};
  return known ? {shape: known[0], hollow: known[1], angle: (options.angle || 0) + (known[2] || 0)} : null;
}
