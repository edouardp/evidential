import { h } from "./dom.js";
import { columnHeading } from "./headers.js";
import { tooltipText, tooltipValue } from "./tooltip-data.js";
import { pointVisual } from "./point-clusters.js";

const targets = new WeakMap();
const delays = new WeakMap();
let nextId = 0;

/** Register data rather than event handlers. Weak keys leave no detached-row cache. */
export function inspectable(node, data, {priority = 1, navigate = true} = {}) {
  targets.set(node, {data, priority, navigate});
  node.setAttribute("data-et-tooltip", "");
  // Useful when a mark is rendered on its own. The controller removes native
  // titles from managed nodes, so browsers never show a second tooltip.
  if (node.namespaceURI === "http://www.w3.org/2000/svg") {
    let title = node.querySelector(":scope > title");
    if (!title) { title = document.createElementNS(node.namespaceURI, "title"); node.append(title); }
    title.textContent = tooltipText(data);
  } else node.title = tooltipText(data);
  return node;
}

export function inspectionData(node) { return targets.get(node)?.data; }

/** Apply column overrides once, including nulls and every child mark. */
export function inspectCell(cell, col, row, options, formatCode) {
  targets.delete(cell);
  delete cell.dataset.etTooltipCell;
  cell.removeAttribute("tabindex");
  if (!cell.textContent && !cell.querySelector("[data-et-tooltip]")) return;
  if (col.tooltip === false || typeof col.tooltip === "string") {
    for (const node of cell.querySelectorAll("[data-et-tooltip]")) {
      targets.delete(node); node.removeAttribute("data-et-tooltip");
      node.removeAttribute("title"); node.querySelector(":scope > title")?.remove();
    }
    for (const node of cell.querySelectorAll("[data-mark-label][title]")) node.removeAttribute("title");
    if (col.tooltip === false) return;
  }
  const marks = [...cell.querySelectorAll("[data-et-tooltip]")].filter(node => targets.get(node)?.navigate);
  const override = typeof col.tooltip === "string"
    ? col.tooltip.startsWith("@") ? row[col.tooltip.slice(1)] : col.tooltip : null;
  if (typeof col.tooltip === "string" && override == null) return;
  const value = row[col.name];
  const numeric = typeof value === "number" && Number.isFinite(value);
  const text = typeof value === "string" && !col.html && !col.markdown;
  if (!marks.length && !numeric && !text && override == null) return;
  const data = override != null ? {value: String(override)} : {
    name: columnHeading(col, options), value: marks.length ? "" : tooltipValue(value, formatCode ?? col.fmt, col),
  };
  targets.set(cell, {data, priority: 0, navigate: false});
  cell.dataset.etTooltipCell = "";
  const timing = {...options.tooltips, ...col.tooltip_options};
  const graphic = Boolean(cell.querySelector(".et-marks, .et-sparkline, .et-bar-cell, .et-symbols, .et-delta"));
  delays.set(cell, (graphic ? timing.delay ?? 0 : timing.text_delay ?? 0.8) * 1000);
  const summary = marks.length ? marks.map(node => tooltipText(targets.get(node).data)).join("\n") : tooltipText(data);
  cell.setAttribute("aria-label", summary);
  if (marks.length || override != null) cell.tabIndex = 0;
  for (const graphic of cell.querySelectorAll(".et-marks, .et-sparkline")) {
    graphic.setAttribute("role", "group");
    const counts = graphic.classList.contains("et-sparkline-change") ? graphic.getAttribute("aria-label") : null;
    graphic.setAttribute("aria-label", counts ? `${counts}\n${summary}` : summary);
  }
}

function entries(cell) {
  return [...cell.querySelectorAll("[data-et-tooltip]")].filter(node => targets.has(node));
}

/** All marks in the enlarged hit area; foreground points take precedence. */
export function hitTargets(cell, x, y, direct) {
  const owner = direct?.closest?.("[data-mark-label][data-et-tooltip]");
  if (owner && targets.has(owner)) return [owner];
  const nodes = entries(cell);
  const sparkline = cell.querySelector(".et-sparkline");
  if (sparkline) {
    const bounds = sparkline.getBoundingClientRect();
    if (x < bounds.left || x > bounds.right || y < bounds.top || y > bounds.bottom) return [];
    const circles = nodes.filter(node => node.tagName.toLowerCase() === "circle");
    const observations = circles.length ? circles : nodes;
    return observations.length ? [observations.reduce((nearest, node) => {
      const center = item => { const rect = item.getBoundingClientRect(); return rect.left + rect.width / 2; };
      return Math.abs(center(node) - x) < Math.abs(center(nearest) - x) ? node : nearest;
    })] : [];
  }
  const hits = nodes.filter(node => {
    const rect = node.getBoundingClientRect();
    const tolerance = targets.get(node).priority >= 3 ? 5 : 0;
    return rect.width > 0 && rect.height > 0 && x >= rect.left - tolerance && x <= rect.right + tolerance &&
      y >= rect.top - tolerance && y <= rect.bottom + tolerance;
  });
  const priority = Math.max(-1, ...hits.map(node => targets.get(node).priority));
  const foreground = hits.filter(node => targets.get(node).priority === priority);
  if (foreground.length && foreground.every(node => node.matches(".et-mark-stack-seg, .et-strip-seg, .et-strip-run"))) {
    // At a shared edge, the segment beginning here owns the position.
    return [foreground.find(node => x < node.getBoundingClientRect().right) || foreground.at(-1)];
  }
  if (foreground.length) return foreground;
  const label = direct?.closest?.("[data-et-tooltip]");
  return label && cell.contains(label) && targets.has(label) ? [label] : nodes.length ? [] : [cell];
}

