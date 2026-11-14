import {createColorScale, getColorForValue} from "./color.js";

/** A numeric x gradient, cropped to the visible interval without restarting it. */
export function rangePaint(enc, view, left, right, fallback) {
  const rounded = enc.cap === "round";
  const raw = [view.pos(view.row[enc.source]), view.pos(view.row[enc.high])];
  const radius = position => rounded && raw.some(value => value === position) ? "999px" : "0";
  const style = rounded ? {borderRadius: `${radius(left)} ${radius(right)} ${radius(right)} ${radius(left)}`} : {};
  if (!enc.gradient) return {style, colorAt: () => fallback, at: () => fallback};
  const opts = enc.gradient;
  const scale = createColorScale([], {colorPalette: opts.color_scale, colorStops: opts.color_stops,
    min: opts.min ?? view.lo, max: opts.max ?? view.hi, midpoint: opts.midpoint, mode: opts.scale_mode});
  const colorAt = value => getColorForValue(value, scale);
  const valueAt = percent => {
    const t = (view.reverse ? 100 - percent : percent) / 100;
    return view.col.scale?.transform === "log" && view.lo > 0 && view.hi > view.lo
      ? view.lo * Math.pow(view.hi / view.lo, t) : view.lo + t * (view.hi - view.lo);
  };
  const positions = new Set([left, right]);
  // Bound the work per mark; include exact color anchors so narrow bands survive.
  for (let step = 1; step < 32; step++) positions.add(left + (right - left) * step / 32);
  const anchors = scale.domain.length === scale.colorPalette.length ? scale.domain
    : scale.colorPalette.map((_, index) => scale.minValue + index / (scale.colorPalette.length - 1) * (scale.maxValue - scale.minValue));
  for (const value of anchors) {
    const position = view.pos(value);
    if (position != null && position > left && position < right) positions.add(position);
  }
  const stops = [...positions].sort((a, b) => a - b)
    .map(position => `${colorAt(valueAt(position))} ${100 * (position - left) / (right - left || 1)}%`);
  return {style: {...style, backgroundColor: "transparent", backgroundImage: `linear-gradient(to right, ${stops.join(", ")})`}, colorAt, at: position => colorAt(valueAt(position))};
}
