// Evidence-style data table renderer for the anywidget frontend.
//
// The widget receives fully JSON-serializable `rows`, `columns`, and `options`
// from Python and renders a sortable, searchable, formattable table with
// conditional visualizations, collapsible groups, frozen columns, pagination,
// CSV export, and a fullscreen dialog.
import { formatValue, formatTitle, BASE_AUTO_FORMATS } from "./format.js";
import {
  calculateVizRanges,
  calculateFormatRanges,
  buildColorVizScale,
  calculateColorStyles,
  colorStylesFromHex,
} from "./color.js";

const ROW_HEIGHT = 28;
const MODAL_OVERHEAD = 150;

// Loading transition timing (ms).
const LOADING_SHOW_DELAY = 180; // don't show the overlay for updates faster than this
const FADE_MS = 600; // fade current data out and "Processing…" in over this long
const LOADING_HIDE_DEBOUNCE = 120; // settle time before revealing new data

// Pagination press-and-hold repeat schedule.
const HOLD_DELAY = 700; // wait before auto-repeat starts
const HOLD_START_INTERVAL = 700; // slowest repeat interval (ms)
const HOLD_END_INTERVAL = 100; // fastest repeat interval (ms)
const HOLD_RAMP = 2300; // time spent easing from slow to fast (reaches 100ms at 3s total)

/** Repeat interval (ms) after the pointer has been held for `elapsedMs`. */
export function holdInterval(elapsedMs) {
  const t = Math.min(Math.max(elapsedMs - HOLD_DELAY, 0), HOLD_RAMP);
  return HOLD_START_INTERVAL + (HOLD_END_INTERVAL - HOLD_START_INTERVAL) * (t / HOLD_RAMP);
}

function h(tag, attrs = {}, children = []) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "dataset") Object.assign(el.dataset, v);
    else if (k === "style" && typeof v === "object") Object.assign(el.style, v);
    else if (k.startsWith("on") && typeof v === "function") el.addEventListener(k.slice(2), v);
    else if (k === "html") el.innerHTML = v;
    else el.setAttribute(k, v);
  }
  const kids = Array.isArray(children) ? children : [children];
  for (const child of kids) {
    if (child === null || child === undefined || child === false) continue;
    el.append(child instanceof Node ? child : document.createTextNode(String(child)));
  }
  return el;
}

function _isNumeric(value) {
  if (typeof value === "number") return Number.isFinite(value);
  if (typeof value === "string") return value.trim() !== "" && !isNaN(Number(value));
  return false;
}

function compareValues(a, b, type) {
  if (a === null || a === undefined) return b === null || b === undefined ? 0 : 1;
  if (b === null || b === undefined) return -1;
  if (type === "number") {
    const na = Number(a);
    const nb = Number(b);
    if (!isNaN(na) && !isNaN(nb)) return na - nb;
  }
  if (a instanceof Date || b instanceof Date) return new Date(a) - new Date(b);
  if (typeof a === "string" && typeof b === "string") {
    return a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" });
  }
  if (a < b) return -1;
  if (a > b) return 1;
  return 0;
}

export class EvidenceTableRenderer {
  constructor(model, el) {
    this.model = model;
    this.el = el;
    this._state = {
      sort: null,
      search: "",
      page: 0,
      collapsed: new Set(),
      expanded: new Set(),
      hidden: new Set(),
    };
    this._columnWidths = [];
    this._pageCount = 1;
    this._pageSizeOverride = null;
    this._fitting = false;
    this._hold = null;
    this._holdFired = false;
    this._onPointerUp = () => this._stopHold();
    this._build();
  }

  get rows() { return this.model.get("rows") || []; }
  get columns() { return this.model.get("columns") || []; }
  get options() { return this.model.get("options") || {}; }

