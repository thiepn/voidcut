/* VOIDCUT — VD0 Visual Infrastructure runtime */
(() => {
  'use strict';

  const VERSION = 'VD0.1.0';
  const STORAGE_THEME = 'voidcut.design.theme';
  const STORAGE_TEXTURE = 'voidcut.design.texture';

  const THEMES = Object.freeze([
    Object.freeze({ id: 'paper', name: 'Paper', tone: 'light', description: 'Warm editorial stock with vermilion and cobalt ink.' }),
    Object.freeze({ id: 'carbon', name: 'Carbon', tone: 'dark', description: 'Black stock with cream, yellow and rust ink.' }),
    Object.freeze({ id: 'cobalt', name: 'Cobalt', tone: 'light', description: 'International-poster blue with yellow and red.' }),
    Object.freeze({ id: 'kelp', name: 'Kelp', tone: 'light', description: 'Deep green stock with coral and chartreuse.' }),
    Object.freeze({ id: 'plum', name: 'Plum', tone: 'light', description: 'Aubergine ground with rose and warm orange.' }),
    Object.freeze({ id: 'mono', name: 'Mono', tone: 'light', description: 'Black-and-white high-legibility pattern language.' })
  ]);

  const THEME_IDS = new Set(THEMES.map(theme => theme.id));
  const TEXTURE_MODES = new Set(['full', 'reduced', 'off']);

  const REQUIRED_TOKENS = Object.freeze([
    '--vc-bg', '--vc-bg-alt', '--vc-surface', '--vc-surface-raised', '--vc-bg-ink', '--vc-bg-ink-muted',
    '--vc-ink', '--vc-ink-secondary', '--vc-ink-muted',
    '--vc-line', '--vc-line-strong', '--vc-accent', '--vc-accent-alt',
    '--vc-arena', '--vc-arena-edge', '--vc-substrate',
    '--vc-node-a', '--vc-node-b', '--vc-node-c',
    '--vc-danger', '--vc-success', '--vc-shadow', '--vc-focus'
  ]);

  const ICONS = Object.freeze({
    play: [['path', { d: 'M8 5l10 7-10 7z' }]],
    daily: [['rect', { x: '4', y: '5', width: '16', height: '15' }], ['path', { d: 'M8 3v4M16 3v4M4 9h16M8 13h3M13 13h3M8 16h3' }]],
    mastery: [['path', { d: 'M12 3l2.8 5.7L21 9.6l-4.5 4.4 1.1 6.2L12 17.3l-5.6 2.9 1.1-6.2L3 9.6l6.2-.9z' }]],
    records: [['path', { d: 'M5 20V10M12 20V4M19 20v-7' }], ['path', { d: 'M3 20h18' }]],
    cosmetics: [['path', { d: 'M4 17l7-11 9 5-7 11z' }], ['path', { d: 'M8 15l8-5M10 18l8-5' }]],
    settings: [['circle', { cx: '12', cy: '12', r: '3' }], ['path', { d: 'M12 3v3M12 18v3M3 12h3M18 12h3M5.6 5.6l2.1 2.1M16.3 16.3l2.1 2.1M18.4 5.6l-2.1 2.1M7.7 16.3l-2.1 2.1' }]],
    sound: [['path', { d: 'M4 10v4h4l5 4V6L8 10zM16 9c1 .9 1.5 1.9 1.5 3S17 14.1 16 15M18.5 6.5c1.8 1.6 2.7 3.4 2.7 5.5s-.9 3.9-2.7 5.5' }]],
    haptics: [['rect', { x: '7', y: '3', width: '10', height: '18' }], ['path', { d: 'M4 8v8M20 8v8M2 10v4M22 10v4' }]],
    accessibility: [['circle', { cx: '12', cy: '5', r: '2' }], ['path', { d: 'M4 9h16M12 7v13M12 12l-5 8M12 12l5 8' }]],
    reset: [['path', { d: 'M5 7V3M5 3h4M5 3l3 3M5.5 8.5A7 7 0 1 0 8 5.5' }]],
    export: [['path', { d: 'M12 3v12M8 7l4-4 4 4M5 13v7h14v-7' }]],
    import: [['path', { d: 'M12 3v12M8 11l4 4 4-4M5 13v7h14v-7' }]],
    replay: [['path', { d: 'M6 8V4M6 4h4M6 4l3 3M6.2 8.4A7 7 0 1 1 5 15' }], ['path', { d: 'M10 9l6 3-6 3z' }]],
    back: [['path', { d: 'M19 12H5M10 7l-5 5 5 5' }]],
    close: [['path', { d: 'M5 5l14 14M19 5L5 19' }]]
  });

  function safeStorageGet(key) {
    try { return localStorage.getItem(key); } catch (_) { return null; }
  }

  function safeStorageSet(key, value) {
    try { localStorage.setItem(key, value); return true; } catch (_) { return false; }
  }

  function normalizeTheme(id) {
    return THEME_IDS.has(id) ? id : 'paper';
  }

  function getTheme() {
    return normalizeTheme(document.documentElement.dataset.vcTheme || 'paper');
  }

  function applyTheme(id, options = {}) {
    const theme = normalizeTheme(id);
    const previous = getTheme();
    const persist = options.persist !== false;

    document.documentElement.dataset.vcTheme = theme;
    if (persist) safeStorageSet(STORAGE_THEME, theme);

    if (previous !== theme || options.forceEvent) {
      document.dispatchEvent(new CustomEvent('voidcut:themechange', {
        detail: Object.freeze({ previous, theme })
      }));
    }
    return theme;
  }

  function cycleTheme(step = 1) {
    const index = THEMES.findIndex(theme => theme.id === getTheme());
    const next = (index + step % THEMES.length + THEMES.length) % THEMES.length;
    return applyTheme(THEMES[next].id);
  }

  function getTextureMode() {
    const value = document.documentElement.dataset.vcTexture || 'full';
    return TEXTURE_MODES.has(value) ? value : 'full';
  }

  function setTextureMode(mode, options = {}) {
    const value = TEXTURE_MODES.has(mode) ? mode : 'full';
    document.documentElement.dataset.vcTexture = value;
    if (options.persist !== false) safeStorageSet(STORAGE_TEXTURE, value);
    document.dispatchEvent(new CustomEvent('voidcut:texturechange', { detail: Object.freeze({ mode: value }) }));
    return value;
  }

  function createIcon(name, options = {}) {
    const definition = ICONS[name];
    if (!definition) throw new RangeError(`Unknown VOIDCUT icon: ${name}`);

    const ns = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(ns, 'svg');
    const size = Number.isFinite(options.size) ? Math.max(8, options.size) : 24;
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', String(size));
    svg.setAttribute('height', String(size));
    svg.setAttribute('fill', 'none');
    svg.setAttribute('stroke', 'currentColor');
    svg.setAttribute('stroke-width', '2');
    svg.setAttribute('stroke-linecap', 'square');
    svg.setAttribute('stroke-linejoin', 'miter');
    svg.setAttribute('class', ['vc-icon', options.className || ''].filter(Boolean).join(' '));

    if (options.title) {
      const title = document.createElementNS(ns, 'title');
      title.textContent = String(options.title);
      svg.appendChild(title);
      svg.setAttribute('role', 'img');
    } else {
      svg.setAttribute('aria-hidden', 'true');
      svg.setAttribute('focusable', 'false');
    }

    for (const [tag, attrs] of definition) {
      const el = document.createElementNS(ns, tag);
      for (const [key, value] of Object.entries(attrs)) el.setAttribute(key, value);
      svg.appendChild(el);
    }
    return svg;
  }

  function parseColor(value) {
    const text = String(value || '').trim();
    const hex = text.match(/^#([0-9a-f]{6})$/i);
    if (hex) {
      const n = parseInt(hex[1], 16);
      return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
    }
    const rgb = text.match(/^rgba?\(\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)\s*[, ]\s*(\d+(?:\.\d+)?)/i);
    return rgb ? rgb.slice(1, 4).map(Number) : null;
  }

  function relativeLuminance(rgb) {
    if (!rgb) return null;
    const linear = rgb.map(channel => {
      const c = channel / 255;
      return c <= .04045 ? c / 12.92 : ((c + .055) / 1.055) ** 2.4;
    });
    return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2];
  }

  function contrast(a, b) {
    const la = relativeLuminance(parseColor(a));
    const lb = relativeLuminance(parseColor(b));
    if (la == null || lb == null) return null;
    const lighter = Math.max(la, lb);
    const darker = Math.min(la, lb);
    return (lighter + .05) / (darker + .05);
  }

  function audit() {
    const style = getComputedStyle(document.documentElement);
    const missingTokens = REQUIRED_TOKENS.filter(token => !style.getPropertyValue(token).trim());
    const ink = style.getPropertyValue('--vc-ink').trim();
    const bgInk = style.getPropertyValue('--vc-bg-ink').trim();
    const bg = style.getPropertyValue('--vc-bg').trim();
    const surface = style.getPropertyValue('--vc-surface').trim();
    const bgContrast = contrast(bgInk, bg);
    const surfaceContrast = contrast(ink, surface);
    const result = {
      version: VERSION,
      theme: getTheme(),
      texture: getTextureMode(),
      missingTokens,
      contrast: {
        inkOnBackground: bgContrast == null ? null : Number(bgContrast.toFixed(2)),
        inkOnSurface: surfaceContrast == null ? null : Number(surfaceContrast.toFixed(2))
      }
    };
    result.pass = missingTokens.length === 0 &&
      (bgContrast == null || bgContrast >= 4.5) &&
      (surfaceContrast == null || surfaceContrast >= 4.5);
    return Object.freeze(result);
  }

  function initialize() {
    const storedTheme = safeStorageGet(STORAGE_THEME);
    const existingTheme = document.documentElement.dataset.vcTheme;
    applyTheme(normalizeTheme(existingTheme || storedTheme || 'paper'), { persist: false });

    const storedTexture = safeStorageGet(STORAGE_TEXTURE);
    const existingTexture = document.documentElement.dataset.vcTexture;
    setTextureMode(TEXTURE_MODES.has(existingTexture) ? existingTexture : (TEXTURE_MODES.has(storedTexture) ? storedTexture : 'full'), { persist: false });
  }

  const api = Object.freeze({
    version: VERSION,
    themes: THEMES,
    iconNames: Object.freeze(Object.keys(ICONS)),
    applyTheme,
    cycleTheme,
    getTheme,
    getTextureMode,
    setTextureMode,
    createIcon,
    audit
  });

  Object.defineProperty(window, 'VoidcutDesign', { value: api, enumerable: true, configurable: false, writable: false });
  initialize();
})();

