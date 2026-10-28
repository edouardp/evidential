// Compact, wrapping color keys in the title area's free right-hand space.
import { h } from "./dom.js";
import { columnHeading, headerLayout } from "./headers.js";
import { markSeries, markColor } from "./mark-series.js";

function legendItem(series, negative = false) {
  const name = negative ? `${series.label} (negative)` : series.label;
  const kind = series.enc.kind;
  return h("li", {class: "et-legend-item"}, [
    h("span", {class: `et-legend-swatch et-legend-swatch-${kind}`, "aria-hidden": "true",
      style: {backgroundColor: negative ? markColor(series.enc, null, series.color, true) : series.color}}),
    h("span", {class: "et-legend-label"}, name),
  ]);
}

export function renderLegends(columns, allColumns, options) {
  const enabled = columns.filter(col => col.legend !== false && col.legend != null && col.encodings?.length);
  if (!enabled.length) return null;
  const outlined = enabled.some(col => col.legend_options?.outline);
  const legends = h("aside", {class: `et-legends${outlined ? " et-legends-outlined" : ""}`, "aria-label": "Legend"});
  const groups = h("div", {class: "et-legend-groups"});
  const {leaves} = headerLayout(columns);
  for (const column of enabled) {
    const index = columns.indexOf(column);
    const leaf = leaves.find(leaf => index >= leaf.start && index < leaf.start + leaf.span);
    const title = columnHeading(column, options, leaf?.label);
    const group = h("div", {class: "et-legend-group", role: "group", "aria-label": title},
      h("div", {class: "et-legend-column"}, title));
    const items = h("ul", {class: "et-legend-items", role: "list"});
    for (const series of markSeries(column, allColumns, options)) {
      if (series.label == null) continue;
      items.append(legendItem(series));
      if (series.enc.color_negative) items.append(legendItem(series, true));
    }
    if (items.childElementCount) {
      group.append(items);
      groups.append(group);
    }
  }
  if (!groups.childElementCount) return null;
  legends.append(groups);
  return legends;
}