  _build() {
    const opts = this.options;
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
    this.root.append(this.titlebar, this.toolbar, this.body, this.footer);
    this._loading = !!this.model.get("loading");
    const defaultSort = this.options.default_sort;
    if (defaultSort && defaultSort.column) {
      this._state.sort = {
        column: defaultSort.column,
        direction: defaultSort.direction === "asc" ? "asc" : "desc",
      };
    }
    this._loadingShown = false;
    this._showTimer = null;
    this._hideTimer = null;
    this._loadingSince = 0;
    this._baselineHeight = 0;
    this._baselinePageSize = null;

    // Fullscreen dialog (same pattern as galaga's cga3d widget).
    this.dialog = h("dialog", { class: "et-dialog", "aria-label": "Expanded data table" });
    this.expandBtn = h("button", {
      class: "et-icon-btn", type: "button", title: "Expand table",
      "aria-label": "Expand table", "aria-expanded": "false",
      onclick: () => this._toggleExpanded(),
    });
    this.expandBtn.textContent = "⛶";
    // The comment marks where the widget lives inline so it can be moved back
    // after the fullscreen dialog closes. It must be attached to the DOM
    // before it can anchor anything.
    this.placeholder = document.createComment("evidence-table inline position");
    this.el.append(this.placeholder, this.root, this.dialog);

    this.dialog.addEventListener("close", () => this._restoreInline());
    this.dialog.addEventListener("cancel", (e) => { e.preventDefault(); this._closeExpanded(); });
    // Clicking the backdrop (the dialog element itself, outside the content)
    // dismisses. Track where the press started so a drag that begins inside
    // the content and ends on the backdrop does not close it.
    this._backdropPress = false;
    this.dialog.addEventListener("pointerdown", (e) => {
      this._backdropPress = e.target === this.dialog;
    });
    this.dialog.addEventListener("click", (e) => {
      const onBackdrop = e.target === this.dialog && this._backdropPress;
      this._backdropPress = false;
      if (onBackdrop) this._closeExpanded();
    });
    this._expanded = false;

    this._applyTheme();
    this.render();

    this._resizeObserver = new ResizeObserver(() => {
      this._applyFrozenOffsets();
      if (this._expanded) this._fitFullscreen();
    });
    this._resizeObserver.observe(this.scroller);
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
      if (!v) continue;
      this.root.style.setProperty(k, v);
      // The dialog is a sibling of the root, so it needs the surface tokens too.
      this.dialog.style.setProperty(k, v);
    }
  }

  destroy() {
    this._stopHold();
    if (this._showTimer) clearTimeout(this._showTimer);
    if (this._hideTimer) clearTimeout(this._hideTimer);
    this._resizeObserver?.disconnect();
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

  _toggleGroup(key) {
    const set = this._defaultCollapsed() ? this._state.expanded : this._state.collapsed;
    if (set.has(key)) set.delete(key);
    else set.add(key);
    this.render();
  }

  _hiddenColumns() {
    const set = new Set(this._state.hidden);
    for (const col of this.columns) if (col.hide) set.add(col.name);
    return set;
  }

  /** Cluster columns that share a `column_group` at the group's first
   * occurrence, preserving the relative order of ungrouped columns. */
  _orderedColumns(columns) {
    if (this.options.order_columns_by_group === false) return columns;
    const grouped = new Map();
    for (const col of columns) {
      if (!col.column_group) continue;
      if (!grouped.has(col.column_group)) grouped.set(col.column_group, []);
      grouped.get(col.column_group).push(col);
    }
    if (!grouped.size) return columns;
    const emitted = new Set();
    const ordered = [];
    for (const col of columns) {
      const group = col.column_group;
      if (!group) {
        ordered.push(col);
        continue;
      }
      if (emitted.has(group)) continue;
      emitted.add(group);
      ordered.push(...grouped.get(group));
    }
    return ordered;
  }

  // --------------------------------------------------------------- filter ---
  _visibleRows(rows) {
    const hasGroups = rows.some((r) => r.render_type && r.render_type !== "cell_data");
    if (!hasGroups) return rows;
    const collapsed = new Set();
    for (const row of rows) {
      const key = row.__group_key;
      if ((row.render_type === "row_subtotal" || row.render_type === "row_total") && key && this._isCollapsed(key)) {
        collapsed.add(key);
      }
    }
    return rows.filter((row) => {
      const ancestors = row.__ancestors || [];
      return !ancestors.some((k) => collapsed.has(k));
    });
  }

  _searchRows(rows) {
    const term = this._state.search.trim().toLowerCase();
    if (!term) return rows;
    const hidden = this._hiddenColumns();
    const cols = this.columns.filter((c) => !hidden.has(c.name));
    const matches = (row) => cols.some((c) => {
      const v = row[c.name];
      return v !== null && v !== undefined && String(v).toLowerCase().includes(term);
    });
    const keepGroups = new Set();
    for (const row of rows) {
      if (row.render_type && row.render_type !== "cell_data") {
        if (row.render_type === "row_total") keepGroups.add(row.__group_key);
        continue;
      }
      if (matches(row)) for (const key of row.__ancestors || []) keepGroups.add(key);
    }
    return rows.filter((row) => {
      if (row.render_type === "row_total") return true;
      if (row.render_type === "row_subtotal") return keepGroups.has(row.__group_key);
      return matches(row);
    });
  }

  _sortRows(rows) {
    const sort = this._state.sort;
    if (!sort) return rows;
    const col = this.columns.find((c) => c.name === sort.column);
    const type = col?.type;
    const dir = sort.direction === "asc" ? 1 : -1;

    const hasGroups = rows.some((r) => r.render_type && r.render_type !== "cell_data");
    const cmp = (a, b) => dir * compareValues(a[sort.column], b[sort.column], type);

    if (!hasGroups) return [...rows].sort(cmp);

    // Grouped: sort only detail rows inside each parent group, preserving the
    // position of subtotal/total rows.
    const queues = new Map();
    for (const row of rows) {
      if (row.render_type && row.render_type !== "cell_data") continue;
      const key = row.__parent_key ?? "__root__";
      if (!queues.has(key)) queues.set(key, []);
      queues.get(key).push(row);
    }
    for (const queue of queues.values()) queue.sort(cmp);
    const out = [];
    for (const row of rows) {
      if (row.render_type && row.render_type !== "cell_data") {
        out.push(row);
      } else {
        const key = row.__parent_key ?? "__root__";
        out.push(queues.get(key).shift());
      }
    }
    return out;
  }

  _effectivePageSize() {
    return this._pageSizeOverride ?? this.options.page_size;
  }

  _paginate(rows) {
    const opts = this.options;
    const pageSize = this._effectivePageSize();
    const hasGroups = rows.some((r) => r.render_type && r.render_type !== "cell_data");
    if (!pageSize || pageSize === "all" || pageSize <= 0 || hasGroups || opts.collapsible) {
      return { rows, pageCount: 1, page: 0, total: rows.length };
    }
    const total = rows.length;
    const pageCount = Math.max(1, Math.ceil(total / pageSize));
    const page = Math.min(Math.max(0, this._state.page), pageCount - 1);
    this._state.page = page;
    return { rows: rows.slice(page * pageSize, (page + 1) * pageSize), pageCount, page, total };
  }

  // --------------------------------------------------------------- render ---
  render() {
    const opts = this.options;
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
    this.root.classList.toggle("et-row-shading", !!opts.row_shading);
    this.root.classList.toggle("et-compact", !!opts.compact);
    this._renderTitle();
    this._renderToolbar();

    const hidden = this._hiddenColumns();
    const columns = this._orderedColumns(this.columns.filter((c) => !hidden.has(c.name)));
    const allRows = this.rows;
    const hasGroups = allRows.some((r) => r.render_type && r.render_type !== "cell_data");
    const headerRowCount = columns.some((c) => c.column_group) ? 2 : 1;

    const searched = this._searchRows(allRows);
    const sorted = this._sortRows(searched);
    const visible = this._visibleRows(sorted);
    const { rows, pageCount, page, total } = this._paginate(visible);
    this._pageCount = pageCount;

    // Section-style groups merge each group's dimension cell across its rows.
    const dimCount = rows.reduce((max, row) => Math.max(max, row.__level ?? 0), 0);
    const section = opts.group_type === "section" && hasGroups && dimCount > 0;
    const rowspans = section
      ? this._computeRowspans(rows, dimCount, opts.subtotal_position !== "bottom")
      : null;

    const ranges = calculateVizRanges(columns, sorted);
    const formatRanges = calculateFormatRanges(columns, sorted);
    const colorScales = new Map();
    for (const col of columns) {
      if (col.viz === "color" && ranges.has(col.name)) {
        colorScales.set(col.name, buildColorVizScale(col, ranges.get(col.name), opts.color_scale));
      }
    }

    this.scroller.replaceChildren();
    if (!rows.length) {
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
          dimCount,
          rowspans,
        }),
      );
    }
    this._renderFooter(page, pageCount, total);
    this._updateBaselineHeight();
    requestAnimationFrame(() => this._applyFrozenOffsets());

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
    this._loading = !!loading;
    this.el.dataset.loading = String(this._loading);
    if (this._loading) {
      if (this._hideTimer) {
        clearTimeout(this._hideTimer);
        this._hideTimer = null;
      }
      if (this._loadingShown || this._showTimer) return;
      this._showTimer = setTimeout(() => {
        this._showTimer = null;
        this._loadingShown = true;
        this._loadingSince = performance.now();
        this._applyLoadingClass();
      }, LOADING_SHOW_DELAY);
    } else {
      if (this._showTimer) {
        // Finished before the overlay was shown: never flash it.
        clearTimeout(this._showTimer);
        this._showTimer = null;
        return;
      }
      if (!this._loadingShown) return;
      const elapsed = performance.now() - this._loadingSince;
      const wait = Math.max(LOADING_HIDE_DEBOUNCE, FADE_MS - elapsed);
      if (this._hideTimer) clearTimeout(this._hideTimer);
      this._hideTimer = setTimeout(() => {
        this._hideTimer = null;
        this._loadingShown = false;
        this._applyLoadingClass();
      }, wait);
    }
  }

  _applyLoadingClass() {
    this.root.classList.toggle("et-loading", this._loadingShown);
    this.loadingOverlay.setAttribute("aria-hidden", String(!this._loadingShown));
    this.el.dataset.loading = String(this._loading);
    this.el.dataset.loadingShown = String(this._loadingShown);
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
      const t = h("span", { class: "et-title" }, title);
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
    if (subtitle) text.append(h("div", { class: "et-subtitle" }, subtitle));
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
    if (opts.download) {
      right.append(h("button", { class: "et-btn", type: "button", title: "Download CSV", onclick: () => this._downloadCsv() }, "Download"));
    }
    right.append(this.expandBtn);
    this.toolbar.append(left, right);
    this.toolbar.classList.toggle("et-toolbar-empty", !left.childElementCount && right.childElementCount <= 1);
  }

  _renderTable(columns, rows, ctx) {
    const opts = this.options;
    const table = h("table", { class: "et-table" });
    table.append(this._renderHeader(columns, ctx));
    const tbody = h("tbody");
    rows.forEach((row, index) => tbody.append(this._renderRow(row, columns, ctx, index)));
    table.append(tbody);
    return table;
  }

  _renderHeader(columns, ctx) {
    const opts = this.options;
    const thead = h("thead");
    const groups = columns.some((c) => c.column_group);
    if (groups) {
      const groupRow = h("tr", { class: "et-header-groups" });
      if (ctx.rowNumbers) {
        groupRow.append(h("th", { class: "et-th et-th-group et-row-num" }, ""));
      }
      let i = 0;
      while (i < columns.length) {
        const group = columns[i].column_group;
        if (group) {
          let span = 1;
          while (i + span < columns.length && columns[i + span].column_group === group) span++;
          groupRow.append(
            h(
              "th",
              { class: "et-th et-th-group", colspan: span, "data-group": group, title: group },
              group,
            ),
          );
          i += span;
        } else {
          // Count consecutive ungrouped columns and emit a blank spanning header.
          let span = 1;
          while (i + span < columns.length && !columns[i + span].column_group) span++;
          groupRow.append(h("th", { class: "et-th et-th-group et-th-group-blank", colspan: span }, ""));
          i += span;
        }
      }
      thead.append(groupRow);
    }

    const row = h("tr");
    if (ctx.rowNumbers) {
      row.append(h("th", { class: "et-th et-row-num", "aria-label": "Row number" }, "#"));
    }
    for (const col of columns) {
      const sorted = this._state.sort?.column === col.name;
      const dir = sorted ? this._state.sort.direction : null;
      const th = h("th", {
        class: `et-th${sorted ? " et-th-sorted" : ""}`,
        style: this._alignStyle(col),
        "aria-sort": sorted ? (dir === "asc" ? "ascending" : "descending") : "none",
      });
      const inner = h("span", { class: "et-th-inner" });
      const title = opts.format_titles === false ? col.name : (col.title || formatTitle(col.name));
      inner.append(h("span", { class: "et-th-title" }, title));
      if (col.info) {
        inner.append(
          h("span", { class: "et-th-info", title: String(col.info), role: "img", "aria-label": String(col.info) }, "ⓘ"),
        );
      }
      if (col.viz && col.viz !== "sparkline") inner.append(h("span", { class: "et-viz-badge", title: `${col.viz} visualization` }, ""));
      if (sorted) inner.append(h("span", { class: "et-sort-arrow" }, dir === "asc" ? "▲" : "▼"));
      th.append(inner);
      if (opts.sortable !== false) {
        th.addEventListener("click", () => this._sortColumn(col.name));
      }
      row.append(th);
    }
    thead.append(row);
    return thead;
  }

  _alignStyle(col) {
    const align = col.align || (col.type === "number" ? "right" : "left");
    return { textAlign: align };
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
    const spans = new Array(rows.length).fill(1);
    rows.forEach((row, index) => {
      if (row.render_type !== "row_subtotal") return;
      const level = row.__level ?? dimCount;
      let count = 1;
      if (top) {
        for (let j = index + 1; j < rows.length && (rows[j].__level ?? dimCount) > level; j++) count++;
      } else {
        for (let j = index - 1; j >= 0 && (rows[j].__level ?? dimCount) > level; j--) count++;
      }
      spans[index] = count;
    });
    return spans;
  }

  _renderRow(row, columns, ctx, index) {
    const opts = this.options;
    const renderType = row.render_type || "cell_data";
    const isTotal = renderType === "row_total";
    const isSubtotal = renderType === "row_subtotal";
    const isCollapsed = isSubtotal && row.__group_key && this._isCollapsed(row.__group_key);
    const hasLink = opts.link && row[opts.link];
    const hidden = row.__hide_cell || {};
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
        renderType === "cell_data" && index % 2 === 1 ? "et-row-shaded" : "",
      ].filter(Boolean).join(" "),
    });
    if (hasLink) tr.addEventListener("click", () => { window.location.href = String(row[opts.link]); });

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
    columns.forEach((col, index) => {
      const td = h("td", { class: "et-td", style: this._alignStyle(col) });
      if (ctx.section && index < ctx.dimCount) {
        const dimIndex = (row.__level ?? ctx.dimCount) - 1;
        const renders =
          isTotal ? index === 0 : isSubtotal ? index === dimIndex : index === ctx.dimCount - 1;
        if (!renders) return;
        if (isSubtotal) td.rowSpan = ctx.rowspans?.[rowIndex] ?? 1;
      }
      if (rowColorStyles) {
        td.style.backgroundColor = rowColorStyles.backgroundColor;
        td.style.color = rowColorStyles.color;
      }
      if (col.viz_include_subtotals === false && isSubtotal && col.viz) td.classList.add("et-no-viz");

      // Collapsible chevron in the subtotal's own dimension column.
      const dimIndex = (row.__level ?? 0) - 1;
      if (isSubtotal && index === dimIndex && !ctx.section) {
        const chev = h("span", { class: `et-chevron${isCollapsed ? "" : " et-chevron-open"}` }, "▶");
        td.append(chev);
        td.dataset.groupKey = row.__group_key;
        td.addEventListener("click", (e) => {
          e.stopPropagation();
          this._toggleGroup(row.__group_key);
        });
      }

      if (hidden[col.name]) {
        tr.append(td);
        return;
      }

      const value = row[col.name];
      if (value === null || value === undefined) {
        td.append(h("span", { class: "et-null" }, "–"));
        tr.append(td);
        return;
      }

      const baseFormat =
        col.fmt_column && row[col.fmt_column] != null ? String(row[col.fmt_column]) : col.fmt;
      const formatCode =
        isTotal && col.total_fmt
          ? col.total_fmt
          : isSubtotal && col.subtotal_fmt
            ? col.subtotal_fmt
            : baseFormat;
      const formatted = formatValue(value, formatCode, {
        type: col.type,
        range: ctx.formatRanges.get(col.name),
        fallback: optString(value),
      });

      // Conditional color background.
      let vizStyles = null;
      if (col.viz === "color" && !(isTotal) && !(isSubtotal && col.viz_include_subtotals === false)) {
        const range = ctx.ranges.get(col.name);
        if (range) vizStyles = calculateColorStyles(col, row, range, ctx.colorScales.get(col.name));
      }

      let content;
      if (col.viz === "bar" && !(isSubtotal && col.viz_include_subtotals === false) && row.render_type !== "row_total") {
        content = this._renderBar(col, value, formatted, ctx.ranges.get(col.name));
      } else if (col.viz === "delta") {
        content = this._renderDelta(col, value);
      } else if (col.viz === "sparkline") {
        content = this._renderSparkline(col, value);
      } else if (col.html) {
        content = h("span", { html: String(value) });
      } else if (col.logo && row[col.logo]) {
        const domain = String(row[col.logo]);
        const logoOptions = col.logo_options || {};
        content = h("span", { class: "et-cell-media" }, [
          h("img", {
            class: "et-cell-logo",
            src: `https://img.logo.dev/${encodeURIComponent(domain)}`,
            alt: domain,
            loading: "lazy",
            style: logoOptions.height ? { height: `${logoOptions.height}px` } : {},
          }),
          h("span", { class: "et-cell-media-label" }, formatted),
        ]);
      } else if (col.image && row[col.image]) {
        const imageOptions = col.image_options || {};
        content = h("span", { class: "et-cell-media" }, [
          h("img", {
            class: "et-cell-image",
            src: String(row[col.image]),
            alt: String(imageOptions.alt || ""),
            style: {
              ...(imageOptions.height ? { height: `${imageOptions.height}px` } : {}),
              ...(imageOptions.width ? { width: `${imageOptions.width}px` } : {}),
            },
          }),
          h("span", { class: "et-cell-media-label" }, formatted),
        ]);
      } else {
        content = h("span", { class: "et-cell-value" }, formatted);
      }

      if (col.red_negatives && !isNaN(Number(value)) && Number(value) < 0) {
        content.classList?.add("et-negative");
      }

      const link = col.link ? row[col.link] : null;
      if (link && row.render_type !== "row_total") {
        td.append(h("a", {
          class: "et-cell-link", href: String(link),
          target: col.link_new_tab ? "_blank" : null,
          rel: col.link_new_tab ? "noopener noreferrer" : null,
        }, col.link_label ? col.link_label : content));
      } else {
        td.append(content);
      }

      if (vizStyles) {
        td.style.backgroundColor = vizStyles.backgroundColor;
        td.style.color = vizStyles.color;
        td.classList.add("et-color-cell");
      }
      tr.append(td);
    });

    if (opts.link) {
      const chevTd = h("td", { class: "et-td et-td-chevron" });
      if (hasLink) chevTd.append(h("span", { class: "et-row-chevron" }, "›"));
      tr.append(chevTd);
    }
    return tr;
  }

  _renderBar(col, value, formatted, range) {
    const opts = col.bar_options || {};
    const num = Number(value);
    const min = opts.fit_to_data ? (range?.min ?? 0) : Math.min(0, range?.min ?? 0);
    const max = opts.fit_to_data ? (range?.max ?? 0) : Math.max(0, range?.max ?? 0);
    const span = max - min || 1;
    const pct = Math.max(0, Math.min(100, ((num - min) / span) * 100));
    const negative = num < 0;
    const color = negative
      ? (opts.bar_color_negative || opts.bar_color || "var(--et-negative, #dc2626)")
      : (opts.bar_color || "var(--et-accent, #2563eb)");
    const bar = h("div", { class: "et-bar", style: { width: `${pct}%`, backgroundColor: color } });
    const wrap = h("div", { class: `et-bar-wrap${negative ? " et-bar-negative" : ""}` }, bar);
    const label = h("span", { class: `et-bar-label${opts.hide_labels ? " et-hidden" : ""}` }, formatted);
    const cell = h("div", {
      class: "et-bar-cell",
      style: opts.background_color ? { backgroundColor: opts.background_color } : {},
    }, [wrap, label]);
    return cell;
  }

  _renderDelta(col, value) {
    const opts = col.delta_options || {};
    const num = Number(value);
    const [lo, hi] = opts.neutral_range || [opts.neutral_min ?? 0, opts.neutral_max ?? 0];
    const isNeutral = (lo == null || num >= lo) && (hi == null || num <= hi);
    const positive = num > 0;
    const good = isNeutral ? false : (opts.down_is_good ? !positive : positive);
    const cls = isNeutral ? "et-delta-neutral" : good ? "et-delta-good" : "et-delta-bad";
    const symbol = opts.show_symbol === false ? "" : (positive ? "▲" : num < 0 ? "▼" : "");
    const pct = Math.abs(num) <= 1 && col.fmt && col.fmt.startsWith("pct")
      ? Math.abs(num * 100).toFixed(1) + "%"
      : Math.abs(num).toLocaleString(undefined, { maximumFractionDigits: 1 });
    const text = [symbol, opts.show_value === false ? "" : pct].filter(Boolean).join(" ");
    const classes = ["et-delta", cls, opts.chip ? "et-delta-chip" : ""].filter(Boolean).join(" ");
    return h("span", { class: classes }, text || "–");
  }

  _renderSparkline(col, value) {
    const opts = col.sparkline_options || {};
    const points = this._sparklinePoints(value, opts);
    if (!points.length) return h("span", { class: "et-null" }, "–");

    const width = opts.width || 64;
    const height = opts.height || 18;
    const pad = 1.5;
    const ys = points.map((point) => point[1]);
    let min = Math.min(...ys);
    let max = Math.max(...ys);
    if (!opts.fit_to_data) {
      min = Math.min(0, min);
      max = Math.max(0, max);
    }
    const span = max - min || 1;
    const step = points.length > 1 ? (width - pad * 2) / (points.length - 1) : 0;
    const baseline = pad + (height - pad * 2) * (1 - (Math.max(0, min) - min) / span);
    const scaled = points.map(([x, y], index) => ({
      x: points.length > 1 ? pad + index * step : width / 2,
      y: pad + (height - pad * 2) * (1 - (y - min) / span),
      raw: [x, y],
    }));

    const color = opts.color || "var(--et-accent, #2563eb)";
    const svgNS = "http://www.w3.org/2000/svg";
    const svg = document.createElementNS(svgNS, "svg");
    svg.setAttribute("class", "et-sparkline");
    svg.setAttribute("width", String(width));
    svg.setAttribute("height", String(height));
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);

    const tooltip = ([x, y]) => {
      const title = document.createElementNS(svgNS, "title");
      const yText = formatValue(y, opts.y_fmt, { type: "number", fallback: String(y) });
      title.textContent = x === undefined || x === null || x === "" ? yText : `${x}: ${yText}`;
      return title;
    };

    // Zero baseline when the scale crosses zero (matching Evidence's defaults).
    if (!opts.fit_to_data && min < 0 && max > 0) {
      const zero = document.createElementNS(svgNS, "line");
      zero.setAttribute("x1", "0");
      zero.setAttribute("x2", String(width));
      zero.setAttribute("y1", String(baseline));
      zero.setAttribute("y2", String(baseline));
      zero.setAttribute("stroke", "color-mix(in srgb, CanvasText 20%, transparent)");
      zero.setAttribute("stroke-width", "1");
      svg.append(zero);
    }

    const type = opts.type || "line";
    if (type === "bar") {
      const slot = width / scaled.length;
      const barWidth = Math.max(1, slot * 0.7);
      scaled.forEach((point) => {
        const top = Math.min(point.y, baseline);
        const rect = document.createElementNS(svgNS, "rect");
        rect.setAttribute("x", String(Math.max(0, point.x - barWidth / 2)));
        rect.setAttribute("y", String(top));
        rect.setAttribute("width", String(barWidth));
        rect.setAttribute("height", String(Math.max(1, Math.abs(baseline - point.y))));
        rect.setAttribute("rx", "0.5");
        rect.setAttribute("fill", color);
        rect.append(tooltip(point.raw));
        svg.append(rect);
      });
    } else {
      const linePoints = scaled.map((point) => `${point.x},${point.y}`).join(" ");
      if (type === "area") {
        const area = document.createElementNS(svgNS, "polygon");
        area.setAttribute(
          "points",
          `${linePoints} ${scaled[scaled.length - 1].x},${baseline} ${scaled[0].x},${baseline}`,
        );
        area.setAttribute("fill", color);
        area.setAttribute("opacity", "0.18");
        svg.append(area);
      }
      const poly = document.createElementNS(svgNS, "polyline");
      poly.setAttribute("points", linePoints);
      poly.setAttribute("fill", "none");
      poly.setAttribute("stroke", color);
      poly.setAttribute("stroke-width", "1.25");
      poly.setAttribute("stroke-linejoin", "round");
      poly.setAttribute("stroke-linecap", "round");
      svg.append(poly);
      scaled.forEach((point) => {
        const dot = document.createElementNS(svgNS, "circle");
        dot.setAttribute("cx", String(point.x));
        dot.setAttribute("cy", String(point.y));
        dot.setAttribute("r", "2.5");
        dot.setAttribute("fill", "transparent");
        dot.append(tooltip(point.raw));
        svg.append(dot);
      });
    }
    return svg;
  }

  /** Normalise a cell value into ``[x, y]`` sparkline points.
   *
   * Accepts an array of numbers, an array of ``[x, y]`` pairs, or an array of
   * objects (e.g. DuckDB ``ARRAY_AGG({'date': date, 'sales': sales})``). For
   * objects, ``sparkline_options.x`` / ``.y`` name the fields; otherwise the
   * first numeric field is used for y and the first non-numeric field for x. */
  _sparklinePoints(value, opts) {
    if (!Array.isArray(value)) return [];
    const xKey = opts.x;
    const yKey = opts.y;
    const points = [];
    value.forEach((item, index) => {
      if (item === null || item === undefined) return;
      let x = index;
      let y;
      if (Array.isArray(item)) {
        x = item[0];
        y = Number(item[1]);
      } else if (typeof item === "object") {
        const keys = Object.keys(item);
        const yField = yKey && yKey in item ? yKey : keys.find((key) => _isNumeric(item[key]));
        const xField =
          xKey && xKey in item ? xKey : keys.find((key) => key !== yField && !_isNumeric(item[key]));
        x = xField ? item[xField] : index;
        y = Number(yField ? item[yField] : NaN);
      } else {
        y = Number(item);
      }
      if (y !== null && !isNaN(y)) points.push([x, y]);
    });
    return points;
  }

  _renderFooter(page, pageCount, total) {
    this.footer.replaceChildren();
    if (pageCount <= 1) return;
    const opts = this.options;
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
        if (this._holdFired) {
          this._holdFired = false;
          return;
        }
        this._gotoPage(this._state.page + (direction === "next" ? 1 : -1));
      });
      return button;
    };

    this.footer.append(
      h("span", { class: "et-page-info" }, `${start}–${end} of ${total}`),
      h("div", { class: "et-page-controls" }, [
        pageButton("‹", "prev", page === 0),
        h("span", { class: "et-page-current" }, `${page + 1} / ${pageCount}`),
        pageButton("›", "next", page >= pageCount - 1),
      ]),
    );
  }

  _gotoPage(page) {
    const count = Math.max(1, this._pageCount || 1);
    this._state.page = Math.min(Math.max(0, page), count - 1);
    this.render();
  }

  // Press-and-hold pagination: after HOLD_DELAY, advance one page every
  // HOLD_START_INTERVAL ms, easing linearly to HOLD_END_INTERVAL ms.
  _startHold(direction) {
    this._stopHold();
    this._holdFired = false;
    this._hold = { direction, start: performance.now(), timer: null };
    window.addEventListener("pointerup", this._onPointerUp);
    window.addEventListener("pointercancel", this._onPointerUp);
    window.addEventListener("blur", this._onPointerUp);
    this._hold.timer = setTimeout(() => this._holdStep(), HOLD_DELAY);
  }

  _stopHold() {
    if (this._hold?.timer) clearTimeout(this._hold.timer);
    this._hold = null;
    window.removeEventListener("pointerup", this._onPointerUp);
    window.removeEventListener("pointercancel", this._onPointerUp);
    window.removeEventListener("blur", this._onPointerUp);
  }

  _holdStep() {
    if (!this._hold) return;
    this._holdFired = true;
    const advanced = this._advance(this._hold.direction);
    if (!advanced) {
      this._stopHold();
      return;
    }
    const interval = holdInterval(performance.now() - this._hold.start);
    this._hold.timer = setTimeout(() => this._holdStep(), interval);
  }

  _advance(direction) {
    const next = this._state.page + (direction === "next" ? 1 : -1);
    if (next < 0 || next >= this._pageCount) return false;
    this._gotoPage(next);
    return true;
  }

  // ----------------------------------------------------------- fullscreen ---
  _toggleExpanded() {
    if (this._expanded) { this._closeExpanded(); return; }
    this._expanded = true;
    this.expandBtn.textContent = "×";
    this.expandBtn.title = "Close expanded table";
    this.expandBtn.setAttribute("aria-expanded", "true");
    this.dialog.append(this.root);
    this.dialog.showModal();
    this.root.classList.add("et-expanded");
    // Drop the inline max-height immediately so the first fit measurement sees
    // the real available height instead of the capped inline one.
    this.scroller.style.maxHeight = "none";
    this._resetBaselineHeight();
    requestAnimationFrame(() => {
      this._applyFrozenOffsets();
      this._fitFullscreen();
    });
  }

  _closeExpanded() {
    if (this.dialog.open) this.dialog.close();
    else this._restoreInline();
  }

  _restoreInline() {
    if (!this._expanded) return;
    this._expanded = false;
    this._pageSizeOverride = null;
    this.placeholder.after(this.root);
    this.root.classList.remove("et-expanded");
    this.expandBtn.textContent = "⛶";
    this.expandBtn.title = "Expand table";
    this.expandBtn.setAttribute("aria-expanded", "false");
    this.expandBtn.focus({ preventScroll: true });
    // Restore the notebook's configured page size and drop the fullscreen
    // height baseline so the inline table shrinks back to its natural size.
    this._resetBaselineHeight();
    this.render();
    requestAnimationFrame(() => this._applyFrozenOffsets());
  }

  _resetBaselineHeight() {
    this._baselineHeight = 0;
    this._baselinePageSize = null;
    this.scroller.style.minHeight = "";
  }

  // Size the fullscreen page so the rows fill the available viewport height.
  _fitFullscreen() {
    if (!this._expanded || this._fitting) return;
    this._fitting = true;
    try {
      for (let attempt = 0; attempt < 3; attempt++) {
        const row = this.scroller.querySelector("tbody tr");
        const rowHeight = row ? row.getBoundingClientRect().height : ROW_HEIGHT;
        const head = this.scroller.querySelector("thead");
        const headerHeight = head ? head.getBoundingClientRect().height : 0;
        const available = this.scroller.clientHeight - headerHeight;
        if (available <= 0 || rowHeight <= 0) break;
        // Leave a hair of slack so we never introduce a scrollbar.
        const fit = Math.max(1, Math.floor((available - 2) / rowHeight));
        if (fit === this._pageSizeOverride) break;
        this._pageSizeOverride = fit;
        this.render();
      }
    } finally {
      this._fitting = false;
    }
  }

  // --------------------------------------------------------- frozen cols ---
  _applyFrozenOffsets() {
    const n = this.options.freeze_columns || 0;
    const table = this.scroller.querySelector("table");
    if (!table || n <= 0) return;
    const headerCells = table.querySelectorAll("thead tr:last-child th");
    const offsets = [];
    let cumulative = 0;
    for (let i = 0; i < n && i < headerCells.length; i++) {
      offsets.push(cumulative);
      cumulative += headerCells[i].getBoundingClientRect().width;
    }
    const rows = table.querySelectorAll("tbody tr");
    rows.forEach((tr) => {
      const cells = tr.children;
      for (let i = 0; i < n && i < cells.length; i++) {
        const cell = cells[i];
        cell.style.position = "sticky";
        cell.style.left = `${offsets[i]}px`;
        cell.style.zIndex = String(10 + (n - i));
        cell.classList.add("et-frozen");
        if (i === n - 1) cell.classList.add("et-frozen-last");
      }
    });
    headerCells.forEach((th, i) => {
      if (i < n) {
        th.style.position = "sticky";
        th.style.left = `${offsets[i] ?? 0}px`;
        th.style.zIndex = String(30 + (n - i));
        th.classList.add("et-frozen");
      }
    });
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

function optString(value) {
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

export function render({ model, el }) {
  el.classList.add("evidence-tables-widget");
  const renderer = new EvidenceTableRenderer(model, el);
  const rerender = () => renderer.render();
  const setLoading = () => renderer.setLoading(model.get("loading"));
  model.on("change:rows", rerender);
  model.on("change:columns", rerender);
  model.on("change:options", rerender);
  model.on("change:loading", setLoading);
  return () => {
    model.off("change:rows", rerender);
    model.off("change:columns", rerender);
    model.off("change:options", rerender);
    model.off("change:loading", setLoading);
    renderer.destroy();
  };
}

export default { render };
