// Display projection over detail records. Annotation entries are never data rows.
import { formatValue } from "./format.js";
import { aggregateValues } from "./aggregates.js";

export function summaryValue(spec, members) {
  if (!spec.operation) return spec.value;
  const values = spec.source == null ? members : members.map(row => row[spec.source]).filter(value => value != null);
  const value = aggregateValues(spec.operation, values);
  if (value != null && (spec.prefix || spec.suffix)) {
    return `${spec.prefix || ""}${formatValue(value, spec.format || "num", {type: "number", fallback: String(value)})}${spec.suffix || ""}`;
  }
  return value;
}

/** Find only the groups overlapping the current display-slot window. */
function* overlappingGroups(groups, start, end) {
  let low = 0, high = groups.length;
  while (low < high) {
    const middle = (low + high) >>> 1;
    if (groups[middle].last < start) low = middle + 1;
    else high = middle;
  }
  for (let index = low; index < groups.length && groups[index].first < end; index++) yield groups[index];
}

/** Dataset preparation survives paging; only a collapse revision rebuilds slots. */
export class LayoutProjection {
  constructor(layout, allRows, sortedRows) {
    this.layout = layout;
    this.indices = new Map(allRows.map((row, index) => [row, index]));
    this.rank = new Map(sortedRows.map((row, index) => [row, index]));
    this.ordered = [];
    this.cells = new WeakMap();
    this.tree = this.prepareGroups(layout.groups || [], allRows);
    if (!layout.groups?.length) for (const row of sortedRows) this.ordered.push(row);
    this.ordinals = new Map(this.ordered.map((row, index) => [row, index]));
    this.folded = null;
  }

  prepareGroups(groups, allRows) {
    return groups.map(group => {
      const members = group.members.map(index => allRows[index]).filter(row => this.rank.has(row))
        .sort((a, b) => this.rank.get(a) - this.rank.get(b));
      const children = this.prepareGroups(group.children, allRows);
      if (!children.length) for (const row of members) this.ordered.push(row);
      return {group, members, children};
    }).filter(node => node.members.length);
  }

  dataUnit(row, depth = 0, inset = false, toggleDepth = 0) {
    return {kind: "data", row, depth, inset, toggleDepth,
      index: this.indices.get(row), ordinal: this.ordinals.get(row)};
  }

  fold(isCollapsed, revision) {
    const state = {units: [], starts: new Map(), collapsedGroups: 0, revision};
    const prepare = (nodes, inset = false, toggleDepth = 0) => nodes.map(({group, members, children}) => {
      const first = state.units.length;
      state.starts.set(group.id, first);
      const collapsed = !!group.section?.collapsible && isCollapsed(group.id);
      const indent = inset || (group.section && group.section.align !== "center") || group.summary?.position === "top";
      const childToggleDepth = toggleDepth + (group.section?.collapsible && group.section.align !== "center" ? 1 : 0);
      let descendants = [];
      if (collapsed) {
        state.units.push({kind: "collapsed", groupKey: group.id});
        state.collapsedGroups++;
      } else if (children.length) descendants = prepare(children, indent, childToggleDepth);
      else for (const row of members) state.units.push(this.dataUnit(row, group.depth + 1, indent, childToggleDepth));
      const heading = collapsed && group.section?.collapsed_summary && !Object.keys(group.section.cells || {}).length && group.summary
        ? {...group.section, cells: group.summary.cells} : group.section;
      return {group, members, collapsed, children: descendants, inset: indent, toggleDepth, childToggleDepth,
        heading, first, last: state.units.length - 1};
    });
    state.tree = prepare(this.tree);
    if (!this.layout.groups?.length) for (const row of this.ordered) state.units.push(this.dataUnit(row));
    this.folded = state;
    return state;
  }

  annotation(kind, id, spec, members, depth, continuation = false, toggleDepth = 0) {
    let byMembers = this.cells.get(spec);
    if (!byMembers) { byMembers = new WeakMap(); this.cells.set(spec, byMembers); }
    let cells = byMembers.get(members);
    if (!cells) {
      cells = Object.fromEntries(Object.entries(spec.cells || {}).map(([name, value]) =>
        [name, {...value, value: summaryValue(value, members)}]));
      byMembers.set(members, cells);
    }
    return {kind, id, depth, toggleDepth, label: `${spec.label}${continuation ? " (cont.)" : ""}`,
      cells, style: spec.style || {}, rule: spec.rule || "none", align: spec.align || "left",
      labelColumn: spec.label_column, labelStyle: spec.label_style || {}, continuation};
  }

  appendGroups(groups, start, end, units, entries) {
    for (const node of overlappingGroups(groups, start, end)) {
      const {group, members, collapsed, children, inset, toggleDepth, childToggleDepth, first, last, heading} = node;
      if (heading) entries.push({...this.annotation("section", `${group.id}:section`, heading, members, group.depth, first < start, toggleDepth),
        groupKey: group.id, collapsible: !!heading.collapsible, collapsed});
      if (collapsed) continue;
      const depth = group.depth + (inset && group.summary?.indent !== false ? 1 : 0);
      const summaryToggle = group.summary?.indent !== false ? childToggleDepth : toggleDepth;
      if (group.summary?.position === "top" && first >= start)
        entries.push(this.annotation("summary", `${group.id}:summary`, group.summary, members, depth, false, summaryToggle));
      if (children.length) this.appendGroups(children, start, end, units, entries);
      else for (const unit of units.slice(Math.max(start, first), Math.min(end, last + 1))) entries.push(unit);
      if (group.summary?.position === "bottom" && last < end)
        entries.push(this.annotation("summary", `${group.id}:summary`, group.summary, members, depth, false, summaryToggle));
    }
  }

  page(pageSize, pageIndex, paginate = null, {isCollapsed = () => false, anchorGroup = null, revision = 0} = {}) {
    const {tree, units, starts, collapsedGroups} = this.folded?.revision === revision ? this.folded : this.fold(isCollapsed, revision);
    const total = units.length;
    const size = pageSize === "all" || !(Number(pageSize) > 0) ? Math.max(1, total) : Number(pageSize);
    const pageCount = Math.max(1, Math.ceil(total / size));
    const requested = starts.has(anchorGroup) ? Math.floor(starts.get(anchorGroup) / size) : pageIndex;
    const page = Math.min(Math.max(0, requested), pageCount - 1);
    const bounds = paginate ? paginate(total) : {pageCount, page, start: page * size, end: Math.min(total, (page + 1) * size)};
    const {start, end} = bounds;
    const entries = [];
    if (tree.length) this.appendGroups(tree, start, end, units, entries);
    else for (const unit of units.slice(start, end)) entries.push(unit);
    if (total && end === total && this.layout.grand_summary)
      entries.push(this.annotation("grand_summary", "grand-summary", this.layout.grand_summary, this.ordered, 0));
    return {...bounds, entries, rows: units.slice(start, end).filter(unit => unit.kind === "data").map(unit => unit.row),
      total, unitCount: end - start, matchingTotal: this.ordered.length, collapsedGroups};
  }
}

/** Standalone projection for inspection/export; the renderer retains a prepared instance. */
export function projectLayout(layout, allRows, sortedRows, pageSize, pageIndex, paginate = null, options = {}) {
  return new LayoutProjection(layout, allRows, sortedRows).page(pageSize, pageIndex, paginate, options);
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
