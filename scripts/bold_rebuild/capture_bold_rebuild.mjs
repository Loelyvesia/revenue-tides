import { spawn } from 'node:child_process'
import { mkdir, mkdtemp, rm, writeFile } from 'node:fs/promises'
import { tmpdir } from 'node:os'
import path from 'node:path'

const args = Object.fromEntries(process.argv.slice(2).map((item) => { const [key, ...rest] = item.replace(/^--/, '').split('='); return [key, rest.join('=')] }))
const binary = args.binary
const browserName = args.browser || 'Chromium'
const url = args.url || 'http://127.0.0.1:4173/'
const output = path.resolve(args.output || `research/bold-rebuild/${browserName.toLowerCase()}_qa.json`)
const screenshots = path.resolve(args.screenshots || 'research/bold-rebuild/screenshots')
const capture = args.capture === 'true'
const finalReview = args['final-review'] === 'true'
const port = Number(args.port || 9444)
if (!binary) throw new Error('--binary is required')
await mkdir(path.dirname(output), { recursive: true })
await mkdir(screenshots, { recursive: true })
const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms))

class CDP {
  constructor(ws) { this.id = 0; this.pending = new Map(); this.listeners = new Map(); this.ws = new WebSocket(ws) }
  async connect() { await new Promise((resolve, reject) => { this.ws.addEventListener('open', resolve, { once: true }); this.ws.addEventListener('error', reject, { once: true }) }); this.ws.addEventListener('message', (event) => { const message = JSON.parse(event.data); if (message.id) { const pending = this.pending.get(message.id); if (!pending) return; this.pending.delete(message.id); message.error ? pending.reject(new Error(message.error.message)) : pending.resolve(message.result) } else for (const listener of this.listeners.get(message.method) || []) listener(message.params || {}) }) }
  send(method, params = {}) { const id = ++this.id; this.ws.send(JSON.stringify({ id, method, params })); return new Promise((resolve, reject) => this.pending.set(id, { resolve, reject })) }
  on(method, callback) { this.listeners.set(method, [...(this.listeners.get(method) || []), callback]) }
  close() { this.ws.close() }
}

