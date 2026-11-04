// @ts-check
import { formatTitle } from "./format.js";

/** Serialize raw fields without losing record boundaries to either newline form.
 * @param {unknown} value
 */
export function csvField(value) {
  if (value == null) return "";
  const text = typeof value === "object" ? JSON.stringify(value) : String(value);
  return /[",\r\n]/.test(text) ? `"${text.replaceAll('"', '""')}"` : text;
}

/** @param {import('./contracts.js').CsvColumn[]} columns
 * @param {Record<string, unknown>[]} rows
 */
export function serializeCsv(columns, rows) {
  const lines = [columns.map(column => csvField(column.title || formatTitle(column.name))).join(",")];
  for (const row of rows) lines.push(columns.map(column => csvField(row[column.name])).join(","));
  return lines.join("\n");
}
