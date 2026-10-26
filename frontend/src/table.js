// Evidence-style data table renderer for the anywidget frontend.
//
// The widget receives fully JSON-serializable `rows`, `columns`, and `options`
// from Python and renders a sortable, searchable, formattable table with
// conditional visualizations, collapsible groups, frozen columns, pagination,
// CSV export, and a fullscreen dialog.
import { footnoteMark, labelFootnotes } from "./footnotes.js";
import { fitMarkLabels } from "./mark-labels.js";
import { projectLayout, projectLegacy } from "./row-layout.js";
import { renderAnnotation } from "./display-rows.js";
import { renderStatsRow } from "./statistics.js";
import { renderHeader, headerLayout, decorateSubcolumn, orderedColumns } from "./headers.js";
import { renderColumnSizing } from "./column-sizing.js";
import { RowPipeline } from "./derived.js";
import { HoldController, bindRowSelection } from "./interactions.js";
import { LoadingController } from "./loading.js";
import { TableViewport } from "./viewport.js";
import { h, inlineMarkdown, withFigure, formatRowRanges, alignStyle, isStub } from "./dom.js";
import { hiddenColumns, visibleRows, searchRows, sortRows, paginateRows,
  computeRowspans, shaded, sectionContinuation } from "./rows.js";
import { renderCell } from "./cells.js";
import { formatTitle, formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { axisTicks, marksDomain, scalePosition } from "./visualizations.js";

/** Map a `font_size` to a CSS value.
 *
 * An absolute CSS length ("14px", "1rem") is used as-is. A relative step — a
 * number or a "+2" / "-1" string — is added to `--et-font-size-base` by that
 * many 0.0625rem (1px at the usual 16px root) steps, so a table can sit a little
 * above or below the shared baseline.
 */
export function fontSizeValue(value) {
  if (value == null || value === "") return null;
  const text = String(value).trim();
  if (typeof value === "number" || /^[+-]?\d+(\.\d+)?$/.test(text)) {
    const steps = Number(text);
    return `calc(var(--et-font-size-base, 0.75rem) + ${steps * 0.0625}rem)`;
  }
  return text;
}
import { colorStylesFromHex, resolveColor } from "./color.js";

export class EvidentialTableRenderer {
  constructor(model, el) {
    this.model = model;
    this.el = el;
    this.destroyed = false;
    this._state = {
      sort: null,
      search: "",
      page: 0,
      collapsed: new Set(),
      expanded: new Set(),
      hidden: new Set(),
      statsMembers: new Map(),
    };
    this._pipeline = new RowPipeline();
    this._groupVersion = 0;
    this._pageCount = 1;
    this._pageSizeOverride = null;
    this._holdController = new HoldController((direction) => this._advance(direction));
    this._build();
  }

  get rows() { return this.model.get("rows") || []; }
  get columns() { return this.model.get("columns") || []; }
  get options() { return this.model.get("options") || {}; }

  _build() {
    this.root = h("div", { class: "et-root", dataset: { widget: "evidence-table" } });
    this.titlebar = h("div", { class: "et-titlebar" });
    this.toolbar = h("div", { class: "et-toolbar" });
    this.scroller = h("div", { class: "et-scroller" });
    // The body wrapper keeps the loading overlay fixed over the scroller even
    // when the table is scrolled, and lets us lock the height during updates.
    this.body = h("div", { class: "et-body" }, this.scroller);
    this.loadingOverlay = h(
      "div",
      { class: "et-loading-overlay", role: "status", "aria-live": "polite", "aria-hidden": "true" },
      [h("span", { class: "et-spinner", "aria-hidden": "true" }), "Processing…"],
    );
    this.body.append(this.loadingOverlay);
    this.footer = h("div", { class: "et-footer" });
    this.footnotesEl = h("div", { class: "et-footnotes" });
    this.caption = h("div", { class: "et-caption" });
    this.root.append(this.titlebar, this.toolbar, this.body, this.footer, this.footnotesEl, this.caption);
    this._loadingController = new LoadingController(this.root, this.loadingOverlay, this.el);
    const defaultSort = this.options.default_sort;
    if (defaultSort && defaultSort.column) {
      this._state.sort = {
        column: defaultSort.column,
        direction: defaultSort.direction === "asc" ? "asc" : "desc",
      };
    }
    this._baselineHeight = 0;
    this._baselinePageSize = null;

    // Fullscreen dialog and its controls.
    this.dialog = h("dialog", { class: "et-dialog", "aria-label": "Expanded data table" });
    this.expandBtn = h("button", {
      class: "et-text-btn et-expand-btn", type: "button", title: "Expand table",
      "aria-label": "Expand table", "aria-expanded": "false",
      onclick: () => this._viewport.toggle(),
    });
    this.expandBtn.textContent = "⛶ Expand";
    // A conventional close icon in the top-right corner, shown only while the
    // table is expanded (the dialog also closes on Esc and a backdrop click).
    this.closeBtn = h("button", {
      class: "et-text-btn et-close-btn", type: "button",
      title: "Close expanded table", "aria-label": "Close expanded table",
      onclick: () => this._viewport.close(),
    });
    this.closeBtn.textContent = "✕";
    this.root.append(this.closeBtn);
    // The comment marks where the widget lives inline so it can be moved back
    // after the fullscreen dialog closes. It must be attached to the DOM
    // before it can anchor anything.
    this.placeholder = document.createComment("evidence-table inline position");
    this.el.append(this.placeholder, this.root, this.dialog);

    this._viewport = new TableViewport({
      root: this.root, dialog: this.dialog, button: this.expandBtn,
      placeholder: this.placeholder, scroller: this.scroller,
      getOptions: () => this.options, rerender: () => this.render(),
      resetBaseline: () => this._resetBaselineHeight(),
      getPageSizeOverride: () => this._pageSizeOverride,
      setPageSizeOverride: (value) => { this._pageSizeOverride = value; },
    });

    this.render();
    this.setLoading(this.model.get("loading"));
  }

  _applyTheme() {
    const opts = this.options;
    const theme = opts.theme || {};
    const surface =
      theme.surface || theme.dialog_background || theme.background || opts.background_color;
    const vars = {
      "--et-bg": theme.background || opts.background_color,
      "--et-surface": surface,
      "--et-text": theme.text,
      "--et-muted": theme.muted,
      "--et-border": theme.border,
      "--et-row-border": theme.row_border || (typeof opts.row_lines === "string" ? opts.row_lines : null),
      "--et-header-bg": theme.header_bg || opts.header_color || surface,
      "--et-header-border": theme.header_border,
      "--et-header-text": theme.header_text || opts.header_font_color,
      "--et-hover": theme.hover,
      "--et-shading": theme.shading,
      "--et-total-bg": theme.total_bg || opts.total_row_color,
      "--et-total-text": theme.total_text || opts.total_font_color,
      "--et-subtotal-bg": theme.subtotal_bg,
      "--et-pivot-bg": theme.pivot_bg,
      "--et-link": theme.link,
      "--et-negative": theme.negative,
      "--et-accent": theme.accent,
      "--et-font": theme.font,
      "--et-font-size": fontSizeValue(opts.font_size) || theme.font_size,
    };
    for (const [k, v] of Object.entries(vars)) {
      for (const element of [this.root, this.dialog]) {
        if (v) element.style.setProperty(k, resolveColor(v));
        else element.style.removeProperty(k);
      }
    }
  }

  destroy() {
    this.destroyed = true;
    this._holdController.stop();
    this._loadingController.destroy();
    this._viewport.destroy();
    this._pipeline.clear();
    this.dialog.remove();
    this.placeholder.remove();
    this.root.remove();
  }

  // ---------------------------------------------------------------- state ---
  _defaultCollapsed() {
    // Section groups are always fully expanded (their cells are merged).
    if (this.options.group_type === "section") return false;
    return this.options.collapsible && this.options.collapsed !== false;
  }

  _isCollapsed(key) {
    if (this._defaultCollapsed()) return !this._state.expanded.has(key);
    return this._state.collapsed.has(key);
  }

  _toggleGroup(key, focus = false) {
    const set = this._defaultCollapsed() ? this._state.expanded : this._state.collapsed;
    if (set.has(key)) set.delete(key);
    else set.add(key);
    this._groupVersion++;
    // Expanding/collapsing is a deliberate change in row count, so drop the
    // "never shrink below the tallest page" baseline; otherwise collapsing a
    // group would leave the table at its expanded height (most visible with a
    // `max_height`).
    this._resetBaselineHeight();
    this.render();
    if (focus) {
      const cell = [...this.scroller.querySelectorAll("td[data-group-key]")]
        .find((cell) => cell.dataset.groupKey === key);
      cell?.querySelector("button.et-chevron")?.focus({ preventScroll: true });
    }
  }

  // ----------------------------------------------------------- pagination ---
  _effectivePageSize() {
    return this._pageSizeOverride ?? this.options.page_size;
  }

  _paginate(rows, hasGroups) {
    const page = paginateRows(rows, this._effectivePageSize(), this._state.page, this.options, hasGroups);
    this._state.page = page.page;
    return page;
  }
  // --------------------------------------------------------------- render ---
  render() {
    const opts = this.options;
    this._applyTheme();
    this.root.style.maxWidth =
      opts.width == null
        ? ""
        : typeof opts.width === "number"
          ? `${opts.width}px`
          : String(opts.width);
    // Inline max_height is for the compact notebook view; fullscreen must be
    // free to grow to the dialog height.
    if (this._viewport.expanded) {
      this.scroller.style.maxHeight = "none";
    } else if (opts.max_height) {
      this.scroller.style.maxHeight =
        typeof opts.max_height === "number" ? `${opts.max_height}px` : opts.max_height;
    } else {
      this.scroller.style.maxHeight = "";
    }
    this.root.classList.toggle("et-wrap", !!opts.wrap);
    this.root.classList.toggle("et-nowrap-titles", opts.wrap_titles === false);
    this.root.classList.toggle("et-no-row-lines", opts.row_lines === false);
    this.root.classList.toggle("et-no-border", opts.border === false);
    this.root.classList.toggle("et-row-shading", !!opts.row_shading);
    this.root.classList.toggle("et-compact", !!opts.compact);
    this.root.classList.toggle("et-stretch-off", opts.stretch === false);
    this.root.classList.toggle("et-group-gap", !!opts.group_gap);
    this._renderTitle();
    this._renderToolbar();

    const processed = this._pipeline.get({
      rows: this.rows, columns: this.columns, options: opts,
      rowLayout: this.model.get("row_layout"),
      search: this._state.search, hidden: hiddenColumns(this.columns, this._state.hidden), sort: this._state.sort,
    });
    const { columns, hasGroups, dimCount, ranges, formatRanges, decimals, colorScales, changeScales, stats } = processed;
    const layout = headerLayout(columns);
    const subcolumns = layout.joins;
    const visibility = this._pipeline.visible(processed, this._groupVersion, (key) => this._isCollapsed(key));
    const rowLayout = processed.rowLayout;
    const displayPage = rowLayout?.version && !rowLayout.legacy
      ? projectLayout(rowLayout, this.rows, processed.sorted, this._effectivePageSize(), this._state.page) : null;
    const { rows, pageCount, page, total, start } = displayPage || this._paginate(visibility.rows, visibility.hasGroups);
    this._state.page = page;
    this._pageCount = pageCount;
    const continuationLabel = displayPage ? null : sectionContinuation(visibility.rows, start, rows);

    // Section-style groups merge each group's dimension cell across its rows.
    // Count levels over all rows (not just the page) so a fully collapsed table
    // still knows how many dimensions it has.
    const section = opts.group_type === "section" && hasGroups && dimCount > 0;
    // Accordion groups indent child/parent dimension cells (Evidence parity).
    const accordion = hasGroups && !section && dimCount > 0;
    const rowspans = section
      ? computeRowspans(rows, dimCount, opts.subtotal_position !== "bottom")
      : null;

    // Oblique headings need a taller header and a little right padding.
    let obliqueAngle = null;
    let longestLabel = 0;
    for (const col of columns) {
      const rotation = col.rotate_title ?? (isStub(opts, col) ? null : opts.rotate_titles);
      if (typeof rotation !== "number") continue;
      obliqueAngle = rotation;
      const label = opts.format_titles === false ? col.name : col.title || formatTitle(col.name);
      longestLabel = Math.max(longestLabel, String(label).length);
    }
    if (obliqueAngle != null) {
      const sine = Math.abs(Math.sin((Math.abs(obliqueAngle) * Math.PI) / 180));
      this.root.style.setProperty(
        "--et-th-oblique-height",
        `${Math.max(4, longestLabel * 0.62 * sine + 1.5).toFixed(2)}em`,
      );
      this.root.classList.add("et-oblique");
    } else {
      this.root.classList.remove("et-oblique");
      this.root.style.removeProperty("--et-th-oblique-height");
    }
    this.scroller.replaceChildren();
    const footnotes = [];
    const isEmpty = rows.length === 0;
    const axisColumns = columns.filter((col) => col.encodings && (col.scale || {}).axis);
    const hasTopAxis = !isEmpty && axisColumns.some(col => col.scale.axis_position !== "bottom");
    const hasBottomAxis = !isEmpty && axisColumns.some(col => col.scale.axis_position === "bottom");
    // With columns configured, an empty table keeps its headers and shows blank
    // placeholder rows under a translucent message overlay, so it holds its size
    // while a filter or selection is pending. Without columns there is nothing
    // to draw, so fall back to a plain message.
    if (isEmpty && !columns.length) {
      this.scroller.append(
        h("div", { class: "et-empty" }, [h("span", {}, opts.empty_message || "No records")]),
      );
    } else {
      this.scroller.append(
        this._renderTable(columns, rows, {
          ranges,
          formatRanges,
          colorScales,
          changeScales,
          hasGroups,
          subcolumns,
          layout,
          rowNumbers: !!opts.row_numbers,
          rowNumberBase: page * (Number(this._effectivePageSize()) || 0),
          section,
          accordion,
          dimCount,
          rowspans,
          footnotes,
          decimals,
          stats,
          selected: opts.select ? this.model.get("selected") : null,
          isEmpty,
          emptyRows: isEmpty ? this._emptyRowCount(opts) : 0,
          emptyMessage: opts.empty_message || "No records",
          continuationLabel,
          displayEntries: displayPage?.entries,
          insetGroups: new Set(visibility.rows.filter(row => row.render_type === "row_section" && row.__align !== "center")
            .map(row => row.__group_key)),
          hasTopAxis,
          hasBottomAxis,
        }),
      );
    }
    const hasBelow = Boolean(opts.caption) || footnotes.length > 0 || (opts.footnotes || []).length > 0;
    this._renderFooter(page, pageCount, total, hasBelow);
    this._renderFootnotes(footnotes, opts.footnotes);
    this.caption.replaceChildren();
    if (opts.caption) this.caption.append(inlineMarkdown(opts.caption));
    this._updateBaselineHeight();
    this._viewport.frame(() => {
      this._viewport.applyFrozenOffsets();
      fitMarkLabels(this.root);
    });

    this.el.dataset.rowCount = String(total);
    this.el.dataset.renderCount = String((Number(this.el.dataset.renderCount) || 0) + 1);
  }

  // ------------------------------------------------------------- loading ---
  /** Reflect the loading trait through its lifecycle controller. */
  setLoading(loading) {
    this._loadingController.set(loading);
  }

  /** Keep the table from shrinking below the tallest page seen for the
   * current page size, so live updates never change the layout. */
  _updateBaselineHeight() {
    const pageSize = this._effectivePageSize();
    if (pageSize !== this._baselinePageSize) {
      // Page size changed (e.g. entering/leaving fullscreen): drop the old
      // baseline and clear min-height so we measure the natural new height
      // instead of the previous layout's forced height.
      this._baselinePageSize = pageSize;
      this._baselineHeight = 0;
      this.scroller.style.minHeight = "";
    }
    const height = this.scroller.getBoundingClientRect().height;
    if (height <= 0) return;
    this._baselineHeight = Math.max(this._baselineHeight || 0, height);
    this.scroller.style.minHeight = `${Math.round(this._baselineHeight)}px`;
    this.el.dataset.baselineHeight = String(Math.round(this._baselineHeight));
  }

  _renderTitle() {
    const { title, subtitle, info, info_link, info_link_title } = this.options;
    this.titlebar.replaceChildren();
    if (!title && !subtitle) return;
    const text = h("div", { class: "et-title-text" });
    if (title) {
      const t = h("span", { class: "et-title" });
      t.append(inlineMarkdown(title));
      if (info) {
        const infoSpan = h("span", { class: "et-info", title: info }, "ⓘ");
        if (info_link) {
          const a = h("a", { href: info_link, target: "_blank", rel: "noopener", class: "et-info-link" }, "ⓘ");
          a.title = info;
          if (info_link_title) a.append(document.createTextNode(` ${info_link_title}`));
          text.append(t, " ", a);
        } else {
          text.append(t, " ", infoSpan);
        }
      } else {
        text.append(t);
      }
    }
    if (subtitle) {
      const s = h("div", { class: "et-subtitle" });
      s.append(inlineMarkdown(subtitle));
      text.append(s);
    }
    this.titlebar.append(text);
  }

  _renderToolbar() {
    const opts = this.options;
    this.toolbar.replaceChildren();
    const left = h("div", { class: "et-toolbar-left" });
    const right = h("div", { class: "et-toolbar-right" });
    if (opts.search) {
      const input = h("input", {
        class: "et-search", type: "search", placeholder: "Search",
        "aria-label": "Search table", value: this._state.search,
      });
      input.addEventListener("input", () => {
        this._state.search = input.value;
        this._state.page = 0;
        this.render();
        // Restore focus + caret after the table re-renders.
        requestAnimationFrame(() => {
          const el = this.toolbar.querySelector(".et-search");
          if (el) { el.focus(); el.setSelectionRange(el.value.length, el.value.length); }
        });
      });
      left.append(input);
    }
    this.toolbar.append(left, right);
    this.toolbar.classList.toggle("et-toolbar-empty", !left.childElementCount && !right.childElementCount);
  }

  /** How many blank rows an empty table shows, to hold its height. */
  _emptyRowCount(opts) {
    const configured = Number(opts.empty_rows);
    if (Number.isFinite(configured) && configured > 0) return Math.min(Math.floor(configured), 200);
    const pageSize = Number(this._effectivePageSize());
    if (Number.isFinite(pageSize) && pageSize > 0) return Math.min(Math.floor(pageSize), 200);
    return 10;
  }

  _renderTable(columns, rows, ctx) {
    const opts = this.options;
    const table = h("table", { class: `et-table${ctx.hasTopAxis ? " et-has-top-axis" : ""}` });
    const sizing = renderColumnSizing(columns, {rowNumbers: ctx.rowNumbers, link: !!opts.link});
    if (sizing) table.append(sizing);
    const thead = this._renderHeader(columns, ctx);
    if (!ctx.isEmpty && ctx.stats) thead.append(this._renderStatsRow(columns, ctx));
    if (ctx.hasTopAxis) this._appendTopAxis(thead, columns, ctx);
    table.append(thead);
    const tbody = h("tbody");
    ctx.shadingCounter = { value: 0 };
    if (ctx.isEmpty) {
      // A placeholder body: the message overlay is a `::after` on the tbody, so
      // it covers the rows but not the header.
      tbody.classList.add("et-empty-body");
      tbody.dataset.emptyMessage = ctx.emptyMessage;
      for (let i = 0; i < ctx.emptyRows; i++) {
        tbody.append(this._renderPlaceholderRow(columns, ctx));
      }
    } else {
      if (ctx.continuationLabel) {
        // A section that spans pages repeats its label at the top of the page.
        const colSpan = columns.length + (ctx.rowNumbers ? 1 : 0) + (opts.link ? 1 : 0);
        tbody.append(
          h("tr", { class: "et-row et-row-section et-row-continuation" }, [
            h("td", { class: "et-td et-section-cell", colspan: colSpan }, String(ctx.continuationLabel)),
          ]),
        );
      }
      if (ctx.displayEntries) {
        for (const entry of ctx.displayEntries) {
          if (entry.kind === "data") {
            ctx.displayInset = entry.inset ? entry.depth : 0;
            tbody.append(this._renderRow(entry.row, columns, ctx, entry.ordinal - ctx.rowNumberBase));
          } else tbody.append(renderAnnotation(entry, columns, ctx, opts));
        }
        ctx.displayInset = false;
      } else rows.forEach((row, index) => tbody.append(this._renderRow(row, columns, ctx, index)));
    }
    table.append(tbody);
    if (ctx.hasBottomAxis) table.append(h("tfoot", {}, this._renderAxisRow(columns, ctx, "bottom")));
    labelFootnotes(table, ctx.footnotes.length, opts);
    return table;
  }

  /** Unscaled labels stay at the body's first line while scaled labels move up. */
  _appendTopAxis(thead, columns, ctx) {
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
    thead.append(this._renderAxisRow(columns, ctx, "top", covered));
  }

  /** A tick axis for the marks columns that ask for one (`scale(axis=True)`). */
  _renderAxisRow(columns, ctx, position, covered = new Set()) {
    const opts = this.options;
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
  _renderPlaceholderRow(columns, ctx) {
    const opts = this.options;
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

  _renderStatsRow(columns, ctx) {
    return renderStatsRow({columns, layout: ctx.layout, stats: ctx.stats,
      formatRanges: ctx.formatRanges, options: this.options, rowNumbers: ctx.rowNumbers,
      selections: this._state.statsMembers,
      onLayout: () => this._viewport.frame(() => this._viewport.applyFrozenOffsets())});
  }

  _renderHeader(columns, ctx) {
    return renderHeader({columns, rowNumbers: ctx.rowNumbers, options: this.options,
      sort: this._state.sort, onSort: (name) => {
        this._sortColumn(name);
        const replacement = [...this.scroller.querySelectorAll("thead [data-column]")]
          .find((cell) => cell.dataset.column === name);
        replacement?.focus({preventScroll: true});
      }});
  }

  _sortColumn(name) {
    const current = this._state.sort;
    if (!current || current.column !== name) {
      this._state.sort = { column: name, direction: "desc" };
    } else if (current.direction === "desc") {
      this._state.sort = { column: name, direction: "asc" };
    } else {
      this._state.sort = null;
    }
    this._state.page = 0;
    this.render();
  }

  _renderRow(row, columns, ctx, index) {
    const opts = this.options;
    if (row.render_type === "row_section" && row.__combined) {
      // Render explicit section values in ordinary cells beside the label.
      row = {...row, render_type: "row_subtotal", __level: 0,
        [columns[0]?.name]: row.__label};
    } else if (["row_total", "row_subtotal"].includes(row.render_type) && row.__label && columns[0] && row[columns[0].name] == null) {
      row = {...row, [columns[0].name]: row.__label};
    }
    const renderType = row.render_type || "cell_data";
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
    const isCollapsed = isSubtotal && row.__group_key && this._isCollapsed(row.__group_key);
    const hasLink = opts.link && row[opts.link];
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
    if (hasLink) tr.addEventListener("click", () => { window.location.href = String(row[opts.link]); });

    bindRowSelection(tr, row, ctx.selected, opts, this.model, (key) =>
      [...this.scroller.querySelectorAll("tr.et-row-selectable")]
        .find((row) => row.dataset.selectKey === String(key)));

    if (ctx.rowNumbers) {
      const numberCell = h(
        "td",
        { class: "et-td et-row-num", "data-column-index": 0 },
        String((ctx.rowNumberBase || 0) + index + 1),
      );
      if (rowColorStyles) {
        numberCell.style.backgroundColor = rowColorStyles.backgroundColor;
        numberCell.style.color = rowColorStyles.color;
      }
      tr.append(numberCell);
    }

    const rowIndex = index;
    columns.forEach((col, columnIndex) => {
      const cell = renderCell({row, col, index: columnIndex, ctx, rowIndex, options: opts,
        toggleGroup: (key, focus) => this._toggleGroup(key, focus), isCollapsed, rowColorStyles});
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
    return tr;
  }

  /** Render the footer notes collected while building rows, plus any static
   * `footnotes`, with the row numbers each note appears on. */
  _renderFootnotes(footnotes, staticFootnotes) {
    this.footnotesEl.replaceChildren();
    const items = footnotes.map((note) => ({
      mark: footnoteMark(note.index, this.options, footnotes.length),
      text: note.text,
      rows: [...note.rows].sort((a, b) => a - b),
    }));
    for (const text of staticFootnotes || []) {
      items.push({ mark: null, text: String(text), rows: [] });
    }
    if (!items.length) return;
    const list = h("ol", { class: "et-footnotes-list" });
    for (const item of items) {
      const entry = h("li", { class: "et-footnote-item" });
      if (item.mark) entry.append(h("sup", { class: "et-footnote-mark" }, item.mark));
      entry.append(document.createTextNode((item.mark ? " " : "") + item.text));
      if (item.rows.length) {
        entry.append(h("span", { class: "et-footnote-rows" }, ` (rows ${formatRowRanges(item.rows)})`));
      }
      list.append(entry);
    }
    this.footnotesEl.append(list);
  }

  _renderFooter(page, pageCount, total, hasBelow) {
    this.footer.replaceChildren();
    // With a single page there is no pager row to hold the actions. If
    // something sits below the table (footnotes or a caption) the actions float
    // at the bottom-right so that content keeps its place; with nothing below,
    // the footer stays in flow so the actions do not land on the last row.
    this.root.classList.toggle("et-float-actions", pageCount <= 1 && !!hasBelow);
    if (pageCount > 1) {
      const left = h("div", { class: "et-page-controls" });
      const pageSize = this._effectivePageSize();
      const start = page * pageSize + 1;
      const end = Math.min(total, (page + 1) * pageSize);

      const pageButton = (label, direction, disabled) => {
        const button = h(
          "button",
          {
            class: "et-btn et-page-btn",
            type: "button",
            disabled,
            "aria-label": direction === "next" ? "Next page" : "Previous page",
          },
          label,
        );
        button.addEventListener("pointerdown", (event) => {
          if (event.button !== undefined && event.button !== 0) return;
          this._holdController.start(direction);
        });
        button.addEventListener("click", () => {
          if (this._holdController.consumeClick()) return;
          this._gotoPage(this._state.page + (direction === "next" ? 1 : -1));
        });
        return button;
      };

      // A single left-aligned run: ‹ 1/3 › (1–2 of 5). The arrows stay real
      // buttons (same hitbox as before) but are styled as plain text.
      left.append(
        pageButton("‹", "prev", page === 0),
        h("span", { class: "et-page-current" }, `${page + 1}/${pageCount}`),
        pageButton("›", "next", page >= pageCount - 1),
        h("span", { class: "et-page-info" }, `(${start}–${end} of ${total})`),
      );
      this.footer.append(left);
    }
    this.footer.append(this._renderActions());
  }

  /** Bottom-right table actions (download, fullscreen) rendered as plain text.
   *  CSS fades them in while the pointer is anywhere over the table. */
  _renderActions() {
    const actions = h("div", { class: "et-table-actions" });
    if (this.options.download) {
      actions.append(
        h(
          "button",
          {
            class: "et-text-btn et-download-btn",
            type: "button",
            title: "Download CSV",
            "aria-label": "Download CSV",
            onclick: () => this._downloadCsv(),
          },
          "⤓ Download",
        ),
      );
    }
    actions.append(this.expandBtn);
    return actions;
  }

  _gotoPage(page) {
    const count = Math.max(1, this._pageCount || 1);
    this._state.page = Math.min(Math.max(0, page), count - 1);
    this.render();
  }

  _advance(direction) {
    const next = this._state.page + (direction === "next" ? 1 : -1);
    if (next < 0 || next >= this._pageCount) return false;
    this._gotoPage(next);
    return true;
  }

  // ----------------------------------------------------------- fullscreen ---

  _resetBaselineHeight() {
    this._baselineHeight = 0;
    this._baselinePageSize = null;
    this.scroller.style.minHeight = "";
  }

  // ------------------------------------------------------------- download ---
  _downloadCsv() {
    const hidden = hiddenColumns(this.columns, this._state.hidden);
    const columns = orderedColumns(this.columns.filter((c) => !hidden.has(c.name)), this.options);
    const searched = searchRows(this.rows, this.columns, this._state.search, hidden);
    const sorted = sortRows(searched, this.columns, this._state.sort);
    const layout = this.model.get("row_layout");
    const rows = layout?.legacy
      ? projectLegacy(layout, this.rows, sorted, key => this._isCollapsed(key)).filter(row => !row.render_type || row.render_type === "cell_data")
      : layout?.version ? projectLayout(layout, this.rows, sorted, "all", 0).rows
        : visibleRows(sorted, key => this._isCollapsed(key));
    const escape = (v) => {
      if (v === null || v === undefined) return "";
      const s = typeof v === "object" ? JSON.stringify(v) : String(v);
      return /[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s;
    };
    const lines = [columns.map((c) => escape(c.title || formatTitle(c.name))).join(",")];
    for (const row of rows) {
      lines.push(columns.map((c) => escape(row[c.name])).join(","));
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = (this.options.title || "table").replace(/\s+/g, "_").toLowerCase() + ".csv";
    a.click();
    URL.revokeObjectURL(url);
  }
}

export function render({ model, el }) {
  el.classList.add("evidential-widget");
  const renderer = new EvidentialTableRenderer(model, el);
  const rerender = () => renderer.render();
  let pendingDataRender = false;
  const dataChanged = () => {
    renderer._pipeline.clear();
    if (pendingDataRender) return;
    pendingDataRender = true;
    queueMicrotask(() => {
      pendingDataRender = false;
      if (!renderer.destroyed) renderer.render();
    });
  };
  const setLoading = () => renderer.setLoading(model.get("loading"));
  model.on("change:rows", dataChanged);
  model.on("change:columns", dataChanged);
  model.on("change:options", dataChanged);
  model.on("change:row_layout", dataChanged);
  model.on("change:loading", setLoading);
  model.on("change:selected", rerender);
  return () => {
    model.off("change:rows", dataChanged);
    model.off("change:columns", dataChanged);
    model.off("change:options", dataChanged);
    model.off("change:row_layout", dataChanged);
    model.off("change:selected", rerender);
    model.off("change:loading", setLoading);
    renderer.destroy();
  };
}

export default { render };