/* v6.0.0 post-release layout hotfix 2 */
(() => {
  'use strict';
  const style = document.createElement('style');
  style.id = 'voidcut-layout-hotfix-2';
  style.textContent = `
#pauseBtn{
  left:50%!important;
  right:auto!important;
  top:0!important;
  transform:translateX(-50%)!important;
  width:44px!important;
  height:44px!important;
  min-width:44px!important;
  min-height:44px!important;
  padding:2px 0 0!important;
  display:grid!important;
  place-items:start center!important;
  isolation:isolate!important;
  background:transparent!important;
  border:0!important;
  box-shadow:none!important;
  backdrop-filter:none!important;
  color:var(--vc-on-accent)!important;
  font:800 clamp(12px,1.7vw,14px)/1 var(--vc-font-sans)!important;
}
#pauseBtn::before{
  content:""!important;
  position:absolute!important;
  z-index:-1!important;
  left:50%!important;
  top:0!important;
  transform:translateX(-50%)!important;
  box-sizing:border-box!important;
  width:clamp(30px,5.4vw,38px)!important;
  height:clamp(18px,2.8vw,24px)!important;
  background:var(--vc-accent)!important;
  border:2px solid var(--vc-line-strong)!important;
  box-shadow:2px 2px 0 var(--vc-line-strong)!important;
}
#pauseBtn:active{
  transform:translate(-50%,2px)!important;
  box-shadow:none!important;
}
#pauseBtn:active::before{
  box-shadow:none!important;
  transform:translate(calc(-50% + 1px),1px)!important;
}
#recordsPanel>.screen-nav,
#competitionPanel>.screen-nav,
#masteryPanel>.screen-nav,
#settingsPanel>.screen-nav{
  width:min(1180px,94vw)!important;
  margin-left:auto!important;
  margin-right:auto!important;
}
@media(max-width:760px){
  #recordsPanel>.screen-nav,
  #competitionPanel>.screen-nav,
  #masteryPanel>.screen-nav,
  #settingsPanel>.screen-nav{
    width:100%!important;
  }
}
#recordsPanel .screen-nav #recordsBack{
  width:auto!important;
  min-width:104px!important;
  max-width:none!important;
  margin:0!important;
}
`;
  document.head.appendChild(style);
})();
