import { test } from "node:test";
import assert from "node:assert/strict";
import { projectLayout, projectLegacy, summaryValue } from "./src/row-layout.js";
import { RowPipeline } from "./src/derived.js";

const sum = {operation: "sum", source: "value"};
const count = {operation: "count", source: null, suffix: " products", format: "num0"};
const heading = label => ({label, align: "left", cells: {value: sum, name: count}});
const summary = {label: "Subtotal", cells: {value: sum}, position: "bottom"};
const grand = {label: "Total", cells: {value: sum}};
const source = [Object.freeze({name: "A", value: 10}), Object.freeze({name: "B", value: 30}), Object.freeze({name: "C", value: 100})];
const layout = {version: 1, groups: [
  {id: "north", members: [0, 1], depth: 0, children: [], section: heading("North"), summary},
  {id: "south", members: [2], depth: 0, children: [], section: heading("South"), summary},
], grand_summary: grand};

test("pagination counts detail records and keeps summaries with their final member", () => {
  const first = projectLayout(layout, source, source, 1, 0);
  assert.equal(first.total, 3);
  assert.equal(first.pageCount, 3);
  assert.deepEqual(first.entries.map(entry => entry.kind), ["section", "data"]);
  assert.equal(first.entries[0].cells.name.value, "2 products");
  const second = projectLayout(layout, source, source, 1, 1);
  assert.deepEqual(second.entries.map(entry => entry.kind), ["section", "data", "summary"]);
  assert.equal(second.entries[0].label, "North (cont.)");
  assert.deepEqual(second.entries[0].cells, first.entries[0].cells);
  assert.deepEqual({...second.entries[0], label: first.entries[0].label, continuation: false}, first.entries[0]);
  assert.equal(second.entries[2].cells.value.value, 40);
  const last = projectLayout(layout, source, source, 1, 2);
  assert.deepEqual(last.entries.map(entry => entry.kind), ["section", "data", "summary", "grand_summary"]);
  assert.equal(last.entries[0].label, "South");
  assert.equal(last.entries.at(-1).cells.value.value, 140);
});

const collapsible = {...layout, groups: layout.groups.map(group => ({...group, section: {...group.section, collapsible: true}}))};
const closed = (keys, anchorGroup = null) => ({isCollapsed: key => keys.includes(key), anchorGroup});

test("closed groups occupy one display slot and hide details and top/bottom summaries", () => {
  for (const position of ["top", "bottom"]) {
    const plan = {...collapsible, groups: collapsible.groups.map(group => ({...group, summary: {...summary, position}}))};
    const page = projectLayout(plan, source, source, 1, 0, null, closed(["north", "south"]));
    assert.deepEqual(page.entries.map(entry => entry.kind), ["section"]);
    assert.equal(page.entries[0].collapsed, true);
    assert.equal(page.entries[0].groupKey, "north");
    assert.equal(page.entries[0].cells.value.value, 40);
    assert.equal(page.total, 2);
    assert.equal(page.matchingTotal, 3);
    assert.equal(page.unitCount, 1);
    assert.deepEqual(page.rows, []);
    const last = projectLayout(plan, source, source, 1, 1, null, closed(["north", "south"]));
    assert.deepEqual(last.entries.map(entry => entry.kind), ["section", "grand_summary"]);
    assert.equal(last.entries[1].cells.value.value, 140);
    assert.equal(projectLayout(plan, source, [], 1, 0, null, closed(["north"])).entries.length, 0);
  }
});

test("closed heading totals are opt-in, search-sensitive, and never replace explicit heading values", () => {
  const base = {...collapsible.groups[0], section: {...heading("North"), cells: {}, collapsible: true}};
  const project = section => projectLayout({groups: [{...base, section}]}, source, [source[1]], 0, 0, null, closed(["north"]));
  assert.deepEqual(project(base.section).entries[0].cells, {});
  const promoted = project({...base.section, collapsed_summary: true});
  assert.equal(promoted.entries[0].cells.value.value, 30);
  assert.equal(promoted.entries[0].label, "North");
  const explicit = project({...base.section, cells: {value: {value: "Custom"}}, collapsed_summary: true});
  assert.equal(explicit.entries[0].cells.value.value, "Custom");
  assert.equal(projectLayout({groups: [base]}, source, source, 0, 0).entries.at(-1).kind, "summary");
});

