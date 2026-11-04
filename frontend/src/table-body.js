// Physical table DOM: headers, axes, placeholders and display/data rows.
import {h, isStub, withFigure, alignStyle} from "./dom.js";
import {labelFootnotes} from "./footnotes.js";
import {renderColumnSizing} from "./column-sizing.js";
import {decorateSubcolumn} from "./headers.js";
import {renderAnnotation} from "./display-rows.js";
import {renderDataRow} from "./row-dom.js";
import {axisTicks, marksDomain, scalePosition} from "./mark-scales.js";
import {formatValue} from "./format.js";
import {formattedText} from "./formatted-text.js";

export function renderTable(columns, rows, context, ports) {
  const ctx = {...context};
  const opts = ctx.options;
  const table = h("table", { class: `et-table${ctx.hasTopAxis ? " et-has-top-axis" : ""}` });
  const sizing = renderColumnSizing(columns, {rowNumbers: ctx.rowNumbers, link: !!opts.link});
  if (sizing) table.append(sizing);
  const thead = ports.header;
  if (!ctx.isEmpty && ctx.stats) thead.append(ports.statistics);
  if (ctx.hasTopAxis) appendTopAxis(thead, columns, ctx);
  table.append(thead);
  const tbody = h("tbody");
  ctx.shadingCounter = { value: 0 };
  ctx.previousDetailRow = null;
  if (ctx.isEmpty) {
    // A placeholder body: the message overlay is a `::after` on the tbody, so
    // it covers the rows but not the header.
    tbody.classList.add("et-empty-body");
    tbody.dataset.emptyMessage = ctx.emptyMessage;
    for (let i = 0; i < ctx.emptyRows; i++) {
      tbody.append(renderPlaceholderRow(columns, ctx));
    }
  } else {
    if (ctx.continuationRow) {
      // A section that spans pages repeats its label at the top of the page.
      const heading = renderDataRow(ctx.continuationRow, columns, ctx, 0, ports);
      heading.classList.add("et-row-continuation");
      tbody.append(heading);
    }
    if (ctx.displayEntries) {
      for (const entry of ctx.displayEntries) {
        if (entry.kind === "data") {
          ctx.displayInset = entry.inset ? entry.depth : 0;
          ctx.displayToggleDepth = entry.toggleDepth || 0;
          tbody.append(renderDataRow(entry.row, columns, ctx, entry.ordinal - ctx.rowNumberBase, ports));
        } else {
          ctx.previousDetailRow = null;
          tbody.append(renderAnnotation(entry, columns, ctx, opts));
        }
      }
      ctx.displayInset = false;
      ctx.displayToggleDepth = 0;
    } else rows.forEach((row, index) => tbody.append(renderDataRow(row, columns, ctx, index, ports)));
  }
  table.append(tbody);
  if (ctx.hasBottomAxis) table.append(h("tfoot", {}, renderAxisRow(columns, ctx, "bottom")));
  labelFootnotes(table, ctx.footnotes.length, opts);
  return table;
}

/** Unscaled labels stay at the body's first line while scaled labels move up. */
function appendTopAxis(thead, columns, ctx) {
  const covered = new Set();
  if (!ctx.stats) {
    for (const cell of thead.querySelector(".et-header-leaves").children) {
      const start = Number(cell.dataset.columnStart);
      const first = start - (ctx.rowNumbers ? 1 : 0);
      const members = columns.slice(Math.max(0, first), first + cell.colSpan);
      const hasAxis = first >= 0 && members.some(col => col.encodings && col.scale?.axis && col.scale.axis_position !== "bottom");
      if (hasAxis) continue;
      cell.rowSpan = 2;
      for (let index = start; index < start + cell.colSpan; index++) covered.add(index);
    }
  }
  thead.append(renderAxisRow(columns, ctx, "top", covered));
}

/** A tick axis for the marks columns that ask for one (`scale(axis=True)`). */
function renderAxisRow(columns, ctx, position, covered = new Set()) {
  const opts = ctx.options;
  const tr = h("tr", { class: `et-axis-row et-axis-row-${position}` });
  if (ctx.rowNumbers && !covered.has(0)) tr.append(h("td", { class: "et-td et-row-num", "data-column-index": 0 }));
  for (const [index, col] of columns.entries()) {
    if (covered.has(index + (ctx.rowNumbers ? 1 : 0))) continue;
    const scale = col.scale || {};
    const cell = h("td", { class: `et-td${isStub(opts, col) ? " et-stub" : ""}` });
    decorateSubcolumn(cell, col, index, ctx);
    tr.append(cell);
    if (!col.encodings || !scale.axis || (scale.axis_position || "top") !== position) {
      continue;
    }
    cell.classList.add("et-axis-cell");
    const { lo, hi } = marksDomain(col, ctx.ranges.get(col) || ctx.ranges.get(col.name));
    const pos = scalePosition(lo, hi, scale.transform, (col.encodings || []).some(enc => enc.kind === "bar" && enc.direction === "left"));
    const axis = h("div", { class: "et-axis" });
    for (const {value: tick, major} of axisTicks(lo, hi, 4, scale.transform)) {
      const raw = pos(tick);
      if (raw == null) continue;
      const pct = Math.max(0, Math.min(100, raw));
      const label = major ? formatValue(tick, col.fmt || (Number.isInteger(tick) ? "num0" : "num"), {
        type: col.type,
        range: ctx.formatRanges.get(col.name),
        fallback: String(tick),
      }) : "";
      axis.append(h("span", { class: `et-axis-tick${major ? "" : " et-axis-tick-minor"}`,
        "aria-hidden": major ? null : "true", style: { left: `${pct}%` } }, formattedText(label)));
    }
    cell.append(axis);
  }
  if (opts.link) tr.append(h("td", { class: "et-td" }));
  return tr;
}

/** A blank row; its cells keep the column alignment and borders. */
function renderPlaceholderRow(columns, ctx) {
  const opts = ctx.options;
  const tr = h("tr", { class: "et-row et-row-placeholder" });
  let first = null;
  if (ctx.rowNumbers) {
    first = h("td", { class: "et-td et-row-num", "data-column-index": 0 });
    tr.append(first);
  }
  for (const [index, col] of columns.entries()) {
    const td = h("td", { class: "et-td", style: withFigure(alignStyle(col), col, opts) });
    if (!first) first = td;
    decorateSubcolumn(td, col, index, ctx);
    tr.append(td);
  }
  if (opts.link) tr.append(h("td", { class: "et-td et-td-chevron" }));
  // One non-breaking space gives the empty row the normal line height.
  if (first) first.append(document.createTextNode("\u00a0"));
  return tr;
}

