import {test} from "node:test";
import assert from "node:assert/strict";
import {ExpandedPages} from "./src/expanded-pages.js";

test("measured page capacities keep consecutive record offsets and restore visited pages", () => {
  const pages = new ExpandedPages();
  assert.equal(pages.project(20, 10, 0).start, 0);
  pages.project(20, 3, 0);
  assert.deepEqual(pages.move(1), {page: 1, size: 3});
  assert.equal(pages.project(20, 3, 1).start, 3);
  assert.equal(pages.project(20, 5, 1).end, 8);
  assert.deepEqual(pages.move(2), {page: 2, size: 5});
  assert.equal(pages.project(20, 5, 2).start, 8);
  assert.deepEqual(pages.move(1), {page: 1, size: 5});
  assert.equal(pages.project(20, 5, 1).start, 3);
  assert.deepEqual(pages.move(0), {page: 0, size: 3});
});

test("reflow discards stale future boundaries without moving the current start", () => {
  const pages = new ExpandedPages();
  pages.project(20, 5, 0);
  pages.move(1);
  pages.project(20, 5, 1);
  pages.move(0);
  pages.project(20, 3, 0);
  assert.equal(pages.pages.length, 1);
  pages.move(1);
  assert.equal(pages.project(20, 3, 1).start, 3);
  assert.equal(pages.project(20, 2, 1).start, 3);
});

test("last, empty and reset page navigation respects the actual data bounds", () => {
  const pages = new ExpandedPages();
  pages.project(3, 2, 0);
  pages.move(1);
  const last = pages.project(3, 2, 1);
  assert.deepEqual([last.start, last.end, last.pageCount], [2, 3, 2]);
  assert.equal(pages.move(2), null);
  assert.deepEqual(pages.move(0), {page: 0, size: 2});
  pages.reset();
  const empty = pages.project(0, 10, 100);
  assert.deepEqual([empty.page, empty.start, empty.end, empty.pageCount], [0, 0, 0, 1]);
  assert.equal(pages.move(1), null);
});
