/**
 * anchorStore.ts - 国证A股指数五年之锚状态管理
 *
 * 功能说明：
 * 本Store负责管理"五年之锚"页面的所有数据状态，包括：
 * - 图表数据的获取和管理
 * - 时间范围选择状态（1年/3年/5年/全部/自定义）
 * - 自定义日期范围
 * - 加载状态和错误信息
 *
 * 主要API：
 * - anchorApi.getChartData: 获取指定时间范围的图表数据
 * - anchorApi.refreshData: 刷新数据缓存
 *
 * State状态：
 * - data: 图表数据对象
 * - loading: 加载状态标志
 * - error: 错误信息
 * - selectedRange: 当前选择的时间范围
 * - customStartDate/customEndDate: 自定义日期范围
 * - lastUpdate: 最后更新时间
 *
 * Getters：
 * - isLoading: 是否正在加载
 * - hasError: 是否有错误
 * - chartData: 图表数据的别名
 */

import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { anchorApi } from '@/api/anchor'
import type { ChartData, TimeRangeOption } from '@/types/anchor'

export const useAnchorStore = defineStore('anchor', () => {
  // State: 状态定义

  /** 图表数据对象，包含主图、RSI、回撤等数据 */
  const data = ref<ChartData | null>(null)

  /** 加载状态：请求数据时为true */
  const loading = ref(false)

  /** 错误信息：请求失败时存储错误消息 */
  const error = ref<string | null>(null)

  /** 当前选择的时间范围选项，默认为'all' */
  const selectedRange = ref<TimeRangeOption>('all')

  /** 自定义日期范围：起始日期 */
  const customStartDate = ref<string | null>(null)

  /** 自定义日期范围：结束日期 */
  const customEndDate = ref<string | null>(null)

  /** 最后更新时间戳 */
  const lastUpdate = ref<string | null>(null)

  // Getters: 计算属性

  /** 是否正在加载的别名 */
  const isLoading = computed(() => loading.value)

  /** 是否有错误信息 */
  const hasError = computed(() => error.value !== null)

  /** 图表数据的别名，方便访问 */
  const chartData = computed(() => data.value)

  // Actions: 操作方法

  /**
   * fetchData - 获取图表数据
   * @param range: 时间范围选项，默认为当前选择的范围
   *
   * 执行流程：
   * 1. 设置加载状态为true，清空错误信息
   * 2. 计算日期范围（根据range参数）
   * 3. 调用API获取图表数据
   * 4. 更新data和lastUpdate
   * 5. 更新selectedRange
   * 6. 捕获错误并显示
   * 7. 最后设置加载状态为false
   */
  async function fetchData(range: TimeRangeOption = selectedRange.value) {
    loading.value = true
    error.value = null

    try {
      const { startDate, endDate } = calculateDateRange(range)
      const response = await anchorApi.getChartData('sz.399317', startDate, endDate)
      data.value = response
      lastUpdate.value = response.last_update
      selectedRange.value = range
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取数据失败'
      console.error('获取图表数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * refreshData - 刷新图表数据
   *
   * 执行流程：
   * 1. 设置加载状态为true，清空错误信息
   * 2. 调用API刷新数据缓存
   * 3. 重新获取最新图表数据
   * 4. 捕获错误并显示
   * 5. 最后设置加载状态为false
   */
  async function refreshData() {
    loading.value = true
    error.value = null

    try {
      await anchorApi.refreshData('sz.399317')
      await fetchData(selectedRange.value)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '刷新数据失败'
      console.error('刷新数据失败:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * setCustomDateRange - 设置自定义日期范围
   * @param start: 起始日期字符串，null表示不清除
   * @param end: 结束日期字符串，null表示不清除
   *
   * 功能：更新自定义日期范围，如有值则自动切换到custom模式
   */
  function setCustomDateRange(start: string | null, end: string | null) {
    customStartDate.value = start
    customEndDate.value = end
    if (start || end) {
      selectedRange.value = 'custom'
    }
  }

  /**
   * calculateDateRange - 计算日期范围
   * @param range: 时间范围选项
   * @returns: 包含startDate和endDate的对象
   *
   * 日期计算逻辑：
   * - '5y': 当前日期往前推5年
   * - '3y': 当前日期往前推3年
   * - '1y': 当前日期往前推1年
   * - 'custom': 使用customStartDate和customEndDate
   * - 'all': startDate为null（获取全部历史数据）
   */
  function calculateDateRange(range: TimeRangeOption): { startDate: string | null; endDate: string | null } {
    const now = new Date()
    const endDate = now.toISOString().split('T')[0]
    let startDate: string | null = null

    switch (range) {
      case '5y':
        startDate = new Date(now.getFullYear() - 5, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case '3y':
        startDate = new Date(now.getFullYear() - 3, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case '1y':
        startDate = new Date(now.getFullYear() - 1, now.getMonth(), now.getDate()).toISOString().split('T')[0]
        break
      case 'custom':
        startDate = customStartDate.value
        break
      case 'all':
      default:
        startDate = null
    }

    return { startDate, endDate }
  }

  // 暴露状态和方法供组件使用
  return {
    data,
    loading,
    error,
    selectedRange,
    customStartDate,
    customEndDate,
    lastUpdate,
    isLoading,
    hasError,
    chartData,
    fetchData,
    refreshData,
    setCustomDateRange,
    calculateDateRange
  }
})
