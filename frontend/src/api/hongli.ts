import axios from 'axios'
import type { HongliData } from '@/types/hongli'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
})

export const hongliApi = {
  async getData(start_date?: string, end_date?: string): Promise<HongliData> {
    const params: Record<string, string> = {}
    if (start_date) params.start_date = start_date
    if (end_date) params.end_date = end_date
    const response = await api.get('/hongli/data', { params })
    return response.data
  },

  async refreshData(): Promise<{ message: string; generated_at: string }> {
    const response = await api.post('/hongli/refresh')
    return response.data
  }
}