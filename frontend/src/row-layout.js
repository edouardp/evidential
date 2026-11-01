// Display projection over detail records. Annotation entries are never data rows.
import { formatValue } from "./format.js";
import { numeric } from "./mark-data.js";

export function summaryValue(spec, members) {
  if (!spec.operation) return spec.value;
  const op = spec.operation;
  const values = spec.source == null ? members : members.map(row => row[spec.source]).filter(value => value != null);
  const numbers = values.map(numeric).filter(value => value != null);
  let value = null;
  if (op === "count") value = values.length;
  else if (["count_distinct", "countdistinct", "distinct_count"].includes(op)) value = new Set(values.map(value => JSON.stringify(value))).size;
  else if (numbers.length) {
    if (op === "sum") value = numbers.reduce((sum, item) => sum + item, 0);
    else if (op === "min") value = numbers.reduce((low, item) => Math.min(low, item), Infinity);
    else if (op === "max") value = numbers.reduce((high, item) => Math.max(high, item), -Infinity);
    else if (op === "median") {
      const sorted = [...numbers].sort((a, b) => a - b);
      const mid = Math.floor(sorted.length / 2);
      value = sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
    } else value = numbers.reduce((sum, item) => sum + item, 0) / numbers.length;
  }
  if (value != null && (spec.prefix || spec.suffix)) {
    return `${spec.prefix || ""}${formatValue(value, spec.format || "num", {type: "number", fallback: String(value)})}${spec.suffix || ""}`;
  }
  return value;
}

function annotationEntry(kind, id, spec, members, depth, continuation = false) {
  const cells = Object.fromEntries(Object.entries(spec.cells || {}).map(([name, value]) =>
    [name, {...value, value: summaryValue(value, members)}]));
  return {kind, id, depth, label: `${spec.label}${continuation ? " (cont.)" : ""}`,
    cells, style: spec.style || {}, rule: spec.rule || "none", align: spec.align || "left",
    labelColumn: spec.label_column, labelStyle: spec.label_style || {}, continuation};
}

/** Fold the display tree, paginate details/closed groups, then add annotations. */
export function projectLayout(layout, allRows, sortedRows, pageSize, pageIndex, paginate = null,
  {isCollapsed = () => false, anchorGroup = null} = {}) {
  const rank = new Map(sortedRows.map((row, index) => [row, index]));
  const indices = new Map(allRows.map((row, index) => [row, index]));
  const memberCache = new Map();
  const membersOf = group => {
    if (!memberCache.has(group)) memberCache.set(group, group.members.map(index => allRows[index]).filter(row => rank.has(row))
      .sort((a, b) => rank.get(a) - rank.get(b)));
    return memberCache.get(group);
  };
  const ordered = [];
  const orderGroups = groups => {
    for (const group of groups) {
      if (group.children.length) orderGroups(group.children);
      else for (const row of membersOf(group)) ordered.push(row);
    }
  };
  if (layout.groups?.length) orderGroups(layout.groups);
  else for (const row of sortedRows) ordered.push(row);
  const ordinals = new Map(ordered.map((row, index) => [row, index]));
  const units = [], starts = new Map();
  let collapsedGroups = 0;
  const prepare = (groups, inset = false) => groups.flatMap(group => {
    const members = membersOf(group);
    if (!members.length) return [];
    const first = units.length;
    starts.set(group.id, first);
    const collapsed = !!group.section?.collapsible && isCollapsed(group.id);
    const indent = inset || (group.section && group.section.align !== "center") || group.summary?.position === "top";
    let children = [];
    if (collapsed) {
      units.push({kind: "collapsed", groupKey: group.id});
      collapsedGroups++;
    } else if (group.children.length) children = prepare(group.children, indent);
    else for (const row of members) units.push({kind: "data", row, depth: group.depth + 1, inset: indent,
      index: indices.get(row), ordinal: ordinals.get(row)});
    return [{group, members, collapsed, children, inset: indent, first, last: units.length - 1}];
  });
  const tree = prepare(layout.groups || []);
  if (!layout.groups?.length) for (const row of ordered) units.push({kind: "data", row, depth: 0, inset: false,
    index: indices.get(row), ordinal: ordinals.get(row)});
  const total = units.length;
  const size = pageSize === "all" || !(Number(pageSize) > 0) ? Math.max(1, total) : Number(pageSize);
  const fixedCount = Math.max(1, Math.ceil(total / size));
  const requested = starts.has(anchorGroup) ? Math.floor(starts.get(anchorGroup) / size) : pageIndex;
  const fixedPage = Math.min(Math.max(0, requested), fixedCount - 1);
  const bounds = paginate ? paginate(total) : {pageCount: fixedCount, page: fixedPage,
    start: fixedPage * size, end: Math.min(total, (fixedPage + 1) * size)};
  const {start, end} = bounds;
  const entries = [];
  const visit = groups => {
    for (const {group, members, collapsed, children, inset, first, last} of groups) {
      if (last < start || first >= end) continue;
      if (group.section) {
        const spec = collapsed && group.section.collapsed_summary && !Object.keys(group.section.cells || {}).length && group.summary
          ? {...group.section, cells: group.summary.cells} : group.section;
        entries.push({...annotationEntry("section", `${group.id}:section`, spec, members, group.depth, first < start),
          groupKey: group.id, collapsible: !!group.section.collapsible, collapsed});
      }
      // A closed group contributes just its heading. Its summaries and children
      // are hidden, but all matching members still feed heading/grand totals.
      if (collapsed) continue;
      const summaryDepth = group.depth + (inset && group.summary?.indent !== false ? 1 : 0);
      if (group.summary?.position === "top" && first >= start) {
        entries.push(annotationEntry("summary", `${group.id}:summary`, group.summary, members, summaryDepth));
      }
      if (children.length) visit(children);
      else for (const unit of units.slice(Math.max(start, first), Math.min(end, last + 1))) entries.push(unit);
      if (group.summary?.position === "bottom" && last < end) {
        entries.push(annotationEntry("summary", `${group.id}:summary`, group.summary, members, summaryDepth));
      }
    }
  };
  if (tree.length) visit(tree);
  else for (const unit of units.slice(start, end)) entries.push(unit);
  if (total && end === total && layout.grand_summary) {
    entries.push(annotationEntry("grand_summary", "grand-summary", layout.grand_summary, ordered, 0));
  }
  return {...bounds, entries, rows: units.slice(start, end).filter(unit => unit.kind === "data").map(unit => unit.row),
    total, unitCount: end - start, matchingTotal: ordered.length, collapsedGroups};
}

/** Historical flattened inputs are reconstructed only at the display boundary. */
export function projectLegacy(layout, allRows, sortedRows, isCollapsed) {
  const indices = new Map(allRows.map((row, index) => [row, index]));
  const rank = new Map(sortedRows.map((row, index) => [indices.get(row), index]));
  const collapsed = new Set(layout.legacy.filter(token => token.row?.__group_key && isCollapsed(token.row.__group_key))
    .map(token => token.row.__group_key));
  const allowed = row => !(row.__ancestors || []).some(key => collapsed.has(key));
  const result = [];
  let pending = [];
  const flush = () => {
    pending.sort((a, b) => rank.get(a) - rank.get(b));
    for (const index of pending) if (allowed(allRows[index])) result.push(allRows[index]);
    pending = [];
  };
  for (const token of layout.legacy) {
    if (token.index != null) {
      if (rank.has(token.index)) pending.push(token.index);
      continue;
    }
    flush();
    if (rank.size && token.members.some(index => rank.has(index)) && allowed(token.row)) result.push(token.row);
  }
  flush();
  return result;
}
