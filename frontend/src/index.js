/* global EVIDENTIAL_TABLE_CSS */
import {render} from "./table.js";
import {widgetSurface} from "./widget-surface.js";

export default {
  render({el, model}) {
    const surface = widgetSurface(el, EVIDENTIAL_TABLE_CSS, model);
    const dispose = render({el, model, container: surface.mount});
    return () => { dispose(); surface.destroy(); };
  },
};
