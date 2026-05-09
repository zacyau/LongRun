import { defineStore } from 'pinia'
import { ref } from 'vue'
import { hongliApi } from '@/api/hongli'
import type { HongliData } from '@/types/hongli'
import type { TimeRangeOption } from '@/types/anchor'

export type { TimeRangeOption }

export const useHongliStore = defineStore('hongli', () => {
  const data = ref<HongliData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const selectedRange = ref<TimeRangeOption>('all')
  const customStartDate = ref<string | null>(null)
  const customEndDate = ref<string | null>(null)

  function calculateDateRange(range: TimeRangeOption): { start: string | null; end: string | null } {
    const now = new Date()
    const end = now.toISOString().slice(0, 10)
    let start: string | null = null

    switch (range) {
      case '5y':
        start = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate()).toISOString().slice(0, 10)
        break
      case '3y':
        start = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate()).toISOString().slice(0, 10)
        break
      case '1y':
        start = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()).toISOString().slice(0, 10)
        break
      case 'custom':
        start = customStartDate.value
        break
      default:
        start = null
    }
    return { start, end }
  }

  async function fetchData(range?: TimeRangeOption) {
    if (range) {
      selectedRange.value = range
    }
    loading.value = true
    error.value = null
    try {
      const { start, end } = calculateDateRange(selectedRange.value)
      const res = await hongliApi.getData(start || undefined, end || undefined)
      data.value = res
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取数据失败'
    } finally {
      loading.value = false
    }
  }

  async function refreshData() {
    loading.value = true
    error.value = null
    try {
      const { start, end } = calculateDateRange(selectedRange.value)
      const res = await hongliApi.getData(start || undefined, end || undefined)
      data.value = res
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取数据失败'
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, selectedRange, customStartDate, customEndDate, fetchData, refreshData }
})