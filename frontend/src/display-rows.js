// Annotation cells have their own presentation; detail bindings never run here.
import { h, isStub } from "./dom.js";
import { formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { shaded } from "./rows.js";
import { decorateSubcolumn } from "./headers.js";

export function renderAnnotation(entry, columns, ctx, options) {
  const section = entry.kind === "section";
  const classes = ["et-row", "et-display-row", `et-display-${entry.kind}`,
    section ? "et-row-section" : entry.kind === "summary" ? "et-row-subtotal" : "et-row-total",
    entry.continuation ? "et-row-continuation" : "", `et-display-rule-${entry.rule}`,
    shaded(ctx.shadingCounter.value++, options) ? "et-row-shaded" : ""];
  const tr = h("tr", {class: classes.filter(Boolean).join(" "), "data-display-id": entry.id});
  const applyStyle = cell => {
    for (const [key, value] of Object.entries(entry.style)) cell.style.setProperty(key.replaceAll("_", "-"), String(value));
  };
  const indentLabel = cell => {
    if (entry.depth && entry.align !== "center" && options.section_indent) {
      cell.style.paddingLeft = `calc(0.25rem + ${entry.depth * Math.max(0, Number(options.section_indent))}rem)`;
    }
  };
  if (section && !Object.keys(entry.cells).length) {
    const cell = h("td", {class: `et-td et-display-heading et-display-align-${entry.align}`,
      colspan: columns.length + (ctx.rowNumbers ? 1 : 0) + (options.link ? 1 : 0)}, entry.label);
    indentLabel(cell);
    applyStyle(cell);
    tr.append(cell);
    return tr;
  }
  if (ctx.rowNumbers) tr.append(h("td", {class: "et-td et-row-num"}));
  const labelColumn = entry.labelColumn || columns.find(col => isStub(options, col))?.name || columns[0]?.name;
  columns.forEach((col, index) => {
    const cell = h("td", {class: `et-td${isStub(options, col) ? " et-stub" : ""}`,
      style: {textAlign: col.align || (col.type === "number" ? "right" : "left")}});
    const spec = entry.cells[col.name];
    if (col.name === labelColumn && entry.label) {
      cell.append(h("span", {class: "et-display-label"}, entry.label));
      indentLabel(cell);
    }
    if (spec) {
      const raw = spec.value;
      const text = raw == null ? (col.null_text ?? options.null_text ?? "–")
        : typeof raw === "string" ? raw
          : formatValue(raw, spec.format || col.fmt, {type: col.type, fallback: String(raw)});
      cell.append(h("span", {class: "et-display-value"}, formattedText(text)));
    }
    decorateSubcolumn(cell, col, index, ctx);
    applyStyle(cell);
    tr.append(cell);
  });
  if (options.link) tr.append(h("td", {class: "et-td et-td-chevron"}));
  return tr;
}
