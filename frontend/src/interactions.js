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

export class HoldController {
  constructor(advance) {
    this.advance = advance;
    this.hold = null;
    this.fired = false;
    this.onPointerUp = () => this.stop();
  }

  consumeClick() {
    const fired = this.fired;
    this.fired = false;
    return fired;
  }

  start(direction) {
    this.stop();
    this.fired = false;
    this.hold = { direction, start: performance.now(), timer: null };
    window.addEventListener("pointerup", this.onPointerUp);
    window.addEventListener("pointercancel", this.onPointerUp);
    window.addEventListener("blur", this.onPointerUp);
    this.hold.timer = setTimeout(() => this.step(), HOLD_DELAY);
  }

  stop() {
    if (this.hold?.timer) clearTimeout(this.hold.timer);
    this.hold = null;
    window.removeEventListener("pointerup", this.onPointerUp);
    window.removeEventListener("pointercancel", this.onPointerUp);
    window.removeEventListener("blur", this.onPointerUp);
  }

  step() {
    if (!this.hold) return;
    this.fired = true;
    const advanced = this.advance(this.hold.direction);
    if (!advanced) {
      this.stop();
      return;
    }
    const interval = holdInterval(performance.now() - this.hold.start);
    this.hold.timer = setTimeout(() => this.step(), interval);
  }
}

export function bindRowSelection(tr, row, selected, opts, model, findSelectedRow) {
  const selectKey = opts.select ? row[opts.select] : undefined;
  if (opts.select && selectKey !== undefined && selectKey !== null) {
    const isSelected =
      selected !== null && selected !== undefined && String(selected) === String(selectKey);
    tr.classList.add("et-row-selectable");
    tr.tabIndex = 0;
    tr.dataset.selectKey = String(selectKey);
    tr.setAttribute("aria-selected", String(isSelected));
    if (isSelected) tr.classList.add("et-row-selected");
    const select = (event) => {
      if (event.target.closest && event.target.closest("a, button, input, select, textarea")) return;
      // Clicking the selected row again clears the selection. `save_changes`
      // is what lets Marimo treat the new value as a cell dependency.
      model.set("selected", isSelected ? null : selectKey);
      model.save_changes();
      if (event.type === "keydown") {
        requestAnimationFrame(() => {
          const replacement = findSelectedRow(selectKey);
          replacement?.focus({ preventScroll: true });
        });
      }
    };
    tr.addEventListener("click", select);
    tr.addEventListener("keydown", (event) => {
      if (event.target !== tr || (event.key !== "Enter" && event.key !== " ")) return;
      event.preventDefault();
      select(event);
    });
  }
}
