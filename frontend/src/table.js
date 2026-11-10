// Evidence-style data table renderer for the anywidget frontend.
//
// The widget receives fully JSON-serializable `rows`, `columns`, and `options`
// from Python and renders a sortable, searchable, formattable table with
// conditional visualizations, collapsible groups, frozen columns, pagination,
// CSV export, and a fullscreen dialog.
import { footnoteMark } from "./footnotes.js";
import { fitMarkLabels } from "./mark-labels.js";
import { projectLayout, projectLegacy } from "./row-layout.js";
import { renderStatsRow } from "./statistics.js";
import { renderHeader, orderedColumns } from "./headers.js";
import { renderLegends } from "./legends.js";
import { RowPipeline } from "./derived.js";
import { HoldController } from "./interactions.js";
import { LoadingController } from "./loading.js";
import { TableViewport } from "./viewport.js";
import { ExpandedPages } from "./expanded-pages.js";
import { renderTable } from "./table-body.js";
import { buildRenderPlan } from "./render-plan.js";
import { navigationUrl } from "./urls.js";
import { serializeCsv } from "./csv.js";
import { h, inlineMarkdown, formatRowRanges, isStub } from "./dom.js";
import { hiddenColumns, visibleRows, searchRows, sortRows, paginateRows,
 } from "./rows.js";
