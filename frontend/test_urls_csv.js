import {test} from "node:test";
import assert from "node:assert/strict";
import {navigationUrl} from "./src/urls.js";
import {csvField, serializeCsv} from "./src/csv.js";

test("safe navigation preserves web, relative, anchor, mail and telephone targets", () => {
  for (const value of ["https://example.com", "http://example.com", "/details/1", "../report", "#note", "//example.com", "mailto:a@example.com", "tel:+1234"])
    assert.equal(navigationUrl(value), value);
  assert.equal(navigationUrl("  /details  "), "/details");
});

test("executable and malformed URLs are rejected after browser normalization", () => {
  for (const value of [null, "", " ", "javascript:alert(1)", "java\nscript:alert(1)", "JaVa\tScRiPt:alert(1)",
    "data:text/html,<script>alert(1)</script>", "vbscript:bad", "file:///tmp/private", "http://["])
    assert.equal(navigationUrl(value), null, String(value));
});

test("CSV quotes CR, LF, CRLF, commas and quotes while preserving raw values", () => {
  for (const text of ["one\rtwo", "one\ntwo", "one\r\ntwo", "one,two", 'one"two'])
    assert.equal(csvField(text), '"' + text.replaceAll('"', '""') + '"');
  assert.equal(serializeCsv([{name: "value"}], [{value: "one\rtwo"}, {value: null}, {value: 0}]), 'Value\n"one\rtwo"\n\n0');
  assert.equal(csvField({a: 1}), '"{""a"":1}"');
});
