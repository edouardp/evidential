export { groupPath, groupKey, buildHeaderLevels, orderedColumns } from "./headers.js";
// Pure row and column processing; input records are never mutated.
export function compareValues(a, b, type) {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  if (type === "number") {
    const na = Number(a);
    const nb = Number(b);
    if (!isNaN(na) && !isNaN(nb)) return na - nb;
  }
  if (a instanceof Date || b instanceof Date) return new Date(a) - new Date(b);
  if (typeof a === "string" && typeof b === "string") {
    return a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" });
  }
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

export function decimalPlaces(value) {
  if (value === null || value === undefined || typeof value === "boolean") return null;
  const text = String(value);
  if (text.trim() === "" || isNaN(Number(text))) return null;
  const dot = text.indexOf(".");
  return dot === -1 ? 0 : text.length - dot - 1;
}

export function withDecimals(format, decimals) {
  const code = String(format || "num");
  const base = code.replace(/\d+$/, "");
  const bases = ["num", "usd", "eur", "gbp", "aud", "cad", "cny", "jpy", "inr", "krw", "ngn", "sek", "pct"];
  if (!bases.includes(base)) return code;
  const max = base === "pct" ? 3 : 4;
  return base + Math.min(decimals, max);
}

export function hiddenColumns(columns, hiddenState) {
  const set = new Set(hiddenState);
  for (const col of columns) if (col.hide) set.add(col.name);
  return set;
}

export function visibleRows(rows, isCollapsed) {
  const hasGroups = rows.some((r) => r.render_type && r.render_type !== "cell_data");
  if (!hasGroups) return rows;
  const collapsed = new Set();
  for (const row of rows) {
    const key = row.__group_key;
    if ((row.render_type === "row_subtotal" || row.render_type === "row_total") && key && isCollapsed(key)) {
      collapsed.add(key);
    }
  }
  return rows.filter((row) => {
    const ancestors = row.__ancestors || [];
    return !ancestors.some((k) => collapsed.has(k));
  });
}

export function searchRows(rows, columns, search, hidden) {
  const term = search.trim().toLowerCase();
  if (!term) return rows;

  const cols = columns.filter((c) => !hidden.has(c.name));
  const matches = (row) => cols.some((c) => {
    const v = row[c.name];
    return v !== null && v !== undefined && String(v).toLowerCase().includes(term);
  });
  const keepGroups = new Set();
  for (const row of rows) {
    if (row.render_type && row.render_type !== "cell_data") {
      if (row.render_type === "row_total") keepGroups.add(row.__group_key);
      continue;
    }
    if (matches(row)) for (const key of row.__ancestors || []) keepGroups.add(key);
  }
  return rows.filter((row) => {
    if (row.render_type === "row_total") return true;
    if (row.render_type === "row_subtotal") return keepGroups.has(row.__group_key);
    return matches(row);
  });
}

export function sortRows(rows, columns, sort) {

  if (!sort) return rows;
  const col = columns.find((c) => c.name === sort.column);
  // A column can sort by another column's values (e.g. a sparkline sorted by
  // a score). `sort_by` may name a column that is hidden from the table — or
  // one that is in the data but not a configured column at all.
  const key = col?.sort_by || sort.column;
  const keyType = columns.find((c) => c.name === key)?.type;
  const dir = sort.direction === "asc" ? 1 : -1;

  const hasGroups = rows.some((r) => r.render_type && r.render_type !== "cell_data");
  const cmp = (a, b) => dir * compareValues(a[key], b[key], keyType);

  if (!hasGroups) return [...rows].sort(cmp);

  // Grouped: sort only detail rows inside each parent group, preserving the
  // position of subtotal/total rows.
  const queues = new Map();
  for (const row of rows) {
    if (row.render_type && row.render_type !== "cell_data") continue;
    const key = row.__parent_key ?? "__root__";
    if (!queues.has(key)) queues.set(key, []);
    queues.get(key).push(row);
  }
  for (const queue of queues.values()) queue.sort(cmp);
  const out = [];
  for (const row of rows) {
    if (row.render_type && row.render_type !== "cell_data") {
      out.push(row);
    } else {
      const key = row.__parent_key ?? "__root__";
      out.push(queues.get(key).shift());
    }
  }
  return out;
}

export function paginateRows(rows, pageSize, pageIndex, options,
  hasGroups = rows.some((row) => row.render_type && row.render_type !== "cell_data")) {
  const opts = options;

  if (!pageSize || pageSize === "all" || pageSize <= 0 || hasGroups || opts.collapsible) {
    return { rows, pageCount: 1, page: 0, total: rows.length };
  }
  const total = rows.length;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const page = Math.min(Math.max(0, pageIndex), pageCount - 1);

  return { rows: rows.slice(page * pageSize, (page + 1) * pageSize), pageCount, page, total };
}

export function columnStats(columns, rows) {
  const data = rows.filter((row) => !row.render_type || row.render_type === "cell_data");
  const stats = new Map();
  for (const col of columns) {
    let min = null;
    let max = null;
    let sum = 0;
    let numeric = 0;
    let nulls = 0;
    const distinct = new Set();
    for (const row of data) {
      const value = row[col.name];
      if (value === null || value === undefined) {
        nulls += 1;
        continue;
      }
      distinct.add(typeof value === "object" ? JSON.stringify(value) : String(value));
      if (col.type === "number") {
        const num = Number(value);
        if (!Number.isNaN(num) && Number.isFinite(num)) {
          if (min === null || num < min) min = num;
          if (max === null || num > max) max = num;
          sum += num;
          numeric += 1;
        }
      }
    }
    stats.set(col.name, {
      min,
      max,
      avg: numeric ? sum / numeric : null,
      nulls,
      distinct: distinct.size,
    });
  }
  return stats;
}

export function computeRowspans(rows, dimCount, top) {
  const spans = new Array(rows.length).fill(1);
  rows.forEach((row, index) => {
    if (row.render_type !== "row_subtotal") return;
    const level = row.__level ?? dimCount;
    let count = 1;
    if (top) {
      for (let j = index + 1; j < rows.length && (rows[j].__level ?? dimCount) > level; j++) count++;
    } else {
      for (let j = index - 1; j >= 0 && (rows[j].__level ?? dimCount) > level; j--) count++;
    }
    spans[index] = count;
  });
  return spans;
}

export function indentForCell(row, columnIndex, ctx) {
  if (columnIndex >= ctx.dimCount) return 0;
  const level = row.__level ?? 0;
  const renderType = row.render_type || "cell_data";
  if (renderType === "cell_data") {
    return columnIndex === ctx.dimCount - 1 ? 0 : 2;
  }
  if (renderType === "row_subtotal" && columnIndex < level - 1) return 2;
  return 0;
}

export function shaded(index, options) {
  const shading = options.row_shading;
  if (!shading) return false;
  let shaded = 1;
  let unshaded = 1;
  if (Array.isArray(shading)) {
    shaded = Math.max(1, Number(shading[0]) || 1);
    unshaded = Math.max(1, Number(shading[1]) || shaded);
  } else if (typeof shading === "number") {
    shaded = Math.max(1, shading);
    unshaded = shaded;
  }
  return index % (shaded + unshaded) >= unshaded;
}
