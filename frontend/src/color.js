// Color scale utilities, ported from Evidence's color-scale-utils.
import chroma from "chroma-js";

export const FALLBACK_COLOR_SCALE = ["#dbeafe", "#1e40af"];

// Named colour-scale presets (Evidence's `colorScale="green"` etc.).
export const COLOR_PRESETS = {
  green: ["#f0fdf4", "#16a34a"],
  blue: ["#eff6ff", "#2563eb"],
  red: ["#fef2f2", "#dc2626"],
  orange: ["#fff7ed", "#ea580c"],
  purple: ["#faf5ff", "#9333ea"],
  grey: ["#f8fafc", "#334155"],
  gray: ["#f8fafc", "#334155"],
};

function resolvePalette(palette) {
  if (typeof palette === "string") return COLOR_PRESETS[palette.toLowerCase()];
  return palette;
}

function isValidColor(color) {
  try {
    chroma(color);
    return true;
  } catch {
    return false;
  }
}

function normalizeColorStops(stops) {
  if (!Array.isArray(stops) || stops.length < 2) return null;
  const valid = stops.filter(
    (s) => s && typeof s.value === "number" && isFinite(s.value) &&
      typeof s.color === "string" && isValidColor(s.color)
  );
  if (valid.length < 2) return null;
  const sorted = [...valid].sort((a, b) => a.value - b.value);
  const deduped = [];
  for (const stop of sorted) {
    if (deduped.length === 0 || stop.value > deduped[deduped.length - 1].value) {
      deduped.push(stop);
    }
  }
  return deduped.length >= 2 ? deduped : null;
}

function isStrictlyIncreasing(arr) {
  for (let i = 1; i < arr.length; i++) if (!(arr[i] > arr[i - 1])) return false;
  return true;
}

function buildDivergingScale(min, max, mid, palette) {
  const n = palette.length;
  const midIdx = (n - 1) / 2;
  if (mid > min && mid < max) {
    const domain = new Array(n);
    for (let i = 0; i < n; i++) {
      if (i < midIdx) domain[i] = min + (i / midIdx) * (mid - min);
      else if (i > midIdx) domain[i] = mid + ((i - midIdx) / (n - 1 - midIdx)) * (max - mid);
      else domain[i] = mid;
    }
    return isStrictlyIncreasing(domain) ? { palette, domain, midpoint: mid } : null;
  }
  if (mid <= min) {
    const sub = palette.slice(Math.floor(midIdx));
    if (sub.length < 2) return null;
    const domain = sub.map((_, i) => mid + (i / (sub.length - 1)) * (max - mid));
    return isStrictlyIncreasing(domain) ? { palette: sub, domain, midpoint: null } : null;
  }
  const sub = palette.slice(0, Math.ceil(midIdx) + 1);
  if (sub.length < 2) return null;
  const domain = sub.map((_, i) => min + (i / (sub.length - 1)) * (mid - min));
  return isStrictlyIncreasing(domain) ? { palette: sub, domain, midpoint: null } : null;
}

export function createColorScale(values, options) {
  const {
    colorPalette,
    defaultColorScale = FALLBACK_COLOR_SCALE,
    mode = "lch",
    min: minOverride,
    max: maxOverride,
    midpoint,
    colorStops,
  } = options;

  const stops = normalizeColorStops(colorStops);
  if (stops) {
    const stopColors = stops.map((s) => s.color);
    const stopValues = stops.map((s) => s.value);
    const scale = chroma.scale(stopColors).domain(stopValues).mode(mode);
    return {
      scale,
      kind: "stops",
      colorPalette: stopColors,
      minValue: stopValues[0],
      maxValue: stopValues[stopValues.length - 1],
      domain: stopValues,
      midpoint: null,
    };
  }

  const validValues = values.filter((v) => !isNaN(v) && isFinite(v));
  const hasMin = typeof minOverride === "number" && isFinite(minOverride);
  const hasMax = typeof maxOverride === "number" && isFinite(maxOverride);
  if (validValues.length === 0 && !(hasMin && hasMax)) return null;

  let minValue = hasMin ? minOverride : Math.min(...validValues);
  let maxValue = hasMax ? maxOverride : Math.max(...validValues);
  if (!(minValue < maxValue)) {
    if (minValue === maxValue) maxValue = minValue + 1;
    else [minValue, maxValue] = [maxValue, minValue];
  }

  let finalPalette;
  if (colorPalette && colorPalette.length > 0) {
    const validColors = resolvePalette(colorPalette).filter(isValidColor);
    if (validColors.length >= 2) finalPalette = validColors;
    else if (validColors.length === 1) finalPalette = [defaultColorScale[0] ?? "#ffffff", validColors[0]];
    else finalPalette = defaultColorScale;
  } else {
    finalPalette = defaultColorScale;
  }

  const hasMidpoint = typeof midpoint === "number" && isFinite(midpoint);
  const supportsMidpoint = hasMidpoint && finalPalette.length >= 3;

  let scalePalette = finalPalette;
  let domain = [minValue, maxValue];
  let finalMidpoint = null;
  let kind = "linear";

  if (supportsMidpoint) {
    const diverging = buildDivergingScale(minValue, maxValue, midpoint, finalPalette);
    if (diverging) {
      scalePalette = diverging.palette;
      domain = diverging.domain;
      finalMidpoint = diverging.midpoint;
      kind = "diverging";
    }
  }

  const scale = chroma.scale(scalePalette).domain(domain).mode(mode);
  return {
    scale,
    kind,
    colorPalette: scalePalette,
    minValue,
    maxValue,
    domain,
    midpoint: finalMidpoint,
  };
}

