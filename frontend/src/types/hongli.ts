export interface HongliChart1 {
  dates: string[]
  hongli: (number | null)[]
  guozheng: (number | null)[]
}

export interface HongliChart2 {
  dates: string[]
  ratio: (number | null)[]
  ma242: (number | null)[]
  upper: (number | null)[]
  lower: (number | null)[]
  pctB: number
  bandwidth: number
}

export interface HongliChart3 {
  dates: string[]
  diff: (number | null)[]
  diff_ma242: (number | null)[]
  mean: number
}

export interface HongliChart4 {
  dates: string[]
  rsi: (number | null)[]
  rsi_ma242: (number | null)[]
  latest_rsi: number
  latest_rsi_ma: number
}

export interface HongliData {
  chart1: HongliChart1
  chart2: HongliChart2
  chart3: HongliChart3
  chart4: HongliChart4
  generated_at: string
}