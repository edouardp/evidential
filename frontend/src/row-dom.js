// Ordinary and legacy-compatible row DOM; dataset projection lives elsewhere.
import {h} from "./dom.js";
import {shaded} from "./rows.js";
import {navigationUrl} from "./urls.js";
import {colorStylesFromHex, setCellBackground} from "./color.js";
import {bindRowSelection} from "./interactions.js";
import {renderCell} from "./cells.js";
import {decorateSubcolumn} from "./headers.js";

export function renderDataRow(row, columns, ctx, index, ports) {
  const opts = ctx.options;
  if (row.render_type === "row_section" && row.__combined) {
    // Render explicit section values in ordinary cells beside the label.
    row = {...row, render_type: "row_subtotal", __level: 0,
      [columns[0]?.name]: row.__label};
  } else if (["row_total", "row_subtotal"].includes(row.render_type) && row.__label && columns[0] && row[columns[0].name] == null) {
    row = {...row, [columns[0].name]: row.__label};
  }
  const renderType = row.render_type || "cell_data";
  if (renderType !== "cell_data") ctx.previousDetailRow = null;
  if (renderType === "row_section") {
    const colSpan = columns.length + (ctx.rowNumbers ? 1 : 0) + (opts.link ? 1 : 0);
    const label = row.__label ?? (columns[0] ? row[columns[0].name] : "");
    const align = row.__align === "center" ? "center" : "left";
    // A section row takes part in the alternating shading pattern.
    const shadedSection = shaded(ctx.shadingCounter.value++, opts);
    return h("tr", { class: `et-row et-row-section${shadedSection ? " et-row-shaded" : ""}` }, [
      h("td", { class: `et-td et-section-cell et-section-${align}`, colspan: colSpan }, String(label ?? "")),
    ]);
  }
  if (renderType === "row_spacer") {
    const colSpan = columns.length + (ctx.rowNumbers ? 1 : 0) + (opts.link ? 1 : 0);
    const style =
      row.__height == null
        ? {}
        : { height: typeof row.__height === "number" ? `${row.__height}px` : String(row.__height) };
    return h("tr", { class: "et-row et-row-spacer" }, [
      h("td", { class: "et-td et-spacer-cell", colspan: colSpan, style }),
    ]);
  }
  const isTotal = renderType === "row_total";
  const isSubtotal = renderType === "row_subtotal";
  const isCollapsed = isSubtotal && row.__group_key && ports.isCollapsed(row.__group_key);
  const hasLink = opts.link && navigationUrl(row[opts.link]);
  const rowColorValue = opts.row_conditional_colors ? row[opts.row_conditional_colors] : null;
  const rowColorStyles =
    typeof rowColorValue === "string" ? colorStylesFromHex(rowColorValue) : null;

  const tr = h("tr", {
    class: [
      "et-row",
      isTotal ? "et-row-total" : "",
      isSubtotal ? "et-row-subtotal" : "",
      row.__combined ? "et-row-combined" : "",
      hasLink ? "et-row-link" : "",
      isSubtotal ? "et-row-collapsible" : "",
      (renderType === "cell_data" || row.__combined) && shaded(ctx.shadingCounter.value++, opts) ? "et-row-shaded" : "",
    ].filter(Boolean).join(" "),
  });
  if (hasLink) tr.addEventListener("click", () => { window.location.href = hasLink; });

  bindRowSelection(tr, row, ctx.selected, opts, ports.model, ports.findSelectedRow);

  if (ctx.rowNumbers) {
    const numberCell = h(
      "td",
      { class: "et-td et-row-num", "data-column-index": 0 },
      String((ctx.rowNumberBase || 0) + index + 1),
    );
    if (rowColorStyles) {
      setCellBackground(numberCell, rowColorStyles.backgroundColor);
      numberCell.style.color = rowColorStyles.color;
    }
    tr.append(numberCell);
  }

  const rowIndex = index;
  columns.forEach((col, columnIndex) => {
    const cell = renderCell({row, col, index: columnIndex, ctx, rowIndex, options: opts,
      toggleGroup: (key, focus) => ports.toggleGroup(key, focus), isCollapsed, rowColorStyles});
    if (cell) {
      decorateSubcolumn(cell, col, columnIndex, ctx);
      tr.append(cell);
    }
  });

  if (opts.link) {
    const chevTd = h("td", { class: "et-td et-td-chevron" });
    if (hasLink) chevTd.append(h("span", { class: "et-row-chevron" }, "›"));
    tr.append(chevTd);
  }
  ctx.previousDetailRow = renderType === "cell_data" ? row : null;
  return tr;
}

