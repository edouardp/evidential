import { searchRows, sortRows, visibleRows, columnStats, decimalPlaces } from "./rows.js";
import { orderedColumns } from "./headers.js";
import { calculateVizRanges, calculateFormatRanges, buildColorVizScale } from "./color.js";
import { applySharedDomains } from "./shared-domains.js";
import { prepareChangeScales } from "./change-sparkline.js";
import { projectLegacy } from "./row-layout.js";

/** One current dataset projection per widget; pagination/selection do not invalidate it. */
export class RowPipeline {
  constructor() { this.clear(); }

  clear() {
    this.cache = null;
    this.visibility = null;
  }

  get({rows, columns: allColumns, options, search, hidden, sort, rowLayout}) {
    const key = [rows, allColumns, options, search, JSON.stringify([...hidden].sort()), sort?.column, sort?.direction, rowLayout];
    if (this.cache && key.every((part, index) => Object.is(part, this.cache.key[index]))) return this.cache.result;
    const columns = orderedColumns(allColumns.filter((column) => !hidden.has(column.name)), options);
    const searched = searchRows(rows, allColumns, search, hidden);
    const sorted = sortRows(searched, allColumns, sort);
    const ranges = applySharedDomains(allColumns, sorted, calculateVizRanges(columns, sorted));
    const formatRanges = calculateFormatRanges(columns, sorted);
    const decimals = new Map();
    if (options.align_decimals) {
      for (const column of columns) {
        if (column.type !== "number" || column.align_decimals === false) continue;
        let max = null;
        for (const row of sorted) {
          const places = decimalPlaces(row[column.name]);
          if (places !== null) max = max === null ? places : Math.max(max, places);
        }
        if (max !== null) decimals.set(column.name, max);
      }
    }
    const colorScales = new Map();
    for (const column of columns) {
      if ((column.viz === "color" || column.viz === "chip") && ranges.has(column.name)) {
        const scale = buildColorVizScale(column, ranges.get(column) || ranges.get(column.name), options.color_scale);
        colorScales.set(column, scale);
        colorScales.set(column.name, scale);
      }
    }
    const result = {
      columns, sorted, ranges, formatRanges, decimals, colorScales,
      changeScales: prepareChangeScales(columns, sorted, ranges), sourceRows: rows, rowLayout,
      hasGroups: !!rowLayout?.legacy || rows.some((row) => row.render_type && row.render_type !== "cell_data"),
      dimCount: (rowLayout?.legacy || []).reduce((max, token) => Math.max(max, token.row?.__level || 0),
        rows.reduce((max, row) => Math.max(max, row.__level ?? 0), 0)),
      stats: options.column_stats ? columnStats(columns, rows) : null,
    };
    this.cache = {key, result};
    this.visibility = null;
    return result;
  }

  visible(result, groupVersion, isCollapsed) {
    if (this.visibility?.result === result && this.visibility.groupVersion === groupVersion) return this.visibility;
    const rows = result.rowLayout?.legacy
      ? projectLegacy(result.rowLayout, result.sourceRows, result.sorted, isCollapsed)
      : visibleRows(result.sorted, isCollapsed);
    this.visibility = {result, groupVersion, rows,
      hasGroups: rows.some((row) => row.render_type && row.render_type !== "cell_data")};
    return this.visibility;
  }
}
