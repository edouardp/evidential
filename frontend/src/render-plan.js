// Describe one page without constructing DOM or writing renderer/UI state.
import {headerLayout} from "./headers.js";
import {computeRowspans, sectionContinuation} from "./rows.js";

export function buildRenderPlan(processed, visibility, view) {
  const {columns, hasGroups, dimCount} = processed;
  const {options, pageSize, pageIndex, expandedPage, isCollapsed, revision, anchorGroup, selected, emptyRows} = view;
  const displayPage = processed.displayProjection?.page(pageSize, pageIndex, expandedPage,
    {isCollapsed, revision, anchorGroup});
  const pagination = displayPage || view.paginate(visibility.rows, visibility.hasGroups);
  const {rows, start} = pagination;
  const section = options.group_type === "section" && hasGroups && dimCount > 0;
  const layout = headerLayout(columns);
  const isEmpty = displayPage ? displayPage.entries.length === 0 : rows.length === 0;
  const axes = columns.filter(column => column.encodings && column.scale?.axis);
  return {columns, rows, pagination, context: {
    columns: processed.sourceColumns, options,
    ranges: processed.ranges, formatRanges: processed.formatRanges, decimals: processed.decimals,
    colorScales: processed.colorScales, sparklineScales: processed.sparklineScales,
    hasGroups, dimCount, section, accordion: hasGroups && !section && dimCount > 0,
    layout, subcolumns: layout.joins, rowNumbers: !!options.row_numbers, rowNumberBase: start,
    rowspans: section ? computeRowspans(rows, dimCount, options.subtotal_position !== "bottom") : null,
    continuationRow: displayPage ? null : sectionContinuation(visibility.rows, start, rows),
    displayEntries: displayPage?.entries, insetGroups: visibility.insetGroups,
    selected, stats: processed.stats, footnotes: [], isEmpty, emptyRows: isEmpty ? emptyRows : 0,
    emptyMessage: options.empty_message || "No records",
    hasTopAxis: !isEmpty && axes.some(column => column.scale.axis_position !== "bottom"),
    hasBottomAxis: !isEmpty && axes.some(column => column.scale.axis_position === "bottom"),
    toggleSection: view.toggleSection,
  }};
}
