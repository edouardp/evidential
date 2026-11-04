import { buildDomainColorScale, createColorScale, getColorForValue } from "./color.js";
import { changeColorScale } from "./change-sparkline.js";
import { sparklinePoints } from "./sparkline-data.js";

/** The ordinary .color() declaration maps y to a palette, independently of geometry. */
export function sparklineColorScale(column, values = [], sharedRange, defaultPalette) {
  const opts = column.sparkline_options || {};
  const colors = column.color_options || {};
  const domain = typeof column.domain === "object" ? column.domain : {};
  const palette = domain.palette || colors.color_scale || opts.color_scale;
  const gradient = palette || Object.keys(colors).length;
  const min = colors.min ?? opts.color_domain?.[0];
  const max = colors.max ?? opts.color_domain?.[1];
  const change = opts.type === "change";
  if (!gradient) return change ? changeColorScale(opts, []) : null;
  if (sharedRange?.shared) {
    const scale = buildDomainColorScale({...domain, midpoint: domain.midpoint ?? colors.midpoint}, sharedRange,
      palette || defaultPalette, colors.scale_mode);
    const constant = !domain.neutral_range && sharedRange.min === sharedRange.max;
    return colorLookup(scale, constant, domain.neutral_range
      ? [sharedRange.min, ...domain.neutral_range, sharedRange.max] : undefined);
  }
  if (change && !colors.color_stops) {
    const steady = opts.steady || [0, 0];
    let low = min ?? steady[0], high = max ?? steady[1];
    for (const value of values) {
      if (min == null) low = Math.min(low, value);
      if (max == null) high = Math.max(high, value);
    }
    return changeColorScale({...opts, color_scale: palette || defaultPalette || ["#dbeafe", "#1e40af"],
      color_domain: [low, high]}, [], colors.scale_mode);
  }
  const scale = createColorScale(values, {colorPalette: palette || defaultPalette,
    colorStops: colors.color_stops, min, max, midpoint: colors.midpoint, mode: colors.scale_mode});
  if (!scale) return null;
  const constant = !colors.color_stops && min == null && max == null && values.length && values.every(value => value === values[0]);
  return colorLookup(scale, constant);
}

/** Keep palette anchors available to the SVG painter, including narrow bands. */
function colorLookup(scale, constant, anchors) {
  const lookup = value => getColorForValue(constant ? (scale.minValue + scale.maxValue) / 2 : value, scale);
  lookup.breakpoints = anchors || (scale.domain.length === scale.colorPalette.length ? scale.domain
    : scale.colorPalette.map((_, index) => scale.minValue + index / (scale.colorPalette.length - 1) * (scale.maxValue - scale.minValue)));
  return lookup;
}

/** Cache inferred color bounds over matching detail rows, before pagination. */
export function prepareSparklineScales(columns, rows, ranges, defaultPalette) {
  const scales = new Map();
  for (const column of columns) {
    if (column.viz !== "sparkline") continue;
    const opts = column.sparkline_options || {}, colors = column.color_options || {};
    const values = [];
    if (!ranges?.get(column)?.shared && !colors.color_stops &&
      (colors.color_scale || opts.color_scale || Object.keys(colors).length) &&
      !(opts.color_domain || (colors.min != null && colors.max != null))) {
      let min = Infinity, max = -Infinity;
      for (const row of rows) {
        if (row.render_type && row.render_type !== "cell_data") continue;
        for (const [, value] of sparklinePoints(row[column.name], opts)) {
          if (value != null) { min = Math.min(min, value); max = Math.max(max, value); }
        }
      }
      if (min !== Infinity) values.push(min, max);
    }
    const scale = sparklineColorScale(column, values, ranges?.get(column), defaultPalette);
    if (scale) scales.set(column, scale);
  }
  return scales;
}
