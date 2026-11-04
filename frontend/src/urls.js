const navigationProtocols = new Set(["http:", "https:", "mailto:", "tel:"]);

/** Validate using the browser's URL parser, including whitespace normalization. */
export function navigationUrl(value, base = globalThis.document?.baseURI) {
  if (value == null || value === "") return null;
  const text = String(value).trim();
  if (!text) return null;
  try {
    const origin = base && /^https?:/i.test(base) ? base : "https://evidential.invalid/";
    return navigationProtocols.has(new URL(text, origin).protocol) ? text : null;
  } catch {
    return null;
  }
}
