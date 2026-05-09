<template>
  <div class="chart-wrapper">
    <div class="chart-header">
      <h3 class="chart-title">滚动5年最大回撤</h3>
      <div v-if="minDrawdown !== null" class="badge badge-red">
        最小值: {{ minDrawdown }}%
      </div>
    </div>
    <v-chart ref="vChartRef" class="chart" :option="chartOption" :update-options="{ notMerge: false, replaceMerge: ['series'] }" />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { CHART_COLORS } from '@/utils/chartTheme'

const isMobile = ref(false)
const vChartRef = ref()

function handleResize() {
  isMobile.value = window.innerWidth <= 768
  vChartRef.value?.chart?.resize()
}

onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize, { passive: true })
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

const xAxisInterval = computed(() => isMobile.value ? 1400 : 500)
const dataZoomConfig = computed(() => {
  const sliderBase = {
    type: 'slider' as const,
    start: 0,
    end: 100,
    height: 20,
    bottom: 10,
    handleSize: '80%',
    showDetail: false,
    borderColor: CHART_COLORS.zoomBorder,
    backgroundColor: CHART_COLORS.zoomBg,
    fillerColor: CHART_COLORS.zoomFill,
    handleStyle: { color: CHART_COLORS.zoomHandle }
  }
  if (isMobile.value) {
    return [sliderBase]
  }
  return [
    { type: 'inside' as const, start: 0, end: 100 },
    sliderBase
  ]
})
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import type { ChartData } from '@/types/anchor'

use([
  CanvasRenderer,
  LineChart,
  GridComponent,
  TooltipComponent,
  DataZoomComponent,
  MarkLineComponent
])

interface Props {
  data: ChartData | null
}

const props = defineProps<Props>()

const minDrawdown = computed(() => {
  return props.data?.min_drawdown ?? null
})

const chartOption = computed(() => {
  if (!props.data) return {}

  const { dates, drawdown_5y } = props.data

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        lineStyle: {
          color: CHART_COLORS.crosshair,
          type: 'dashed'
        }
      },
      formatter: (params: any[]) => {
        const date = params[0]?.axisValue
        const value = params[0]?.value
        return `<div style="font-weight:600;margin-bottom:4px">${date}</div>
                <div>最大回撤: ${value?.toFixed(2) ?? '--'}%</div>`
      }
    },
    grid: {
      left: 60,
      right: 40,
      top: 30,
      bottom: 60
    },
    xAxis: {
      type: 'category',
      data: dates,
      boundaryGap: false,
      axisLine: {
        lineStyle: { color: CHART_COLORS.axisLine }
      },
      axisLabel: {
        color: CHART_COLORS.axisLabel,
        fontSize: 11,
        interval: xAxisInterval.value,
        formatter: (value: string) => {
          return value.substring(0, 4)
        }
      },
      axisTick: {
        show: true,
        alignWithLabel: true
      }
    },
    yAxis: {
      type: 'value',
      max: 0,
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: CHART_COLORS.axisLabel,
        fontSize: 11,
        formatter: (value: number) => `${value}%`
      },
      splitLine: {
        lineStyle: {
          color: CHART_COLORS.splitLine
        }
      }
    },
    dataZoom: dataZoomConfig.value,
    series: [
      {
        name: '滚动5年最大回撤',
        type: 'line',
        data: drawdown_5y,
        smooth: false,
        symbol: 'none',
        lineStyle: {
          color: CHART_COLORS.drawdown,
          width: 1.5
        },
        areaStyle: {
          color: CHART_COLORS.drawdownFill
        }
      }
    ]
  }
})
</script>

<style scoped>
.chart-wrapper {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-base);
}

.chart-wrapper:hover {
  box-shadow: var(--shadow-card-hover);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.chart-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.chart {
  width: 100%;
  height: 280px;
  touch-action: pan-y;
}

@media (max-width: 768px) {
  .chart {
    height: 220px;
  }
}
</style>
