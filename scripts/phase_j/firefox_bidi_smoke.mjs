import { spawn } from 'node:child_process'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'

const args = Object.fromEntries(process.argv.slice(2).map((item) => {
  const [key, ...rest] = item.replace(/^--/, '').split('=')
  return [key, rest.join('=')]
}))
const binary = args.binary
const targetUrl = args.url || 'http://127.0.0.1:4173/'
const outputPath = path.resolve(args.output || 'research/phase-j/firefox_smoke.json')
const port = Number(args.port || 9445)
if (!binary) throw new Error('--binary is required')

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

class BidiClient {
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
        if (message.type === 'error') pending.reject(new Error(`${message.error}: ${message.message}`))
        else pending.resolve(message.result)
        return
      }
      for (const listener of this.listeners.get(message.method) || []) listener(message.params || {})
    })
  }
  send(method, params = {}) {
    const id = ++this.id
    this.socket.send(JSON.stringify({ id, method, params }))
    return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject }))
  }
  on(method, callback) {
    const list = this.listeners.get(method) || []
    list.push(callback)
    this.listeners.set(method, list)
  }
  close() { this.socket.close() }
}

async function waitForEndpoint() {
  const deadline = Date.now() + 15000
  while (Date.now() < deadline) {
    try {
      const response = await fetch(`http://127.0.0.1:${port}/`)
      if (response.ok) return
    } catch {}
    await sleep(150)
  }
  throw new Error('Firefox WebDriver BiDi endpoint did not start')
}

const profile = await mkdtemp(path.join(tmpdir(), 'revenue-tides-firefox-'))
const child = spawn(binary, [
  '--new-instance', '--no-remote', '--profile', profile, '--headless',
  `--remote-debugging-port=${port}`, 'about:blank',
], { stdio: ['ignore', 'pipe', 'pipe'] })
let stderr = ''
child.stderr.on('data', (chunk) => { stderr += chunk.toString() })

const results = {
  browser: 'Firefox', url: targetUrl, checks: [], viewport_audits: [],
  console: { errors: [], warnings: [] }, network: { responses: [], errors: [] },
}
function check(id, condition, detail = '') {
  results.checks.push({ id, status: condition ? 'PASS' : 'FAIL', detail })
  if (!condition) throw new Error(`${id}: ${detail}`)
}

