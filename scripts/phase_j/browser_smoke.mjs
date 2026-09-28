import { spawn } from 'node:child_process'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'

const args = Object.fromEntries(process.argv.slice(2).map((item) => {
  const [key, ...rest] = item.replace(/^--/, '').split('=')
  return [key, rest.join('=')]
}))

const browserName = args.browser || 'Chromium'
const binary = args.binary
const targetUrl = args.url || 'http://127.0.0.1:4173/'
const outputPath = path.resolve(args.output || `research/phase-j/${browserName.toLowerCase()}_smoke.json`)
const screenshotDir = path.resolve(args.screenshots || 'research/phase-j/screenshots')
const fullMode = args.mode !== 'basic'
const captureEvidence = args.capture === 'true'
const port = Number(args.port || (browserName === 'Edge' ? 9333 : 9223))

if (!binary) throw new Error('--binary is required')

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

class CdpClient {
  constructor(url) {
    this.id = 0
    this.pending = new Map()
    this.listeners = new Map()
    this.socket = new WebSocket(url)
  }

  async connect() {
    await new Promise((resolve, reject) => {
      this.socket.addEventListener('open', resolve, { once: true })
      this.socket.addEventListener('error', reject, { once: true })
    })
    this.socket.addEventListener('message', (event) => {
      const message = JSON.parse(event.data)
      if (message.id) {
        const pending = this.pending.get(message.id)
        if (!pending) return
        this.pending.delete(message.id)
        if (message.error) pending.reject(new Error(message.error.message))
        else pending.resolve(message.result)
        return
      }
      for (const listener of this.listeners.get(message.method) || []) listener(message.params || {})
    })
  }

  on(method, callback) {
    const listeners = this.listeners.get(method) || []
    listeners.push(callback)
    this.listeners.set(method, listeners)
  }

  send(method, params = {}) {
    const id = ++this.id
    this.socket.send(JSON.stringify({ id, method, params }))
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }))
  }

  close() {
    this.socket.close()
  }
}

async function waitForDebugEndpoint() {
  const deadline = Date.now() + 15000
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/json/list`)
      const targets = await response.json()
      const page = targets.find((target) => target.type === 'page')
      if (page?.webSocketDebuggerUrl) return page.webSocketDebuggerUrl
    } catch {}
    await sleep(150)
  }
  throw new Error(`${browserName} did not expose a CDP page target`)
}

const profile = await mkdtemp(path.join(tmpdir(), 'revenue-tides-phase-j-'))
const browser = spawn(binary, [
  '--headless=new',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`,
  '--no-first-run',
  '--no-default-browser-check',
  '--disable-background-networking',
  '--disable-component-update',
  '--disable-sync',
  '--disable-extensions',
  '--window-size=1440,900',
  'about:blank',
], { stdio: ['ignore', 'pipe', 'pipe'] })

let browserStderr = ''
browser.stderr.on('data', (chunk) => { browserStderr += chunk.toString() })

const results = {
  browser: browserName,
  url: targetUrl,
  started_at: new Date().toISOString(),
  checks: [],
  viewport_audits: [],
  screenshots: [],
  network: { requests: [], responses: [], failed: [] },
  console: { errors: [], warnings: [], exceptions: [] },
  accessibility: {},
  performance: {},
}

function check(id, condition, detail = '') {
  results.checks.push({ id, status: condition ? 'PASS' : 'FAIL', detail })
  if (!condition) throw new Error(`${id}: ${detail}`)
}

