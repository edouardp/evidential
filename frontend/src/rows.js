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

/** The base formats a fixed decimal precision can be applied to. */
const DECIMAL_BASES = [
  "num",
  "usd",
  "eur",
  "gbp",
  "aud",
  "cad",
  "cny",
  "jpy",
  "inr",
  "krw",
  "ngn",
  "sek",
  "pct",
];

/** Apply a fixed decimal precision to a supported base format. */
export function withDecimals(format, decimals) {
  const code = String(format || "num");
  // An explicit precision (`num2`, `pct1`, `usd0`, …) is already aligned, so
  // keep it rather than re-deriving a wider one from the raw values.
  const explicit = /^([a-z]+)(\d+)$/.exec(code);
  if (explicit && DECIMAL_BASES.includes(explicit[1])) return code;
  if (!DECIMAL_BASES.includes(code)) return code;
  // A percent format renders `value * 100`, so the raw value's decimal places
  // are two more than the rendered percentage's.
  const places = code === "pct" ? Math.max(0, decimals - 2) : decimals;
  return code + Math.min(places, code === "pct" ? 3 : 4);
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
    if (row.render_type === "row_subtotal" || row.render_type === "row_section") {
      return keepGroups.has(row.__group_key) || matches(row);
    }
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
  const cmp = (a, b) => {
    const av = a[key], bv = b[key];
    const comparison = compareValues(av, bv, keyType);
    // Missing keys stay last; descending only reverses actual values.
    if (av === null || av === undefined || bv === null || bv === undefined) return comparison;
    return dir * comparison;
  };

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

  // Synthetic *section* rows (`.row_section`) may paginate; accordion groups
  // and subtotal/total rows stay on one page so a group is never split.
  const grouping = rows.some(
    (row) => !row.__row_builder && (row.render_type === "row_subtotal" || row.render_type === "row_total"),
  );
  void hasGroups;
  if (!pageSize || pageSize === "all" || pageSize <= 0 || grouping || opts.collapsible) {
    return { rows, pageCount: 1, page: 0, total: rows.length, start: 0 };
  }
  const total = rows.length;
  const pageCount = Math.max(1, Math.ceil(total / pageSize));
  const page = Math.min(Math.max(0, pageIndex), pageCount - 1);
  const start = page * pageSize;

  return { rows: rows.slice(start, start + pageSize), pageCount, page, total, start };
}

/** Summarize all detail rows; subtotal and total rows are excluded. */
export function columnStats(columns, rows) {
  const data = rows.filter((row) => !row.render_type || row.render_type === "cell_data");
  const stats = new Map();
  for (const col of columns) {
    let min = null;
    let max = null;
    let sum = 0;
    let numeric = 0;
    let nulls = 0;
    let trues = 0;
    let falses = 0;
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
      } else if (col.type === "boolean") {
        if (value === true) trues += 1;
        else if (value === false) falses += 1;
      }
    }
    stats.set(col.name, {
      min,
      max,
      avg: numeric ? sum / numeric : null,
      nulls,
      distinct: distinct.size,
      trues,
      falses,
    });
  }
  return stats;
}

/** Span each section subtotal across its adjacent descendant rows. */
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

/** Indent ancestor dimensions in accordion groups, leaving leaf dimensions unindented. */
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

/** Support alternating stripes, fixed-size bands and [shaded, unshaded] pairs. */
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

/**
 * The label for a repeated section row at the top of a page. A section that
 * spans a page break is re-introduced as `"<label> (cont.)"` so the reader
 * knows which section the page continues.
 */
export function sectionContinuation(allRows, start, pageRows) {
  if (!start || !pageRows || !pageRows.length) return null;
  if (pageRows[0].render_type === "row_section") return null;
  if (pageRows[0].render_type === "row_total") return null;
  for (let index = start - 1; index >= 0; index -= 1) {
    const row = allRows[index];
    if (row.render_type === "row_section") {
      if (pageRows[0].__parent_key && pageRows[0].__parent_key !== row.__group_key) return null;
      const label = row.__label;
      return label == null || label === "" ? null : `${label} (cont.)`;
    }
    if (row.render_type === "row_total") break;
  }
  return null;
}
