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
