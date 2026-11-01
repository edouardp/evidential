// Annotation cells have their own presentation; detail bindings never run here.
import { h, isStub } from "./dom.js";
import { formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { shaded, sectionPadding } from "./rows.js";
import { decorateSubcolumn } from "./headers.js";
import { setCellBackground } from "./color.js";

export function renderAnnotation(entry, columns, ctx, options) {
  const section = entry.kind === "section";
  const classes = ["et-row", "et-display-row", `et-display-${entry.kind}`,
    section ? "et-row-section" : entry.kind === "summary" ? "et-row-subtotal" : "et-row-total",
    entry.continuation ? "et-row-continuation" : "", `et-display-rule-${entry.rule}`,
    shaded(ctx.shadingCounter.value++, options) ? "et-row-shaded" : ""];
  const tr = h("tr", {class: classes.filter(Boolean).join(" "), "data-display-id": entry.id});
  const renderLabel = () => {
    const label = h("span", {class: "et-display-label"});
    for (const [key, value] of Object.entries(entry.labelStyle || {})) {
      label.style.setProperty(key.replaceAll("_", "-"), String(value));
    }
    if (section && entry.collapsible) {
      label.append(h("button", {class: "et-section-toggle", type: "button", "data-section-key": entry.groupKey,
        "aria-expanded": String(!entry.collapsed), "aria-label": `Toggle section ${entry.label}`,
        onclick: event => { event.stopPropagation(); ctx.toggleSection(entry.groupKey); }},
      [h("span", {class: "et-section-chevron", "aria-hidden": "true"}, entry.collapsed ? "▸" : "▾"), entry.label]));
    } else label.append(document.createTextNode(entry.label));
    return label;
  };
  const applyStyle = cell => {
    for (const [key, value] of Object.entries(entry.style)) {
      const property = key.replaceAll("_", "-");
      if (["background", "background-color"].includes(property) && setCellBackground(cell, String(value))) continue;
      cell.style.setProperty(property, String(value));
    }
  };
  const indentLabel = cell => {
    const padding = entry.align !== "center" && sectionPadding(entry.depth, options, entry.toggleDepth);
    if (padding) cell.style.paddingLeft = padding;
  };
  if (section && !Object.keys(entry.cells).length) {
    const cell = h("td", {class: `et-td et-display-heading et-display-align-${entry.align}`,
      colspan: columns.length + (ctx.rowNumbers ? 1 : 0) + (options.link ? 1 : 0)},
    renderLabel());
    indentLabel(cell);
    applyStyle(cell);
    tr.append(cell);
    return tr;
  }
  if (ctx.rowNumbers) tr.append(h("td", {class: "et-td et-row-num", "data-column-index": 0}));
  const labelColumn = columns.find(col => col.name === entry.labelColumn)?.name ||
    columns.find(col => isStub(options, col))?.name || columns[0]?.name;
  columns.forEach((col, index) => {
    const cell = h("td", {class: `et-td${isStub(options, col) ? " et-stub" : ""}`,
      style: {textAlign: col.align || (col.type === "number" ? "right" : "left")}});
    const spec = entry.cells[col.name];
    if (col.name === labelColumn && (entry.label || entry.collapsible)) {
      if (section) cell.classList.add("et-display-label-cell");
      cell.append(renderLabel());
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
