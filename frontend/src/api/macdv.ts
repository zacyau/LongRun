import axios from 'axios'
import type { MacdvResponse } from '@/types/macdv'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export const macdvApi = {
  async batchQuery(queries: string[]): Promise<MacdvResponse> {
    const response = await api.post('/macdv/batch_query', queries)
    return response.data
  }
}