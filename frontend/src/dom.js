// DOM construction and presentation utilities.
export function h(tag, attrs = {}, children = []) {
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

export function optString(value) {
  if (typeof value === "object") return JSON.stringify(value);
  return String(value);
}

/** Minimal inline markdown: bold, italic and code; never raw HTML. */
export function inlineMarkdown(text) {
  const fragment = document.createDocumentFragment();
  const source = String(text ?? "");
  const pattern = /\*\*([^*]+)\*\*|__([^_]+)__|\*([^*]+)\*|_([^_]+)_|`([^`]+)`/g;
  let last = 0;
  for (const match of source.matchAll(pattern)) {
    if (match.index > last) fragment.append(document.createTextNode(source.slice(last, match.index)));
    const [full, bold, bold2, italic, italic2, code] = match;
    const value = bold ?? bold2 ?? italic ?? italic2 ?? code ?? full;
    if (code != null) fragment.append(h("code", {}, value));
    else if (bold != null || bold2 != null) fragment.append(h("strong", {}, value));
    else fragment.append(h("em", {}, value));
    last = match.index + full.length;
  }
  if (last < source.length) fragment.append(document.createTextNode(source.slice(last)));
  return fragment;
}

/** Map a figure style to its font-variant-numeric value. */
export function figureVariant(style) {
  switch (style) {
    case "oldstyle":
    case "oldstyle-tabular":
      return "oldstyle-nums tabular-nums";
    case "proportional":
    case "lining-proportional":
      return "lining-nums proportional-nums";
    case "oldstyle-proportional":
      return "oldstyle-nums proportional-nums";
    case "lining":
    case "tabular":
    case "lining-tabular":
      return "lining-nums tabular-nums";
    case "default":
    case "auto":
    case "none":
      // Use the font's own default figures (e.g. Hoefler Text's oldstyle).
      return "normal";
    default:
      return null;
  }
}

export function withFigure(baseStyle, col, opts) {
  const style = { ...baseStyle };
  const variant = figureVariant(col.figure_style ?? opts.figure_style);
  if (variant) style.fontVariantNumeric = variant;
  if (col.font) style.fontFamily = col.font;
  return style;
}

/** Compress sorted row numbers into ranges such as "1–3, 5". */
export function formatRowRanges(rows) {
  if (!rows.length) return "";
  const ranges = [];
  let start = rows[0];
  let prev = rows[0];
  for (let index = 1; index <= rows.length; index++) {
    const value = rows[index];
    if (value === prev + 1) {
      prev = value;
      continue;
    }
    ranges.push(start === prev ? String(start) : `${start}–${prev}`);
    start = value;
    prev = value;
  }
  return ranges.join(", ");
}

/** Explicit alignment wins; otherwise numbers go right and chips center. */
export function alignStyle(col) {
  const fallback = col.type === "number" ? "right" : "left";
  const align = col.align || (col.viz === "chip" ? "center" : fallback);
  return { textAlign: align };
}
