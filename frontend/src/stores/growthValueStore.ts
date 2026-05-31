/**
 * growthValueStore.ts - 成长100/价值100风格轮动分析状态管理
 *
 * 本Store负责管理"成长价值"页面的所有数据状态。
 * 该页面对比分析成长100与价值100的相对表现。
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { growthValueApi } from '@/api/growthValue'
import type { GrowthValueData } from '@/types/growthValue'
import type { TimeRangeOption } from '@/types/anchor'

export const useGrowthValueStore = defineStore('growthValue', () => {
  const data = ref<GrowthValueData | null>(null)
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
      const res = await growthValueApi.getData(start || undefined, end || undefined)
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
      await growthValueApi.refreshData()
      const { start, end } = calculateDateRange(selectedRange.value)
      const res = await growthValueApi.getData(start || undefined, end || undefined)
      data.value = res
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取数据失败'
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, selectedRange, customStartDate, customEndDate, fetchData, refreshData }
})
