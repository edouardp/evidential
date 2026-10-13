// Column ordering and header layout, independent of row processing.
import { h, withFigure, alignStyle } from "./dom.js";
import { formatTitle } from "./format.js";

export function groupPath(group) {
  if (!group) return [];
  return Array.isArray(group) ? group.map(String) : [String(group)];
}

/** Stable map key for a single group or a nested group path. */
export function groupKey(group) {
  return Array.isArray(group) ? group.join("\u0000") : String(group);
}

/** Build one row of contiguous spanners per hierarchy level. */
export function buildHeaderLevels(paths, depth) {
  const levels = Array.from({ length: depth }, () => []);
  function recurse(start, end, level) {
    if (level >= depth) return;
    let i = start;
    while (i < end) {
      const label = paths[i][level] ?? "";
      let j = i + 1;
      while (j < end && (paths[j][level] ?? "") === label) j++;
      levels[level].push({ label, span: j - i, start: i });
      recurse(i, j, level + 1);
      i = j;
    }
  }
  recurse(0, paths.length, 0);
  return levels;
}

/** Cluster matching parent groups and sub-columns at their first occurrence. */
export function orderedColumns(columns, options) {
  if (options.order_columns_by_group === false) return columns;
  const grouped = new Map();
  for (const col of columns) {
    if (!col.column_group) continue;
    const key = groupKey(col.column_group);
    if (!grouped.has(key)) grouped.set(key, []);
    grouped.get(key).push(col);
  }
  const emitted = new Set();
  const ordered = [];
  for (const col of columns) {
    const group = col.column_group;
    if (!group) {
      ordered.push(col);
      continue;
    }
    const key = groupKey(group);
    if (emitted.has(key)) continue;
    emitted.add(key);
    ordered.push(...grouped.get(key));
  }
  // A composite is local to its parent path, including the ungrouped root.
  const composites = new Map();
  for (const col of ordered) {
    if (!col.subcolumn_group) continue;
    const key = compositeKey(col);
    if (!composites.has(key)) composites.set(key, []);
    composites.get(key).push(col);
  }
  const joined = [];
  const seen = new Set();
  for (const col of ordered) {
    if (!col.subcolumn_group) { joined.push(col); continue; }
    const key = compositeKey(col);
    if (seen.has(key)) continue;
    seen.add(key);
    joined.push(...composites.get(key));
  }
  return joined;
}

function compositeKey(col) {
  return JSON.stringify([groupPath(col.column_group), col.subcolumn_group]);
}

/** All spans refer to physical columns, after hiding and ordering. */
export function headerLayout(columns) {
  const paths = columns.map((col) => groupPath(col.column_group));
  const depth = Math.max(0, ...paths.map((path) => path.length));
  const leaves = [];
  const joins = new Map();
  for (let start = 0; start < columns.length;) {
    const col = columns[start];
    let end = start + 1;
    if (col.subcolumn_group) {
      while (end < columns.length && compositeKey(columns[end]) === compositeKey(col)) end++;
    }
    const span = end - start;
    leaves.push({start, span, label: col.subcolumn_group || null});
    for (let index = start; span > 1 && index < end; index++) {
      joins.set(columns[index].name, {
        left: index > start, right: index < end - 1, label: col.subcolumn_group,
      });
    }
    start = end;
  }
  return {depth, levels: buildHeaderLevels(paths, depth), leaves, joins};
}

export function decorateSubcolumn(cell, col, index, ctx) {
  cell.dataset.columnIndex = index + (ctx.rowNumbers ? 1 : 0);
  const join = ctx.subcolumns.get(col.name);
  if (!join) return;
  cell.classList.toggle("et-subcolumn-left", join.left);
  cell.classList.toggle("et-subcolumn-right", join.right);
  // Keep individual member names available to assistive technology.
  cell.setAttribute("aria-label", `${join.label}: ${col.title ?? formatTitle(col.name)}: ${cell.textContent}`);
}

function headerTitle(title) {
  const label = h("span", {class: "et-th-title"});
  String(title).split("\n").forEach((line, index) => {
    if (index > 0) label.append(h("br"));
    label.append(h("span", {class: "et-th-line"}, line));
  });
  return label;
}