import { TooltipController, inspectHeader } from "./tooltips.js";
import { combinePoints } from "./point-clusters.js";
import { formatTitle } from "./format.js";

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
import { resolveColor } from "./color.js";

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
      sectionCollapsed: new Set(),
      expanded: new Set(),
      hidden: new Set(),
      statsMembers: new Map(),
    };
    this._pipeline = new RowPipeline();
    this._groupVersion = 0;
    this._pageCount = 1;
    this._pageSizeOverride = null;
    this._expandedPages = new ExpandedPages();
    this._expandedProjection = null;
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
      title: "Close expanded table (Esc)", "aria-label": "Close expanded table",
      onclick: () => this._viewport.close(),
    });
    this.closeBtn.textContent = "✕";
    this.root.append(this.closeBtn);
    this._tooltips = new TooltipController(this.root);
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
      getPageMetrics: () => this._pageMetrics,
      onExpand: () => {
        this._inlinePage = this._state.page;
        this._state.page = 0;
        this._pageSizeOverride = 10;
        this._expandedPages.reset();
        this._expandedProjection = null;
      },
      onRestore: () => { this._state.page = this._inlinePage ?? 0; },
      advancePage: direction => this._advance(direction),
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
    this._tooltips.destroy();
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
  _toggleSection(key) {
    const collapsed = this._state.sectionCollapsed;
    if (collapsed.has(key)) collapsed.delete(key);
    else collapsed.add(key);
    this._sectionAnchor = key;
    this._groupVersion++;
    this._resetBaselineHeight();
    this.render();
    const toggles = [...this.scroller.querySelectorAll("button[data-section-key]")];
    (toggles.find(button => button.dataset.sectionKey === key) || toggles[0])?.focus({preventScroll: true});
  }

  _effectivePageSize() {
    return this._pageSizeOverride ?? this.options.page_size;
  }

  _paginate(rows, hasGroups) {
    if (this._viewport.expanded) {
      const page = this._expandedPages.project(rows.length, this._effectivePageSize(), this._state.page);
      return {...page, rows: rows.slice(page.start, page.end)};
    }
    const page = paginateRows(rows, this._effectivePageSize(), this._state.page, this.options, hasGroups);
    this._state.page = page.page;
    return page;
  }
  // --------------------------------------------------------------- render ---
  render() {
    this._tooltips.hide();
    const opts = this.options;
    this._applyTheme();
    this.root.style.maxWidth =
      this._viewport.expanded || opts.width == null
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
    this._renderToolbar();

    const processed = this._pipeline.get({
      rows: this.rows, columns: this.columns, options: opts,
      rowLayout: this.model.get("row_layout"),
      search: this._state.search, hidden: hiddenColumns(this.columns, this._state.hidden), sort: this._state.sort,
    });
    const { columns } = processed;
    this._renderTitle(columns);
    const visibility = this._pipeline.visible(processed, this._groupVersion, (key) => this._isCollapsed(key));
    if (this._viewport.expanded && (this._expandedProjection !== processed || this._expandedGroupVersion !== this._groupVersion)) {
      this._expandedPages.reset();
      this._state.page = 0;
      this._expandedProjection = processed;
      this._expandedGroupVersion = this._groupVersion;
    }
    const plan = buildRenderPlan(processed, visibility, {
      options: opts, pageSize: this._effectivePageSize(), pageIndex: this._state.page,
      expandedPage: this._viewport.expanded ? total => this._expandedPages.project(total, this._effectivePageSize(), this._state.page) : null,
      isCollapsed: key => this._state.sectionCollapsed.has(key), revision: this._groupVersion, anchorGroup: this._sectionAnchor,
      selected: opts.select ? this.model.get("selected") : null, emptyRows: this._emptyRowCount(opts),
      paginate: (rows, hasGroups) => this._paginate(rows, hasGroups), toggleSection: key => this._toggleSection(key),
    });
    this._sectionAnchor = null;
    const {rows, pageCount, page, total, start} = plan.pagination;
    this._pageMetrics = {count: plan.context.displayEntries ? plan.pagination.unitCount : rows.length,
      remaining: total - start, projection: processed};
    this._state.page = page;
    this._pageCount = pageCount;

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
    const {footnotes, isEmpty} = plan.context;
    if (isEmpty && !columns.length) {
      this.scroller.append(h("div", {class: "et-empty"}, [h("span", {}, opts.empty_message || "No records")]));
    } else {
      this.scroller.append(renderTable(columns, rows, plan.context, {
        header: this._renderHeader(columns, plan.context),
        statistics: !isEmpty && plan.context.stats ? this._renderStatsRow(columns, plan.context) : null,
        model: this.model, isCollapsed: key => this._isCollapsed(key),
        toggleGroup: (key, focus) => this._toggleGroup(key, focus),
        findSelectedRow: key => [...this.scroller.querySelectorAll("tr.et-row-selectable")]
          .find(row => row.dataset.selectKey === String(key)),
      }));
    }
    const hasBelow = Boolean(opts.caption) || footnotes.length > 0 || (opts.footnotes || []).length > 0;
    this._renderFooter(page, pageCount, total, hasBelow, plan.pagination);
    this._renderFootnotes(footnotes, opts.footnotes);
    this.caption.replaceChildren();
    if (opts.caption) this.caption.append(inlineMarkdown(opts.caption));
    this._updateBaselineHeight();
    this._viewport.observeTable(this.scroller.querySelector("table"));
    this._tooltips.refresh();
    this._viewport.frame(() => {
      this._viewport.applyFrozenOffsets();
      fitMarkLabels(this.root);
      combinePoints(this.root);
      if (this._viewport.expanded) this._viewport.fit();
    });

    this.el.dataset.rowCount = String(plan.pagination.matchingTotal ?? total);
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
    if (this._viewport.expanded) {
      this._resetBaselineHeight();
      return;
    }
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

  _renderTitle(columns) {
    const { title, subtitle, info, info_link, info_link_title } = this.options;
    this.titlebar.replaceChildren();
    const text = h("div", { class: "et-title-text" });
    if (title) {
      const t = h("span", { class: "et-title" });
      t.append(inlineMarkdown(title));
      if (info) {
        const infoSpan = h("span", { class: "et-info", title: info }, "ⓘ");
        const infoUrl = navigationUrl(info_link);
        if (infoUrl) {
          const a = h("a", { href: infoUrl, target: "_blank", rel: "noopener noreferrer", class: "et-info-link" }, "ⓘ");
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
    if (text.childElementCount) this.titlebar.append(text);
    const legends = renderLegends(columns, this.columns, this.options);
    if (legends) this.titlebar.append(legends);
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
    if (this._viewport.expanded) return Math.min(200, Number(this._effectivePageSize()) || 10);
    const configured = Number(opts.empty_rows);
    if (Number.isFinite(configured) && configured > 0) return Math.min(Math.floor(configured), 200);
    const pageSize = Number(this._effectivePageSize());
    if (Number.isFinite(pageSize) && pageSize > 0) return Math.min(Math.floor(pageSize), 200);
    return 10;
  }

  _renderStatsRow(columns, ctx) {
    return renderStatsRow({columns, layout: ctx.layout, stats: ctx.stats,
      formatRanges: ctx.formatRanges, options: this.options, rowNumbers: ctx.rowNumbers,
      selections: this._state.statsMembers,
      onLayout: () => this._viewport.frame(() => {
        this._viewport.applyFrozenOffsets();
        if (this._viewport.expanded) this._viewport.fit();
      })});
  }

  _renderHeader(columns, ctx) {
    return renderHeader({columns, rowNumbers: ctx.rowNumbers, options: this.options,
      onInfo: (header, col) => inspectHeader(header, col, this.options),
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

  _renderFooter(page, pageCount, total, hasBelow, pagination = {}) {
    this.footer.replaceChildren();
    // With a single page there is no pager row to hold the actions. If
    // something sits below the table (footnotes or a caption) the actions float
    // at the bottom-right so that content keeps its place; with nothing below,
    // the footer stays in flow so the actions do not land on the last row.
    this.root.classList.toggle("et-float-actions", pageCount <= 1 && !pagination.collapsedGroups && !!hasBelow);
    if (pageCount > 1 || (pagination.variable && page > 0) || pagination.collapsedGroups) {
      const left = h("div", { class: "et-page-controls" });
      const pageSize = this._effectivePageSize();
      const start = pagination.start == null ? page * pageSize + 1 : pagination.start + 1;
      const end = pagination.end == null ? Math.min(total, (page + 1) * pageSize) : pagination.end;

      const pageButton = (label, direction, disabled) => {
        const button = h(
          "button",
          {
            class: "et-btn et-page-btn",
            type: "button",
            disabled,
            "aria-label": direction === "next" ? "Next page" : "Previous page",
            title: this._viewport.expanded
              ? direction === "next" ? "Next page (→)" : "Previous page (←)" : null,
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

      // Current page and exact record range. A final page count is available
      // only for fixed-size inline pages. Arrows keep their button hitboxes.
      left.append(
        pageButton("‹", "prev", page === 0),
        h("span", { class: "et-page-current" }, pagination.variable ? String(page + 1) : `${page + 1}/${pageCount}`),
        pageButton("›", "next", page >= pageCount - 1),
        h("span", { class: "et-page-info" }, pagination.collapsedGroups
          ? `(${start}–${end} of ${total} items · ${pagination.matchingTotal} matching records)`
          : `(${start}–${end} of ${total})`),
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
    if (this._viewport.expanded) {
      this._viewport.fit();
      const next = this._expandedPages.move(page);
      if (!next) return;
      this._pageSizeOverride = next.size;
      this._state.page = next.page;
      this.scroller.scrollTop = 0;
      this.render();
      this._viewport.fit();
      return;
    }
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
    const blob = new Blob([serializeCsv(columns, rows)], { type: "text/csv;charset=utf-8;" });
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
