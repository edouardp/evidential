import {gradientPaint} from "./mark-gradient.js";

/** Ranges add endpoint rounding to the common numeric gradient paint. */
export function rangePaint(enc, view, left, right, fallback) {
  const rounded = enc.cap === "round";
  const raw = [view.pos(view.row[enc.source]), view.pos(view.row[enc.high])];
  const radius = position => rounded && raw.some(value => value === position) ? "999px" : "0";
  const style = rounded ? {borderRadius: `${radius(left)} ${radius(right)} ${radius(right)} ${radius(left)}`} : {};
  const paint = gradientPaint(enc, view, left, right, fallback);
  return {...paint, style: {...style, ...paint.style}};
}
