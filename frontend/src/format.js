// Evidence-compatible value formatting built on the `ssf` spreadsheet formatter.
import ssf from "ssf";

const CURRENCIES = {
  usd: "$",
  eur: "€",
  gbp: "£",
  aud: '"A$"',
  cad: '"C$"',
  cny: '"¥"',
  jpy: '"¥"',
  inr: '"₹"',
  krw: '"₩"',
  ngn: '"₦"',
  sek: '"kr"',
};

export const BASE_AUTO_FORMATS = [
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

const UNITS = { k: ',"k"', m: ',,"M"', b: ',,,"B"', t: ',,,,"T"' };
const DECIMALS = ["0", "0.0", "0.00", "0.000", "0.0000"];

function buildPresets() {
  const presets = {
    id: "0",
    fract: "# ?/?",
    sci: "0.00E+0",
    mult: '#,##0.0"x"',
    mult0: '#,##0"x"',
    mult1: '#,##0.0"x"',
    mult2: '#,##0.00"x"',
    date: "yyyy-mm-dd",
    ddd: "ddd",
    dddd: "dddd",
    mmm: "mmm",
    mmmm: "mmmm",
    "mmm-yy": "mmm-yy",
    yyyy: "yyyy",
    quarter: "quarter",
    qq: "qq",
    shortdate: "mmm d/yy",
    longdate: "mmmm d, yyyy",
    fulldate: "dddd mmmm d, yyyy",
    mdy: "m/d/y",
    dmy: "d/m/y",
    hms: "H:MM:SS AM/PM",
  };
  for (let d = 0; d <= 4; d++) presets[`num${d}`] = `#,##${DECIMALS[d]}`;
  for (let d = 0; d <= 3; d++) presets[`pct${d}`] = `#,##${DECIMALS[d]}%`;
  for (const [unit, suffix] of Object.entries(UNITS)) {
    for (let d = 0; d <= 2; d++) presets[`num${d}${unit}`] = `#,##${DECIMALS[d]}${suffix}`;
  }
  for (const [cur, symbol] of Object.entries(CURRENCIES)) {
    for (let d = 0; d <= 2; d++) presets[`${cur}${d}`] = `${symbol}#,##${DECIMALS[d]}`;
    presets[`${cur}0k`] = `${symbol}#,##0,"k"`;
    presets[`${cur}1k`] = `${symbol}#,##0.0,"k"`;
    presets[`${cur}2k`] = `${symbol}#,##0.00,"k"`;
    for (const [unit, suffix] of Object.entries(UNITS)) {
      for (let d = 0; d <= 2; d++) presets[`${cur}${d}${unit}`] = `${symbol}#,##${DECIMALS[d]}${suffix}`;
    }
  }
  return presets;
}

export const FORMAT_PRESETS = buildPresets();

const DATE_FORMATS = new Set([
  "date", "ddd", "dddd", "mmm", "mmmm", "mmm-yy", "yyyy", "quarter", "qq",
  "shortdate", "longdate", "fulldate", "mdy", "dmy", "hms",
]);

function isDateFormatCode(code) {
  if (!code) return false;
  if (DATE_FORMATS.has(code.toLowerCase())) return true;
  return /\b(yyyy|yy|mmmm|mmm|dd|ddd|dddd|hh|ss|AM|PM)\b/i.test(code);
}

function getAutoFormat(base, range) {
  let decimals = "0";
  let unit = "";
  if (range && range.max != null && isFinite(range.max)) {
    const max = Math.abs(range.max);
    if (base === "pct") {
      if (max < 0.1) decimals = "2";
      else if (max < 1) decimals = "1";
    } else {
      if (max < 10) decimals = "2";
      else if (max < 100) decimals = "1";
    }
    if (base !== "pct") {
      if (max >= 1e12) { unit = "t"; decimals = "1"; }
      else if (max >= 1e9) { unit = "b"; decimals = "1"; }
      else if (max >= 1e6) { unit = "m"; decimals = "1"; }
      else if (max >= 4000) { unit = "k"; decimals = "0"; }
    }
  }
  return base + decimals + unit;
}

function standardizeDateString(date) {
  if (typeof date !== "string") return date;
  const parts = date.split(" ");
  let out = date;
  if (!out.includes(":")) out = out + "T00:00:00";
  if (parts.length > 2) out = parts[0] + " " + parts[1];
  out = out.replace(/\.([^\s]+)/, "");
  out = out.replace("Z", "");
  out = out.replace(/[+-]\d{2}:?\d{2}$/, "");
  out = out.replace(" ", "T");
  return out;
}

function toDate(value) {
  if (value instanceof Date) {
    return Number.isNaN(value.getTime()) ? null : value;
  }
  if (typeof value === "number") {
    // Millisecond timestamps.
    if (Math.abs(value) >= 1e11) {
      const d = new Date(value);
      if (!Number.isNaN(d.getTime())) {
        return new Date(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate(),
          d.getUTCHours(), d.getUTCMinutes(), d.getUTCSeconds());
      }
    }
    return null;
  }
  if (typeof value === "string" && !Number.isNaN(Date.parse(standardizeDateString(value)))) {
    return new Date(standardizeDateString(value));
  }
  return null;
}

/** Weekend/month/day-part aware conversions used by Evidence date formats. */
function convertDatePart(value, code, firstDayOfWeek = "sunday") {
  const resolved = FORMAT_PRESETS[code] || code;
  const numeric = typeof value === "number" ? value : (typeof value === "string" && !Number.isNaN(Number(value)) ? Number(value) : null);
  if (numeric === null || !code) return value;

  if (code === "ddd" || code === "dddd" || resolved === "ddd" || resolved === "dddd") {
    if (numeric >= 1 && numeric <= 7) {
      const short = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
      const long = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
      const idx = firstDayOfWeek === "sunday" ? numeric - 1 : (numeric === 7 ? 0 : numeric);
      return code === "ddd" || resolved === "ddd" ? short[idx] : long[idx];
    }
    return toDate(numeric) || value;
  }
  if (code === "mmm" || code === "mmmm" || resolved.includes("mmm")) {
    if (numeric >= 1 && numeric <= 12) return new Date(2024, numeric - 1, 1);
    return toDate(numeric) || value;
  }
  if (code === "yyyy" || resolved.includes("yyyy")) {
    if (numeric >= 1900 && numeric <= 2100) return new Date(numeric, 0, 1);
    return toDate(numeric) || value;
  }
  return value;
}

function formatQuarter(value, bare = false) {
  const date = value instanceof Date ? value : toDate(value);
  if (!date) return null;
  const q = Math.floor(date.getMonth() / 3) + 1;
  return bare ? `Q${q}` : `${date.getFullYear()}-Q${q}`;
}

/**
 * Format a single cell value.
 * @param {*} value
 * @param {string|undefined|null} formatCode
 * @param {object} [opts]
 */
export function formatValue(value, formatCode, opts = {}) {
  const { range, type, fallback, firstDayOfWeek = "sunday" } = opts;
  const fallbackValue = fallback != null ? fallback : (value == null ? "–" : String(value));
  if (value === null || value === undefined) return fallbackValue;
  if (value === "Total") return "Total";

  let code = formatCode;
  if (!code) {
    if (type && /date|time/i.test(type)) code = "date";
    else if (typeof value === "number") code = "num";
    else if (typeof value === "string" && value.trim() !== "" && !Number.isNaN(Number(value))) code = "num";
  }
  if (!code) {
    if (typeof value === "object") return JSON.stringify(value);
    return fallbackValue;
  }

  // Special formatters (Great Tables-style).
  if (code === "bytes") return formatBytes(Number(value));
  if (code === "duration") return formatDuration(Number(value));
  if (code === "roman") return formatRoman(Number(value));
  if (code === "flag") return formatFlag(String(value));

  try {
    let processed = convertDatePart(value, code, firstDayOfWeek);

    if (typeof processed === "string") {
      if (type && /date|time/i.test(type)) processed = toDate(processed) || processed;
      else if (type && /int|decimal|float|double|number/i.test(type)) processed = Number(processed);
      else if (!Number.isNaN(Number(processed)) && !isDateFormatCode(code)) processed = Number(processed);
      else if (!Number.isNaN(Date.parse(standardizeDateString(processed))) && isDateFormatCode(code)) {
        processed = toDate(processed) || processed;
      }
    }

    let actual = code;
    if ((processed === 0 || processed === "0") && code.length === 3 && BASE_AUTO_FORMATS.includes(code)) {
      actual = `${code}0`;
    } else if (code.length === 3 && BASE_AUTO_FORMATS.includes(code)) {
      let effectiveRange = range;
      if (!effectiveRange && typeof processed === "number") {
        effectiveRange = { min: processed, max: processed };
      }
      actual = getAutoFormat(code, effectiveRange);
    }

    if (actual === "quarter") {
      return formatQuarter(processed) ?? fallbackValue;
    }
    if (actual === "qq") {
      return formatQuarter(processed, true) ?? fallbackValue;
    }

    const isDate = isDateFormatCode(actual);
    actual = FORMAT_PRESETS[actual] || actual;
    actual = actual.replace(/'/g, '"');

    if (typeof processed === "number" && (actual.includes('"Q"')) && (processed < 1 || processed > 4)) {
      return "";
    }

    let out = ssf.format(actual, processed, { date1970: true });
    if (out == null || out === "") out = fallbackValue;
    return out;
  } catch (err) {
    if (typeof value === "object") return JSON.stringify(value);
    return fallbackValue;
  }
}

const BYTE_UNITS = ["B", "KB", "MB", "GB", "TB", "PB"];

function formatBytes(value) {
  if (!isFinite(value)) return String(value);
  let amount = Math.abs(value);
  let unit = 0;
  while (amount >= 1024 && unit < BYTE_UNITS.length - 1) {
    amount /= 1024;
    unit += 1;
  }
  const sign = value < 0 ? "-" : "";
  const decimals = amount >= 100 || unit === 0 ? 0 : amount >= 10 ? 1 : 2;
  return `${sign}${amount.toFixed(decimals)} ${BYTE_UNITS[unit]}`;
}

function formatDuration(value) {
  if (!isFinite(value)) return String(value);
  const sign = value < 0 ? "-" : "";
  let seconds = Math.round(Math.abs(value));
  const days = Math.floor(seconds / 86400);
  seconds %= 86400;
  const hours = Math.floor(seconds / 3600);
  seconds %= 3600;
  const minutes = Math.floor(seconds / 60);
  seconds %= 60;
  const parts = [];
  if (days) parts.push(`${days}d`);
  if (hours) parts.push(`${hours}h`);
  if (minutes) parts.push(`${minutes}m`);
  if (seconds || parts.length === 0) parts.push(`${seconds}s`);
  return sign + parts.join(" ");
}

const ROMAN = [
  [1000, "M"], [900, "CM"], [500, "D"], [400, "CD"], [100, "C"], [90, "XC"],
  [50, "L"], [40, "XL"], [10, "X"], [9, "IX"], [5, "V"], [4, "IV"], [1, "I"],
];

function formatRoman(value) {
  if (!Number.isInteger(value) || value <= 0 || value >= 4000) return String(value);
  let remaining = value;
  let out = "";
  for (const [number, symbol] of ROMAN) {
    while (remaining >= number) {
      out += symbol;
      remaining -= number;
    }
  }
  return out;
}

function formatFlag(code) {
  const text = String(code).trim().toUpperCase();
  if (!/^[A-Z]{2}$/.test(text)) return code;
  return String.fromCodePoint(...[...text].map((letter) => 0x1f1e6 + letter.charCodeAt(0) - 65));
}

/** Human-friendly column title from a snake_case / expression-ish name. */
export function formatTitle(name) {
  if (name == null) return "";
  const s = String(name);
  const base = s.includes(".") ? s.slice(s.lastIndexOf(".") + 1) : s;
  return base
    .replace(/_/g, " ")
    .replace(/\b\w/g, (c) => c.toUpperCase());
}