test("collapsed ancestors hide nested headings/summaries without changing child state or export order", () => {
  const plan = {...collapsible, groups: [{id: "root", members: [0, 1, 2], depth: 0,
    section: {...heading("Root"), collapsible: true}, summary, children: collapsible.groups}]};
  const folded = projectLayout(plan, source, source, 0, 0, null, closed(["root", "north"]));
  assert.deepEqual(folded.entries.map(entry => entry.kind), ["section", "grand_summary"]);
  const reopened = projectLayout(plan, source, source, 0, 0, null, closed(["north"]));
  assert.deepEqual(reopened.rows, [source[2]]);
  assert.equal(reopened.entries.find(entry => entry.groupKey === "north").collapsed, true);
  assert.deepEqual(projectLayout(plan, source, source, "all", 0).rows, source);
});

test("continuation headings can collapse back to their group slot and noncollapsible groups ignore state", () => {
  const second = projectLayout(collapsible, source, source, 1, 1);
  assert.equal(second.entries[0].continuation, true);
  const folded = projectLayout(collapsible, source, source, 1, 1, null, closed(["north"], "north"));
  assert.equal(folded.page, 0);
  assert.equal(folded.entries[0].continuation, false);
  const ordinary = projectLayout(layout, source, source, 0, 0, null, closed(["north"]));
  assert.deepEqual(ordinary.rows, source);
});

test("filtering recomputes named summaries and counts without including other summaries", () => {
  const found = projectLayout(layout, source, [source[1]], 2, 10);
  assert.equal(found.page, 0);
  assert.equal(found.total, 1);
  assert.equal(found.entries[0].cells.name.value, "1 products");
  assert.equal(found.entries[0].cells.value.value, 30);
  assert.equal(found.entries.at(-1).cells.value.value, 30);
  assert.ok(!found.entries.some(entry => entry.label === "South"));
  assert.equal(projectLayout(layout, source, [], 1, 0).entries.length, 0);
});

test("sorting changes detail order within groups, without moving records between them", () => {
  const page = projectLayout(layout, source, [source[2], source[1], source[0]], 0, 0);
  assert.deepEqual(page.entries.filter(entry => entry.kind === "data").map(entry => entry.row.name), ["B", "A", "C"]);
  assert.equal(page.entries[1].row, source[1]);
  assert.deepEqual(source[0], {name: "A", value: 10});
});

test("nested groups repeat ancestor context and emit each summary only once", () => {
  const nested = {version: 1, groups: [{id: "root", members: [0, 1, 2], depth: 0, section: heading("Root"), summary,
    children: layout.groups.map(group => ({...group, depth: 1}))}], grand_summary: grand};
  const middle = projectLayout(nested, source, source, 1, 1);
  assert.deepEqual(middle.entries.filter(entry => entry.kind === "section").map(entry => entry.label), ["Root (cont.)", "North (cont.)"]);
  assert.equal(middle.entries.filter(entry => entry.kind === "summary").length, 1);
  const last = projectLayout(nested, source, source, 1, 2);
  assert.equal(last.entries.filter(entry => entry.kind === "summary").length, 2);
  assert.equal(last.entries.filter(entry => entry.kind === "grand_summary").length, 1);
});

test("top summaries appear on the group's first page and optional annotations stay optional", () => {
  const top = {version: 1, groups: [{...layout.groups[0], summary: {...summary, position: "top"}}]};
  assert.deepEqual(projectLayout(top, source, source, 1, 0).entries.map(entry => entry.kind), ["section", "summary", "data"]);
  assert.deepEqual(projectLayout(top, source, source, 1, 1).entries.map(entry => entry.kind), ["section", "data"]);
  const plain = {version: 1, groups: [{id: "n", members: [0, 1], depth: 0, children: []}]};
  assert.ok(projectLayout(plain, source, source, 0, 0).entries.every(entry => entry.kind === "data"));
});

test("top summaries indent detail labels even without a separate section heading", () => {
  const top = {version: 1, groups: [{...layout.groups[0], section: undefined,
    summary: {...summary, position: "top"}}]};
  const page = projectLayout(top, source, source, 0, 0);
  assert.ok(page.entries.filter(entry => entry.kind === "data").every(entry => entry.inset && entry.depth === 1));
});

test("summary labels follow detail indentation at each level, with a heading-aligned override", () => {
  for (const position of ["top", "bottom"]) {
    for (const indent of [undefined, true, false]) {
      const group = {...layout.groups[0], summary: {...summary, position, indent}};
      const plan = {groups: [{...group, id: "root", children: [{...group, depth: 1}]}], grand_summary: grand};
      const page = projectLayout(plan, source, source.slice(0, 2), 0, 0);
      const summaries = page.entries.filter(entry => entry.kind === "summary");
      assert.deepEqual(summaries.map(entry => entry.depth).sort(), indent === false ? [0, 1] : [1, 2]);
      assert.equal(page.entries.find(entry => entry.kind === "data").depth, 2);
      assert.equal(page.entries.at(-1).depth, 0);
      // Pagination and continuation headings preserve the same inset.
      const boundary = projectLayout(plan, source, source.slice(0, 2), 1, position === "top" ? 0 : 1);
      assert.deepEqual(boundary.entries.filter(entry => entry.kind === "summary").map(entry => entry.depth),
        summaries.map(entry => entry.depth));
    }
  }
});

