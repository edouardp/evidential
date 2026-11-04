import {test} from "node:test";
import assert from "node:assert/strict";
import {JSDOM} from "jsdom";
import {RowPipeline} from "./src/derived.js";
import {buildRenderPlan} from "./src/render-plan.js";
import {renderTable} from "./src/table-body.js";
import {renderHeader} from "./src/headers.js";
import {paginateRows} from "./src/rows.js";

function setup(rows, columns, options = {}) {
  const pipeline = new RowPipeline();
  const processed = pipeline.get({rows, columns, options, search: "", hidden: new Set(), sort: null});
  const visibility = pipeline.visible(processed, 0, () => false);
  return buildRenderPlan(processed, visibility, {options, pageSize: 1, pageIndex: 0, emptyRows: 3,
    paginate: (records, grouped) => paginateRows(records, 1, 0, options, grouped)});
}

test("plans distinguish empty placeholders, physical columns, and axes outside rows", () => {
  const columns = [{name: "value", type: "number", encodings: [{kind: "point", source: "value"}], scale: {axis: true}}];
  const empty = setup([], columns);
  assert.equal(empty.context.isEmpty, true);
  assert.equal(empty.context.hasTopAxis, false);
  assert.equal(empty.context.emptyRows, 3);
  const plan = setup([{value: 1}, {value: 2}], columns);
  assert.equal(plan.context.hasTopAxis, true);
  assert.equal(plan.pagination.total, 2);
  assert.equal(plan.rows.length, 1);
  assert.equal(plan.context.columns, columns);
});

test("table DOM construction keeps mutable row-writing state out of the render plan", () => {
  const dom = new JSDOM("<body></body>");
  globalThis.document = dom.window.document;
  globalThis.Node = dom.window.Node;
  const options = Object.freeze({row_numbers: true});
  const rows = [Object.freeze({value: 1})];
  const plan = setup(rows, [{name: "value", type: "number"}], options);
  Object.freeze(plan.context);
  const table = renderTable(plan.columns, plan.rows, plan.context, {
    header: renderHeader({columns: plan.columns, rowNumbers: true, options, sort: null, onSort() {}}),
    model: {}, isCollapsed: () => false, toggleGroup() {}, findSelectedRow() {},
  });
  assert.equal(table.querySelectorAll("tbody tr").length, 1);
  assert.equal(plan.context.previousDetailRow, undefined);
  assert.equal(plan.context.shadingCounter, undefined);
  assert.deepEqual(rows, [{value: 1}]);
  dom.window.close();
});
