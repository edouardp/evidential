// An uncertainty band has one physical height. Density determines alpha only.
import { h } from "./dom.js";

const number = value => typeof value === "number" && Number.isFinite(value);

/** Read continuous support from the precomputed contract. Never fit or sort. */
export function readDensity(raw, spec) {
  if (!Array.isArray(raw) || !spec) return [];
  const runs = [];
  let run = [];
  let previous = -Infinity;
  const gap = () => { if (run.length) runs.push(run); run = []; };
  for (const sample of raw) {
    const x = sample?.[spec.x], density = sample?.[spec.y];
    if (number(x)) {
      if (x <= previous) return [];
      previous = x;
    }
    if (!number(x) || !number(density) || density < 0) { gap(); continue; }
    run.push({x, density});
  }
  gap();
  return runs;
}

/** Geometry is expressed on the SAME horizontal scale as points and axes. */
export function projectBand(runs, spec, position) {
  if (!spec) return [];
  let peak = 0;
  for (const run of runs) for (const sample of run) peak = Math.max(peak, sample.density);
  const ceiling = spec.density_max ?? peak;
  if (!(ceiling > 0) || !(peak > 0)) return [];
  const projected = [];
  for (const run of runs) {
    let stops = [];
    const flush = () => {
      if (stops.length > 1) {
        const left = stops[0].x, width = stops.at(-1).x - left;
        if (width > 0) projected.push({left, width, stops: stops.map(stop => ({
          offset: (stop.x - left) / width * 100, alpha: stop.alpha,
        }))});
      }
      stops = [];
    };
    for (let index = 1; index < run.length; index++) {
      const a = run[index - 1], b = run[index];
      const from = position(a.x), to = position(b.x);
      if (from == null || to == null || !(to > from)) { flush(); continue; }
      const left = Math.max(0, from), right = Math.min(100, to);
      if (!(right > left)) continue;
      const alpha = x => {
        const t = (x - from) / (to - from);
        return Math.min(1, (a.density * (1 - t) + b.density * t) / ceiling);
      };
      if (!stops.length) stops.push({x: left, alpha: alpha(left)});
      // A fixed ceiling creates a plateau; clamping only the endpoint alpha
      // would stretch that fade and misrepresent the supplied density.
      if ((a.density < ceiling && b.density > ceiling) || (a.density > ceiling && b.density < ceiling)) {
        const crossing = from + (ceiling - a.density) / (b.density - a.density) * (to - from);
        if (crossing > left && crossing < right) stops.push({x: crossing, alpha: 1});
      }
      stops.push({x: right, alpha: alpha(right)});
    }
    flush();
  }
  return projected;
}

/** Paint constant-height rectangles; transparent tails reveal the cell below. */
export function renderDensityBand(encoding, row, position, color) {
  const spec = encoding.distribution;
  const runs = projectBand(readDensity(row[encoding.source], spec), spec, position);
  if (!runs.length) return null;
  const band = h("div", {class: "et-mark et-mark-distribution", "aria-hidden": "true",
    style: {height: `${spec.height * 100}%`}});
  for (const run of runs) {
    const mask = run.stops.map(stop => `rgba(0, 0, 0, ${stop.alpha}) ${stop.offset}%`).join(", ");
    band.append(h("div", {class: "et-density-band-run", style: {
      left: `${run.left}%`, width: `${run.width}%`, backgroundColor: color,
      maskImage: `linear-gradient(to right, ${mask})`,
    }}));
  }
  return band;
}
