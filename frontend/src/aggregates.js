// @ts-check
/** Portable display aggregates; fixtures are shared with Python summary_values. */
/** @param {unknown} value
 * @returns {unknown}
 */
function valueKey(value) {
  if (Array.isArray(value)) return ["array", value.map(valueKey)];
  if (value !== null && typeof value === "object") {
    const object = /** @type {Record<string, unknown>} */ (value);
    return ["object", Object.keys(object).sort().map(key => [key, valueKey(object[key])])];
  }
  return [typeof value, value];
}

/** @param {string} left @param {string} right */
function compareStrings(left, right) {
  const a = Array.from(left), b = Array.from(right);
  for (let index = 0; index < Math.min(a.length, b.length); index++) {
    const difference = /** @type {number} */ (a[index].codePointAt(0)) - /** @type {number} */ (b[index].codePointAt(0));
    if (difference) return difference;
  }
  return a.length - b.length;
}

/** @param {string} operation @param {unknown[]} values */
export function aggregateValues(operation, values) {
  const observed = values.filter(value => value != null);
  if (operation === "count") return observed.length;
  if (["count_distinct", "countdistinct", "distinct_count"].includes(operation))
    return new Set(observed.map(value => JSON.stringify(valueKey(value)))).size;
  if (!observed.length) return null;
  if (["min", "max"].includes(operation) && observed.every(value => typeof value === "string"))
    return observed.reduce((result, value) => (operation === "min" ? compareStrings(value, result) < 0 : compareStrings(value, result) > 0) ? value : result);
  if (!observed.every(value => (typeof value === "number" && Number.isFinite(value)) || typeof value === "boolean"))
    throw new TypeError(`summary ${operation} requires numeric values (min/max also accept strings and ISO dates)`);
  const numbers = observed.map(Number);
  if (operation === "min") return observed.reduce((low, value) => value < low ? value : low);
  if (operation === "max") return observed.reduce((high, value) => value > high ? value : high);
  if (operation === "median") {
    const sorted = [...observed].sort((a, b) => Number(a) - Number(b)), mid = Math.floor(sorted.length / 2);
    return sorted.length % 2 ? sorted[mid] : (Number(sorted[mid - 1]) + Number(sorted[mid])) / 2;
  }
  const sum = numbers.reduce((total, value) => total + value, 0);
  if (operation === "sum") return sum;
  if (["mean", "avg", "average", "weighted_mean", "weightedmean"].includes(operation)) return sum / numbers.length;
  throw new TypeError(`Unknown summary aggregation ${operation}`);
}
