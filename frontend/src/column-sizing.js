// Let content determine ordinary widths; reserve surplus space for charts.
import { h } from "./dom.js";

/** Fixed-size sparklines, chips and color fills retain their intrinsic widths. */
export function isFlexibleChart(column) {
  return !!column.encodings?.length || column.viz === "bar";
}

/** Physical columns keep the same sizing under spanners, axes and row spans. */
export function renderColumnSizing(columns, { rowNumbers = false, link = false } = {}) {
  if (!columns.some(isFlexibleChart)) return null;
  const group = h("colgroup");
  const compact = () => h("col", { class: "et-col-content" });
  if (rowNumbers) group.append(compact());
  for (const column of columns) {
    group.append(isFlexibleChart(column) ? h("col", { class: "et-col-chart" }) : compact());
  }
  if (link) group.append(compact());
  return group;
}