test("centered headings and footer-only groups leave summary labels aligned with unindented details", () => {
  for (const section of [undefined, {...heading("North"), align: "center"}]) {
    const plan = {groups: [{...layout.groups[0], section}]};
    const page = projectLayout(plan, source, source, 0, 0);
    assert.equal(page.entries.find(entry => entry.kind === "summary").depth, 0);
    assert.equal(page.entries.find(entry => entry.kind === "data").inset, false);
  }
});

test("label styles survive projection without changing value cells or promoted-heading styles", () => {
  const label_style = {font_style: "italic"};
  const group = {...layout.groups[0], section: {...heading("North"), cells: {}, collapsible: true, collapsed_summary: true},
    summary: {...summary, label_style}};
  const open = projectLayout({groups: [group]}, source, source, 0, 0);
  assert.deepEqual(open.entries.find(entry => entry.kind === "summary").labelStyle, label_style);
  const folded = projectLayout({groups: [group]}, source, source, 0, 0, null, closed(["north"]));
  assert.deepEqual(folded.entries[0].labelStyle, {});
  assert.equal(folded.entries[0].cells.value.value, 40);
});

test("reducers distinguish missing observations, empty sets, counts and formatted strings", () => {
  const data = [{x: null}, {x: 0}, {x: 2}, {x: 2}];
  assert.equal(summaryValue({operation: "count", source: "x"}, data), 3);
  assert.equal(summaryValue({operation: "count", source: null}, data), 4);
  assert.equal(summaryValue({operation: "median", source: "x"}, data), 2);
  assert.equal(summaryValue({operation: "count_distinct", source: "x"}, data), 2);
  assert.equal(summaryValue({operation: "sum", source: "x"}, [{x: null}]), null);
  assert.equal(summaryValue({value: "27 products", scope: "source"}, []), "27 products");
});

test("layout annotations never affect detail statistics or domains", () => {
  const pipeline = new RowPipeline();
  const result = pipeline.get({rows: source, columns: [{name: "value", type: "number", encodings: [{kind: "point", source: "value"}]}],
    options: {column_stats: true}, search: "", hidden: new Set(), sort: null, rowLayout: layout});
  assert.equal(result.stats.get("value").avg, 140 / 3);
  assert.deepEqual(result.ranges.get("value"), {min: 10, max: 100});
  assert.deepEqual(result.sorted, source);
});

test("legacy annotations are restored only for display, after filtering and sorting detail data", () => {
  const north = {render_type: "row_section", __label: "North"};
  const total = {render_type: "row_total", value: 140};
  const legacy = {legacy: [{row: north, members: [0, 1]}, {index: 0}, {index: 1}, {index: 2}, {row: total, members: [0, 1, 2]}]};
  assert.deepEqual(projectLegacy(legacy, source, [source[1]], () => false), [north, source[1], total]);
  assert.deepEqual(projectLegacy(legacy, source, [], () => false), []);
});

test("large groups project without spreading arrays into function arguments", () => {
  const data = Array.from({length: 150000}, (_, value) => ({value}));
  const large = {version: 1, groups: [{id: "all", members: data.map((_, index) => index), depth: 0, children: [], section: heading("All")}]};
  const page = projectLayout(large, data, data, 2, 100);
  assert.equal(page.entries.length, 3);
  assert.equal(page.entries[0].label, "All (cont.)");
});

test("measured pagination projects explicit detail bounds before adding annotations", () => {
  const bounds = {page: 1, pageCount: 2, start: 1, end: 3, variable: true};
  const page = projectLayout(layout, source, source, 10, 1, total => {
    assert.equal(total, 3);
    return bounds;
  });
  assert.deepEqual(page.rows, source.slice(1, 3));
  assert.equal(page.start, 1);
  assert.equal(page.variable, true);
  assert.ok(page.entries.some(entry => entry.kind === "section" && entry.continuation));
  assert.deepEqual(page.entries.filter(entry => entry.kind === "data").map(entry => entry.ordinal), [1, 2]);
  assert.equal(page.entries.at(-1).kind, "grand_summary");
});