export function getColorForValue(value, scaleResult) {
  if (!isFinite(value) || isNaN(value)) return scaleResult.colorPalette[0];
  return scaleResult.scale(value).hex();
}

export function colorStylesFromHex(colorValue) {
  try {
    const bg = chroma(colorValue);
    const color = chroma.contrast(bg, "#000000") > chroma.contrast(bg, "#ffffff") ? "#000000" : "#ffffff";
    const isCellDark = bg.luminance() < 0.5;
    const borderBottomColor = (isCellDark ? bg.brighten(0.5) : bg.darken(0.5)).hex();
    return {
      backgroundColor: bg.hex(),
      color,
      borderBottomColor,
      topBorderColor: isCellDark ? "rgb(75 85 99)" : "rgb(156 163 175)",
    };
  } catch {
    return null;
  }
}

/** Black or white text for a chip, by background luminance: white on darker
 *  backgrounds, black on lighter ones. */
export function contrastTextColor(colorValue) {
  try {
    return chroma(colorValue).luminance() < 0.5 ? "#ffffff" : "#000000";
  } catch {
    return "inherit";
  }
}

/** Compute per-column visualization ranges (bar / color / chip) over data rows. */
export function calculateVizRanges(columns, rows) {
  const ranges = new Map();
  for (const col of columns) {
    if (col.viz !== "bar" && col.viz !== "color" && col.viz !== "chip") continue;
    const opts = col.color_options || {};
    const scaleColumn =
      (col.viz === "color" || col.viz === "chip") && opts.scale_column
        ? opts.scale_column
        : col.name;
    let min = Infinity;
    let max = -Infinity;
    for (const row of rows) {
      if (row.render_type === "row_total") continue;
      if (row.render_type === "row_subtotal" && col.viz_include_subtotals === false) continue;
      const raw = row[scaleColumn];
      if (raw === null || raw === undefined) continue;
      const num = Number(raw);
      if (!isNaN(num) && isFinite(num)) {
        min = Math.min(min, num);
        max = Math.max(max, num);
      }
    }
    if (min !== Infinity && max !== -Infinity) {
      if (opts.min != null && isFinite(opts.min)) min = opts.min;
      if (opts.max != null && isFinite(opts.max)) max = opts.max;
      ranges.set(col.name, { min, max });
    }
  }
  return ranges;
}

/** Compute ranges for auto-scaling base formats (num/usd/pct/...). */
export function calculateFormatRanges(columns, rows) {
  const ranges = new Map();
  for (const col of columns) {
    if (!col.fmt || col.fmt.length !== 3) continue;
    let min = Infinity;
    let max = -Infinity;
    for (const row of rows) {
      if (row.render_type === "row_total" || row.render_type === "row_subtotal") continue;
      const num = Number(row[col.name]);
      if (!isNaN(num) && isFinite(num)) {
        min = Math.min(min, num);
        max = Math.max(max, num);
      }
    }
    if (min !== Infinity && max !== -Infinity) ranges.set(col.name, { min, max });
  }
  return ranges;
}

export function buildColorVizScale(col, range, defaultColorScale) {
  const opts = col.color_options || {};
  return createColorScale([], {
    colorPalette: resolvePalette(opts.color_scale),
    colorStops: opts.color_stops,
    defaultColorScale: defaultColorScale ?? FALLBACK_COLOR_SCALE,
    min: opts.min,
    max: opts.max,
    midpoint: opts.midpoint,
  });
}

/** Resolve the background+border+text styles for a color-viz cell. */
export function calculateColorStyles(col, row, range, scale) {
  const opts = col.color_options || {};
  const conditional = opts.conditional_colors;
  if (conditional && conditional in row) {
    const v = row[conditional];
    if (v && typeof v === "string") return colorStylesFromHex(v);
    return null;
  }
  const scaleColumn = opts.scale_column || col.name;
  const scaleValue = Number(row[scaleColumn]);
  if (isNaN(scaleValue)) return null;
  if (!scale) return null;

  let queryValue = scaleValue;
  if (scale.kind !== "stops") {
    const effectiveMin = opts.min != null && isFinite(opts.min) ? opts.min : range.min;
    const effectiveMax = opts.max != null && isFinite(opts.max) ? opts.max : range.max;
    if (Math.abs(effectiveMax - effectiveMin) < 1e-10) {
      queryValue = (scale.minValue + scale.maxValue) / 2;
    }
  }
  return colorStylesFromHex(getColorForValue(queryValue, scale));
}

export { chroma };
