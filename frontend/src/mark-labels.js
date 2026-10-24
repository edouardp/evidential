import { h } from "./dom.js";
import { formatValue } from "./format.js";
import { resolveColor, contrastTextColor } from "./color.js";

/** Explicit label colours win; otherwise read text against the mark's fill. */
export function autoLabelColor(label, fill) {
  label.dataset.autoContrast = "true";
  label.style.setProperty("--et-label-fill", fill);
  label.style.color = contrastTextColor(fill);
}

/** The label text for a mark: a literal, another field, or the mark's value. */
export function markLabelText(col, enc, row, format) {
  const spec = enc.label || {};
  let text;
  if (spec.text != null) {
    text = String(spec.text);
  } else {
    const raw = spec.source != null ? row[spec.source] : row[enc.source];
    text = format ? format(raw, spec) :
      raw === null || raw === undefined
        ? ""
        : formatValue(raw, spec.format || col.fmt, { type: col.type, fallback: String(raw) });
  }
  if (text === "") return "";
  return `${spec.prefix ?? ""}${text}${spec.suffix ?? ""}`;
}

/** A mark-owned label, positioned relative to its bar or point. */
export function renderMarkLabel(col, enc, row, geometry, format) {
  const spec = enc.label || {};
  const text = markLabelText(col, enc, row, format);
  if (!text) return h("span", { class: "et-mark-label et-mark-label-empty" });
  const position = spec.position || (enc.kind === "bar" ? "outside_end" : "center");
  const node = h("span", { class: `et-mark-label et-mark-label-${position}`,
    title: text, "data-mark-label": "", "data-overflow": spec.overflow || "hide",
    "data-min-width": spec.min_width || 0,
    style: spec.color ? {color: resolveColor(spec.color)} : {},
  }, h("span", {class: "et-mark-label-text"}, text));
  if (geometry.leftPct != null) {
    const inside = ["inside_start", "inside_end", "center"].includes(position);
    if (inside) {
      node.style.left = `${geometry.leftPct}%`;
      node.style.width = `${Math.max(0, geometry.widthPct)}%`;
      node.classList.add("et-mark-label-inside");
      if (!spec.color && geometry.color) autoLabelColor(node, geometry.color);
      if (position === "inside_start") node.classList.add("et-mark-label-start");
      if (spec.align === "begin") node.classList.add("et-mark-label-align-begin");
      if (spec.align === "end") node.classList.add("et-mark-label-align-end");
      if (spec.align === "center" || position === "center") node.classList.add("et-mark-label-align-center");
    } else {
      const atLeft = position === "outside_start" ? !geometry.negative : geometry.negative;
      node.style.left = `${atLeft ? geometry.leftPct : geometry.leftPct + geometry.widthPct}%`;
      if (atLeft && ["outside_start", "outside_end"].includes(position)) node.classList.add("et-mark-label-left");
    }
  } else if (geometry.pointPct != null) {
    node.style.left = `${geometry.pointPct}%`;
    if (position === "outside_start") node.classList.add("et-mark-label-left");
  }
  return node;
}

/** Refit labels after rendering/resizing; hidden text remains in the tooltip. */
export function fitMarkLabels(root) {
  for (const label of root.querySelectorAll("[data-mark-label]")) {
    if (label.dataset.autoContrast) {
      // Resolve CSS variables too, including theme accents and dark-mode fills.
      const style = label.ownerDocument.defaultView.getComputedStyle(label);
      label.style.color = contrastTextColor(style.getPropertyValue("--et-label-fill").trim());
    }
    if (label.dataset.overflow === "show") continue;
    const container = label.classList.contains("et-mark-stack-label") ? label.parentElement : label;
    const bounds = container.getBoundingClientRect();
    const cell = label.closest("td")?.getBoundingClientRect();
    if (!cell || !bounds.width) continue; // Detached DOM / non-layout test runtime.
    const text = label.querySelector(".et-mark-label-text") || label;
    const width = text.getBoundingClientRect().width;
    const inside = label.classList.contains("et-mark-label-inside") || label.classList.contains("et-mark-stack-label");
    const fits = inside ? width + 6 <= bounds.width : bounds.left >= cell.left && bounds.right <= cell.right;
    label.style.visibility = fits && bounds.width >= Number(label.dataset.minWidth || 0) ? "" : "hidden";
  }
}
