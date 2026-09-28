import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { SeriesIndexRecord } from '../types/webData'
import { clearSeriesCache, loadBootstrap, loadSeriesDetail, loadSources, validateManifest, validateSeriesDetail } from './client'

function fileJson(pathname: string): unknown {
  const marker = '/data/'
  const offset = pathname.lastIndexOf(marker)
  const relative = offset >= 0 ? pathname.slice(offset + marker.length) : pathname
  return JSON.parse(readFileSync(resolve(process.cwd(), 'data/web', relative), 'utf8')) as unknown
}

function okResponse(payload: unknown): Response {
  return { ok: true, status: 200, json: async () => payload } as Response
}

afterEach(() => {
  vi.unstubAllGlobals()
  clearSeriesCache()
})

describe('public-data client', () => {
  it('loads only shared bootstrap resources through the bootstrap entry point', async () => {
    const paths: string[] = []
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => {
      const pathname = new URL(String(input)).pathname
      paths.push(pathname)
      return okResponse(fileJson(pathname))
    }))
    const data = await loadBootstrap()
    expect(data.series).toHaveLength(9)
    expect(paths).toHaveLength(5)
    expect(paths.some((path) => path.includes('/series/'))).toBe(false)
    expect(paths.some((path) => path.endsWith('/sources.json'))).toBe(false)
  })

  it('loads the source registry separately on demand', async () => {
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => okResponse(fileJson(new URL(String(input)).pathname)))
    vi.stubGlobal('fetch', fetchMock)
    const loaded = await loadSources()
    expect(loaded).toHaveLength(42)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('lazy-loads one selected series detail', async () => {
    const record = fileJson('series_index.json') as SeriesIndexRecord[]
    vi.stubGlobal('fetch', vi.fn(async (input: RequestInfo | URL) => okResponse(fileJson(new URL(String(input)).pathname))))
    const loaded = await loadSeriesDetail(record[0]!)
    expect(loaded.series_id).toBe(record[0]!.series_id)
  })

  it('caches a series request deterministically in memory', async () => {
    const record = (fileJson('series_index.json') as SeriesIndexRecord[])[0]!
    const fetchMock = vi.fn(async (input: RequestInfo | URL) => okResponse(fileJson(new URL(String(input)).pathname)))
    vi.stubGlobal('fetch', fetchMock)
    await loadSeriesDetail(record)
    await loadSeriesDetail(record)
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('returns a controlled error for a missing series request', async () => {
    const record = (fileJson('series_index.json') as SeriesIndexRecord[])[0]!
    vi.stubGlobal('fetch', vi.fn(async () => ({ ok: false, status: 404, json: async () => ({}) }) as Response))
    await expect(loadSeriesDetail(record)).rejects.toThrow('HTTP 404')
  })

  it('rejects a detail with the wrong identity', () => {
    const payload = fileJson('series/series_nikke.json')
    expect(() => validateSeriesDetail(payload, 'series_wrong')).toThrow('runtime validation')
  })

  it('rejects a manifest with changed frozen counts', () => {
    const payload = { ...(fileJson('manifest.json') as object), observation_count: 0 }
    expect(() => validateManifest(payload)).toThrow('frozen corpus')
  })
})
