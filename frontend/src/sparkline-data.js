import { numeric } from "./mark-data.js";

/** Normalize numbers, [x, y] pairs or objects into sparkline points. */
export function sparklinePoints(value, opts) {
  if (!Array.isArray(value)) return [];
  const xKey = opts.x;
  const yKey = opts.y;
  const points = [];
  value.forEach((item, index) => {
    if (item === null || item === undefined) {
      points.push([index, null, item]);
      return;
    }
    let x = index;
    let y;
    if (Array.isArray(item)) {
      x = item[0];
      y = numeric(item[1]);
    } else if (typeof item === "object") {
      const keys = Object.keys(item);
      const yField = yKey || ["y", "value"].find(key => key in item) || keys.find((key) => _isNumeric(item[key]));
      const xField =
        xKey || ["x", "date"].find(key => key in item) || keys.find((key) => key !== yField && !_isNumeric(item[key]));
      x = xField ? item[xField] : index;
      y = numeric(yField ? item[yField] : null);
    } else {
      y = numeric(item);
    }
    points.push([x, y, item]);
  });
  return points;
}

function _isNumeric(value) {
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value === "string") return value.trim() !== "" && !isNaN(Number(value));
  return false;
}
