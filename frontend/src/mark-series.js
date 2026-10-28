// Names and fills belong to the marks, independently of their drawn labels.
import { resolveColor } from "./color.js";
import { columnHeading } from "./headers.js";

export const DEFAULT_MARK_COLOR = "var(--et-accent, #2563eb)";

/** Resolve the same fill for a mark and its legend swatch. */
export function markColor(enc, row, fallback = DEFAULT_MARK_COLOR, isNegative = Number(row?.[enc.source]) < 0) {
  if (isNegative) {
    const negative = resolveColor(enc.color_negative) || resolveColor(row?.[enc.color_negative_column]);
    if (negative) return negative;
  }
  if (enc.color_column && row) {
    const resolved = resolveColor(row[enc.color_column]);
    if (resolved) return resolved;
  }
  return resolveColor(enc.color) || fallback;
}

/** Ordered series identities, including category keys within a strip. */
export function markSeries(column, columns = [], options = {}) {
  const labels = column.legend;
  const series = (column.encodings || []).flatMap(enc => enc.kind === "strip"
    ? Object.entries(enc.colors || {}).map(([key, color]) => ({key, color: resolveColor(color) || DEFAULT_MARK_COLOR, enc}))
    : [{key: enc.source, color: markColor(enc), enc}]);
  return series.map((item, index) => {
    const source = columns.find(col => col !== column && col.name === item.key);
    const automatic = item.enc.kind === "strip" ? item.key : columnHeading(source || {name: item.key}, options);
    return {...item, label: Array.isArray(labels) && index < labels.length ? labels[index]
      : labels && typeof labels === "object" && Object.hasOwn(labels, item.key) ? labels[item.key] : automatic};
  });
}
