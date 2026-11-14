// A numeric lookup shared by spatial paints and individual marker samples.
import {createColorScale, getColorForValue} from "./color.js";

function gradientScale(enc, view) {
  view.gradientScales ||= new Map();
  const opts = enc.gradient;
  if (!view.gradientScales.has(opts)) {
    const domain = view.col.domain && typeof view.col.domain === "object" ? view.col.domain : {};
    view.gradientScales.set(opts, createColorScale([], {
      colorPalette: opts.color_scale ?? domain.palette, colorStops: opts.color_stops,
      min: opts.min ?? view.lo, max: opts.max ?? view.hi, midpoint: opts.midpoint, mode: opts.scale_mode,
    }));
  }
  return view.gradientScales.get(opts);
}

export function gradientColor(enc, view, value, fallback) {
  if (!enc.gradient) return fallback;
  const scale = gradientScale(enc, view);
  const inferredConstant = view.lo === view.hi && enc.gradient.min == null && enc.gradient.max == null && !enc.gradient.color_stops;
  return getColorForValue(inferredConstant ? (scale.minValue + scale.maxValue) / 2 : value, scale);
}

/** Numeric colors are cropped to the visible span, never restarted per mark. */
export function gradientPaint(enc, view, left, right, fallback) {
  const colorAt = value => gradientColor(enc, view, value, fallback);
  const valueAt = percent => {
    const t = (view.reverse ? 100 - percent : percent) / 100;
    return view.col.scale?.transform === "log" && view.lo > 0 && view.hi > view.lo
      ? view.lo * Math.pow(view.hi / view.lo, t) : view.lo + t * (view.hi - view.lo);
  };
  const at = position => colorAt(valueAt(position));
  if (!enc.gradient) return {style: {}, colorAt, at};
  const scale = gradientScale(enc, view);
  const positions = new Set([left, right]);
  for (let step = 1; step < 32; step++) positions.add(left + (right - left) * step / 32);
  const anchors = scale.domain.length === scale.colorPalette.length ? scale.domain
    : scale.colorPalette.map((_, index) => scale.minValue + index / (scale.colorPalette.length - 1) * (scale.maxValue - scale.minValue));
  for (const value of anchors) {
    const position = view.pos(value);
    if (position != null && position > left && position < right) positions.add(position);
  }
  const stops = [...positions].sort((a, b) => a - b)
    .map(position => `${at(position)} ${100 * (position - left) / (right - left || 1)}%`);
  return {style: {backgroundColor: "transparent", backgroundImage: `linear-gradient(to right, ${stops.join(", ")})`}, colorAt, at};
}
