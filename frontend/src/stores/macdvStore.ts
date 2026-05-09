import { defineStore } from 'pinia'
import { ref } from 'vue'
import { macdvApi } from '@/api/macdv'
import type { MacdvResponse } from '@/types/macdv'

export const useMacdvStore = defineStore('macdv', () => {
  const data = ref<MacdvResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const history = ref<string[]>([])

  async function queryStocks(text: string) {
    const queries = text
      .split(/[,，\s\n]+/)
      .map(s => s.trim())
      .filter(s => s.length > 0)

    if (!queries.length) return

    loading.value = true
    error.value = null
    data.value = null

    try {
      const res = await macdvApi.batchQuery(queries)
      data.value = res
      const newQueries = queries.filter(q => {
        const item = res.results.find(r => r.stock_name === q.trim() || r.stock_code === q.trim())
        return !item?.error
      })
      history.value = [...new Set([...newQueries, ...history.value])].slice(0, 20)
    } catch (e) {
      error.value = e instanceof Error ? e.message : '查询失败，请稍后重试'
    } finally {
      loading.value = false
    }
  }

  function clearResult() {
    data.value = null
    error.value = null
  }

  return { data, loading, error, history, queryStocks, clearResult }
})