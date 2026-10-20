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
  const cells = continuation ? {} : Object.fromEntries(Object.entries(spec.cells || {}).map(([name, value]) =>
    [name, {...value, value: summaryValue(value, members)}]));
  return {kind, id, depth, label: `${spec.label}${continuation ? " (cont.)" : ""}`,
    cells, style: spec.style || {}, rule: spec.rule || "none", align: spec.align || "left",
    labelColumn: spec.label_column, continuation};
}

/** Filter/sort detail records first, paginate detail records, then decorate. */
export function projectLayout(layout, allRows, sortedRows, pageSize, pageIndex) {
  const rank = new Map(sortedRows.map((row, index) => [row, index]));
  const indices = new Map(allRows.map((row, index) => [row, index]));
  const membersOf = group => group.members.map(index => allRows[index]).filter(row => rank.has(row))
    .sort((a, b) => rank.get(a) - rank.get(b));
  const ordered = [];
  const orderGroups = groups => {
    for (const group of groups) {
      if (group.children.length) orderGroups(group.children);
      else for (const row of membersOf(group)) ordered.push(row);
    }
  };
  if (layout.groups?.length) orderGroups(layout.groups);
  else for (const row of sortedRows) ordered.push(row);
  const total = ordered.length;
  const size = pageSize === "all" || !(Number(pageSize) > 0) ? Math.max(1, total) : Number(pageSize);
  const pageCount = Math.max(1, Math.ceil(total / size));
  const page = Math.min(Math.max(0, pageIndex), pageCount - 1);
  const start = page * size;
  const end = Math.min(total, start + size);
  const positions = new Map(ordered.map((row, index) => [row, index]));
  const entries = [];
  const addData = (row, depth = 0, inset = false) => {
    const ordinal = positions.get(row);
    if (ordinal >= start && ordinal < end) entries.push({kind: "data", row, depth, inset,
      index: indices.get(row), ordinal});
  };
  const visit = (groups, inset = false) => {
    for (const group of groups) {
      const members = membersOf(group);
      if (!members.length) continue;
      let first = Infinity;
      let last = -Infinity;
      for (const row of members) {
        first = Math.min(first, positions.get(row));
        last = Math.max(last, positions.get(row));
      }
      if (last < start || first >= end) continue;
      if (group.section) entries.push(annotationEntry("section", `${group.id}:section`, group.section, members, group.depth, first < start));
      if (group.summary?.position === "top" && first >= start) {
        entries.push(annotationEntry("summary", `${group.id}:summary`, group.summary, members, group.depth));
      }
      const indent = inset || (group.section && group.section.align !== "center");
      if (group.children.length) visit(group.children, indent);
      else for (const row of members) addData(row, group.depth + 1, indent);
      if (group.summary?.position === "bottom" && last < end) {
        entries.push(annotationEntry("summary", `${group.id}:summary`, group.summary, members, group.depth));
      }
    }
  };
  if (layout.groups?.length) visit(layout.groups);
  else for (const row of ordered.slice(start, end)) addData(row);
  if (total && end === total && layout.grand_summary) {
    entries.push(annotationEntry("grand_summary", "grand-summary", layout.grand_summary, ordered, 0));
  }
  return {entries, rows: ordered.slice(start, end), total, page, pageCount, start};
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
