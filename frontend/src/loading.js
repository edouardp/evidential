// Loading transition timing (ms).
const LOADING_SHOW_DELAY = 180; // don't show the overlay for updates faster than this
const FADE_MS = 600; // fade current data out and "Processing…" in over this long
const LOADING_HIDE_DEBOUNCE = 120; // settle time before revealing new data

/** Suppress fast-update flashes and keep slow-update fades visible until settled. */
export class LoadingController {
  constructor(root, overlay, el) {
    Object.assign(this, {root, overlay, el});
    this.loading = false;
    this.shown = false;
    this.showTimer = null;
    this.hideTimer = null;
    this.since = 0;
  }

  destroy() {
    clearTimeout(this.showTimer);
    clearTimeout(this.hideTimer);
  }

  set(loading) {
    this.loading = !!loading;
    this.el.dataset.loading = String(this.loading);
    if (this.loading) {
      if (this.hideTimer) {
        clearTimeout(this.hideTimer);
        this.hideTimer = null;
      }
      if (this.shown || this.showTimer) return;
      this.showTimer = setTimeout(() => {
        this.showTimer = null;
        this.shown = true;
        this.since = performance.now();
        this.apply();
      }, LOADING_SHOW_DELAY);
    } else {
      if (this.showTimer) {
        // Finished before the overlay was shown: never flash it.
        clearTimeout(this.showTimer);
        this.showTimer = null;
        return;
      }
      if (!this.shown) return;
      const elapsed = performance.now() - this.since;
      const wait = Math.max(LOADING_HIDE_DEBOUNCE, FADE_MS - elapsed);
      if (this.hideTimer) clearTimeout(this.hideTimer);
      this.hideTimer = setTimeout(() => {
        this.hideTimer = null;
        this.shown = false;
        this.apply();
      }, wait);
    }
  }

  apply() {
    this.root.classList.toggle("et-loading", this.shown);
    this.overlay.setAttribute("aria-hidden", String(!this.shown));
    this.el.dataset.loading = String(this.loading);
    this.el.dataset.loadingShown = String(this.shown);
  }
}
