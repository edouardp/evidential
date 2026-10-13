import {test} from "node:test";
import assert from "node:assert/strict";
import {footnoteMark} from "./src/footnotes.js";

const SYMBOLS = ["*", "†", "‡", "§", "¶", "#", "+", "◆", "◇", "△"];
const marks = (total, options = {}) => Array.from({length: total}, (_, index) => footnoteMark(index + 1, options, total));

test("footnote symbols are the default, with each single used before doubles are needed", () => {
  assert.deepEqual(marks(3), SYMBOLS.slice(0, 3));
  assert.deepEqual(marks(10), SYMBOLS);
  assert.deepEqual(marks(10, {footnote_marks: null}), SYMBOLS);
});

test("additional notes interleave doubles beside their singles, then use numbers", () => {
  assert.deepEqual(marks(11), ["*", "**", ...SYMBOLS.slice(1)]);
  assert.deepEqual(marks(12), ["*", "**", "†", "††", ...SYMBOLS.slice(2)]);
  const pairs = SYMBOLS.flatMap((symbol) => [symbol, symbol + symbol]);
  assert.deepEqual(marks(20, {footnote_marks: "symbols"}), pairs);
  assert.deepEqual(marks(23), [...pairs, "1", "2", "3"]);
  assert.equal(new Set(marks(23)).size, 23);
});

test("explicit numeric and letter schemes remain available", () => {
  assert.deepEqual(marks(3, {footnote_marks: "numbers"}), ["1", "2", "3"]);
  assert.deepEqual(marks(3, {footnote_marks: "letters"}), ["a", "b", "c"]);
});
