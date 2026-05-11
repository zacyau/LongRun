export interface MacdvStockItem {
  stock_name: string
  stock_code: string
  trade_date: string
  current_price: number
  macdv: number
  rsi14: number
  macdv_trend: string
  rsi14_signal: string
  status_description: string | null
  error: string | null
}

export interface MacdvResponse {
  results: MacdvStockItem[]
  updated_at: string
}