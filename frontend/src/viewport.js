// Fullscreen sizing and frozen-column lifecycle, supplied through explicit ports.
import { fitMarkLabels } from "./mark-labels.js";
import { combinePoints } from "./point-clusters.js";

export class TableViewport {
  constructor({root, dialog, button, placeholder, scroller, getOptions, rerender,
    resetBaseline, getPageSizeOverride, setPageSizeOverride, getPageMetrics,
    onExpand, onRestore}) {
    Object.assign(this, {root, dialog, button, placeholder, scroller, getOptions,
      rerender, resetBaseline, getPageSizeOverride, setPageSizeOverride, getPageMetrics,
      onExpand, onRestore});
    if (dialog) {
      this.dialog.addEventListener("close", () => this.restore());
      this.dialog.addEventListener("cancel", (e) => { e.preventDefault(); this.close(); });
      // Clicking the backdrop (the dialog element itself, outside the content)
      // dismisses. Track where the press started so a drag that begins inside
      // the content and ends on the backdrop does not close it.
      this.backdropPress = false;
      this.dialog.addEventListener("pointerdown", (e) => {
        this.backdropPress = e.target === this.dialog;
      });
      this.dialog.addEventListener("click", (e) => {
        const onBackdrop = e.target === this.dialog && this.backdropPress;
        this.backdropPress = false;
        if (onBackdrop) this.close();
      });
    }
    this.expanded = false;
    this.fitting = false;
    this.destroyed = false;
    this.frames = new Set();
    this.observer = new ResizeObserver(() => {
      if (this.layoutPending) return;
      this.layoutPending = true;
      this.frame(() => {
        this.layoutPending = false;
        this.applyFrozenOffsets();
        fitMarkLabels(this.root);
        combinePoints(this.root);
        if (this.expanded) this.fit();
      });
    });
    this.observer.observe(scroller);
    if (root) this.observer.observe(root);
  }

  observeTable(table) {
    if (this.table === table) return;
    if (this.table) this.observer.unobserve(this.table);
    this.table = table;
    if (table) this.observer.observe(table);
  }

  frame(callback) {
    const id = requestAnimationFrame(() => {
      this.frames.delete(id);
      if (!this.destroyed) callback();
    });
    this.frames.add(id);
  }

  destroy() {
    this.destroyed = true;
    this.expanded = false;
    this.observer.disconnect();
    for (const id of this.frames) cancelAnimationFrame(id);
    this.frames.clear();
  }

  toggle() {
    if (this.expanded) { this.close(); return; }
    this.expanded = true;
    this.button.textContent = "× Expand";
    this.button.title = "Collapse table";
    this.button.setAttribute("aria-label", "Collapse table");
    this.button.setAttribute("aria-expanded", "true");
    this.dialog.append(this.root);
    this.dialog.showModal();
    this.root.classList.add("et-expanded");
    // Drop the inline max-height immediately so the first fit measurement sees
    // the real available height instead of the capped inline one.
    this.scroller.style.maxHeight = "none";
    this.scroller.scrollTop = 0;
    this.resetBaseline();
    this.onExpand?.();
    this.rerender();
    this.frame(() => {
      this.applyFrozenOffsets();
      this.fit();
    });
  }

  close() {
    if (this.dialog.open) this.dialog.close();
    else this.restore();
  }

  restore() {
    if (this.destroyed) return;
    if (!this.expanded) return;
    this.expanded = false;
    this.setPageSizeOverride(null);
    this.placeholder.after(this.root);
    this.root.classList.remove("et-expanded");
    this.button.textContent = "⛶ Expand";
    this.button.title = "Expand table";
    this.button.setAttribute("aria-label", "Expand table");
    this.button.setAttribute("aria-expanded", "false");
    this.button.focus({ preventScroll: true });
    // Restore the notebook's configured page size and drop the fullscreen
    // height baseline so the inline table shrinks back to its natural size.
    this.resetBaseline();
    this.onRestore?.();
    this.rerender();
    this.frame(() => this.applyFrozenOffsets());
  }

