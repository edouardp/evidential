import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { JSDOM } from "jsdom";
import { renderMarks } from "./src/visualizations.js";

const dom = new JSDOM("<!doctype html><html><head></head><body></body></html>");
global.document = dom.window.document;
global.Node = dom.window.Node;
const style = document.createElement("style");
style.textContent = readFileSync(new URL("./src/table.css", import.meta.url), "utf8");
document.head.append(style);

test("line and dot caps have explicit endpoint anchors independent of text alignment", () => {
  for (const align of ["left", "center", "right"]) {
    for (const cap of ["line", "dot"]) {
      const cell = document.createElement("td");
      cell.style.textAlign = align;
      const track = renderMarks({encodings: [{kind: "range", source: "lo", high: "hi", cap}]},
        {lo: 2, hi: 8}, {min: 0, max: 10});
      cell.append(track);
      document.body.append(cell);
      const start = dom.window.getComputedStyle(cell.querySelector(".et-mark-cap-start"));
      const end = dom.window.getComputedStyle(cell.querySelector(".et-mark-cap-end"));
      assert.equal(start.left, "0px");
      assert.equal(end.right, "0px");
      cell.remove();
    }
  }
});
