import type {
  BootstrapData,
  Caveat,
  Finding,
  ProjectMetadata,
  SeriesDetail,
  SeriesIndexRecord,
  SourceRecord,
  WebManifest,
} from '../types/webData'

const WEB_DATA_VERSION = 'revenue-tides-webdata-1.0.0'
const dataBase = new URL('data/', new URL(import.meta.env.BASE_URL, window.location.href))
const seriesCache = new Map<string, Promise<SeriesDetail>>()
let sourceCache: Promise<SourceRecord[]> | null = null

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

async function fetchJson(path: string): Promise<unknown> {
  const response = await fetch(new URL(path, dataBase))
  if (!response.ok) throw new Error(`HTTP ${response.status} for ${path}`)
  return response.json() as Promise<unknown>
}

function requireRecord(value: unknown, label: string): Record<string, unknown> {
  if (!isRecord(value)) throw new Error(`${label} is not an object`)
  return value
}

function requireArray(value: unknown, label: string): unknown[] {
  if (!Array.isArray(value)) throw new Error(`${label} is not an array`)
  return value
}

export function validateManifest(value: unknown): WebManifest {
  const record = requireRecord(value, 'manifest')
  if (record.webdata_version !== WEB_DATA_VERSION) throw new Error('Unexpected web-data version')
  if (record.series_count !== 9 || record.observation_count !== 75 || record.finding_count !== 6) {
    throw new Error('Public manifest counts do not match the frozen corpus')
  }
  return record as unknown as WebManifest
}

export function validateSeriesIndex(value: unknown): SeriesIndexRecord[] {
  const rows = requireArray(value, 'series index')
  if (rows.length !== 9 || rows.some((row) => !isRecord(row) || typeof row.series_id !== 'string')) {
    throw new Error('Series index failed runtime validation')
  }
  return rows as SeriesIndexRecord[]
}

export function validateFindings(value: unknown): Finding[] {
  const rows = requireArray(value, 'findings')
  if (rows.length !== 6 || rows.some((row) => !isRecord(row) || typeof row.finding_id !== 'string')) {
    throw new Error('Findings failed runtime validation')
  }
  return rows as Finding[]
}

export function validateSeriesDetail(value: unknown, expectedId: string): SeriesDetail {
  const record = requireRecord(value, 'series detail')
  if (record.series_id !== expectedId || !Array.isArray(record.observations) || !Array.isArray(record.metric_versions)) {
    throw new Error(`Series detail failed runtime validation: ${expectedId}`)
  }
  return record as unknown as SeriesDetail
}

export async function loadBootstrap(): Promise<BootstrapData> {
  const [manifestRaw, projectRaw, seriesRaw, findingsRaw, caveatsRaw] = await Promise.all([
    fetchJson('manifest.json'),
    fetchJson('project.json'),
    fetchJson('series_index.json'),
    fetchJson('findings.json'),
    fetchJson('caveats.json'),
  ])
  const manifest = validateManifest(manifestRaw)
  const project = requireRecord(projectRaw, 'project') as unknown as ProjectMetadata
  const series = validateSeriesIndex(seriesRaw)
  const findings = validateFindings(findingsRaw)
  const caveats = requireArray(caveatsRaw, 'caveats') as Caveat[]
  return { manifest, project, series, findings, caveats }
}

export function loadSources(force = false): Promise<SourceRecord[]> {
  if (force) sourceCache = null
  if (sourceCache) return sourceCache
  sourceCache = fetchJson('sources.json').then((value) => requireArray(value, 'sources') as SourceRecord[])
  sourceCache.catch(() => { sourceCache = null })
  return sourceCache
}

export function loadSeriesDetail(record: SeriesIndexRecord, force = false): Promise<SeriesDetail> {
  if (force) seriesCache.delete(record.series_id)
  const cached = seriesCache.get(record.series_id)
  if (cached) return cached
  const promise = fetchJson(record.detail_path).then((value) => validateSeriesDetail(value, record.series_id))
  seriesCache.set(record.series_id, promise)
  promise.catch(() => seriesCache.delete(record.series_id))
  return promise
}

export function clearSeriesCache(): void {
  seriesCache.clear()
  sourceCache = null
}
