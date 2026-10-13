// Marks are assigned after collecting the distinct notes in the rendered table.
const SYMBOLS = ["*", "†", "‡", "§", "¶", "#", "+", "◆", "◇", "△"];

export function footnoteMark(index, options = {}, total = index) {
  const scheme = options.footnote_marks || "symbols";
  if (scheme === "letters") return String.fromCharCode(96 + ((index - 1) % 26) + 1);
  if (scheme === "numbers") return String(index);
  const doubled = Math.min(SYMBOLS.length, Math.max(0, total - SYMBOLS.length));
  if (index <= doubled * 2) {
    return SYMBOLS[Math.floor((index - 1) / 2)].repeat((index - 1) % 2 + 1);
  }
  if (index <= SYMBOLS.length + doubled) return SYMBOLS[index - doubled - 1];
  return String(index - SYMBOLS.length - doubled);
}

export function labelFootnotes(table, total, options) {
  for (const mark of table.querySelectorAll("sup[data-footnote-index]")) {
    mark.textContent = footnoteMark(Number(mark.dataset.footnoteIndex), options, total);
  }
}
