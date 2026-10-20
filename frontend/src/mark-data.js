/** Missing numeric values never become zero at the rendering boundary. */
export function numeric(value) {
  return value == null || value === "" || !Number.isFinite(Number(value)) ? null : Number(value);
}

export function observationValue(item) {
  return item && typeof item === "object" ? (item.value ?? item.x ?? item.y) : item;
}

/** Contributions of each mark to one column domain, excluding synthetic rows. */
export function encodingRange(col, rows) {
  let min = Infinity;
  let max = -Infinity;
  const add = raw => {
    const value = numeric(raw);
    if (value == null || (col.scale?.transform === "log" && value <= 0)) return;
    min = Math.min(min, value);
    max = Math.max(max, value);
  };
  const stack = col.encodings.filter(enc => enc.kind === "stacked_bar");
  for (const row of rows) {
    if (row.render_type && row.render_type !== "cell_data") continue;
    if (stack.length) {
      const values = stack.map(enc => Math.max(0, numeric(row[enc.source]) ?? 0));
      const total = values.reduce((sum, value) => sum + value, 0);
      const pivot = stack.findIndex(enc => enc.source === stack[0].diverge_at);
      if (col.scale?.normalize === "percent") {
        add(pivot >= 0 ? -100 : 0);
        add(100);
      } else if (pivot >= 0) {
        const left = values.slice(0, pivot).reduce((sum, value) => sum + value, values[pivot] / 2);
        const right = values.slice(pivot + 1).reduce((sum, value) => sum + value, values[pivot] / 2);
        const arm = Math.max(left, right);
        add(-arm);
        add(arm);
      } else {
        add(0);
        add(total);
      }
    }
    for (const enc of col.encodings) {
      const raw = row[enc.source];
      if (enc.kind === "stacked_bar") continue;
      if (enc.kind === "points") {
        for (const item of Array.isArray(raw) ? raw : []) add(observationValue(item));
      } else if (enc.kind === "distribution") {
        for (const item of Array.isArray(raw) ? raw : []) add(item?.[enc.x]);
      } else if (enc.kind === "strip") {
        for (const item of Array.isArray(raw) ? raw : []) {
          if (!item || typeof item !== "object") continue;
          for (const key of ["start", "position", "end", "finish"]) add(item[key]);
        }
      } else {
        for (const field of [enc.source, enc.high, ...Object.values(enc.parts || {})]) add(row[field]);
        for (const item of enc.outliers && Array.isArray(row[enc.outliers]) ? row[enc.outliers] : []) add(item);
      }
    }
  }
  return min === Infinity ? null : {min, max};
}
