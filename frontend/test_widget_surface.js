import {test} from 'node:test';
import assert from 'node:assert/strict';
import {JSDOM} from 'jsdom';
import {widgetSurface} from './src/widget-surface.js';

test('widget CSS and content have their own disposable shadow boundary, reusable after disposal', () => {
  const document = new JSDOM('<main><p>Host content</p></main>').window.document;
  const host = document.querySelector('main');
  const surface = widgetSurface(host, '.et-table {margin:0}');
  surface.mount.innerHTML = '<table class="et-table"><tr><td>Widget</td></tr></table>';
  assert.equal(host.querySelector('table'), null);
  assert.equal(host.shadowRoot.querySelector('td').textContent, 'Widget');
  assert.match(host.shadowRoot.querySelector('style').textContent, /\.et-table \{margin:0\}/);
  surface.destroy();
  assert.equal(host.shadowRoot.childElementCount, 0);
  assert.equal(host.textContent, 'Host content');
  const replacement = widgetSurface(host, '');
  assert.equal(host.shadowRoot.childElementCount, 3);
  replacement.destroy();
});

test('packaged entry points inject scoped styles and dispose without leaving global styles', async () => {
  const dom = new JSDOM('<main></main>', {pretendToBeVisual:true});
  globalThis.document=dom.window.document;
  globalThis.window=dom.window;
  globalThis.Node=dom.window.Node;
  globalThis.ResizeObserver=class {observe(){} unobserve(){} disconnect(){}};
  globalThis.requestAnimationFrame=cb=>setTimeout(cb,0);
  globalThis.cancelAnimationFrame=clearTimeout;
  globalThis.EVIDENTIAL_TABLE_CSS='.et-table {margin:0}';
  globalThis.EVIDENTIAL_GRID_CSS='.edg-root {color:red}';
  const {default:table} = await import('./src/index.js');
  const {default:grid} = await import('./src/dimension-grid-entry.js');
  for(const widget of [table,grid]) {
    const host=document.createElement('div'); document.querySelector('main').append(host);
    const state={rows:[{name:'A'}],columns:[{name:'name'}],options:{height:100,dimension_width:220,color:'red'},facets:[],selected:{}};
    const dispose=widget.render({el:host,model:{get:key=>state[key],on(){},off(){}}});
    assert.ok(host.shadowRoot.querySelector('style'));
    assert.equal(document.querySelectorAll('style').length,0);
    dispose();
    assert.equal(host.shadowRoot.childElementCount,0);
  }
});

test('custom notebook styles stay inside the surface and follow options updates', () => {
  const document = new JSDOM('<main></main>').window.document;
  let options={css:'.et-title {font-size:21px}'};
  const listeners=new Map();
  const model={get:()=>options,on:(name,fn)=>listeners.set(name,fn),off:name=>listeners.delete(name)};
  const surface=widgetSurface(document.querySelector('main'),'base',model);
  const styles=document.querySelector('main').shadowRoot.querySelectorAll('style');
  assert.equal(styles[1].textContent,options.css);
  options={};listeners.get('change:options')();
  assert.equal(styles[1].textContent,'');
  surface.destroy();assert.equal(listeners.size,0);
});
