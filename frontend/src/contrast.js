// Painted backgrounds and theme lifecycle, independent of data preparation.
import {chroma, colorStylesFromHex, compositeOver, contrastTextColor} from "./color.js";

const automatic = new WeakMap();
const selector = "[data-et-auto-contrast]";

export function autoContrast(node, options = {}) {
  automatic.set(node, options);
  node.setAttribute("data-et-auto-contrast", "");
}

export function clearAutoContrast(node) {
  automatic.delete(node);
  node.removeAttribute("data-et-auto-contrast");
}

// Cross the anywidget shadow boundary, and follow the root into its dialog.
function parentOf(node) {
  return node.parentElement || node.getRootNode()?.host || null;
}

/** Cache style reads and shared ancestor paints for one refresh, not across themes. */
export function paintResolver(root) {
  const view = root.ownerDocument.defaultView;
  const styles = new Map(), colors = new Map(), backgrounds = new Map();
  let probe, canvas;
  const style = node => {
    if (!styles.has(node)) styles.set(node, view.getComputedStyle(node));
    return styles.get(node);
  };
  const color = value => {
    if (!value?.trim()) return chroma("#00000000");
    if (colors.has(value)) return colors.get(value);
    let parsed;
    if (chroma.valid(value)) parsed = chroma(value);
    else {
      // Let the browser resolve system colours, var(), color-mix() and newer
      // CSS colour spaces. Canvas converts computed native colours to sRGB.
      probe ||= root.appendChild(root.ownerDocument.createElement("span"));
      probe.style.display = "none";
      probe.style.backgroundColor = "";
      probe.style.backgroundColor = value;
      const computed = view.getComputedStyle(probe).backgroundColor;
      if (chroma.valid(computed)) parsed = chroma(computed);
      else if (probe.style.backgroundColor && view.CanvasRenderingContext2D) {
        if (!canvas) {
          const bitmap = root.ownerDocument.createElement("canvas");
          bitmap.width = bitmap.height = 1;
          canvas = bitmap.getContext("2d", {willReadFrequently: true});
        }
        if (canvas) {
          canvas.clearRect(0, 0, 1, 1);
          canvas.fillStyle = computed;
          canvas.fillRect(0, 0, 1, 1);
          const [r, g, b, a] = canvas.getImageData(0, 0, 1, 1).data;
          parsed = chroma(r, g, b).alpha(a / 255);
        }
      }
    }
    parsed ||= chroma("#00000000");
    colors.set(value, parsed);
    return parsed;
  };
  const background = node => {
    if (!node) return compositeOver(color("Canvas"), "white");
    if (backgrounds.has(node)) return backgrounds.get(node);
    const computed = style(node);
    let seen = compositeOver(color(computed.backgroundColor), background(parentOf(node)));
    if (node.classList.contains("et-td")) {
      // Keep in sync with the CSS background-image stack, bottom to top.
      for (const property of ["--et-row-tint", "--et-cell-fill", "--et-selection-tint"]) {
        seen = compositeOver(color(computed.getPropertyValue(property)), seen);
      }
    }
    if (node.classList.contains("et-marks")) {
      for (const underlay of node.querySelectorAll(":scope > .et-mark-background")) {
        seen = compositeOver(color(style(underlay).backgroundColor), seen, Number(style(underlay).opacity || 1));
      }
    }
    backgrounds.set(node, seen);
    return seen;
  };
  return {style, color, background, destroy: () => probe?.remove()};
}

/** Read paint first, then write text colours; never perform per-cell geometry reads. */
export function refreshContrast(root) {
  const nodes = [...root.querySelectorAll(selector)];
  if (!nodes.length) return;
  const paint = paintResolver(root);
  try {
    const updates = nodes.map(node => {
      const options = automatic.get(node);
      let seen;
      if (options?.mark) {
        const fill = paint.color(paint.style(node).getPropertyValue("--et-label-fill"));
        const opacity = Number(paint.style(options.mark).opacity || 1);
        seen = compositeOver(fill, paint.background(options.mark.parentElement), opacity);
      } else seen = paint.background(node);
      return [node, options?.policy === "cell" ? colorStylesFromHex(seen).color : contrastTextColor(seen)];
    });
    for (const [node, color] of updates) node.style.color = color;
  } finally {
    paint.destroy();
  }
}

/** Theme changes recolour the current DOM without rerunning the data pipeline. */
export class ContrastController {
  constructor(root, frame) {
    this.root = root;
    this.frame = frame;
    this.view = root.ownerDocument.defaultView;
    this.schedule = () => {
      if (this.pending || this.destroyed) return;
      this.pending = true;
      this.frame(() => {
        this.pending = false;
        if (!this.destroyed) refreshContrast(this.root);
      });
    };
    this.observer = new this.view.MutationObserver(records => {
      if (records.some(record => this.ancestors.has(record.target) || record.target.tagName === "TR")) this.schedule();
    });
    this.media = this.view.matchMedia?.("(prefers-color-scheme: dark)");
    this.media?.addEventListener("change", this.schedule);
    this.onPointer = event => {
      const row = event.target.closest?.("tr") ?? null;
      const previous = event.relatedTarget?.closest?.("tr") ?? null;
      if (row !== previous) this.schedule();
    };
    root.addEventListener("pointerover", this.onPointer);
    root.addEventListener("pointerout", this.onPointer);
  }

  watch() {
    this.observer.disconnect();
    this.ancestors = new Set();
    for (let node = this.root; node; node = parentOf(node)) {
      this.ancestors.add(node);
      this.observer.observe(node, {attributes: true, attributeFilter: ["class", "style"], subtree: node === this.root});
    }
  }

  destroy() {
    this.destroyed = true;
    this.observer.disconnect();
    this.media?.removeEventListener("change", this.schedule);
    this.root.removeEventListener("pointerover", this.onPointer);
    this.root.removeEventListener("pointerout", this.onPointer);
  }
}