  /** Size the fullscreen page to fit the available viewport height. */
  fit() {
    if (!this.expanded || this.fitting) return;
    const signature = () => {
      const table = this.scroller.querySelector("table");
      return [this.scroller.clientHeight, this.scroller.clientWidth,
        table?.getBoundingClientRect().height, table?.querySelector("tbody")?.getBoundingClientRect().height,
        this.getPageSizeOverride(), this.getPageMetrics?.()?.remaining].join(":");
    };
    const projection = this.getPageMetrics?.()?.projection;
    if (signature() === this.lastFit && projection === this.lastProjection) return;
    this.fitting = true;
    try {
      let low = 0, high = Infinity, best = null;
      // Estimate from the whole rendered body, then bracket the largest page
      // that actually fits. Annotation rows and variable row heights are part
      // of the measurement. Bound work even for pathological wrapping/layouts.
      for (let attempt = 0; attempt < 12; attempt++) {
        const table = this.scroller.querySelector("table");
        const body = table?.querySelector("tbody");
        if (!body) break;
        const height = table.getBoundingClientRect().height;
        const bodyHeight = body.getBoundingClientRect().height;
        const available = this.scroller.clientHeight - 2;
        const bodyBudget = available - (height - bodyHeight);
        if (bodyBudget <= 0 || bodyHeight <= 0) break;
        const metrics = this.getPageMetrics?.();
        const displayed = metrics?.count || body.children.length;
        const remaining = metrics ? metrics.remaining || displayed : Infinity;
        const count = Number(this.getPageSizeOverride()) || displayed;
        if (height <= available) {
          low = count;
          best = count;
          if (displayed >= remaining || high - low <= 1) break;
        } else {
          high = count;
          // A single oversized record cannot be split safely.
          if (count <= 1 || high - low <= 1) break;
        }
        const estimate = Math.floor(displayed * bodyBudget / bodyHeight);
        let candidate;
        if (!Number.isFinite(high)) candidate = Math.min(remaining, Math.max(count + 1, estimate));
        else if (low > 0) candidate = Math.floor((low + high) / 2);
        else candidate = Math.max(1, Math.min(high - 1, estimate));
        if (candidate === count) break;
        this.setPageSizeOverride(candidate);
        this.rerender();
      }
      if (best != null && best !== this.getPageSizeOverride()) {
        this.setPageSizeOverride(best);
        this.rerender();
      }
    } finally {
      this.lastFit = signature();
      this.lastProjection = projection;
      this.fitting = false;
    }
  }

  applyFrozenOffsets() {
    if (this.destroyed) return;
    const n = this.getOptions().freeze_columns || 0;
    const table = this.scroller.querySelector("table");
    if (!table) return;
    // Each header level sticks below the previous one, even without freezing.
    let top = 0;
    for (const row of table.querySelectorAll("thead tr")) {
      for (const cell of row.children) cell.style.top = `${top}px`;
      top += row.getBoundingClientRect().height;
    }
    // Measure physical column edges, never infer them from spanning headers.
    // Reading before writing avoids measuring already-sticky cells on resize.
    const bodyCells = [...table.querySelectorAll("tbody [data-column-index]")];
    const axisCells = [...table.querySelectorAll("thead .et-axis-row [data-column-index], tfoot [data-column-index]")];
    const spanningCells = [...table.querySelectorAll("[data-column-start]")];
    // A plain section spans the table. Pin its label inside that span rather
    // than freezing the entire cell or splitting it and changing column widths.
    const headingLabels = [...table.querySelectorAll(".et-display-heading:not(.et-display-align-center) > .et-display-label")];
    for (const label of headingLabels) {
      label.classList.toggle("et-frozen-heading-label", n > 0);
      label.style.left = n > 0 ? window.getComputedStyle(label.parentElement).paddingLeft : "";
    }
    for (const cell of [...bodyCells, ...axisCells, ...spanningCells]) {
      if (n <= 0 && !cell.classList.contains("et-frozen")) continue;
      cell.style.left = "";
      cell.classList.remove("et-frozen", "et-frozen-last");
      if (cell.tagName === "TD") cell.style.position = "";
    }
    if (n <= 0) return;
    const offsets = new Map();
    const tableLeft = table.getBoundingClientRect().left;
    for (const cell of bodyCells) {
      const index = Number(cell.dataset.columnIndex);
      if (index < n && !offsets.has(index)) {
        offsets.set(index, cell.getBoundingClientRect().left - tableLeft);
      }
    }
    const freeze = (cell, index, base) => {
      if (index >= n || !offsets.has(index)) return;
      cell.style.position = "sticky";
      cell.style.left = `${offsets.get(index)}px`;
      cell.style.zIndex = String(base + n - index);
      cell.classList.add("et-frozen");
      if (index + cell.colSpan === n) cell.classList.add("et-frozen-last");
    };
    for (const cell of bodyCells) freeze(cell, Number(cell.dataset.columnIndex), 10);
    for (const cell of axisCells) freeze(cell, Number(cell.dataset.columnIndex), cell.closest("thead") ? 30 : 10);
    for (const cell of spanningCells) {
      const start = Number(cell.dataset.columnStart);
      // A spanning header or summary crossing the boundary scrolls as a whole.
      if (start + cell.colSpan <= n) {
        freeze(cell, start, cell.closest("thead") ? 30 : 10);
      }
    }
  }
}
