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

// A curated set of matplotlib colormaps, each sampled at 9 stops (chroma
// interpolates between them, so this is visually the 256-entry LUT). The
// diverging ones pair with a `midpoint`.
export const COLORMAPS = {
  viridis: ["#440154", "#472d7b", "#3b528b", "#2c728e", "#21918c", "#28ae80", "#5ec962", "#addc30", "#fde725"],
  magma: ["#000004", "#1d1147", "#51127c", "#832681", "#b73779", "#e75263", "#fc8961", "#fec488", "#fcfdbf"],
  plasma: ["#0d0887", "#4c02a1", "#7e03a8", "#aa2395", "#cc4778", "#e66c5c", "#f89540", "#fdc527", "#f0f921"],
  inferno: ["#000004", "#210c4a", "#57106e", "#8a226a", "#bc3754", "#e45a31", "#f98e09", "#f9cb35", "#fcffa4"],
  cividis: ["#00224e", "#1a386f", "#434e6c", "#61656f", "#7d7c78", "#9b9476", "#bcae6c", "#dec958", "#fee838"],
  blues: ["#f7fbff", "#deebf7", "#c6dbef", "#9dcae1", "#6aaed6", "#4191c6", "#2070b4", "#08509b", "#08306b"],
  reds: ["#fff5f0", "#fee0d2", "#fcbba1", "#fc9272", "#fb694a", "#ee3a2c", "#ca181d", "#a30f15", "#67000d"],
  greens: ["#f7fcf5", "#e5f5e0", "#c7e9c0", "#a0d99b", "#73c476", "#40aa5d", "#228a44", "#006c2c", "#00441b"],
  greys: ["#ffffff", "#f0f0f0", "#d9d9d9", "#bdbdbd", "#959595", "#727272", "#515151", "#242424", "#000000"],
  oranges: ["#fff5eb", "#fee6ce", "#fdd0a2", "#fdae6a", "#fd8c3b", "#f16813", "#d84801", "#a53603", "#7f2704"],
  purples: ["#fcfbfd", "#efedf5", "#dadaeb", "#bcbddc", "#9e9ac8", "#807cba", "#6950a3", "#53268f", "#3f007d"],
  bugn: ["#f7fcfd", "#e5f5f9", "#ccece6", "#98d8c9", "#65c2a3", "#40ad75", "#228a44", "#006c2c", "#00441b"],
  bupu: ["#f7fcfd", "#e0ecf4", "#bfd3e6", "#9ebcda", "#8c95c6", "#8c6ab1", "#88409c", "#800f7b", "#4d004b"],
  gnbu: ["#f7fcf0", "#e0f3db", "#ccebc5", "#a7ddb5", "#7accc4", "#4db2d3", "#2a8bbe", "#0867ab", "#084081"],
  orrd: ["#fff7ec", "#fee8c8", "#fdd49e", "#fdba83", "#fc8c59", "#ef6447", "#d62f1e", "#b20000", "#7f0000"],
  pubu: ["#fff7fb", "#ece7f2", "#d0d1e6", "#a5bddb", "#73a9cf", "#358fc0", "#056faf", "#04598c", "#023858"],
  rdpu: ["#fff7f3", "#fde0dd", "#fcc5c0", "#fa9eb5", "#f767a1", "#dc3397", "#ad017e", "#790177", "#49006a"],
  ylgn: ["#ffffe5", "#f7fcb9", "#d9f0a3", "#acdd8e", "#77c679", "#40aa5c", "#228343", "#006737", "#004529"],
  ylgnbu: ["#ffffd9", "#edf8b1", "#c6e9b4", "#7ecdbb", "#40b5c4", "#1d90c0", "#225da8", "#243392", "#081d58"],
  ylorbr: ["#ffffe5", "#fff7bc", "#fee390", "#fec34f", "#fe9829", "#eb6f14", "#cb4b02", "#983404", "#662506"],
  ylorrd: ["#ffffcc", "#ffeda0", "#fed976", "#feb24c", "#fd8c3c", "#fc4d2a", "#e2191c", "#bb0026", "#800026"],
  rdbu: ["#67001f", "#bb2a34", "#e58368", "#fbceb7", "#f6f7f7", "#c0dceb", "#68abd0", "#2870b1", "#053061"],
  rdylbu: ["#a50026", "#de402e", "#f98e52", "#fed485", "#feffc0", "#d1ecf4", "#8ec2dc", "#4f81ba", "#313695"],
  rdylgn: ["#a50026", "#de402e", "#f98e52", "#fed481", "#feffbe", "#cbe982", "#84ca66", "#2aa054", "#006837"],
  coolwarm: ["#3b4cc0", "#6282ea", "#8db0fe", "#b9d0f9", "#dddcdc", "#f5c4ac", "#f4987a", "#dd5f4b", "#b40426"],
  bwr: ["#0000ff", "#4040ff", "#8080ff", "#c0c0ff", "#fffefe", "#ffbebe", "#ff7e7e", "#ff3e3e", "#ff0000"],
  spectral: ["#9e0142", "#dd4a4c", "#f98e52", "#fed481", "#ffffbe", "#d6ee9b", "#86cfa5", "#3d95b8", "#5e4fa2"],
  piyg: ["#8e0152", "#cb3289", "#e897c4", "#fad6ea", "#f7f7f6", "#d9f0bc", "#9acd61", "#589b28", "#276419"],
  prgn: ["#40004b", "#7f3c8d", "#ae8bbd", "#dec9e2", "#f6f7f6", "#cbeac5", "#7ec37f", "#298440", "#00441b"],
  brbg: ["#543005", "#995d13", "#cfa256", "#f1dfb3", "#f4f5f5", "#b4e2db", "#58b0a7", "#0c7169", "#003c30"],
};

