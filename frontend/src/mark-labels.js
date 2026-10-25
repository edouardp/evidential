import { h, withFigure } from "./dom.js";
import { formatValue } from "./format.js";
import { formattedText } from "./formatted-text.js";
import { resolveColor, contrastTextColor } from "./color.js";

// Retain the requested placement separately from the position chosen by fitting.
const automaticLabels = new WeakMap();
const placementClasses = ["inside_start", "inside_end", "outside_start", "outside_end", "center", "above", "below"]
  .map(position => `et-mark-label-${position}`)
  .concat(["et-mark-label-inside", "et-mark-label-left", "et-mark-label-start",
    "et-mark-label-align-begin", "et-mark-label-align-center", "et-mark-label-align-end"]);

/** Explicit label colours win; otherwise read text against the mark's fill. */
export function autoLabelColor(label, fill) {
  label.dataset.autoContrast = "true";
  label.style.setProperty("--et-label-fill", fill);
  label.style.color = contrastTextColor(fill);
}

/** Share font/figure formatting with cells; label-specific colour is optional. */
export function labelTextStyle(spec) {
  return withFigure({
    ...(spec.color ? {color: resolveColor(spec.color)} : {}),
    ...(spec.font_weight ? {fontWeight: spec.font_weight} : {}),
    ...(spec.font_style ? {fontStyle: spec.font_style} : {}),
  }, spec, {});
}

/** Position a bar annotation without retaining classes or color from a prior fit. */
function placeBarLabel(node, spec, geometry, position) {
  node.classList.remove(...placementClasses);
  node.classList.add(`et-mark-label-${position}`);
  node.dataset.labelPosition = position;
  node.style.width = "";
  node.style.color = spec.color ? resolveColor(spec.color) : "";
  node.style.removeProperty("--et-label-fill");
  delete node.dataset.autoContrast;
  const inside = ["inside_start", "inside_end", "center"].includes(position);
  if (inside) {
    node.style.left = `${geometry.leftPct}%`;
    node.style.width = `${Math.max(0, geometry.widthPct)}%`;
    node.classList.add("et-mark-label-inside");
    const atLeft = position === "inside_start" ? !geometry.negative : geometry.negative;
    const align = spec.align || (position === "center" ? "center" : atLeft ? "begin" : "end");
    node.classList.add(`et-mark-label-align-${align}`);
    if (!spec.color && geometry.color) autoLabelColor(node, geometry.color);
  } else {
    const atLeft = position === "outside_start" ? !geometry.negative : geometry.negative;
    node.style.left = `${atLeft ? geometry.leftPct : geometry.leftPct + geometry.widthPct}%`;
    if (atLeft && ["outside_start", "outside_end"].includes(position)) node.classList.add("et-mark-label-left");
  }
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
    style: labelTextStyle(spec),
  }, h("span", {class: "et-mark-label-text"}, formattedText(text)));
  if (geometry.leftPct != null) {
    placeBarLabel(node, spec, geometry, position);
    if (spec.auto) automaticLabels.set(node, {spec, geometry, preferred: position});
  } else if (geometry.pointPct != null) {
    node.style.left = `${geometry.pointPct}%`;
    if (position === "outside_start") node.classList.add("et-mark-label-left");
  }
  return node;
}

/** Fit within the cell and, for an inside label, within its own mark. */
function labelFits(label) {
  const container = label.classList.contains("et-mark-stack-label") ? label.parentElement : label;
  const bounds = container.getBoundingClientRect();
  const cell = label.closest("td")?.getBoundingClientRect();
  if (!cell || !(cell.right > cell.left)) return null; // Detached DOM / non-layout test runtime.
  if (!bounds.width) return false;
  const text = label.querySelector(".et-mark-label-text") || label;
  const inside = label.classList.contains("et-mark-label-inside") || label.classList.contains("et-mark-stack-label");
  const fits = inside ? text.getBoundingClientRect().width + 6 <= bounds.width
    : bounds.left >= cell.left && bounds.right <= cell.right;
  return fits && bounds.width >= Number(label.dataset.minWidth || 0);
}

/** Always retry the user's preference first, including after a resize. */
function fitAutomaticLabel(label, {spec, geometry, preferred}) {
  label.hidden = false;
  placeBarLabel(label, spec, geometry, preferred);
  const fits = labelFits(label);
  if (fits == null) return;
  if (fits) {
    label.style.visibility = "";
    return;
  }
  const alternate = preferred.startsWith("outside_") ? preferred.replace("outside_", "inside_")
    : preferred.replace("inside_", "outside_");
  placeBarLabel(label, spec, geometry, alternate);
  const alternateFits = labelFits(label);
  label.style.visibility = alternateFits ? "" : "hidden";
  // Omitted labels must not create scrollable overflow beyond a compact cell.
  label.hidden = !alternateFits;
}

/** Refit labels after rendering/resizing; hidden text remains in the tooltip. */
export function fitMarkLabels(root) {
  for (const label of root.querySelectorAll("[data-mark-label]")) {
    const automatic = automaticLabels.get(label);
    if (automatic) {
      fitAutomaticLabel(label, automatic);
    } else if (label.dataset.overflow !== "show") {
      // Restore omitted labels for measurement, then remove any off-cell box
      // from scrollable overflow as well as hiding its text.
      label.hidden = false;
      const fits = labelFits(label);
      if (fits != null) {
        label.style.visibility = fits ? "" : "hidden";
        label.hidden = !fits;
      }
    }
    if (label.dataset.autoContrast) {
      // Resolve CSS variables too, including theme accents and dark-mode fills.
      const style = label.ownerDocument.defaultView.getComputedStyle(label);
      label.style.color = contrastTextColor(style.getPropertyValue("--et-label-fill").trim());
    }
  }
}
