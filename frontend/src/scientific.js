// Scientific notation stays plain text until an HTML surface renders it.
const digits = "0123456789-";
const raised = "⁰¹²³⁴⁵⁶⁷⁸⁹⁻";

export function scientificText(text) {
  const match = /^(-?\d+(?:\.\d+)?)E([+-]?\d+)$/.exec(text);
  if (!match) return text;
  const exponent = String(Number(match[2])).replace(/[\d-]/g, char => raised[digits.indexOf(char)]);
  return `${match[1]} × 10${exponent}`;
}

/** Identify only canonical numeric notation, including within prefixes/suffixes. */
export function scientificRuns(text) {
  return [...text.matchAll(/(-?\d+(?:\.\d+)?) × 10(⁻?[⁰¹²³⁴⁵⁶⁷⁸⁹]+)/g)].map(match => ({
    index: match.index, length: match[0].length, mantissa: match[1],
    exponent: match[2].replace(/[⁰¹²³⁴⁵⁶⁷⁸⁹⁻]/g, char => digits[raised.indexOf(char)]),
  }));
}