/** Every named scale: the Evidence presets plus the matplotlib colormaps. */
export const COLOR_SCALES = { ...COLOR_PRESETS, ...COLORMAPS };

// matplotlib's Tableau palette (`tab:*`), which `C0`..`C9` index, plus its
// single-letter BASE_COLORS. `resolveColor` turns any of these into hex.
const TABLEAU = [
  ["tab:blue", "#1f77b4"],
  ["tab:orange", "#ff7f0e"],
  ["tab:green", "#2ca02c"],
  ["tab:red", "#d62728"],
  ["tab:purple", "#9467bd"],
  ["tab:brown", "#8c564b"],
  ["tab:pink", "#e377c2"],
  ["tab:gray", "#7f7f7f"],
  ["tab:olive", "#bcbd22"],
  ["tab:cyan", "#17becf"],
];
export const NAMED_COLORS = {
  ...Object.fromEntries(TABLEAU),
  b: "#0000ff",
  g: "#008000",
  r: "#ff0000",
  c: "#00bfbf",
  m: "#bf00bf",
  y: "#bfbf00",
  k: "#000000",
  w: "#ffffff",
};
TABLEAU.forEach(([, hex], index) => {
  NAMED_COLORS[`c${index}`] = hex;
});

/** Resolve a matplotlib colour name (`tab:blue`, `C0`, `k`) to hex; anything else is returned as-is. */
export function resolveColor(value) {
  if (typeof value !== "string") return value;
  return NAMED_COLORS[value.toLowerCase()] ?? value;
}