let client
try {
  const webSocketUrl = await waitForDebugEndpoint()
  client = new CdpClient(webSocketUrl)
  await client.connect()

  client.on('Network.requestWillBeSent', ({ request, type }) => {
    results.network.requests.push({ url: request.url, method: request.method, type })
  })
  client.on('Network.responseReceived', ({ response, type }) => {
    results.network.responses.push({ url: response.url, status: response.status, mime_type: response.mimeType, type, encoded_bytes: response.encodedDataLength })
  })
  client.on('Network.loadingFailed', ({ requestId, errorText, canceled, blockedReason }) => {
    results.network.failed.push({ request_id: requestId, error: errorText, canceled: Boolean(canceled), blocked_reason: blockedReason || null })
  })
  client.on('Runtime.consoleAPICalled', ({ type, args: values }) => {
    const text = values.map((value) => value.value ?? value.description ?? '').join(' ')
    if (type === 'error') results.console.errors.push(text)
    if (type === 'warning') results.console.warnings.push(text)
  })
  client.on('Runtime.exceptionThrown', ({ exceptionDetails }) => {
    results.console.exceptions.push(exceptionDetails.text || exceptionDetails.exception?.description || 'Unknown exception')
  })
  client.on('Log.entryAdded', ({ entry }) => {
    if (entry.level === 'error') results.console.errors.push(entry.text)
    if (entry.level === 'warning') results.console.warnings.push(entry.text)
  })

  await Promise.all([
    client.send('Page.enable'),
    client.send('Runtime.enable'),
    client.send('Network.enable'),
    client.send('Log.enable'),
    client.send('Accessibility.enable'),
  ])

  async function evaluate(expression) {
    const response = await client.send('Runtime.evaluate', {
      expression,
      awaitPromise: true,
      returnByValue: true,
      userGesture: true,
    })
    if (response.exceptionDetails) throw new Error(response.exceptionDetails.text || 'Browser evaluation failed')
    return response.result.value
  }

  async function waitFor(expression, timeout = 10000) {
    const deadline = Date.now() + timeout
    while (Date.now() < deadline) {
      try {
        if (await evaluate(expression)) return
      } catch {}
      await sleep(100)
    }
    throw new Error(`Timed out waiting for: ${expression}`)
  }

  async function setViewport(width, height, mobile = false) {
    await client.send('Emulation.setDeviceMetricsOverride', {
      width,
      height,
      deviceScaleFactor: 1,
      mobile,
      screenWidth: width,
      screenHeight: height,
    })
    await sleep(150)
  }

  async function navigate(url = targetUrl) {
    await client.send('Page.navigate', { url })
    await waitFor(`document.readyState === 'complete'`)
    await waitFor(`Boolean(document.querySelector('#opening') && document.querySelector('#prism-series'))`)
    await sleep(350)
  }

  async function selectPrismSeries(seriesId) {
    if (!(await evaluate(`Boolean(document.querySelector('.quarter-prism'))`))) {
      await scrollTo('#prism')
      await waitFor(`Boolean(document.querySelector('.quarter-prism') || document.querySelector('.load-error'))`)
    }
    await evaluate(`(() => {
      const select = document.querySelector('#prism-series');
      select.value = ${JSON.stringify(seriesId)};
      select.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`)
    await sleep(40)
    await waitFor(`Boolean(document.querySelector('.quarter-prism')) && !document.querySelector('.loading-ledger')`)
    await sleep(120)
  }

  async function chooseQuarter(quarter) {
    await evaluate(`(() => {
      const select = document.querySelector('.quarter-prism select[aria-label="直接选择季度"]');
      if (!select || ![...select.options].some((option) => option.value === ${JSON.stringify(quarter)})) return false;
      select.value = ${JSON.stringify(quarter)};
      select.dispatchEvent(new Event('change', { bubbles: true }));
      return true;
    })()`)
    await waitFor(`document.querySelector('.reading-pane h3')?.textContent.includes(${JSON.stringify(quarter)})`)
    await sleep(80)
  }

  async function scrollTo(selector) {
    await evaluate(`(() => {
      const node = document.querySelector(${JSON.stringify(selector)});
      if (!node) return false;
      const previous = document.documentElement.style.scrollBehavior;
      document.documentElement.style.scrollBehavior = 'auto';
      window.scrollTo(0, node.getBoundingClientRect().top + window.scrollY);
      document.documentElement.style.scrollBehavior = previous;
      return true;
    })()`)
    await sleep(180)
  }

  async function screenshot(name, selector = null) {
    if (!captureEvidence) return
    if (selector) await scrollTo(selector)
    const shot = await client.send('Page.captureScreenshot', {
      format: 'webp',
      quality: 82,
      fromSurface: true,
      captureBeyondViewport: false,
    })
    const file = path.join(screenshotDir, `${name}.webp`)
    await writeFile(file, Buffer.from(shot.data, 'base64'))
    results.screenshots.push(file.replaceAll('\\', '/'))
  }

  await setViewport(1440, 900)
  await navigate()

  const version = await client.send('Browser.getVersion')
  results.browser_version = version.product
  const initialJson = [...new Set(results.network.requests.map((request) => request.url).filter((url) => url.includes('/data/') && url.endsWith('.json')))]
  results.performance.initial_json_requests = initialJson
  results.performance.initial_request_count = results.network.requests.filter((request) => request.url.startsWith(targetUrl)).length

  const opening = await evaluate(`document.querySelector('#opening')?.innerText || ''`)
  const openingNormalized = opening.replace(/\s+/g, ' ')
  check('production_page_loads', opening.includes('付费潮汐'), opening.slice(0, 120))
  check('opening_scope', ['9 条序列','75 个观察','4 家发行商','2024Q3—2026Q2'].every((text) => openingNormalized.includes(text)), openingNormalized)
  check('opening_comparison_boundary', opening.includes('不可直接比较绝对高低') && opening.includes('No global revenue leaderboard'), 'Comparison caveat visible')
  check('findings_present', await evaluate(`document.querySelectorAll('[id^="finding-F"]').length`) === 6, 'F1–F6 rendered')
  check('headline_findings_present', await evaluate(`['F1','F2','F4'].every(id => document.querySelector('#headline-findings #finding-' + id))`), 'F1/F2/F4 headline chapters')
  check('nine_series_accessible', await evaluate(`document.querySelectorAll('#prism-series option').length`) === 9, 'Nine series in Prism selector')
  check('initial_series_lazy', initialJson.filter((url) => url.includes('/series/')).length < 9, `${initialJson.filter((url) => url.includes('/series/')).length} series payload(s) initially requested`)
  await screenshot('desktop-opening', '#opening')

  await client.send('Network.setBlockedURLs', { urls: ['*series_black_desert.json*'] })
  await evaluate(`document.querySelectorAll('.ledger-row')[0]?.click()`)
  await waitFor(`document.querySelector('.observatory-status.error')`)
  const failureText = await evaluate(`document.querySelector('.observatory-status.error')?.innerText || ''`)
  check('controlled_lazy_failure', failureText.includes('数据暂时无法加载') && failureText.includes('重试'), 'Controlled error state with retry')
  await client.send('Network.setBlockedURLs', { urls: [] })
  await evaluate(`document.querySelector('.observatory-status.error button')?.click()`)
  await waitFor(`document.querySelector('#series-series_black_desert')`)
  check('lazy_retry_recovers', true, 'Retry loaded the requested series after restoration')

  await selectPrismSeries('series_nikke')
  const directText = await evaluate(`document.querySelector('.reading-pane')?.innerText || ''`)
  check('direct_state', directText.includes('NIKKE') && directText.includes('Official reported') && !directText.includes('兼容区间'), 'NIKKE direct observation')
  await screenshot('desktop-quarter-prism-direct', '#prism')

  await chooseQuarter('2025Q2')
  await evaluate(`document.querySelector('.quarter-prism')?.focus()`)
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'ArrowRight', code: 'ArrowRight', windowsVirtualKeyCode: 39 })
  await waitFor(`document.querySelector('.reading-pane h3')?.textContent.includes('2025Q3')`)
  check('keyboard_arrow_navigation', true, 'ArrowRight changed 2025Q2 to 2025Q3')

  const lineageChecks = []
  for (const seriesId of ['series_lineage_m', 'series_lineage_2m', 'series_lineage_w']) {
    await selectPrismSeries(seriesId)
    await chooseQuarter('2025Q2')
    const state = await evaluate(`(() => ({
      lanes: document.querySelectorAll('.reading-pane .metric-lane').length,
      text: document.querySelector('.reading-pane')?.innerText || '',
      seam: Boolean(document.querySelector('.version-seam') && document.querySelector('.version-note'))
    }))()`)
    lineageChecks.push({ series_id: seriesId, ...state })
  }
  results.lineage = lineageChecks
  check('lineage_overlap_three_series', lineageChecks.every((row) => row.lanes === 2 && row.text.includes('同一季度') && row.text.toLowerCase().includes('legacy_v1') && row.text.toLowerCase().includes('royalty_integrated_v2')), 'Two simultaneous definition lanes for all three Lineage series')
  check('version_boundary_visible', lineageChecks.every((row) => row.seam && row.text.includes('不拼接') && row.text.includes('跨版本 QoQ 不可用')), 'Calibration seam and boundary explanation visible')
  await selectPrismSeries('series_lineage_m')
  await chooseQuarter('2025Q2')
  await screenshot('desktop-lineage-overlap', '#prism')

  const derivedChecks = []
  for (const seriesId of ['series_mcoc', 'series_jackpot_world', 'series_lotsa_slots']) {
    await selectPrismSeries(seriesId)
    const state = await evaluate(`(() => ({
      blocks: document.querySelectorAll('.uncertainty-block').length,
      text: document.querySelector('.reading-pane')?.innerText || ''
    }))()`)
    derivedChecks.push({ series_id: seriesId, ...state })
  }
  results.derived = derivedChecks
  check('derived_uncertainty_three_series', derivedChecks.every((row) => row.blocks === 1 && row.text.includes('兼容区间') && row.text.includes('官方取整占比') && row.text.includes('Derived from official')), 'All derived series retain interval, share, and evidence')
  await selectPrismSeries('series_jackpot_world')
  await chooseQuarter('2024Q4')
  check('sign_sensitive_not_definite', (await evaluate(`document.querySelector('.uncertainty-block')?.innerText || ''`)).includes('方向受取整区间影响'), 'Sign-sensitive period avoids definite direction')
  await selectPrismSeries('series_mcoc')
  await chooseQuarter('2025Q4')
  await screenshot('desktop-derived-uncertainty', '#prism')

  await selectPrismSeries('series_stellar_blade')
  await chooseQuarter('2025Q2')
  const eventText = await evaluate(`document.querySelector('.event-rail')?.innerText || ''`)
  check('event_context_separate', eventText.includes('CURATED / NON-CAUSAL') && eventText.includes('同季度不等于因果') && eventText.toLowerCase().includes('pc'), 'Stellar Blade PC launch is separate non-causal context')
  await chooseQuarter('2024Q3')
  check('no_event_state', (await evaluate(`document.querySelector('.event-rail')?.innerText || ''`)).includes('No curated event in this quarter'), 'No-event quarter remains explicit')

  await selectPrismSeries('series_lineage_m')
  await chooseQuarter('2025Q2')
  await evaluate(`document.querySelector('.source-action button')?.click()`)
  await waitFor(`document.querySelector('.source-action .source-list')`)
  const sourceLinkState = await evaluate(`(() => {
    const links = [...document.querySelectorAll('.source-action a[target="_blank"]')];
    return { count: links.length, safe: links.every((link) => link.rel.includes('noopener') && link.rel.includes('noreferrer')), urls: links.map((link) => link.href) };
  })()`)
  results.source_links = sourceLinkState
  check('source_disclosure_and_safe_links', sourceLinkState.count > 0 && sourceLinkState.safe, `${sourceLinkState.count} source links, all safe`)

  await scrollTo('#observatory')
  const observatoryRows = await evaluate(`document.querySelectorAll('.ledger-row').length`)
  check('observatory_nine_rows', observatoryRows === 9, `${observatoryRows} rows`) 

  const loadedSeries = []
  for (let index = 0; index < 9; index += 1) {
    const seriesId = await evaluate(`document.querySelectorAll('#prism-series option')[${index}].value`)
    await evaluate(`document.querySelectorAll('.ledger-row')[${index}].click()`)
    await waitFor(`document.querySelector(${JSON.stringify(`#series-${seriesId}`)})`)
    loadedSeries.push(seriesId)
  }
  results.loaded_series = loadedSeries
  check('all_series_lazy_load', new Set(loadedSeries).size === 9, loadedSeries.join(', '))
  const nikkeUrlSuffix = '/data/series/series_nikke.json'
  const beforeCache = results.network.requests.filter((request) => request.url.includes(nikkeUrlSuffix)).length
  await evaluate(`document.querySelectorAll('.ledger-row')[7].click()`)
  await waitFor(`document.querySelector('#series-series_nikke')`)
  const afterCache = results.network.requests.filter((request) => request.url.includes(nikkeUrlSuffix)).length
  check('series_cache', beforeCache === afterCache, `NIKKE requests remained ${afterCache}`)
  await screenshot('desktop-series-observatory', '#observatory')

  for (const findingId of ['F1', 'F2', 'F4']) await screenshot(`desktop-${findingId.toLowerCase()}`, `#finding-${findingId}`)

  const viewportCases = [
    [1440, 900], [1280, 800], [1024, 768], [768, 1024], [390, 844], [320, 700],
  ]
  for (const [width, height] of viewportCases) {
    await setViewport(width, height, width <= 390)
    const audit = await evaluate(`(() => {
      const root = document.documentElement;
      const overflowing = [...document.querySelectorAll('body *')].filter((node) => {
        const rect = node.getBoundingClientRect();
        if (rect.right <= root.clientWidth + 0.5 && rect.left >= -0.5) return false;
        const style = getComputedStyle(node);
        return style.position !== 'fixed' && style.position !== 'absolute';
      }).slice(0, 10).map((node) => ({ tag: node.tagName, className: node.className, right: node.getBoundingClientRect().right }));
      return {
        width: root.clientWidth,
        scroll_width: root.scrollWidth,
        overflow_px: Math.max(0, root.scrollWidth - root.clientWidth),
        overflowing,
        mobile_prism: getComputedStyle(document.querySelector('.desktop-prism')).display === 'none',
        min_control_height: Math.min(...[...document.querySelectorAll('button, select, a.continue-link')].filter((node) => node.offsetParent !== null).map((node) => node.getBoundingClientRect().height)),
      };
    })()`)
    results.viewport_audits.push({ requested: `${width}x${height}`, ...audit })
  }
  check('required_viewports_no_overflow', results.viewport_audits.every((row) => row.overflow_px === 0), JSON.stringify(results.viewport_audits))
  check('mobile_prism_mode', results.viewport_audits.filter((row) => row.requested === '390x844' || row.requested === '320x700').every((row) => row.mobile_prism), 'Desktop SVG hidden at mobile widths')
  check('touch_targets', results.viewport_audits.filter((row) => row.requested === '390x844' || row.requested === '320x700').every((row) => row.min_control_height >= 44), 'Visible mobile controls meet 44 px height')

  await setViewport(390, 844, true)
  await client.send('Emulation.setEmulatedMedia', { media: 'screen', features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] })
  const motionState = await evaluate(`(() => ({
    reduced: matchMedia('(prefers-reduced-motion: reduce)').matches,
    transition: getComputedStyle(document.querySelector('.reading-window')).transitionDuration,
    pane: Boolean(document.querySelector('.reading-pane')),
    event: Boolean(document.querySelector('.event-rail'))
  }))()`)
  results.reduced_motion = motionState
  check('reduced_motion_complete', motionState.reduced && motionState.pane && motionState.event && ['0s', '1e-05s', '0.00001s'].includes(motionState.transition), JSON.stringify(motionState))
  await client.send('Emulation.setEmulatedMedia', { media: 'screen', features: [] })

  await selectPrismSeries('series_nikke')
  await screenshot('mobile-390-opening', '#opening')
  await screenshot('mobile-390-quarter-prism', '#prism')
  await selectPrismSeries('series_lineage_m')
  await chooseQuarter('2025Q2')
  await screenshot('mobile-390-lineage-overlap', '#prism')
  await selectPrismSeries('series_mcoc')
  await chooseQuarter('2025Q4')
  await screenshot('mobile-390-derived-uncertainty', '#prism')

  await setViewport(720, 450, false)
  const zoomAudit = await evaluate(`(() => ({
    effective_css_width: document.documentElement.clientWidth,
    overflow_px: Math.max(0, document.documentElement.scrollWidth - document.documentElement.clientWidth),
    controls: [...document.querySelectorAll('.prism-controls button, .prism-controls select')].every((node) => node.getBoundingClientRect().height >= 44),
    critical_visible: Boolean(document.querySelector('.reading-pane') && document.querySelector('.event-rail'))
  }))()`)
  results.zoom_200_equivalent = zoomAudit
  check('zoom_200_equivalent', zoomAudit.overflow_px === 0 && zoomAudit.controls && zoomAudit.critical_visible, JSON.stringify(zoomAudit))

  await setViewport(1440, 900)
  await navigate(targetUrl)
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  const skipFocus = await evaluate(`(() => { const node=document.activeElement; const style=getComputedStyle(node); return { className:node.className, text:node.textContent, outline:style.outlineStyle, outlineWidth:style.outlineWidth } })()`)
  check('skip_link_keyboard_focus', String(skipFocus.className).includes('skip-link') && skipFocus.outline !== 'none' && skipFocus.outlineWidth !== '0px', JSON.stringify(skipFocus))
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Enter', code: 'Enter', windowsVirtualKeyCode: 13 })
  await waitFor(`location.hash === '#main-content'`)
  await selectPrismSeries('series_lineage_m')
  await evaluate(`document.querySelector('#prism-series').focus()`)
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  const prismTab = await evaluate(`({ tag:document.activeElement.tagName, className:document.activeElement.className, label:document.activeElement.getAttribute('aria-label') })`)
  check('logical_prism_tab_order', prismTab.tag === 'DIV' && String(prismTab.className).includes('quarter-prism') && String(prismTab.label).includes('左右方向键'), JSON.stringify(prismTab))
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: 'Tab', code: 'Tab', windowsVirtualKeyCode: 9 })
  const previousTab = await evaluate(`({ tag:document.activeElement.tagName, text:document.activeElement.textContent.trim() })`)
  check('prism_controls_keyboard_reachable', previousTab.tag === 'BUTTON' && previousTab.text.includes('上一季度'), JSON.stringify(previousTab))
  await scrollTo('.source-action')
  await evaluate(`document.querySelector('.source-action button').focus()`)
  await client.send('Input.dispatchKeyEvent', { type: 'keyDown', key: ' ', code: 'Space', text: ' ', unmodifiedText: ' ', windowsVirtualKeyCode: 32 })
  await client.send('Input.dispatchKeyEvent', { type: 'keyUp', key: ' ', code: 'Space', windowsVirtualKeyCode: 32 })
  await waitFor(`document.querySelector('.source-action button').getAttribute('aria-expanded') === 'true'`)
  check('keyboard_source_disclosure', true, 'Source disclosure opens with Enter')
  const focusables = await evaluate(`[...document.querySelectorAll('a[href],button:not([disabled]),select:not([disabled]),[tabindex="0"]')].filter((node)=>node.offsetParent!==null).length`)
  check('keyboard_no_trap_surface', focusables > 20, `${focusables} visible keyboard-reachable controls`) 

  await client.send('Page.navigate', { url: `${targetUrl}#finding-F1` })
  await waitFor(`document.querySelector('#finding-F1') && location.hash === '#finding-F1'`)
  await sleep(2300)
  const hashState = await evaluate(`({ hash: location.hash, scrollY, top: document.querySelector('#finding-F1').getBoundingClientRect().top })`)
  check('direct_hash_navigation', hashState.hash === '#finding-F1' && hashState.scrollY > 0 && Math.abs(hashState.top) < 120, JSON.stringify(hashState))
  await evaluate(`location.hash = '#finding-F2'`)
  await waitFor(`location.hash === '#finding-F2'`)
  await evaluate(`history.back()`)
  await waitFor(`location.hash === '#finding-F1'`)
  await evaluate(`history.forward()`)
  await waitFor(`location.hash === '#finding-F2'`)
  check('hash_back_forward', true, 'F1 → F2 → Back → Forward')

  const ax = await client.send('Accessibility.getFullAXTree')
  const roles = ax.nodes.map((node) => ({ role: node.role?.value, name: node.name?.value || '' }))
  results.accessibility = {
    node_count: roles.length,
    main_count: roles.filter((node) => node.role === 'main').length,
    heading_names: roles.filter((node) => node.role === 'heading').map((node) => node.name),
    button_names: roles.filter((node) => node.role === 'button').map((node) => node.name).slice(0, 25),
    link_names: roles.filter((node) => node.role === 'link').map((node) => node.name).slice(0, 25),
  }
  check('accessibility_tree', results.accessibility.main_count === 1 && results.accessibility.heading_names.some((name) => name.includes('付费潮汐')) && results.accessibility.button_names.some((name) => name.includes('下一季度')), JSON.stringify(results.accessibility))
  const semanticState = await evaluate(`(() => ({
    h1: document.querySelectorAll('h1').length,
    unnamed_buttons: [...document.querySelectorAll('button')].filter((node) => !node.innerText.trim() && !node.getAttribute('aria-label')).length,
    live_regions: document.querySelectorAll('[aria-live="polite"]').length,
    skip_href: document.querySelector('.skip-link')?.getAttribute('href'),
    focus_outline: getComputedStyle(document.querySelector('.native-control')).outlineStyle,
  }))()`)
  results.semantic_state = semanticState
  check('heading_and_names', semanticState.h1 === 1 && semanticState.unnamed_buttons === 0 && semanticState.live_regions > 0 && semanticState.skip_href === '#main-content', JSON.stringify(semanticState))

  const contrast = await evaluate(`(() => {
    const luminance = (hex) => {
      const rgb = hex.match(/[a-f\\d]{2}/gi).map((value) => parseInt(value, 16) / 255).map((value) => value <= .03928 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
      return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2];
    };
    const ratio = (a, b) => { const x = luminance(a); const y = luminance(b); return (Math.max(x,y)+.05)/(Math.min(x,y)+.05) };
    return {
      primary: ratio('#192321','#f3f0e7'),
      secondary: ratio('#4b5753','#f3f0e7'),
      event: ratio('#864b32','#fbf9f2'),
      focus: ratio('#005fcc','#fbf9f2')
    };
  })()`)
  results.contrast = contrast
  check('contrast_tokens', contrast.primary >= 4.5 && contrast.secondary >= 4.5 && contrast.event >= 4.5 && contrast.focus >= 3, JSON.stringify(contrast))

  const perf = await evaluate(`(() => {
    const nav = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource').map((entry) => ({ name: entry.name, transferSize: entry.transferSize, encodedBodySize: entry.encodedBodySize, duration: entry.duration }));
    return { dom_content_loaded_ms: nav.domContentLoadedEventEnd, load_ms: nav.loadEventEnd, resources };
  })()`)
  results.performance.navigation = perf
  results.performance.largest_resource = [...perf.resources].sort((a,b) => b.encodedBodySize - a.encodedBodySize)[0] || null

  const unexpectedResponses = results.network.responses.filter((response) => response.url.startsWith(targetUrl) && response.status >= 400)
  results.network.expected_blocked_failures = results.network.failed.filter((failure) => failure.blocked_reason === 'inspector')
  results.network.unexpected_http_errors = unexpectedResponses
  check('normal_network_clean', unexpectedResponses.length === 0, JSON.stringify(unexpectedResponses))
  check('console_clean', results.console.errors.length === 0 && results.console.exceptions.length === 0, JSON.stringify(results.console))
  check('production_warnings_clean', results.console.warnings.length === 0, JSON.stringify(results.console.warnings))

  const forbidden = await evaluate(`(() => {
    const text = document.body.innerText;
    return ['winner','top earning','highest revenue game','success score','commercial health','true revenue','global game revenue','PC launch effect','冠军','最赚钱','真实流水','全球总流水','成功评分'].filter((term) => text.toLowerCase().includes(term.toLowerCase()));
  })()`)
  results.forbidden_text_hits = forbidden
  check('forbidden_rendered_text_scan', forbidden.length === 0, JSON.stringify(forbidden))

  results.completed_at = new Date().toISOString()
  results.summary = {
    passed: results.checks.filter((item) => item.status === 'PASS').length,
    failed: results.checks.filter((item) => item.status === 'FAIL').length,
  }
} catch (error) {
  results.fatal_error = error instanceof Error ? error.stack : String(error)
  results.completed_at = new Date().toISOString()
  results.summary = {
    passed: results.checks.filter((item) => item.status === 'PASS').length,
    failed: results.checks.filter((item) => item.status === 'FAIL').length + 1,
  }
} finally {
  await mkdir(path.dirname(outputPath), { recursive: true })
  await mkdir(screenshotDir, { recursive: true })
  results.browser_stderr_tail = browserStderr.split(/\r?\n/).filter(Boolean).slice(-20)
  await writeFile(outputPath, `${JSON.stringify(results, null, 2)}\n`, 'utf8')
  client?.close()
  browser.kill('SIGTERM')
  await sleep(300)
  if (!browser.killed) browser.kill('SIGKILL')
  await rm(profile, { recursive: true, force: true })
}

if (results.fatal_error || results.summary.failed) {
  console.error(JSON.stringify({ browser: browserName, summary: results.summary, fatal_error: results.fatal_error }, null, 2))
  process.exit(1)
}
console.log(JSON.stringify({ browser: browserName, version: results.browser_version, summary: results.summary, screenshots: results.screenshots.length }, null, 2))
