/**
 * macdvStore.ts - MACD-V趋势信号查询状态管理
 *
 * 功能说明：
 * 本Store负责管理"趋势信号"页面的数据状态，
 * 提供股票MACD-V和RSI14指标的批量查询功能。
 *
 * 主要API：
 * - macdvApi.batchQuery: 批量查询多只股票的指标数据
 *
 * State状态：
 * - data: 查询结果数据
 * - loading: 加载状态标志
 * - error: 错误信息
 * - history: 历史查询记录（最多保存20条）
 *
 * 功能特点：
 * - 支持批量查询：一次输入多只股票代码
 * - 历史记录：保存最近成功的查询，支持快速复用
 * - 自动过滤：只保存成功查询的股票代码
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import { macdvApi } from '@/api/macdv'
import type { MacdvResponse } from '@/types/macdv'

export const useMacdvStore = defineStore('macdv', () => {
  // State: 状态定义

  /** 查询结果数据，包含results数组和updated_at时间戳 */
  const data = ref<MacdvResponse | null>(null)

  /** 加载状态：请求数据时为true */
  const loading = ref(false)

  /** 错误信息：请求失败时存储错误消息 */
  const error = ref<string | null>(null)

  /** 历史查询记录：保存最近成功查询的股票代码，最多20条 */
  const history = ref<string[]>([])

  /**
   * queryStocks - 批量查询股票指标
   * @param text: 用户输入的股票代码文本，支持多种分隔符
   *
   * 输入格式支持：
   * - 逗号分隔：000001, sh600519, sz399317
   * - 空格分隔：000001 sh600519 sz399317
   * - 换行分隔：多行输入
   *
   * 执行流程：
   * 1. 解析输入文本，提取股票代码数组
   * 2. 过滤空字符串
   * 3. 设置加载状态为true，清空错误和数据
   * 4. 调用API批量查询
   * 5. 更新data和history
   * 6. 捕获错误并显示
   * 7. 最后设置加载状态为false
   */
  async function queryStocks(text: string) {
    // 解析输入文本：支持逗号、顿号、空格、换行作为分隔符
    const queries = text
      .split(/[,，\s\n]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0)

    // 无有效输入时不执行查询
    if (!queries.length) return

    loading.value = true
    error.value = null
    data.value = null

    try {
      // 调用批量查询API
      const res = await macdvApi.batchQuery(queries)
      data.value = res

      // 过滤出成功查询的股票代码（无error的记录）
      // 用于更新历史记录
      const newQueries = queries.filter(q => {
        const item = res.results.find(r => r.stock_name === q.trim() || r.stock_code === q.trim())
        return !item?.error
      })

      // 更新历史记录：
      // 1. 新查询放在前面
      // 2. 去重处理
      // 3. 最多保留20条
      history.value = [...new Set([...newQueries, ...history.value])].slice(0, 20)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '查询失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }

  /**
   * clearResult - 清除查询结果
   *
   * 功能：清空当前查询结果和错误信息，
   * 用于用户主动重置状态
   */
  function clearResult() {
    data.value = null
    error.value = null
  }

  // 暴露状态和方法供组件使用
  return { data, loading, error, history, queryStocks, clearResult }
})