const profile = await mkdtemp(path.join(tmpdir(), 'revenue-tides-ui2-'))
const child = spawn(binary, ['--headless=new', `--remote-debugging-port=${port}`, `--user-data-dir=${profile}`, '--no-first-run', '--disable-background-networking', '--disable-extensions', '--window-size=1440,900', 'about:blank'], { stdio: 'ignore' })
let client
const results = { browser: browserName, url, checks: [], viewports: [], console: { errors: [], warnings: [], exceptions: [] }, network_errors: [], screenshots: [] }
const check = (id, pass, detail = '') => results.checks.push({ id, status: pass ? 'PASS' : 'FAIL', detail })
try {
  let ws
  for (let i = 0; i < 100; i += 1) { try { const targets = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json(); ws = targets.find((item) => item.type === 'page')?.webSocketDebuggerUrl; if (ws) break } catch {} await sleep(100) }
  if (!ws) throw new Error('CDP unavailable')
  client = new CDP(ws); await client.connect()
  client.on('Runtime.consoleAPICalled', ({ type, args: values }) => { const text = values.map((value) => value.value ?? value.description ?? '').join(' '); if (type === 'error') results.console.errors.push(text); if (type === 'warning') results.console.warnings.push(text) })
  client.on('Runtime.exceptionThrown', ({ exceptionDetails }) => results.console.exceptions.push(exceptionDetails.text || exceptionDetails.exception?.description || 'exception'))
  client.on('Network.responseReceived', ({ response }) => { if (response.status >= 400 && response.url.startsWith(url)) results.network_errors.push({ url: response.url, status: response.status }) })
  await Promise.all([client.send('Page.enable'), client.send('Runtime.enable'), client.send('Network.enable')])
  const evaluate = async (expression) => { const out = await client.send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true, userGesture: true }); if (out.exceptionDetails) throw new Error(out.exceptionDetails.text); return out.result.value }
  const waitFor = async (expression, timeout = 12000) => { const end = Date.now() + timeout; while (Date.now() < end) { try { if (await evaluate(expression)) return } catch {} await sleep(100) } throw new Error(`timeout: ${expression}`) }
  const viewport = async (width, height, mobile = false) => { await client.send('Emulation.setDeviceMetricsOverride', { width, height, screenWidth: width, screenHeight: height, deviceScaleFactor: 1, mobile }); await sleep(100) }
  const scroll = async (selector, offset = 0) => { await evaluate(`(() => { const n=document.querySelector(${JSON.stringify(selector)}); if(!n)return false; document.documentElement.style.scrollBehavior='auto'; window.scrollTo(0,n.getBoundingClientRect().top+scrollY+${offset}); return true })()`); await sleep(500) }
  const shot = async (name, selector, offset = 0) => { if (!capture) return; await scroll(selector, offset); if(finalReview) await sleep(1300); const image = await client.send('Page.captureScreenshot', { format: 'webp', quality: 84, fromSurface: true, captureBeyondViewport: false }); const file = path.join(screenshots, `${name}.webp`); await writeFile(file, Buffer.from(image.data, 'base64')); results.screenshots.push(file.replaceAll('\\','/')) }
  const select = async (id, value) => { await evaluate(`(() => { const n=document.querySelector(${JSON.stringify(id)}); n.value=${JSON.stringify(value)}; n.dispatchEvent(new Event('change',{bubbles:true})); return true })()`); await sleep(500) }

  await viewport(1440, 900); await client.send('Page.navigate', { url }); await waitFor(`document.readyState==='complete' && document.querySelector('#opening') && document.querySelector('#prism-series')`); await sleep(1650)
  check('loads', (await evaluate(`document.querySelector('#opening').innerText.includes('付费潮汐')`)), 'hero title')
  check('four_acts', (await evaluate(`['measurement','prism','headline-findings','observatory'].every(id=>document.getElementById(id))`)), 'four act anchors')
  check('six_findings', (await evaluate(`document.querySelectorAll('[id^="finding-F"]').length`)) === 6, 'F1-F6')
  check('nine_series', (await evaluate(`document.querySelectorAll('#prism-series option').length`)) === 9, 'series selector')
  await shot('desktop-hero', '#opening')
  await shot('desktop-measurement', '#measurement')
  await scroll('#prism'); await waitFor(`document.querySelector('.quarter-prism')`); await shot('desktop-prism-direct', '#prism')
  await select('#prism-series', 'series_lineage_m'); await select('#prism-quarter', '2025Q2'); check('overlap_lanes', (await evaluate(`document.querySelectorAll('.reading-pane .metric-lane').length`)) === 2, 'same-quarter versions'); await shot('desktop-prism-overlap', '#prism')
  await shot('desktop-f1', '#finding-F1'); await shot('desktop-f2', '#finding-F2'); await shot('desktop-f4', '#finding-F4')
  await shot('desktop-observatory', '#observatory', 100); await shot('desktop-notes', '#research-notes', 80); await shot('desktop-method', '#method', 80)

  for (const [width,height] of [[1440,900],[1280,800],[1024,768],[768,1024],[390,844],[320,700]]) { await viewport(width,height,width <= 390); const audit = await evaluate(`({client:document.documentElement.clientWidth,scroll:document.documentElement.scrollWidth,overflow:Math.max(0,document.documentElement.scrollWidth-document.documentElement.clientWidth)})`); results.viewports.push({ viewport:`${width}x${height}`,...audit }); check(`overflow_${width}`, audit.overflow === 0, JSON.stringify(audit)) }
  await viewport(390,844,true); await shot('mobile-390-hero','#opening'); await shot('mobile-390-measurement','#measurement'); await select('#prism-series', 'series_nikke'); await select('#prism-quarter', '2025Q2'); await shot('mobile-390-prism','#prism'); await select('#prism-series', 'series_lineage_m'); await select('#prism-quarter', '2025Q2');
  const overlapLayout = await evaluate(`(() => { const lanes=[...document.querySelectorAll('.prism-composition.is-overlap .metric-lane>strong')]; const reading=document.querySelector('.prism-composition.is-overlap .prism-reading'); const geometry=document.querySelector('.prism-composition.is-overlap .prism-geometry'); if(lanes.length!==2||!reading||!geometry)return null; const a=lanes[0].getBoundingClientRect(),b=lanes[1].getBoundingClientRect(),r=reading.getBoundingClientRect(),g=geometry.getBoundingClientRect(); return {first:lanes[0].textContent,second:lanes[1].textContent,gap:b.left-a.right,readingBottom:r.bottom,geometryTop:g.top,viewportWidth:innerWidth} })()`)
  check('mobile_overlap_no_collision', !!overlapLayout && overlapLayout.first==='121.111' && overlapLayout.second==='127.908' && overlapLayout.gap>=4 && overlapLayout.geometryTop>=overlapLayout.readingBottom-1, JSON.stringify(overlapLayout))
  await shot('mobile-390-overlap','#prism'); await shot('mobile-390-f1','#finding-F1'); await shot('mobile-390-f2','#finding-F2'); await shot('mobile-390-f4','#finding-F4'); await shot('mobile-390-observatory','#observatory')
  await viewport(320,700,true); const controlAudit = await evaluate(`(() => { const nodes=[...document.querySelectorAll('button,select')].filter(n=>n.offsetParent!==null); const undersized=nodes.map(n=>({tag:n.tagName,class:n.className,height:n.getBoundingClientRect().height,text:(n.innerText||n.value||'').trim().slice(0,48)})).filter(n=>n.height<40); return {count:nodes.length,undersized} })()`); check('mobile_320_controls', controlAudit.undersized.length === 0, JSON.stringify(controlAudit))
  if(finalReview){
    for(const [width,height] of [[390,844],[320,700]]){
      await viewport(width,height,true); await select('#prism-series','series_lineage_m'); await select('#prism-quarter','2025Q2'); await scroll('.prism-reading');
      const labelAudit=await evaluate(`(() => { const n=document.querySelector('.prism-event-context'),s=document.querySelector('.prism-source-link--mobile-overlap');const r=n.getBoundingClientRect(),b=s.getBoundingClientRect();return {event:n.innerText,eventLeft:r.left,eventRight:r.right,eventHeight:r.height,eventOverflow:n.scrollWidth>n.clientWidth,sourceHeight:b.height,sourceDisplay:getComputedStyle(s).display,width:innerWidth} })()`);
      check('prism_event_and_source_'+width,labelAudit.eventLeft>=0&&labelAudit.eventRight<=width&&labelAudit.eventHeight>0&&!labelAudit.eventOverflow&&labelAudit.sourceHeight>=40&&labelAudit.sourceDisplay!=='none',JSON.stringify(labelAudit));
      await evaluate(`document.querySelector('.prism-source-link--mobile-overlap').click()`); await sleep(150); check('prism_source_opens_'+width,await evaluate(`!!document.querySelector('#prism .source-list a[href]')`)); await evaluate(`document.querySelector('.prism-source-link--mobile-overlap').click()`);
      await shot('mobile-'+width+'-overlap-reading','.prism-reading',-72);
      await scroll('#finding-F4'); await sleep(1400);
      const f4Audit=await evaluate(`(() => {const n=document.querySelector('.f4-tidal-sequence svg'),r=n.getBoundingClientRect();const labels=[...document.querySelectorAll('.f4-mobile-readings b')].map(n=>n.textContent);const last=[...document.querySelectorAll('.f4-key-value')].at(-1).getBoundingClientRect();return {left:r.left,right:r.right,width:innerWidth,labels,lastLeft:last.left,lastRight:last.right,opacity:getComputedStyle(document.querySelector('.f4-band')).opacity} })()`);
      check('f4_complete_sequence_'+width,f4Audit.left>=0&&f4Audit.right<=width&&f4Audit.lastLeft>=0&&f4Audit.lastRight<=width&&f4Audit.labels.join(',')==='69.2,54.9,79.5,55.0'&&Number(f4Audit.opacity)===1,JSON.stringify(f4Audit));
      await shot('mobile-'+width+'-f4','#finding-F4'); await shot('mobile-'+width+'-f2','#finding-F2');
    }
    await evaluate(`document.querySelector('.quarter-prism').focus()`); const beforeQuarter=await evaluate(`document.querySelector('#prism-quarter').value`); await client.send('Input.dispatchKeyEvent',{type:'keyDown',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39}); await client.send('Input.dispatchKeyEvent',{type:'keyUp',key:'ArrowRight',code:'ArrowRight',windowsVirtualKeyCode:39}); await sleep(200); check('prism_keyboard_arrow',await evaluate(`document.querySelector('#prism-quarter').value`)!==beforeQuarter);
  }
  await client.send('Emulation.setEmulatedMedia', { media: 'screen', features: [{ name:'prefers-reduced-motion', value:'reduce' }] }); check('reduced_motion', await evaluate(`matchMedia('(prefers-reduced-motion: reduce)').matches && getComputedStyle(document.querySelector('.fade-switch-enter-active') || document.body).scrollBehavior !== 'smooth'`), 'media honored')
  if(finalReview) check('reduced_motion_tidal_static',await evaluate(`['.f4-band','.f4-annotations','.spike-area','.refraction-body'].every(selector=>{const n=document.querySelector(selector);if(!n)return false;const s=getComputedStyle(n);return s.transitionDuration.split(',').every(v=>parseFloat(v)===0)&&s.animationName==='none'})`),'Tidal reveal and refraction transitions disabled')
  check('console_clean', results.console.errors.length === 0 && results.console.warnings.length === 0 && results.console.exceptions.length === 0, JSON.stringify(results.console))
  check('network_clean', results.network_errors.length === 0, JSON.stringify(results.network_errors))
  const version = await client.send('Browser.getVersion'); results.browser_version = version.product
} catch (error) {
  results.fatal = error instanceof Error ? error.stack : String(error)
  try { results.debug = await client?.send('Runtime.evaluate', { expression: `({url:location.href,ready:document.readyState,html:document.body?.innerHTML?.slice(0,2000),text:document.body?.innerText?.slice(0,1000)})`, returnByValue: true }).then((item) => item.result.value) } catch {}
} finally {
  results.summary = { passed: results.checks.filter((item)=>item.status==='PASS').length, failed: results.checks.filter((item)=>item.status==='FAIL').length + (results.fatal ? 1 : 0) }
  await mkdir(path.dirname(output), { recursive: true }); await mkdir(screenshots, { recursive: true }); await writeFile(output, `${JSON.stringify(results,null,2)}\n`)
  client?.close(); child.kill('SIGTERM'); await sleep(600); await rm(profile,{recursive:true,force:true,maxRetries:4,retryDelay:250}).catch(() => {})
}
console.log(JSON.stringify({ browser: results.browser, version: results.browser_version, summary: results.summary, screenshots: results.screenshots.length, fatal: results.fatal }, null, 2))
if (results.summary.failed) process.exit(1)