export function renderHeader({columns, rowNumbers, options: opts, sort, onSort}) {
  const thead = h("thead");
  const {depth, levels, leaves} = headerLayout(columns);
  if (depth > 0) {
    levels.forEach((cells, level) => {
      const groupRow = h("tr", { class: "et-header-groups" });
      if (rowNumbers && level === 0) {
        groupRow.append(h("th", { class: "et-th et-th-group et-row-num", rowspan: depth, "data-column-start": 0 }, ""));
      }
      for (const cell of cells) {
        const th = h(
          "th",
          {
            class: `et-th et-th-group${cell.label ? "" : " et-th-group-blank"}`,
            colspan: cell.span,
            scope: "colgroup",
            "data-column-start": cell.start + (rowNumbers ? 1 : 0),
            "data-group": cell.label,
            title: cell.label || null,
          },
          headerTitle(cell.label),
        );
        // Highlight a spanner only when every column it spans shares the same
        // highlight — a whole-group band, not a single-column one.
        const spanned = columns.slice(cell.start, cell.start + cell.span);
        if (spanned.length && spanned.every((c) => c.highlight && c.highlight === spanned[0].highlight)) {
          th.style.backgroundColor = spanned[0].highlight;
        }
        groupRow.append(th);
      }
      thead.append(groupRow);
    });
  }

  const row = h("tr");
  if (rowNumbers) {
    row.append(h("th", { class: "et-th et-row-num", "aria-label": "Row number", "data-column-start": 0 }, "#"));
  }
  for (const leaf of leaves) {
    const col = columns[leaf.start];
    const sorted = sort?.column === col.name;
    const dir = sorted ? sort.direction : null;
    const isStub = opts.stub === col.name;
    const rotation = col.rotate_title ?? (isStub ? null : opts.rotate_titles);
    let thClass = `et-th${sorted ? " et-th-sorted" : ""}${isStub ? " et-stub-head" : ""}`;
    if (rotation === "vertical") thClass += " et-th-vertical";
    else if (typeof rotation === "number") thClass += " et-th-oblique";
    const infoText = col.info ? String(col.info) : null;
    const th = h("th", {
      class: thClass + (leaf.label ? " et-th-subcolumns" : ""),
      colspan: leaf.span,
      scope: leaf.span > 1 ? "colgroup" : "col",
      "data-column-start": leaf.start + (rowNumbers ? 1 : 0),
      style: withFigure(leaf.label ? {textAlign: "center"} : alignStyle(col), col, opts),
      "aria-sort": sorted ? (dir === "asc" ? "ascending" : "descending") : "none",
      // The description tooltip belongs to the whole header cell.
      title: infoText,
    });
    if (typeof rotation === "number") {
      th.style.setProperty("--et-th-angle", `${rotation}deg`);
    }
    const spanned = columns.slice(leaf.start, leaf.start + leaf.span);
    if (col.highlight && spanned.every((member) => member.highlight === col.highlight)) th.style.backgroundColor = col.highlight;
    const inner = h("span", { class: "et-th-inner" });
    let title =
      isStub && opts.stub_head
        ? opts.stub_head
        : opts.format_titles === false
          ? col.name
          : col.title ?? formatTitle(col.name);
    if (leaf.label) title = leaf.label;
    if (opts.all_caps) title = String(title).toUpperCase();
    // A `\n` in the title forces a line break; whether other lines wrap at
    // spaces is up to `wrap_titles` (see CSS).
    inner.append(headerTitle(title));
    if (infoText) {
      inner.append(
        h("span", { class: "et-th-info", role: "img", "aria-label": infoText }, "ⓘ"),
      );
    }
    if (sorted) inner.append(h("span", { class: "et-sort-arrow" }, dir === "asc" ? "▲" : "▼"));
    th.append(inner);
    if (opts.sortable !== false) {
      th.tabIndex = 0;
      th.addEventListener("click", () => onSort(col.name));
      th.addEventListener("keydown", (event) => {
        if (event.key !== "Enter" && event.key !== " ") return;
        event.preventDefault();
        onSort(col.name);
      });
      th.dataset.column = col.name;
    }
    row.append(th);
  }
  thead.append(row);
  return thead;
}
