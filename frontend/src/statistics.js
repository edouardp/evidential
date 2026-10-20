// One summary per displayed header; sub-column selection stays local to a widget.
import {h, isStub} from "./dom.js";
import {formatTitle, formatValue} from "./format.js";

function statsLine(label, value) {
  return h("div", {class: "et-stats-line"}, [
    h("span", {class: "et-stats-label"}, `${label}: `),
    h("span", {class: "et-stats-value"}, value),
  ]);
}

function summary(col, stats, formatRanges) {
  const stat = stats.get(col.name) ||
    {min: null, max: null, avg: null, nulls: 0, distinct: 0, trues: 0, falses: 0};
  const type = String(col.type || "string").toUpperCase();
  const content = h("div", {class: "et-stats-summary"}, [
    h("div", {class: "et-stats-type"}, `${type} (nulls = ${formatValue(stat.nulls, "num0")})`),
    h("div", {class: "et-stats-name"}, `"${col.name}"`),
  ]);
  if (col.type === "number") {
    const range = formatRanges.get(col.name) ||
      (stat.min != null ? {min: stat.min, max: stat.max} : undefined);
    for (const label of ["min", "max", "avg"]) {
      const value = stat[label];
      content.append(statsLine(label, value == null ? "–" :
        formatValue(value, col.fmt, {type: "number", range, fallback: String(value)})));
    }
  } else if (col.type === "boolean") {
    content.append(statsLine("true", formatValue(stat.trues, "num0")));
    content.append(statsLine("false", formatValue(stat.falses, "num0")));
  } else {
    content.append(statsLine("distinct", formatValue(stat.distinct, "num0")));
  }
  return content;
}

/** Selections use the run's first physical column and member name, not indexes. */
export function renderStatsRow({columns, layout, stats, formatRanges, options, rowNumbers,
  selections, onLayout}) {
  const row = h("tr", {class: "et-row et-stats-row"});
  const hasFooter = layout.leaves.some((leaf) => leaf.span > 1);
  const footer = () => h("div", {class: "et-stats-footer"});
  if (rowNumbers) {
    row.append(h("td", {class: "et-td et-row-num", "data-column-index": 0},
      hasFooter ? h("div", {class: "et-stats et-stats-with-footer"}, [
        h("div", {class: "et-stats-summary"}), footer(),
      ]) : ""));
  }
  const anchors = new Set(layout.leaves.map((leaf) => columns[leaf.start].name));
  for (const key of selections.keys()) if (!anchors.has(key)) selections.delete(key);
  for (const leaf of layout.leaves) {
    const members = columns.slice(leaf.start, leaf.start + leaf.span);
    const anchor = members[0].name;
    let current = members.findIndex((col) => col.name === selections.get(anchor));
    if (current < 0) current = 0;
    const block = h("div", {class: `et-stats${hasFooter ? " et-stats-with-footer" : ""}`});
    const content = h("div", {"aria-live": leaf.span > 1 ? "polite" : null});
    block.append(content);
    const label = leaf.label || members[0].title || formatTitle(anchor);
    const cell = h("td", {
      class: `et-td et-stats-cell${isStub(options, { name: anchor }) ? " et-stub" : ""}`,
      colspan: leaf.span,
      // A spanning statistics cell cannot measure an individual column edge.
      "data-column-start": leaf.start + (rowNumbers ? 1 : 0),
    }, block);
    let button;
    if (hasFooter) {
      const bottom = footer();
      if (leaf.span > 1) {
        button = h("button", {type: "button", class: "et-stats-cycle"});
        bottom.append(button);
        button.addEventListener("click", () => {
          current = (current + 1) % members.length;
          selections.set(anchor, members[current].name);
          update();
          onLayout();
        });
      }
      block.append(bottom);
    }
    function update() {
      const col = members[current];
      if (selections.has(anchor)) selections.set(anchor, col.name);
      cell.dataset.statsColumn = col.name;
      content.replaceChildren(summary(col, stats, formatRanges));
      if (button) {
        const title = col.title || formatTitle(col.name);
        const next = members[(current + 1) % members.length];
        button.textContent = members.map((_, index) => index === current ? "●" : "○").join("");
        button.setAttribute("aria-label", `${label} statistics: ${title}, ${current + 1} of ${members.length}. Show ${next.title || formatTitle(next.name)} statistics`);
        button.title = button.getAttribute("aria-label");
      }
    }
    update();
    row.append(cell);
  }
  return row;
}
