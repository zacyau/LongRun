/**
 * hongliStore.ts - 中证红利/国证A股轮动分析状态管理
 *
 * 功能说明：
 * 本Store负责管理"轮动三棱镜"页面的所有数据状态。
 * 该页面对比分析中证红利全收益指数与国证A股全收益指数的相对表现。
 *
 * 主要API：
 * - hongliApi.getData: 获取指定日期范围的图表数据
 * - hongliApi.refreshData: 刷新数据缓存
 *
 * State状态：
 * - data: 图表数据，包含4个图表的绘制数据
 * - loading: 加载状态标志
 * - error: 错误信息
 * - selectedRange: 当前选择的时间范围
 * - customStartDate/customEndDate: 自定义日期范围
 *
 * 数据结构（HongliData）：
 * - chart1: 收益走势对比数据
 * - chart2: 红利/国证比值布林线数据
 * - chart3: 40日收益差数据
 * - chart4: RSI14动能指标数据
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { hongliApi } from '@/api/hongli'
import type { HongliData } from '@/types/hongli'
import type { TimeRangeOption } from '@/types/anchor'

export type { TimeRangeOption }

export const useHongliStore = defineStore('hongli', () => {
  // State: 状态定义

  /** 图表数据对象，包含4个图表的绘制数据 */
  const data = ref<HongliData | null>(null)

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

  /**
   * calculateDateRange - 计算日期范围
   * @param range: 时间范围选项
   * @returns: 包含start和end的对象
   *
   * 日期计算逻辑：
   * - '5y': 当前日期往前推5年
   * - '3y': 当前日期往前推3年
   * - '1y': 当前日期往前推1年
   * - 'custom': 使用customStartDate
   * - 'all'/default: start为null（获取全部历史数据）
   */
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

  /**
   * fetchData - 获取图表数据
   * @param range: 可选的时间范围选项
   *
   * 执行流程：
   * 1. 如果传入range参数，更新selectedRange
   * 2. 设置加载状态为true，清空错误信息
   * 3. 计算日期范围
   * 4. 调用API获取图表数据
   * 5. 更新data
   * 6. 捕获错误并显示
   * 7. 最后设置加载状态为false
   */
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

  /**
   * refreshData - 刷新图表数据
   *
   * 执行流程：
   * 1. 设置加载状态为true，清空错误信息
   * 2. 调用API刷新数据缓存
   * 3. 重新计算日期范围并获取最新图表数据
   * 4. 捕获错误并显示
   * 5. 最后设置加载状态为false
   */
  async function refreshData() {
    loading.value = true
    error.value = null
    try {
      await hongliApi.refreshData()
      const { start, end } = calculateDateRange(selectedRange.value)
      const res = await hongliApi.getData(start || undefined, end || undefined)
      data.value = res
    } catch (e) {
      error.value = e instanceof Error ? e.message : '获取数据失败'
    } finally {
      loading.value = false
    }
  }

  // 暴露状态和方法供组件使用
  return { data, loading, error, selectedRange, customStartDate, customEndDate, fetchData, refreshData }
})
