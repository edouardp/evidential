// Inspection values belong to the data, independently of painted labels.
import { formatValue, FORMAT_PRESETS, isDateFormatCode, currencySymbol } from "./format.js";
import { columnHeading } from "./headers.js";
import { markColor, markSeries } from "./mark-series.js";

/** Expand the source's decimal spelling, without rounding or float multiplication. */
export function fullNumber(value, shift = 0) {
  const match = /^(-?)(\d+)(?:\.(\d*))?(?:e([+-]?\d+))?$/i.exec(String(value));
  if (!match) return String(value);
  const digits = match[2] + (match[3] || "");
  const at = match[2].length + Number(match[4] || 0) + shift;
  const whole = (at <= 0 ? "0" : digits.slice(0, at).padEnd(at, "0")).replace(/^0+(?=\d)/, "");
  const fraction = (at < 0 ? "0".repeat(-at) + digits : digits.slice(Math.max(0, at))).replace(/0+$/, "");
  return `${match[1]}${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}${fraction ? `.${fraction}` : ""}`;
}

/** Keep units, expand abbreviations, and retain all precision in the source. */
export function tooltipValue(value, code, col = {}) {
  if (value == null) return col.null_text ?? "–";
  if (typeof value !== "number" || !Number.isFinite(value)) return String(value);
  const actual = FORMAT_PRESETS[code] || code || "";
  if (isDateFormatCode(actual) || code === "id" || col.relative || ["date", "datetime", "time"].includes(col.type)) {
    return formatValue(value, code, {type: col.type, relative: col.relative, fallback: String(value)});
  }
  const currency = currencySymbol(/^([a-z]{3})(?:\d[kmbt]?)?$/.exec(code || "")?.[1]);
  const pattern = actual.split(";")[0];
  const unquoted = pattern.replace(/"[^"\n]*"/g, "");
  const percent = /^pct\d?$/.test(code || "") || unquoted.includes("%");
  const amount = fullNumber(Math.abs(value), percent ? 2 : 0);
  // Spreadsheet literals convey units too; scale suffixes are replaced by the full number.
  const firstDigit = pattern.search(/[0#?]/);
  const literals = [...pattern.matchAll(/"([^"\n]*)"/g)].filter(match => !/^[kmbt]$/i.test(match[1]));
  const prefix = currency || (unquoted.match(/[$€£¥₹₩₦]/)?.[0] ?? "") +
    literals.filter(match => match.index < firstDigit).map(match => match[1]).join("");
  let suffix = percent ? "%" : code === "bytes" ? " bytes" : /^duration/.test(code || "") ? " seconds"
    : !currency ? literals.filter(match => match.index > firstDigit).map(match => match[1]).join("") : "";
  if (/^mult\d?$/.test(code || "")) suffix = "x";
  const text = `${prefix}${amount}${suffix}`;
  return value < 0 ? col.bracket_negatives ? `(${text})` : `-${text}` : text;
}

export function tooltipText(data) {
  return [data.name ? `${data.name}${data.value ? `: ${data.value}` : ""}` : data.value,
    ...(data.details || []).map(item => `${item.name}: ${item.value}`)].filter(Boolean).join("\n");
}

/** The legend's rendered names are useful even when no key is displayed. */
export function seriesName(col, enc, key = enc.source, context = {}) {
  const series = markSeries(col, context.columns, context.options);
  const item = series.find(item => item.key === key && item.enc === enc)
    ?? series.find(item => item.key === key && item.enc.kind === enc.kind);
  return item?.label ?? item?.name ?? enc.names?.[key] ?? columnHeading({name: key}, context.options);
}

export function markTooltip(col, enc, row, {key = enc.source, value = row[key], total, context = {}} = {}) {
  const code = context.formatCode ?? col.fmt;
  const inspect = raw => tooltipValue(raw, code, col);
  const data = {name: seriesName(col, enc, key, context), value: inspect(value), color: markColor(enc, row), details: []};
  if (enc.kind === "stacked_bar") {
    const share = total ? Number(value) / total : 0;
    const showShare = enc.label?.share || col.scale?.normalize === "percent";
    data.value = showShare ? formatValue(share, enc.label?.format || "pct1") : inspect(value);
    data.details = [{name: showShare ? "Value" : "Share", value: showShare ? inspect(value) : formatValue(share, "pct1")},
      {name: "Total", value: inspect(total)}];
  } else if (enc.kind === "range") {
    const end = row[enc.high];
    data.value = "";
    data.color = markColor(enc, row, undefined, Number(end) < Number(value));
    data.details = [{name: seriesName(col, enc, enc.source, context), value: inspect(value)},
      {name: seriesName(col, enc, enc.high, context), value: inspect(end)},
      {name: "Change", value: inspect(Number(end) - Number(value))}];
  } else if (enc.kind === "boxplot") {
    const labels = {minimum: enc.whisker === "iqr" ? "Lower whisker" : "Minimum", q1: "Lower quartile",
      median: "Median", q3: "Upper quartile", maximum: enc.whisker === "iqr" ? "Upper whisker" : "Maximum"};
    data.value = "";
    data.details = Object.entries(labels).map(([key, name]) => ({name, value: inspect(row[enc.parts?.[key]])}));
  }
  return data;
}

export function observationTooltip(name, value, code, source, color, excluded = []) {
  const details = source && typeof source === "object" && !Array.isArray(source)
    ? Object.entries(source).filter(([key, value]) => !excluded.includes(key) && key !== "color" && value != null && typeof value !== "object")
      .map(([key, value]) => ({name: columnHeading({name: key}), value: typeof value === "number" ? fullNumber(value) : String(value)})) : [];
  return {name: String(name ?? "Value"), value: tooltipValue(value, code), color, details};
}
