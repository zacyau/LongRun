export interface GrowthValueChart1 {
  dates: string[]
  growth: (number | null)[]
  value: (number | null)[]
}

export interface GrowthValueChart2 {
  dates: string[]
  ratio: (number | null)[]
  ma242: (number | null)[]
  upper: (number | null)[]
  lower: (number | null)[]
  pctB: number
  bandwidth: number
}

export interface GrowthValueChart3 {
  dates: string[]
  diff: (number | null)[]
  diff_ma242: (number | null)[]
  mean: number
}

export interface GrowthValueChart4 {
  dates: string[]
  rsi: (number | null)[]
  rsi_ma242: (number | null)[]
  latest_rsi: number
  latest_rsi_ma: number
}

export interface GrowthValueData {
  chart1: GrowthValueChart1
  chart2: GrowthValueChart2
  chart3: GrowthValueChart3
  chart4: GrowthValueChart4
  generated_at: string
}