/** One delegated tooltip per widget, including fullscreen and rerenders. */
export class TooltipController {
  constructor(root) {
    this.root = root;
    this.view = root.ownerDocument.defaultView;
    this.abort = new this.view.AbortController();
    this.popup = h("div", {class: "et-tooltip", role: "tooltip", id: `et-tooltip-${++nextId}`, popover: "manual"});
    this.popup.hidden = true;
    root.append(this.popup);
    const on = (element, event, handler, capture = false) => element.addEventListener(event, handler, {signal: this.abort.signal, capture});
    on(root, "pointermove", event => {
      if (event.pointerType === "touch") return;
      if (this.popup.contains(event.target)) { this.cancelHide(); return; }
      const cell = event.target.closest?.("[data-et-tooltip-cell]");
      if (!cell) { this.scheduleHide(); return; }
      const nodes = hitTargets(cell, event.clientX, event.clientY, event.target);
      if (!nodes.length) { this.scheduleHide(); return; }
      this.hover(nodes, cell, event.clientX, event.clientY);
    });
    on(root, "pointerleave", event => { if (event.pointerType !== "touch") this.scheduleHide(); });
    on(this.popup, "pointerenter", () => this.cancelHide());
    on(this.popup, "pointerleave", event => { if (event.pointerType !== "touch") this.scheduleHide(); });
    on(root, "pointerdown", () => { this.touchInspection = null; clearTimeout(this.touchTimer); });
    on(root, "pointerup", event => {
      if (event.pointerType !== "touch") return;
      const cell = event.target.closest?.("[data-et-tooltip-cell]");
      if (!cell) { this.hide(); return; }
      const data = this.values(hitTargets(cell, event.clientX, event.clientY, event.target));
      this.touchInspection = {data, x: event.clientX, y: event.clientY};
    });
    on(root, "click", () => {
      const inspection = this.touchInspection;
      this.touchInspection = null;
      if (!inspection) return;
      // A synthetic touch click can arrive AFTER a pointerup timer. Wait for
      // the click itself, whose row handler may already have replaced the cell.
      clearTimeout(this.touchTimer);
      this.touchTimer = setTimeout(() => {
        if (this.root.isConnected) this.showData(inspection.data, this.root, inspection.x, inspection.y);
      }, 0);
    });
    on(root, "focusin", event => {
      const cell = event.target.closest?.("[data-et-tooltip-cell]");
      if (event.target === cell) { this.keyboardCell = cell; this.index = 0; this.inspectKeyboard(); }
    });
    on(root, "focusout", () => { this.keyboardCell = null; this.hide(); });
    on(root, "keydown", event => {
      if (event.key === "Escape" && (!this.popup.hidden || this.pending)) {
        event.preventDefault(); event.stopPropagation(); this.hide(); return;
      }
      if (!this.keyboardCell || !["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
      const count = this.keyboardNodes().length;
      this.index = event.key === "Home" ? 0 : event.key === "End" ? count - 1
        : (this.index + (event.key === "ArrowLeft" ? -1 : 1) + count) % count;
      event.preventDefault(); event.stopPropagation(); this.inspectKeyboard();
    });
    on(root, "scroll", () => this.hide(), true);
    on(this.view, "resize", () => this.hide());
    on(this.view, "scroll", () => this.hide(), true);
    on(root.ownerDocument, "pointerdown", event => {
      if (!root.contains(event.target)) { this.touchInspection = null; clearTimeout(this.touchTimer); this.hide(); }
    });
    on(root.ownerDocument, "keydown", event => {
      if (event.key === "Escape" && (!this.popup.hidden || this.pending) && !root.contains(event.target)) {
        event.preventDefault(); this.hide();
      }
    });
  }

  refresh() {
    this.hide(); this.keyboardCell = null;
    for (const node of this.root.querySelectorAll("[data-et-tooltip], .et-marks, [data-mark-label]")) {
      node.removeAttribute("title"); node.querySelector(":scope > title")?.remove();
    }
  }

  keyboardNodes() {
    const nodes = entries(this.keyboardCell).filter(node => targets.get(node).navigate);
    return nodes.length ? nodes : [this.keyboardCell];
  }

  inspectKeyboard() {
    const node = this.keyboardNodes()[this.index];
    const rect = node.getBoundingClientRect();
    // Keyboard inspection reveals overlapping points together too.
    const nodes = (targets.get(node)?.priority || 0) >= 3
      ? hitTargets(this.keyboardCell, rect.left + rect.width / 2, rect.top + rect.height / 2, node) : [node];
    this.show(nodes, this.keyboardCell, rect.left + rect.width / 2, rect.bottom);
    this.active?.classList.remove("et-tooltip-active");
    this.active = pointVisual(node);
    this.active.classList.add("et-tooltip-active");
  }

  values(nodes) {
    const seen = new Set();
    return nodes.map(node => targets.get(node)?.data).filter(data => {
      if (!data || seen.has(tooltipText(data))) return false;
      seen.add(tooltipText(data)); return true;
    }).sort((a, b) => Number.isFinite(a.xValue) && Number.isFinite(b.xValue) ? a.xValue - b.xValue : 0);
  }

  show(nodes, anchor, x, y) { this.showData(this.values(nodes), anchor, x, y); }

  hover(nodes, cell, x, y) {
    this.cancelHide();
    const values = this.values(nodes), key = JSON.stringify(values);
    const delay = delays.get(cell) || 0;
    if (!this.popup.hidden && this.anchor === cell) { this.cancelPending(); this.showData(values, cell, x, y); return; }
    if (!delay) { this.cancelPending(); this.showData(values, cell, x, y); return; }
    if (this.pending?.cell === cell && this.pending.key === key) {
      this.pending.x = x; this.pending.y = y; return;
    }
    this.hide();
    this.pending = {cell, key, values, x, y};
    this.showTimer = setTimeout(() => {
      const pending = this.pending;
      this.pending = null; this.showTimer = null;
      if (pending?.cell.isConnected) this.showData(pending.values, cell, pending.x, pending.y);
    }, delay);
  }

  showData(values, anchor, x, y) {
    this.cancelPending();
    this.cancelHide();
    if (!values.length) { this.hide(); return; }
    const key = JSON.stringify(values);
    if (this.key !== key) {
      this.popup.replaceChildren(...values.map(data => h("div", {class: "et-tooltip-entry"}, [
        data.color ? h("span", {class: "et-tooltip-swatch", "aria-hidden": "true", style: {backgroundColor: data.color}}) : null,
        h("div", {class: "et-tooltip-content"}, [
          data.name ? h("span", {class: "et-tooltip-name"}, `${data.name}${data.value ? ":" : ""}`) : null,
          data.value ? h("span", {class: "et-tooltip-value"}, data.value) : null,
          ...(data.details || []).map(item => h("div", {class: "et-tooltip-detail"}, [
            h("span", {}, `${item.name}: `), h("span", {class: "et-tooltip-value"}, item.value),
          ])),
        ]),
      ])));
      this.key = key;
    }
    if (this.anchor !== anchor) this.anchor?.removeAttribute("aria-describedby");
    this.anchor = anchor;
    anchor.setAttribute("aria-describedby", this.popup.id);
    this.popup.hidden = false;
    if (this.popup.showPopover && !this.popup.matches(":popover-open")) this.popup.showPopover();
    const box = this.popup.getBoundingClientRect();
    const width = this.view.innerWidth, height = this.view.innerHeight;
    this.popup.style.left = `${Math.max(8, Math.min(x + 12, width - box.width - 8))}px`;
    this.popup.style.top = `${Math.max(8, Math.min(y + box.height + 20 > height ? y - box.height - 12 : y + 12, height - box.height - 8))}px`;
  }

  hide() {
    this.cancelPending();
    this.cancelHide();
    this.popup.hidePopover?.();
    this.popup.hidden = true;
    this.anchor?.removeAttribute("aria-describedby"); this.anchor = null;
    this.active?.classList.remove("et-tooltip-active"); this.active = null;
    this.key = null;
  }

  scheduleHide() {
    this.cancelPending();
    if (this.hideTimer) return;
    this.hideTimer = setTimeout(() => { this.hideTimer = null; this.hide(); }, 120);
  }

  cancelHide() { clearTimeout(this.hideTimer); this.hideTimer = null; }

  cancelPending() { clearTimeout(this.showTimer); this.showTimer = null; this.pending = null; }

  destroy() { clearTimeout(this.touchTimer); this.cancelPending(); this.abort.abort(); this.hide(); this.popup.remove(); }
}
