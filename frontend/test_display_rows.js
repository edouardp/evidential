import { test } from "node:test";
import assert from "node:assert/strict";
import { JSDOM } from "jsdom";
import { renderAnnotation } from "./src/display-rows.js";

const dom = new JSDOM("<body></body>");
global.document = dom.window.document;
global.Node = dom.window.Node;
const columns = [{name: "name"}, {name: "sales", type: "number"}];
const context = () => ({rowNumbers: true, subcolumns: new Map(), shadingCounter: {value: 0}});
const heading = {kind: "section", id: "north", depth: 1, label: "North", align: "left", cells: {}, style: {}, rule: "below"};

test("plain and continuation headings retain a full-width cell with an independently pinnable label", () => {
  for (const continuation of [false, true]) {
    const row = renderAnnotation({...heading, continuation}, columns, context(), {link: "url", section_indent: 1});
    assert.equal(row.cells.length, 1);
    assert.equal(row.cells[0].colSpan, 4);
    assert.equal(row.querySelector(".et-display-label").textContent, "North");
    assert.equal(row.cells[0].style.paddingLeft, "calc(1.25rem)");
    assert.equal(row.classList.contains("et-row-continuation"), continuation);
  }
});

test("annotations with cells index the row-number spacer like regular data cells", () => {
  for (const kind of ["section", "summary", "grand_summary"]) {
    const row = renderAnnotation({...heading, kind, cells: {sales: {value: 25}}}, columns, context(), {});
    assert.deepEqual([...row.cells].map(cell => cell.dataset.columnIndex), ["0", "1", "2"]);
    assert.equal(row.cells[0].textContent, "");
    assert.equal(row.cells[1].textContent, "North");
    assert.equal(row.cells[2].textContent, "25.0");
  }
});

test("section toggles expose state, escape labels and do not bubble into row selection", () => {
  const keys = [];
  const row = renderAnnotation({...heading, label: "<script>North</script>", collapsible: true,
    collapsed: true, groupKey: '["North"]'}, columns, {...context(), toggleSection: key => keys.push(key)}, {});
  let selected = 0;
  row.addEventListener("click", () => selected++);
  const button = row.querySelector("button");
  assert.equal(button.getAttribute("aria-expanded"), "false");
  assert.equal(button.getAttribute("aria-label"), "Toggle section <script>North</script>");
  assert.equal(row.querySelector("script"), null);
  button.click();
  assert.deepEqual(keys, ['["North"]']);
  assert.equal(selected, 0);
});

test("a hidden label column falls back to a visible column so closed totals remain toggleable", () => {
  const row = renderAnnotation({...heading, collapsible: true, labelColumn: "hidden",
    cells: {sales: {value: 25}}}, columns, context(), {});
  assert.ok(row.cells[1].querySelector("button"));
});
