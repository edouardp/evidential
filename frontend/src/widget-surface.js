// The host owns placement and theme signals; the widget owns its CSS cascade.
export function widgetSurface(el, css, model) {
  const shadow = el.shadowRoot || el.attachShadow({mode: "open"});
  const style = el.ownerDocument.createElement("style");
  style.textContent = `:host { display: block; min-width: 0; }
    *, *::before, *::after { box-sizing: border-box; }
    table { font: inherit; color: inherit; }
    .evidential-widget > :is(.et-root, .edg-root) { font-family: var(--et-font, Arial, sans-serif);
      font-style: normal; font-weight: normal; letter-spacing: normal;
      text-transform: none; text-indent: 0; text-align: start; }
    ${css}`;
  const mount = el.ownerDocument.createElement("div");
  mount.className = "evidential-widget";
  const custom = el.ownerDocument.createElement("style");
  const update = () => { custom.textContent = model?.get("options")?.css || ""; };
  update();
  model?.on("change:options", update);
  shadow.append(style, custom, mount);
  return {mount, destroy() { model?.off("change:options", update); mount.remove(); custom.remove(); style.remove(); }};
}
