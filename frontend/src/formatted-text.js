import { scientificRuns } from "./scientific.js";

/** Render formatted text safely; markup is constructed, never parsed from strings. */
export function formattedText(value) {
  const text = String(value ?? "");
  if (!text.includes(" × 10")) return text;
  const runs = scientificRuns(text);
  if (!runs.length) return text;
  const fragment = document.createDocumentFragment();
  let start = 0;
  for (const run of runs) {
    fragment.append(document.createTextNode(text.slice(start, run.index)));
    const notation = document.createElement("span");
    notation.className = "et-scientific";
    notation.setAttribute("role", "math");
    notation.setAttribute("aria-label", `${run.mantissa} times 10 to the power of ${run.exponent}`);
    notation.append(document.createTextNode(`${run.mantissa} × 10`));
    const exponent = document.createElement("sup");
    exponent.className = "et-scientific-exponent";
    exponent.textContent = run.exponent;
    notation.append(exponent);
    fragment.append(notation);
    start = run.index + run.length;
  }
  fragment.append(document.createTextNode(text.slice(start)));
  return fragment;
}
