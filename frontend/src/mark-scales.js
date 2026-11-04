// @ts-check
// Shared coordinate domains, transforms and ticks.
import {numeric} from "./mark-data.js";

/** @param {import('./contracts.js').ScaleColumn} col
 * @param {{min: number, max: number, shared?: boolean} | null} range
 * @returns {import('./contracts.js').MarkDomain}
 */
export function marksDomain(col, range) {
  const scale = col.scale || {};
  if (range?.shared) return {lo: range.min, hi: range.max, span: (range.max - range.min) || 1, transform: scale.transform};
  let lo = scale.domain && scale.domain[0] != null ? Number(scale.domain[0]) : (range?.min ?? 0);
  let hi = scale.domain && scale.domain[1] != null ? Number(scale.domain[1]) : (range?.max ?? 1);
  const hasBar = (col.encodings || []).some((enc) => enc.kind === "bar" || enc.kind === "stacked_bar");
  const bars = (col.encodings || []).filter(enc => enc.kind === "bar");
  const fitToData = bars.length > 0 && bars.every(enc => enc.fit_to_data) && !(col.encodings || []).some(enc => enc.kind === "stacked_bar");
  if (scale.include_zero !== false && hasBar && !fitToData && scale.transform !== "log") {
    if (scale.domain?.[0] == null) lo = Math.min(0, lo);
    if (scale.domain?.[1] == null) hi = Math.max(0, hi);
  }
  // Two-sided layouts accept a 0..magnitude domain or an explicit symmetric
  // signed domain. Their axes, references and overlay points use signed x.
  if ((col.encodings || []).some(enc => enc.center || enc.side || enc.diverge_at) && (!scale.domain || lo >= 0)) {
    hi = Math.max(Math.abs(lo), Math.abs(hi));
    lo = -hi;
  }
  return { lo, hi, span: (hi - lo) || 1, transform: scale.transform };
}

/** Round tick values spanning ``lo..hi`` (for an axis or gridlines).
 * @param {number} lo @param {number} hi @param {number} [count] @param {string | null} [transform]
 */
export function niceTicks(lo, hi, count = 4, transform = null) {
  if (!isFinite(lo) || !isFinite(hi) || hi <= lo) return [];
  if (transform === "log" && lo > 0) {
    // A power-of-ten ladder (with 2x and 5x subdivisions) for a log axis.
    const ticks = [];
    for (let exp = Math.floor(Math.log10(lo)) - 1; exp <= Math.ceil(Math.log10(hi)); exp += 1) {
      for (const multiple of [1, 2, 5]) {
        const value = multiple * Math.pow(10, exp);
        if (value >= lo && value <= hi) ticks.push(Number(value.toPrecision(12)));
      }
    }
    if (ticks.length) return ticks;
  }
  const step0 = (hi - lo) / Math.max(1, count);
  const magnitude = Math.pow(10, Math.floor(Math.log10(step0)));
  const normalized = step0 / magnitude;
  const step = (normalized >= 5 ? 5 : normalized >= 2.5 ? 2.5 : normalized >= 2 ? 2 : 1) * magnitude;
  const ticks = [];
  for (let value = Math.ceil(lo / step) * step; value <= hi + step * 1e-6; value += step) {
    ticks.push(Number(value.toFixed(10)));
  }
  return ticks;
}

/** Log decades/endpoints are labeled; subdivisions reveal logarithmic spacing.
 * @param {number} lo @param {number} hi @param {number} [count] @param {string | null} [transform]
 */
export function axisTicks(lo, hi, count = 4, transform = null) {
  if (transform !== "log") return niceTicks(lo, hi, count, transform).map(value => ({value, major: true}));
  if (!(lo > 0) || !Number.isFinite(hi) || hi <= lo) return [];
  const ticks = new Map([[lo, {value: lo, major: true}], [hi, {value: hi, major: true}]]);
  for (let exponent = Math.floor(Math.log10(lo)); exponent <= Math.ceil(Math.log10(hi)); exponent++) {
    for (let multiple = 1; multiple <= 9; multiple++) {
      const value = Number((multiple * Math.pow(10, exponent)).toPrecision(12));
      if (value >= lo && value <= hi && !ticks.has(value)) ticks.set(value, {value, major: multiple === 1});
    }
  }
  return [...ticks.values()].sort((a, b) => a.value - b.value);
}

/** A position function mapping a value in ``lo..hi`` to 0..100 (percent).
 * @param {number} lo @param {number} hi @param {string | null} transform @param {boolean} [reverse]
 */
export function scalePosition(lo, hi, transform, reverse = false) {
  const position = markScale(lo, hi, transform);
  return (/** @type {unknown} */ value) => {
    const pct = position(value);
    return pct == null ? null : reverse ? 100 - pct : pct;
  };
}

/** @param {number} lo @param {number} hi @param {string | null} transform */
function markScale(lo, hi, transform) {
  if (transform === "log" && lo > 0 && hi > lo) {
    const l0 = Math.log(lo);
    const lspan = (Math.log(hi) - l0) || 1;
    return (/** @type {unknown} */ value) => {
      const num = numeric(value);
      if (num == null || num <= 0) return null;
      return ((Math.log(num) - l0) / lspan) * 100;
    };
  }
  const span = (hi - lo) || 1;
  return (/** @type {unknown} */ value) => {
    const num = numeric(value);
    return num != null ? ((num - lo) / span) * 100 : null;
  };
}

