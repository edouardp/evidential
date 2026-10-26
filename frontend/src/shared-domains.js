import { encodingRange, numeric } from "./mark-data.js";
import { sparklinePoints } from "./sparkline-data.js";

/** Pool numeric observations without coupling domain membership to display groups. */
function memberRange(column, rows) {
  if (column.encodings?.length) return encodingRange(column, rows);
  let min = Infinity, max = -Infinity;
  const add = raw => {
    const value = numeric(raw);
    if (value == null) return;
    min = Math.min(min, value);
    max = Math.max(max, value);
  };
  for (const row of rows) {
    if (row.render_type && row.render_type !== "cell_data") continue;
    if (column.viz === "sparkline") {
      for (const [, value] of sparklinePoints(row[column.name], column.sparkline_options || {})) add(value);
    } else add(row[column.color_options?.scale_column || column.name]);
  }
  if (column.viz === "sparkline" && min !== Infinity) add(column.sparkline_options?.reference);
  return min === Infinity ? null : {min, max};
}

/** Enrich the existing range map; hidden members continue to anchor their domain. */
export function applySharedDomains(columns, rows, ranges) {
  const groups = new Map();
  for (const column of columns) {
    if (!column.domain) continue;
    const spec = typeof column.domain === "string" ? {name: column.domain} : column.domain;
    if (!groups.has(spec.name)) groups.set(spec.name, {spec: {...spec}, members: []});
    const group = groups.get(spec.name);
    Object.assign(group.spec, spec);
    group.members.push(column);
  }
  for (const {spec, members} of groups.values()) {
    let min = Infinity, max = -Infinity;
    let zero = false, centered = false;
    for (const column of members) {
      const range = memberRange(column, rows);
      if (range) { min = Math.min(min, range.min); max = Math.max(max, range.max); }
      const encodings = column.encodings || [];
      centered ||= column.bar_options?.center || encodings.some(enc => enc.center || enc.side || enc.diverge_at);
      zero ||= column.viz === "bar" || encodings.some(enc => ["bar", "stacked_bar"].includes(enc.kind) && !enc.fit_to_data)
        || (["bar", "area"].includes(column.sparkline_options?.type) && !column.sparkline_options.fit_to_data);
    }
    if (min === Infinity) { min = 0; max = 1; }
    if (spec.bounds) [min, max] = spec.bounds;
    else {
      if (spec.include_zero ?? zero) { min = Math.min(min, 0); max = Math.max(max, 0); }
      if (spec.neutral_range) { min = Math.min(min, spec.neutral_range[0]); max = Math.max(max, spec.neutral_range[1]); }
    }
    if (centered) { max = Math.max(Math.abs(min), Math.abs(max)); min = -max; }
    const range = {min, max, shared: true};
    for (const column of members) {
      ranges.set(column, range);
      ranges.set(column.name, range);
    }
  }
  return ranges;
}
