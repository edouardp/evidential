// Fullscreen sizing and frozen-column lifecycle, supplied through explicit ports.
const ROW_HEIGHT = 28;

export class TableViewport {
  constructor({root, dialog, button, placeholder, scroller, getOptions, rerender,
    resetBaseline, getPageSizeOverride, setPageSizeOverride}) {
    Object.assign(this, {root, dialog, button, placeholder, scroller, getOptions,
      rerender, resetBaseline, getPageSizeOverride, setPageSizeOverride});
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
      this.applyFrozenOffsets();
      if (this.expanded) this.fit();
    });
    this.observer.observe(scroller);
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
    this.resetBaseline();
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
    this.rerender();
    this.frame(() => this.applyFrozenOffsets());
  }

  fit() {
    if (!this.expanded || this.fitting) return;
    this.fitting = true;
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
        if (fit === this.getPageSizeOverride()) break;
        this.setPageSizeOverride(fit);
        this.rerender();
      }
    } finally {
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
    if (n <= 0) return;
    // Measure physical column edges, never infer them from spanning headers.
    // Reading before writing avoids measuring already-sticky cells on resize.
    const bodyCells = [...table.querySelectorAll("tbody [data-column-index]")];
    const headerCells = [...table.querySelectorAll("thead [data-column-start]")];
    for (const cell of [...bodyCells, ...headerCells]) {
      cell.style.left = "";
      cell.classList.remove("et-frozen", "et-frozen-last");
      if (cell.tagName === "TD") cell.style.position = "";
    }
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
    for (const cell of headerCells) {
      const start = Number(cell.dataset.columnStart);
      // A header crossing the frozen boundary continues to scroll as a whole.
      if (start + cell.colSpan <= n) {
        freeze(cell, start, 30);
      }
    }
  }
}
