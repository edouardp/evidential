import { chroma } from "./color.js";

const svgNS = "http://www.w3.org/2000/svg";
// Symbol.for shares the counter across independently loaded widget bundles.
const counter = Symbol.for("evidential.sparklineGradientCounter");

/** Paint in data-y space, never across x intervals or an individual path's box. */
export function verticalGradient(svg, lookup, {min, max, top, bottom, origin, opacity = 1}) {
  const gradient = document.createElementNS(svgNS, "linearGradient");
  const id = `et-sparkline-gradient-${document[counter] = (document[counter] || 0) + 1}`;
  gradient.setAttribute("id", id);
  gradient.setAttribute("gradientUnits", "userSpaceOnUse");
  gradient.setAttribute("x1", "0");
  gradient.setAttribute("x2", "0");
  gradient.setAttribute("y1", String(bottom));
  gradient.setAttribute("y2", String(top));
  gradient.setAttribute("spreadMethod", "pad");
  const span = max - min || 1;
  // Sample within each palette interval: preserve exact stop/midpoint positions
  // and approximate the shared LCH lookup with bounded RGB SVG interpolation.
  const anchors = [...new Set([min, max, origin, ...(lookup.breakpoints || [])])]
    .filter(value => value >= min && value <= max).sort((a, b) => a - b);
  const samples = new Set(anchors);
  for (let index = 1; index < anchors.length; index++) {
    const lo = anchors[index - 1], hi = anchors[index];
    const steps = Math.max(1, Math.ceil(32 * (hi - lo) / span));
    for (let step = 1; step < steps; step++) samples.add(lo + step / steps * (hi - lo));
  }
  for (const value of [...samples].sort((a, b) => a - b)) {
    const stop = document.createElementNS(svgNS, "stop");
    stop.setAttribute("offset", String((value - min) / span));
    // Constant paints may be CSS variables; gradients from the numeric lookup
    // are concrete colors. Keep alpha separate for consistent SVG compositing.
    const paint = lookup(value);
    let color = paint, alpha = 1;
    if (chroma.valid(paint)) {
      const parsed = chroma(paint);
      color = parsed.hex("rgb");
      alpha = parsed.alpha();
    }
    const ramp = Array.isArray(opacity)
      ? opacity[0] + (opacity[1] - opacity[0]) * (value < origin
        ? (origin - value) / (origin - min || 1) : (value - origin) / (max - origin || 1))
      : opacity;
    stop.setAttribute("stop-color", color);
    stop.setAttribute("stop-opacity", String(alpha * ramp));
    gradient.append(stop);
  }
  let defs = svg.querySelector("defs");
  if (!defs) {
    defs = document.createElementNS(svgNS, "defs");
    svg.prepend(defs);
  }
  defs.append(gradient);
  return `url(#${id})`;
}