let client
try {
  await waitForEndpoint()
  client = new BidiClient(`ws://127.0.0.1:${port}/session`)
  await client.connect()
  const session = await client.send('session.new', { capabilities: { alwaysMatch: { acceptInsecureCerts: true } } })
  results.browser_version = session.capabilities?.browserVersion || 'unknown'
  await client.send('session.subscribe', { events: ['log.entryAdded', 'network.responseCompleted', 'network.fetchError'] })
  client.on('log.entryAdded', (entry) => {
    const record = { level: entry.level, text: entry.text || '' }
    if (entry.level === 'error') results.console.errors.push(record)
    if (entry.level === 'warn') results.console.warnings.push(record)
  })
  client.on('network.responseCompleted', (event) => {
    results.network.responses.push({ url: event.request?.url, status: event.response?.status })
  })
  client.on('network.fetchError', (event) => {
    results.network.errors.push({ url: event.request?.url, error: event.errorText })
  })

  const tree = await client.send('browsingContext.getTree', {})
  const context = tree.contexts[0].context
  await client.send('browsingContext.navigate', { context, url: targetUrl, wait: 'complete' })

  function remoteToValue(remote) {
    if (!remote || remote.type === 'undefined') return undefined
    if (remote.type === 'null') return null
    if (remote.type === 'array') return (remote.value || []).map(remoteToValue)
    if (remote.type === 'object') return Object.fromEntries((remote.value || []).map(([key, value]) => [key, remoteToValue(value)]))
    return remote.value
  }

  async function evaluate(expression) {
    const response = await client.send('script.evaluate', {
      expression, target: { context }, awaitPromise: true, resultOwnership: 'none',
    })
    if (response.type === 'exception') throw new Error(response.exceptionDetails?.text || 'Firefox evaluation failed')
    return remoteToValue(response.result)
  }
  async function waitFor(expression, timeout = 10000) {
    const deadline = Date.now() + timeout
    while (Date.now() < deadline) {
      try { if (await evaluate(expression)) return } catch {}
      await sleep(100)
    }
    throw new Error(`Timed out waiting for ${expression}`)
  }
  async function setViewport(width, height) {
    await client.send('browsingContext.setViewport', { context, viewport: { width, height }, devicePixelRatio: 1 })
    await sleep(120)
  }
  async function selectSeries(id) {
    await evaluate(`(() => { document.querySelector('#prism').scrollIntoView(); return true })()`)
    await waitFor(`Boolean(document.querySelector('.quarter-prism'))`)
    await evaluate(`(() => { const node=document.querySelector('#prism-series'); node.value=${JSON.stringify(id)}; node.dispatchEvent(new Event('change',{bubbles:true})); return true })()`)
    await sleep(50)
    await waitFor(`Boolean(document.querySelector('.quarter-prism')) && !document.querySelector('.loading-ledger')`)
  }
  async function chooseQuarter(quarter) {
    await evaluate(`(() => { const node=document.querySelector('.quarter-prism select[aria-label="直接选择季度"]'); node.value=${JSON.stringify(quarter)}; node.dispatchEvent(new Event('change',{bubbles:true})); return true })()`)
    await waitFor(`document.querySelector('.reading-pane h3')?.textContent.includes(${JSON.stringify(quarter)})`)
  }

  await waitFor(`Boolean(document.querySelector('#opening') && document.querySelector('#prism-series'))`)
  const opening = (await evaluate(`document.querySelector('#opening').innerText`)).replace(/\s+/g, ' ')
  check('production_page_loads', opening.includes('付费潮汐'), opening.slice(0, 120))
  check('opening_scope', ['9 条序列','75 个观察','4 家发行商','2024Q3—2026Q2'].every((text) => opening.includes(text)), opening)
  check('nine_series', await evaluate(`document.querySelectorAll('#prism-series option').length`) === 9, 'Nine series')
  check('six_findings', await evaluate(`document.querySelectorAll('[id^="finding-F"]').length`) === 6, 'Six Findings')

  await selectSeries('series_lineage_m')
  await chooseQuarter('2025Q2')
  const overlap = await evaluate(`({ lanes: document.querySelectorAll('.reading-pane .metric-lane').length, text: document.querySelector('.reading-pane').innerText })`)
  check('lineage_overlap', overlap.lanes === 2 && overlap.text.includes('同一季度') && overlap.text.includes('不能拼成一条连续趋势'), 'Two definitions and seam')

  await selectSeries('series_jackpot_world')
  await chooseQuarter('2024Q4')
  const derived = await evaluate(`document.querySelector('.uncertainty-block').innerText`)
  check('derived_sign_sensitive', derived.includes('兼容区间') && derived.includes('方向受取整区间影响'), derived)

  await selectSeries('series_stellar_blade')
  await chooseQuarter('2025Q2')
  const event = await evaluate(`document.querySelector('.event-rail').innerText`)
  check('event_noncausal', event.includes('同期事件') && event.toLowerCase().includes('pc'), event)

  for (const [width, height] of [[1440, 900], [1280, 800], [390, 844], [320, 700]]) {
    await setViewport(width, height)
    const audit = await evaluate(`({ width: document.documentElement.clientWidth, scrollWidth: document.documentElement.scrollWidth, overflow: Math.max(0, document.documentElement.scrollWidth-document.documentElement.clientWidth), mobile: getComputedStyle(document.querySelector('.desktop-prism')).display==='none' })`)
    results.viewport_audits.push({ requested: `${width}x${height}`, ...audit })
  }
  check('responsive_no_overflow', results.viewport_audits.every((item) => item.overflow === 0), JSON.stringify(results.viewport_audits))
  check('mobile_mode', results.viewport_audits.filter((item) => item.width <= 390).every((item) => item.mobile), 'Mobile Prism active')

  for (const [width,height] of [[390,844],[320,700]]) {
    await setViewport(width,height)
    await selectSeries('series_lineage_m'); await chooseQuarter('2025Q2')
    await evaluate(`document.querySelector('.prism-reading').scrollIntoView()`); await sleep(500)
    check('mobile_event_readable_'+width,await evaluate(`(() => {const n=document.querySelector('.prism-event-context'),r=n.getBoundingClientRect();return r.width>0&&r.left>=0&&r.right<=innerWidth&&n.scrollWidth<=n.clientWidth})()`),'Event text in document flow')
    await evaluate(`document.querySelector('.prism-source-link--mobile-overlap').click()`); await sleep(150)
    check('mobile_source_operable_'+width,await evaluate(`!!document.querySelector('#prism .source-list a[href]')`),'Source registry opens')
    await evaluate(`document.querySelector('.prism-source-link--mobile-overlap').click()`)
    await evaluate(`document.querySelector('#finding-F4').scrollIntoView()`); await sleep(1800)
    check('mobile_f4_complete_'+width,await evaluate(`(() => {const r=document.querySelector('.f4-tidal-sequence svg').getBoundingClientRect();return r.left>=0&&r.right<=innerWidth&&[...document.querySelectorAll('.f4-mobile-readings b')].map(n=>n.textContent).join(',')==='69.2,54.9,79.5,55.0'})()`),'Four anchors and second drawdown fit viewport')
  }

  await setViewport(1280, 800)
  await client.send('browsingContext.navigate', { context, url: `${targetUrl}#finding-F1`, wait: 'complete' })
  await waitFor(`Boolean(document.querySelector('#finding-F1'))`)
  await sleep(2300)
  const hash = await evaluate(`({ hash: location.hash, top: document.querySelector('#finding-F1').getBoundingClientRect().top, y: scrollY })`)
  check('hash_navigation', hash.hash === '#finding-F1' && hash.y > 0 && Math.abs(hash.top) < 120, JSON.stringify(hash))

  const external = await evaluate(`(() => { const links=[...document.querySelectorAll('a[target="_blank"]')]; return { count:links.length, safe:links.every((a)=>a.rel.includes('noopener')&&a.rel.includes('noreferrer')) } })()`)
  if (external.count > 0) check('safe_external_links', external.safe, JSON.stringify(external))

  await sleep(300)
  const httpErrors = results.network.responses.filter((item) => item.url?.startsWith(targetUrl) && item.status >= 400)
  check('network_clean', httpErrors.length === 0 && results.network.errors.length === 0, JSON.stringify({ httpErrors, fetchErrors: results.network.errors }))
  check('console_clean', results.console.errors.length === 0, JSON.stringify(results.console))
  check('warnings_reviewed', results.console.warnings.length === 0, JSON.stringify(results.console.warnings))

  results.summary = { passed: results.checks.filter((item) => item.status === 'PASS').length, failed: 0 }
  await client.send('session.end', {})
} catch (error) {
  results.fatal_error = error instanceof Error ? error.stack : String(error)
  results.summary = { passed: results.checks.filter((item) => item.status === 'PASS').length, failed: results.checks.filter((item) => item.status === 'FAIL').length + 1 }
} finally {
  results.browser_stderr_tail = stderr.split(/\r?\n/).filter(Boolean).slice(-20)
  await mkdir(path.dirname(outputPath), { recursive: true })
  await writeFile(outputPath, `${JSON.stringify(results, null, 2)}\n`, 'utf8')
  client?.close()
  child.kill('SIGTERM')
  await sleep(300)
  await rm(profile, { recursive: true, force: true })
}

if (results.fatal_error || results.summary.failed) {
  console.error(JSON.stringify({ browser: 'Firefox', summary: results.summary, fatal_error: results.fatal_error }, null, 2))
  process.exit(1)
}
console.log(JSON.stringify({ browser: 'Firefox', version: results.browser_version, summary: results.summary }, null, 2))
