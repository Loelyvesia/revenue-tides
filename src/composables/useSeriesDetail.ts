import { ref, type Ref } from 'vue'
import { loadSeriesDetail } from '../data/client'
import type { LoadState, SeriesDetail, SeriesIndexRecord } from '../types/webData'

export interface SeriesDetailLoader {
  detail: Ref<SeriesDetail | null>
  state: Ref<LoadState>
  error: Ref<string | null>
  load: (record: SeriesIndexRecord, force?: boolean) => Promise<void>
}

export function useSeriesDetail(): SeriesDetailLoader {
  const detail = ref<SeriesDetail | null>(null)
  const state = ref<LoadState>('idle')
  const error = ref<string | null>(null)
  let requestToken = 0

  async function load(record: SeriesIndexRecord, force = false): Promise<void> {
    const token = ++requestToken
    state.value = 'loading'
    error.value = null
    try {
      const loaded = await loadSeriesDetail(record, force)
      if (token !== requestToken) return
      detail.value = loaded
      state.value = 'ready'
    } catch (reason) {
      if (token !== requestToken) return
      detail.value = null
      error.value = reason instanceof Error ? reason.message : 'Unknown series loading error'
      state.value = 'error'
    }
  }

  return { detail, state, error, load }
}
