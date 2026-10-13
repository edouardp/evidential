import { RowPipeline } from "./derived.js";
// Evidence-style data table renderer for the anywidget frontend.
//
// The widget receives fully JSON-serializable `rows`, `columns`, and `options`
// from Python and renders a sortable, searchable, formattable table with
// conditional visualizations, collapsible groups, frozen columns, pagination,
// CSV export, and a fullscreen dialog.
import { HoldController, bindRowSelection } from "./interactions.js";
export { holdInterval } from "./interactions.js";
import { LoadingController } from "./loading.js";
import { TableViewport } from "./viewport.js";
import { h, optString, inlineMarkdown, withFigure, formatRowRanges } from "./dom.js";
import { hiddenColumns, orderedColumns, visibleRows, searchRows, sortRows, paginateRows,
  columnStats, computeRowspans, shaded, groupPath,
  buildHeaderLevels } from "./rows.js";
import { renderCell, alignStyle, footnoteMark } from "./cells.js";
import { formatValue, formatTitle } from "./format.js";
import {
  colorStylesFromHex,
} from "./color.js";

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
  get _expanded() { return this._viewport?.expanded ?? false; }
  set _expanded(value) { if (this._viewport) this._viewport.expanded = value; }

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

    // Fullscreen dialog (same pattern as galaga's cga3d widget).
    this.dialog = h("dialog", { class: "et-dialog", "aria-label": "Expanded data table" });
    this.expandBtn = h("button", {
      class: "et-text-btn et-expand-btn", type: "button", title: "Expand table",
      "aria-label": "Expand table", "aria-expanded": "false",
      onclick: () => this._toggleExpanded(),
    });
    this.expandBtn.textContent = "⛶ Expand";
    // A conventional close icon in the top-right corner, shown only while the
    // table is expanded (the dialog also closes on Esc and a backdrop click).
    this.closeBtn = h("button", {
      class: "et-text-btn et-close-btn", type: "button",
      title: "Close expanded table", "aria-label": "Close expanded table",
      onclick: () => this._closeExpanded(),
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
      "--et-row-border": theme.row_border,
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
      "--et-font-size": theme.font_size,
    };
    for (const [k, v] of Object.entries(vars)) {
      for (const element of [this.root, this.dialog]) {
        if (v) element.style.setProperty(k, v);
        else element.style.removeProperty(k);
      }
    }
  }

  destroy() {
    this.destroyed = true;
    this._stopHold();
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
    this.render();
    if (focus) {
      const cell = [...this.scroller.querySelectorAll("td[data-group-key]")]
        .find((cell) => cell.dataset.groupKey === key);
      cell?.querySelector("button.et-chevron")?.focus({ preventScroll: true });
    }
  }

  _hiddenColumns() {
    return hiddenColumns(this.columns, this._state.hidden);
  }
  /** Cluster columns that share a `column_group` at the group's first
   * occurrence, preserving the relative order of ungrouped columns. */
  _orderedColumns(columns) {
    return orderedColumns(columns, this.options);
  }
  // --------------------------------------------------------------- filter ---
  _visibleRows(rows) {
    return visibleRows(rows, (key) => this._isCollapsed(key));
  }
  _searchRows(rows) {
    return searchRows(rows, this.columns, this._state.search, this._hiddenColumns());
  }
  _sortRows(rows) {
    return sortRows(rows, this.columns, this._state.sort);
  }
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
    if (this._expanded) {
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
      search: this._state.search, hidden: this._hiddenColumns(), sort: this._state.sort,
    });
    const { columns, hasGroups, dimCount, ranges, formatRanges, decimals, colorScales, stats } = processed;
    const headerRowCount = columns.some((column) => column.column_group) ? 2 : 1;
    const visibility = this._pipeline.visible(processed, this._groupVersion, (key) => this._isCollapsed(key));
    const { rows, pageCount, page, total } = this._paginate(visibility.rows, visibility.hasGroups);
    this._pageCount = pageCount;

    // Section-style groups merge each group's dimension cell across its rows.
    // Count levels over all rows (not just the page) so a fully collapsed table
    // still knows how many dimensions it has.
    const section = opts.group_type === "section" && hasGroups && dimCount > 0;
    // Accordion groups indent child/parent dimension cells (Evidence parity).
    const accordion = hasGroups && !section && dimCount > 0;
    const rowspans = section
      ? this._computeRowspans(rows, dimCount, opts.subtotal_position !== "bottom")
      : null;

    // Oblique headings need a taller header and a little right padding.
    let obliqueAngle = null;
    let longestLabel = 0;
    for (const col of columns) {
      const rotation = col.rotate_title ?? (opts.stub === col.name ? null : opts.rotate_titles);
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
          hasGroups,
          headerRowCount,
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
        }),
      );
    }
    this._renderFooter(page, pageCount, total);
    this._renderFootnotes(footnotes, opts.footnotes);
    this.caption.replaceChildren();
    if (opts.caption) this.caption.append(inlineMarkdown(opts.caption));
    this._updateBaselineHeight();
    this._viewport.frame(() => this._applyFrozenOffsets());

    this.el.dataset.rowCount = String(total);
    this.el.dataset.renderCount = String((Number(this.el.dataset.renderCount) || 0) + 1);
  }

  // ------------------------------------------------------------- loading ---
  /** Reflect the `loading` trait in the UI.
   *
   * Fast updates finish within `LOADING_SHOW_DELAY`, so they never flash the
   * overlay — the table simply swaps in place (no flicker). Slower updates fade
   * the current data out over `FADE_MS`; once shown, the overlay is held until
   * the fade completes and then removed immediately to reveal the new data.
   */
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
    const table = h("table", { class: "et-table" });
    table.append(this._renderHeader(columns, ctx));
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
      if (ctx.stats) tbody.append(this._renderStatsRow(columns, ctx));
      rows.forEach((row, index) => tbody.append(this._renderRow(row, columns, ctx, index)));
    }
    table.append(tbody);
    return table;
  }

  /** A blank row; its cells keep the column alignment and borders. */
  _renderPlaceholderRow(columns, ctx) {
    const opts = this.options;
    const tr = h("tr", { class: "et-row et-row-placeholder" });
    let first = null;
    if (ctx.rowNumbers) {
      first = h("td", { class: "et-td et-row-num" });
      tr.append(first);
    }
    for (const col of columns) {
      const td = h("td", { class: "et-td", style: withFigure(this._alignStyle(col), col, opts) });
      if (!first) first = td;
      tr.append(td);
    }
    if (opts.link) tr.append(h("td", { class: "et-td et-td-chevron" }));
    // One non-breaking space gives the empty row the normal line height.
    if (first) first.append(document.createTextNode("\u00a0"));
    return tr;
  }

  /** Per-column summary over the full dataset: min/max/avg/null for numeric
   *  columns, distinct/null for everything else. Subtotal/total rows are
   *  ignored. */
  _columnStats(columns, rows) {
    return columnStats(columns, rows);
  }
  /** The row of `[TYPE] min/max/…` (or `distinct`) blocks under the header. */
  _renderStatsRow(columns, ctx) {
    const opts = this.options;
    const row = h("tr", { class: "et-row et-stats-row" });
    if (ctx.rowNumbers) row.append(h("td", { class: "et-td et-row-num" }, ""));
    for (const col of columns) {
      const stat = ctx.stats.get(col.name) || { min: null, max: null, avg: null, nulls: 0, distinct: 0 };
      const block = h("div", { class: "et-stats" });
      block.append(
        h("div", { class: "et-stats-type" }, `[${String(col.type || "string").toUpperCase()}]`),
      );
      if (col.type === "number") {
        const range =
          ctx.formatRanges.get(col.name) ||
          (stat.min != null ? { min: stat.min, max: stat.max } : undefined);
        for (const [label, value] of [["min", stat.min], ["max", stat.max], ["avg", stat.avg]]) {
          block.append(this._statsLine(label, this._formatStat(col, value, range)));
        }
      } else {
        block.append(this._statsLine("distinct", formatValue(stat.distinct, "num0")));
      }
      block.append(this._statsLine("null", formatValue(stat.nulls, "num0")));
      row.append(
        h("td", { class: `et-td et-stats-cell${opts.stub === col.name ? " et-stub" : ""}` }, block),
      );
    }
    return row;
  }

  _statsLine(label, value) {
    return h("div", { class: "et-stats-line" }, [
      h("span", { class: "et-stats-label" }, `${label}: `),
      h("span", { class: "et-stats-value" }, value),
    ]);
  }

  _formatStat(col, value, range) {
    if (value === null || value === undefined) return "–";
    return formatValue(value, col.fmt, { type: "number", range, fallback: optString(value) });
  }

  _renderHeader(columns, ctx) {
    const opts = this.options;
    const thead = h("thead");
    const paths = columns.map((column) => groupPath(column.column_group));
    const depth = paths.reduce((max, path) => Math.max(max, path.length), 0);
    if (depth > 0) {
      const levels = buildHeaderLevels(paths, depth);
      levels.forEach((cells, level) => {
        const groupRow = h("tr", { class: "et-header-groups" });
        if (ctx.rowNumbers && level === 0) {
          groupRow.append(h("th", { class: "et-th et-th-group et-row-num", rowspan: depth }, ""));
        }
        for (const cell of cells) {
          const th = h(
            "th",
            {
              class: `et-th et-th-group${cell.label ? "" : " et-th-group-blank"}`,
              colspan: cell.span,
              "data-group": cell.label,
              title: cell.label || null,
            },
            cell.label,
          );
          // Highlight a spanner only when every column it spans shares the same
          // highlight — a whole-group band, not a single-column one.
          const spanned = columns.slice(cell.start, cell.start + cell.span);
          if (spanned.length && spanned.every((c) => c.highlight && c.highlight === spanned[0].highlight)) {
            th.style.backgroundColor = spanned[0].highlight;
          }
          groupRow.append(th);
        }
        thead.append(groupRow);
      });
    }

    const row = h("tr");
    if (ctx.rowNumbers) {
      row.append(h("th", { class: "et-th et-row-num", "aria-label": "Row number" }, "#"));
    }
    for (const col of columns) {
      const sorted = this._state.sort?.column === col.name;
      const dir = sorted ? this._state.sort.direction : null;
      const isStub = opts.stub === col.name;
      const rotation = col.rotate_title ?? (isStub ? null : opts.rotate_titles);
      let thClass = `et-th${sorted ? " et-th-sorted" : ""}${isStub ? " et-stub-head" : ""}`;
      if (rotation === "vertical") thClass += " et-th-vertical";
      else if (typeof rotation === "number") thClass += " et-th-oblique";
      const infoText = col.info ? String(col.info) : null;
      const th = h("th", {
        class: thClass,
        style: withFigure(this._alignStyle(col), col, opts),
        "aria-sort": sorted ? (dir === "asc" ? "ascending" : "descending") : "none",
        // The description tooltip belongs to the whole header cell.
        title: infoText,
      });
      if (typeof rotation === "number") {
        th.style.setProperty("--et-th-angle", `${rotation}deg`);
      }
      if (col.highlight) th.style.backgroundColor = col.highlight;
      const inner = h("span", { class: "et-th-inner" });
      let title =
        isStub && opts.stub_head
          ? opts.stub_head
          : opts.format_titles === false
            ? col.name
            : col.title || formatTitle(col.name);
      if (opts.all_caps) title = String(title).toUpperCase();
      // A `\n` in the title forces a line break; whether other lines wrap at
      // spaces is up to `wrap_titles` (see CSS).
      const titleEl = h("span", { class: "et-th-title" });
      String(title)
        .split("\n")
        .forEach((line, index) => {
          if (index > 0) titleEl.append(h("br"));
          titleEl.append(document.createTextNode(line));
        });
      inner.append(titleEl);
      if (infoText) {
        inner.append(
          h("span", { class: "et-th-info", role: "img", "aria-label": infoText }, "ⓘ"),
        );
      }
      if (sorted) inner.append(h("span", { class: "et-sort-arrow" }, dir === "asc" ? "▲" : "▼"));
      th.append(inner);
      if (opts.sortable !== false) {
        th.tabIndex = 0;
        th.addEventListener("click", () => this._sortColumn(col.name));
        th.addEventListener("keydown", (event) => {
          if (event.key !== "Enter" && event.key !== " ") return;
          event.preventDefault();
          this._sortColumn(col.name);
          const replacement = [...this.scroller.querySelectorAll("thead tr:last-child th")]
            .find((cell) => cell.dataset.column === col.name);
          replacement?.focus({ preventScroll: true });
        });
        th.dataset.column = col.name;
      }
      row.append(th);
    }
    thead.append(row);
    return thead;
  }

  _alignStyle(col) {
    return alignStyle(col);
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

  /** Rowspan each subtotal's dimension cell should span in section mode. */
  _computeRowspans(rows, dimCount, top) {
    return computeRowspans(rows, dimCount, top);
  }
  /** Indent (in rem) for a dimension cell in accordion mode.
   *
   * Matches Evidence's `getIndentAmount`: detail rows indent their *parent*
   * dimension columns but not the leaf dimension, and subtotal rows indent
   * their ancestor columns. Non-dimension columns are never indented.
   */
  /** Substitute a displayed value per `sub_*` rules (returns text or null). */
  /** Footnote mark for a 1-based index under the chosen scheme. */
  _footnoteMark(index) {
    return footnoteMark(index, this.options);
  }
  /** Merge the style/format rules matching a cell (last match wins). */
  /** Whether the nth data row should be shaded, per `row_shading`.
   * `true` = alternating (1,1); a number = groups (n,n); a pair = [shaded, unshaded]. */
  _shaded(index) {
    return shaded(index, this.options);
  }
  _renderRow(row, columns, ctx, index) {
    const opts = this.options;
    const renderType = row.render_type || "cell_data";
    if (renderType === "row_section") {
      const colSpan = columns.length + (ctx.rowNumbers ? 1 : 0) + (opts.link ? 1 : 0);
      const label = row.__label ?? (columns[0] ? row[columns[0].name] : "");
      return h("tr", { class: "et-row et-row-section" }, [
        h("td", { class: "et-td et-section-cell", colspan: colSpan }, String(label ?? "")),
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
        hasLink ? "et-row-link" : "",
        isSubtotal ? "et-row-collapsible" : "",
        renderType === "cell_data" && this._shaded(ctx.shadingCounter.value++) ? "et-row-shaded" : "",
      ].filter(Boolean).join(" "),
    });
    if (hasLink) tr.addEventListener("click", () => { window.location.href = String(row[opts.link]); });

    bindRowSelection(tr, row, ctx.selected, opts, this.model, (key) =>
      [...this.scroller.querySelectorAll("tr.et-row-selectable")]
        .find((row) => row.dataset.selectKey === String(key)));

    if (ctx.rowNumbers) {
      const numberCell = h(
        "td",
        { class: "et-td et-row-num" },
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
      if (cell) tr.append(cell);
    });

    if (opts.link) {
      const chevTd = h("td", { class: "et-td et-td-chevron" });
      if (hasLink) chevTd.append(h("span", { class: "et-row-chevron" }, "›"));
      tr.append(chevTd);
    }
    return tr;
  }

  /** Apply effects shared by ordinary, null, substituted and template cells. */
  /** Neutral band from `neutral_range`.
   * Accepts a `"lo:hi"` string (e.g. `"-0.1:0.1"`), a `[lo, hi]` pair, a single
   * ±value, or `neutral_min` / `neutral_max`. Defaults to "only exactly 0". */
  /** Normalise a cell value into ``[x, y]`` sparkline points.
   *
   * Accepts an array of numbers, an array of ``[x, y]`` pairs, or an array of
   * objects (e.g. DuckDB ``ARRAY_AGG({'date': date, 'sales': sales})``). For
   * objects, ``sparkline_options.x`` / ``.y`` name the fields; otherwise the
   * first numeric field is used for y and the first non-numeric field for x. */
  /** Render the footer notes collected while building rows, plus any static
   * `footnotes`, with the row numbers each note appears on. */
  _renderFootnotes(footnotes, staticFootnotes) {
    this.footnotesEl.replaceChildren();
    const items = footnotes.map((note) => ({
      mark: this._footnoteMark(note.index),
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

  _renderFooter(page, pageCount, total) {
    this.footer.replaceChildren();
    // With a single page there is no pager row to hold the actions, so they
    // float at the bottom-right and the footnotes/caption sit right under the
    // table (see `.et-no-pager` in the stylesheet).
    this.root.classList.toggle("et-no-pager", pageCount <= 1);
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
          this._startHold(direction);
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

  // Press-and-hold pagination: after HOLD_DELAY, advance one page every
  // HOLD_START_INTERVAL ms, easing linearly to HOLD_END_INTERVAL ms.
  _startHold(direction) {
    return this._holdController.start(direction);
  }

  _stopHold() {
    return this._holdController.stop();
  }

  _advance(direction) {
    const next = this._state.page + (direction === "next" ? 1 : -1);
    if (next < 0 || next >= this._pageCount) return false;
    this._gotoPage(next);
    return true;
  }

  // ----------------------------------------------------------- fullscreen ---
  _toggleExpanded() {
    return this._viewport.toggle();
  }

  _closeExpanded() {
    return this._viewport.close();
  }

  _restoreInline() {
    return this._viewport.restore();
  }

  _resetBaselineHeight() {
    this._baselineHeight = 0;
    this._baselinePageSize = null;
    this.scroller.style.minHeight = "";
  }

  // Size the fullscreen page so the rows fill the available viewport height.
  _fitFullscreen() {
    return this._viewport.fit();
  }

  // --------------------------------------------------------- frozen cols ---
  _applyFrozenOffsets() {
    return this._viewport.applyFrozenOffsets();
  }

  // ------------------------------------------------------------- download ---
  _downloadCsv() {
    const hidden = this._hiddenColumns();
    const columns = this._orderedColumns(this.columns.filter((c) => !hidden.has(c.name)));
    const rows = this._visibleRows(this._sortRows(this._searchRows(this.rows)));
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

/** Minimal inline markdown: **bold**, *italic* and `code` (no raw HTML). */

/** Map a figure style to a `font-variant-numeric` value (ALA). */

/** Stable Map/Set key for a group, which may be a string or a path array. */

/** Force a base format (num/usd/pct/…) to a fixed number of decimals. */

/** Build one row of header cells per group level, nesting sub-groups. */

/** Compress a sorted list of row numbers into ranges, e.g. [1,2,3,5] -> "1–3, 5". */

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
  model.on("change:loading", setLoading);
  model.on("change:selected", rerender);
  return () => {
    model.off("change:rows", dataChanged);
    model.off("change:columns", dataChanged);
    model.off("change:options", dataChanged);
    model.off("change:selected", rerender);
    model.off("change:loading", setLoading);
    renderer.destroy();
  };
}

export default { render };