function resolvePalette(palette) {
  if (typeof palette !== "string") return palette;
  return COLOR_SCALES[palette.toLowerCase()];
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
    const validColors = (resolvePalette(colorPalette) || []).filter(isValidColor);
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

/**
 * Split a diverging stack into its left and right arms. Categories before the
 * ``diverge_at`` segment grow left; those after grow right; the pivot segment
 * is halved across the origin.
 */
export function divergingTotals(encodings, row) {
  const pivot = encodings.findIndex((enc) => enc.source === encodings[0].diverge_at);
  let left = 0;
  let right = 0;
  encodings.forEach((enc, index) => {
    const num = Number(row[enc.source]);
    const value = isFinite(num) && num > 0 ? num : 0;
    if (index < pivot) left += value;
    else if (index > pivot) right += value;
    else {
      left += value / 2;
      right += value / 2;
    }
  });
  return { left, right };
}

/** Compute per-column visualization ranges (bar / color / chip) over data rows. */
export function calculateVizRanges(columns, rows) {
  const ranges = new Map();
  for (const col of columns) {
    if (col.encodings && col.encodings.length) {
      // A marks column shares one scale across every encoding's sources.
      const stacked = col.encodings.some((enc) => enc.kind === "stacked_bar");
      const diverging = stacked && col.encodings.some((enc) => enc.diverge_at);
      const strip = col.encodings.some((enc) => enc.kind === "strip");
      const distribution = col.encodings.some((enc) => enc.kind === "distribution");
      const scatter = col.encodings.some((enc) => enc.kind === "points");
      let min = Infinity;
      let max = -Infinity;
      for (const row of rows) {
        if (row.render_type === "row_total" || row.render_type === "row_subtotal") continue;
        if (scatter) {
          // An array-of-points column shares an axis across its observations.
          for (const enc of col.encodings) {
            const raw = row[enc.source];
            if (!Array.isArray(raw)) continue;
            for (const item of raw) {
              const value = item && typeof item === "object" ? (item.value ?? item.x ?? item.y) : item;
              const num = Number(value);
              if (isFinite(num)) {
                min = Math.min(min, num);
                max = Math.max(max, num);
              }
            }
          }
          continue;
        }
        if (distribution) {
          // A density band shares an ordered x axis across rows.
          for (const enc of col.encodings) {
            const raw = row[enc.source];
            if (!Array.isArray(raw)) continue;
            for (const item of raw) {
              const num = Number(item && item[enc.x]);
              if (item && item[enc.x] != null && isFinite(num)) {
                min = Math.min(min, num);
                max = Math.max(max, num);
              }
            }
          }
          continue;
        }
        if (strip) {
          // A positioned strip shares a time/value axis across all rows.
          for (const enc of col.encodings) {
            const raw = row[enc.source];
            if (!Array.isArray(raw)) continue;
            for (const item of raw) {
              if (!item || typeof item !== "object") continue;
              for (const key of ["start", "position", "end", "finish"]) {
                const num = Number(item[key]);
                if (isFinite(num)) {
                  min = Math.min(min, num);
                  max = Math.max(max, num);
                }
              }
            }
          }
          continue;
        }
        if (diverging) {
          // A diverging stack is read against the larger of its two arms.
          const arms = divergingTotals(col.encodings, row);
          const span = Math.max(Math.abs(arms.left), Math.abs(arms.right));
          if (span > 0) {
            min = 0;
            max = Math.max(max, span);
          }
          continue;
        }
        if (stacked) {
          // A stack's scale is its cumulative total, not its individual parts.
          let total = 0;
          for (const enc of col.encodings) {
            const num = Number(row[enc.source]);
            if (isFinite(num) && num > 0) total += num;
          }
          if (total > 0) {
            min = 0;
            max = Math.max(max, total);
          }
          continue;
        }
        for (const enc of col.encodings) {
          const fields = [enc.source, enc.high];
          if (enc.parts) fields.push(...Object.values(enc.parts));
          for (const field of fields) {
            const raw = field == null ? null : row[field];
            const num = Number(raw);
            if (raw !== null && raw !== undefined && isFinite(num)) {
              min = Math.min(min, num);
              max = Math.max(max, num);
            }
          }
          if (enc.outliers && Array.isArray(row[enc.outliers])) {
            for (const outlier of row[enc.outliers]) {
              const num = Number(outlier);
              if (isFinite(num)) {
                min = Math.min(min, num);
                max = Math.max(max, num);
              }
            }
          }
        }
      }
      if (min !== Infinity && max !== -Infinity) ranges.set(col.name, { min, max });
      continue;
    }
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
  if (typeof opts.color_scale === "string" && !COLOR_SCALES[opts.color_scale.toLowerCase()]) {
    throw new Error(
      `Unknown colour scale '${opts.color_scale}'. Use one of ${Object.keys(COLOR_SCALES).sort().join(", ")}, or a list of colours.`,
    );
  }
  return createColorScale([], {
    colorPalette: resolvePalette(opts.color_scale),
    colorStops: opts.color_stops,
    defaultColorScale: resolvePalette(defaultColorScale) ?? FALLBACK_COLOR_SCALE,
    min: opts.min ?? range.min,
    max: opts.max ?? range.max,
    midpoint: opts.midpoint,
    mode: opts.scale_mode ?? "lch",
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
