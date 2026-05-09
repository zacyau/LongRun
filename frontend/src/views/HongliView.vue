<template>
  <div class="hongli-view">
    <header class="hongli-header">
      <div class="header-inner">
        <div class="header-brand">
          <div class="brand-tag">量化分析</div>
          <div class="brand-info">
            <h1 class="header-title">中证红利 <span class="title-sep">/</span> 国证A股</h1>
            <p class="header-subtitle">轮动三棱镜 · 中证红利相对国证A股的超额收益分析</p>
          </div>
        </div>
        <div class="header-actions">
          <div class="data-meta" v-if="store.data">
            <span class="meta-item">
              <span class="meta-dot"></span>
              共 {{ store.data.chart1.dates.length }} 个交易日
            </span>
          </div>
          <TimeRangeSelector
            v-model="store.selectedRange"
            v-model:customStart="store.customStartDate"
            v-model:customEnd="store.customEndDate"
            :loading="store.loading"
            @change="handleRangeChange"
            @refresh="store.refreshData()"
          />
        </div>
      </div>
    </header>

    <main class="hongli-main">
      <div v-if="store.error" class="error-banner">
        <span>{{ store.error }}</span>
        <button @click="store.error = null">×</button>
      </div>

      <div v-if="store.data" class="charts-grid">
        <div class="chart-card">
          <div class="card-meta">
            <h3 class="card-title">收益走势对比</h3>
            <div class="card-legend">
              <span class="legend-item legend-hongli">
                <span class="legend-dot"></span>中证红利
              </span>
              <span class="legend-item legend-guozheng">
                <span class="legend-dot"></span>国证A股
              </span>
            </div>
          </div>
          <div ref="chart1Ref" class="chart-box"></div>
        </div>

        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">红利/国证 比值布林线</h3>
              <span class="card-desc">242日 ±2σ 通道</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-ratio">比值 {{ store.data.chart2.ratio[store.data.chart2.ratio.length - 1]?.toFixed(4) }}</span>
                <span class="badge badge-pctb">%B {{ store.data.chart2.pctB }}</span>
              </div>
              <button class="info-btn" @click="showModal2 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <div ref="chart2Ref" class="chart-box"></div>
        </div>

        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">40日收益差</h3>
              <span class="card-desc">中证红利 − 国证A股（MA242）</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-diff">差值 {{ store.data.chart3.diff[store.data.chart3.diff.length - 1]?.toFixed(2) }}%</span>
              </div>
              <button class="info-btn" @click="showModal3 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <div ref="chart3Ref" class="chart-box"></div>
        </div>

        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">RSI14 动能指标</h3>
              <span class="card-desc">比值 RSI（MA242）</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-rsi">RSI {{ store.data.chart4.latest_rsi }}</span>
              </div>
              <button class="info-btn" @click="showModal4 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <div ref="chart4Ref" class="chart-box"></div>
        </div>
      </div>

      <div v-else-if="store.loading" class="loading-state">
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
        <p>加载图表数据...</p>
      </div>

      <div v-else class="empty-state">
        <p>暂无数据</p>
      </div>
    </main>

    <!-- Modals -->
    <div v-if="showModal2" class="modal-overlay" @click.self="showModal2 = false">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>布林线说明</h3>
          <button class="modal-close" @click="showModal2 = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-section">
            <h4>计算</h4>
            <ul class="modal-list">
              <li>比值 = 中证红利全收益 / 国证A股全收益</li>
              <li>中轨 = 比值的242日简单移动平均（MA242）</li>
              <li>上轨 = 中轨 + 2×标准差</li>
              <li>下轨 = 中轨 - 2×标准差</li>
              <li>%B = (当前比值 - 下轨) / (上轨 - 下轨)</li>
              <li>带宽 = (上轨 - 下轨) / 中轨 × 100%</li>
            </ul>
          </div>
          <div class="modal-section">
            <h4>作用</h4>
            <p>判断红利/国证比值处于历史波动区间的什么位置。%B靠近0说明比值接近下轨（红利相对偏弱），靠近1说明比值接近上轨（红利相对偏强）。带宽变宽说明波动加大。</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal3" class="modal-overlay" @click.self="showModal3 = false">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>收益差说明</h3>
          <button class="modal-close" @click="showModal3 = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-section">
            <h4>计算</h4>
            <ul class="modal-list">
              <li>40日收益差 = 中证红利40日累计收益率 - 国证A股40日累计收益率</li>
              <li>再叠加一条242日均线（MA242）</li>
            </ul>
          </div>
          <div class="modal-section">
            <h4>作用</h4>
            <p>衡量短期（40日）内红利指数相对国证A股的超额收益方向和幅度。差值为正说明红利短期跑赢，反之跑输。均线方向反映中期趋势。</p>
            <p class="modal-tip">过高的时候不要追高，可以静待回落到零轴甚至此前常见的低点时杀入。</p>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showModal4" class="modal-overlay" @click.self="showModal4 = false">
      <div class="modal-panel">
        <div class="modal-header">
          <h3>RSI 说明</h3>
          <button class="modal-close" @click="showModal4 = false">&times;</button>
        </div>
        <div class="modal-body">
          <div class="modal-section">
            <h4>计算</h4>
            <ul class="modal-list">
              <li>先算出比值（中证红利/国证A股）</li>
              <li>RSI(14) = 100 - 100/(1+RS)</li>
              <li>RS = 14日内上涨幅度均值 / 14日内下跌幅度均值（绝对值）</li>
              <li>同样叠加242日均线</li>
            </ul>
          </div>
          <div class="modal-section">
            <h4>作用</h4>
            <p>RSI反映比值的动能强弱。RSI&gt;70说明比值处于强势上涨区间（红利相对强势），RSI&lt;30说明比值弱势（红利相对跑输）。和图2结合可以看价格位置+动能方向。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import { useHongliStore } from '@/stores/hongliStore'
import type { TimeRangeOption } from '@/types/anchor'
import TimeRangeSelector from '@/components/anchor/TimeRangeSelector.vue'

const store = useHongliStore()
const chart1Ref = ref<HTMLDivElement | null>(null)
const chart2Ref = ref<HTMLDivElement | null>(null)
const chart3Ref = ref<HTMLDivElement | null>(null)
const chart4Ref = ref<HTMLDivElement | null>(null)
const showModal2 = ref(false)
const showModal3 = ref(false)
const showModal4 = ref(false)

function handleRangeChange(range: TimeRangeOption) {
  store.fetchData(range)
}

const COLORS = {
  hongli: '#E53935',
  guozheng: '#2962FF',
  ratio: '#333333',
  ma242: '#E53935',
  bollingerUpper: 'rgba(144, 168, 204, 0.5)',
  bollingerLower: 'rgba(144, 168, 204, 0.5)',
  diff: '#333333',
  diffMa: '#E53935',
  rsi: '#333333',
  rsiMa: '#E53935',
  grid: '#F5F5F5',
}

const chart1 = ref<echarts.ECharts | null>(null)
const chart2 = ref<echarts.ECharts | null>(null)
const chart3 = ref<echarts.ECharts | null>(null)
const chart4 = ref<echarts.ECharts | null>(null)

function initCharts() {
  if (chart1Ref.value && !chart1.value) chart1.value = echarts.init(chart1Ref.value)
  if (chart2Ref.value && !chart2.value) chart2.value = echarts.init(chart2Ref.value)
  if (chart3Ref.value && !chart3.value) chart3.value = echarts.init(chart3Ref.value)
  if (chart4Ref.value && !chart4.value) chart4.value = echarts.init(chart4Ref.value)
}

function resizeCharts() {
  chart1.value?.resize()
  chart2.value?.resize()
  chart3.value?.resize()
  chart4.value?.resize()
}

function buildChart1Option(d: any, isMobile: boolean) {
  return {
    tooltip: { trigger: 'axis', confine: true, backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#E8E8E8', borderWidth: 1, padding: [8, 12], textStyle: { color: '#333', fontSize: 12 }, axisPointer: { type: 'cross', lineStyle: { color: '#DDD', type: 'dashed' } } },
    legend: { show: false },
    grid: { left: 52, right: 20, top: 24, bottom: 24 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, interval: isMobile ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, formatter: (v: number) => v.toFixed(0) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '中证红利', type: 'line', data: d.hongli, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.hongli } },
      { name: '国证A股', type: 'line', data: d.guozheng, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.guozheng } },
    ],
  }
}

function buildChart2Option(d: any, isMobile: boolean) {
  const dates = d.dates as string[]
  const upper = d.upper as (number | null)[]
  const lower = d.lower as (number | null)[]
  const N = dates.length
  const upperValid: number[] = upper.map((v, i) => v ?? (lower[i] ?? 0))
  const lowerValid: number[] = lower.map((v, i) => v ?? (upper[i] ?? 0))

  return {
    tooltip: { trigger: 'axis', confine: true, backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#E8E8E8', borderWidth: 1, padding: [8, 12], textStyle: { color: '#333', fontSize: 12 }, axisPointer: { type: 'cross', lineStyle: { color: '#DDD', type: 'dashed' } } },
    legend: { show: false },
    grid: { left: 52, right: 20, top: 24, bottom: 24 },
    xAxis: { type: 'category', data: dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, interval: isMobile ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, formatter: (v: number) => v.toFixed(2) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '上轨', type: 'line', data: d.upper, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dotted', color: COLORS.bollingerUpper }, z: 3 },
      {
        name: '布林带填充',
        type: 'custom',
        renderItem: (_params: any, api: any) => {
          if (N === 0) return null
          const pts: [number, number][] = new Array(N * 2)
          for (let i = 0; i < N; i++) {
            const x = api.coord([i, upperValid[i]])[0]
            const yUp = api.coord([i, upperValid[i]])[1]
            pts[i] = [x, yUp]
          }
          for (let i = N - 1; i >= 0; i--) {
            const x = api.coord([i, lowerValid[i]])[0]
            const yDown = api.coord([i, lowerValid[i]])[1]
            pts[N + (N - 1 - i)] = [x, yDown]
          }
          return { type: 'polygon', shape: { points: pts }, style: { fill: 'rgba(224, 224, 224, 0.6)', stroke: 'none' }, z: 0 }
        },
        data: [0],
        z: 0,
        silent: true,
      },
      { name: '下轨', type: 'line', data: d.lower, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dotted', color: COLORS.bollingerLower }, z: 2 },
      { name: 'MA242', type: 'line', data: d.ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.ma242 } },
      { name: '比值', type: 'line', data: d.ratio, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.ratio } },
    ],
  }
}

function buildChart3Option(d: any, isMobile: boolean) {
  return {
    tooltip: { trigger: 'axis', confine: true, backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#E8E8E8', borderWidth: 1, padding: [8, 12], textStyle: { color: '#333', fontSize: 12 }, axisPointer: { type: 'cross', lineStyle: { color: '#DDD', type: 'dashed' } } },
    legend: { show: false },
    grid: { left: 52, right: 20, top: 24, bottom: 24 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, interval: isMobile ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, formatter: (v: number) => `${v.toFixed(1)}%` }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '收益差', type: 'line', data: d.diff, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.diff } },
      { name: 'MA242', type: 'line', data: d.diff_ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.diffMa } },
    ],
  }
}

function buildChart4Option(d: any, isMobile: boolean) {
  return {
    tooltip: { trigger: 'axis', confine: true, backgroundColor: 'rgba(255,255,255,0.96)', borderColor: '#E8E8E8', borderWidth: 1, padding: [8, 12], textStyle: { color: '#333', fontSize: 12 }, axisPointer: { type: 'cross', lineStyle: { color: '#DDD', type: 'dashed' } } },
    legend: { show: false },
    grid: { left: 52, right: 20, top: 24, bottom: 24 },
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, interval: isMobile ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', min: 0, max: 100, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: '#AAAAAA', fontSize: 10, formatter: (v: number) => v.toFixed(0) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: 'RSI14', type: 'line', data: d.rsi, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.rsi } },
      { name: 'MA242', type: 'line', data: d.rsi_ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.rsiMa } },
    ],
  }
}

function renderAllCharts() {
  if (!store.data) return
  const isMobile = window.innerWidth <= 768
  const d1 = store.data.chart1
  const d2 = store.data.chart2
  const d3 = store.data.chart3
  const d4 = store.data.chart4
  chart1.value?.setOption(buildChart1Option(d1, isMobile), { notMerge: false })
  chart2.value?.setOption(buildChart2Option(d2, isMobile), { notMerge: false })
  chart3.value?.setOption(buildChart3Option(d3, isMobile), { notMerge: false })
  chart4.value?.setOption(buildChart4Option(d4, isMobile), { notMerge: false })
}

let resizeTimer: ReturnType<typeof setTimeout> | null = null
function onResize() {
  if (resizeTimer) clearTimeout(resizeTimer)
  resizeTimer = setTimeout(() => {
    resizeCharts()
    renderAllCharts()
  }, 100)
}

onMounted(() => {
  window.addEventListener('resize', onResize, { passive: true })
  store.fetchData()
})

onUnmounted(() => {
  chart1.value?.dispose()
  chart2.value?.dispose()
  chart3.value?.dispose()
  chart4.value?.dispose()
  chart1.value = null
  chart2.value = null
  chart3.value = null
  chart4.value = null
  window.removeEventListener('resize', onResize)
})

watch(() => store.data, () => {
  nextTick(() => {
    nextTick(() => {
      initCharts()
      renderAllCharts()
    })
  })
})
</script>

<style scoped>
.hongli-view {
  min-height: calc(100vh - 56px);
  background: #F7F8FA;
  touch-action: manipulation;
}

.hongli-header {
  background: #fff;
  border-bottom: 1px solid #EBEBEB;
  padding: 20px 32px;
  touch-action: manipulation;
}

.header-inner {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.header-brand {
  display: flex;
  align-items: flex-start;
  gap: 14px;
}

.brand-tag {
  background: #1A1A1A;
  color: #fff;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 3px;
  letter-spacing: 0.05em;
  margin-top: 4px;
  white-space: nowrap;
}

.header-title {
  font-size: 20px;
  font-weight: 700;
  color: #1A1A1A;
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.title-sep {
  color: #CCC;
  font-weight: 400;
  margin: 0 2px;
}

.header-subtitle {
  font-size: 13px;
  color: #999;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.data-meta {
  display: flex;
  align-items: center;
}

.meta-item {
  font-size: 12px;
  color: #999;
  display: flex;
  align-items: center;
  gap: 5px;
}

.meta-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #52C41A;
  display: inline-block;
}

.hongli-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 32px;
  touch-action: manipulation;
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #FFF2F0;
  border: 1px solid #FFCCC7;
  color: #CF1322;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
  font-size: 14px;
}

.error-banner button {
  background: none;
  border: none;
  color: #CF1322;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.charts-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px 24px 16px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 0 0 1px rgba(0, 0, 0, 0.03);
  transition: box-shadow 0.2s;
}

.chart-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.07), 0 0 0 1px rgba(0, 0, 0, 0.04);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.card-title-group {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.card-title {
  font-size: 14px;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.card-desc {
  font-size: 12px;
  color: #AAA;
}

.card-legend {
  display: flex;
  gap: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 12px;
  color: #666;
}

.legend-dot {
  width: 20px;
  height: 2px;
  border-radius: 1px;
  display: inline-block;
}

.legend-hongli .legend-dot { background: #E53935; }
.legend-guozheng .legend-dot { background: #2962FF; }

.card-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.card-badges {
  display: flex;
  gap: 6px;
}

.badge {
  font-size: 11px;
  font-weight: 500;
  padding: 3px 8px;
  border-radius: 4px;
  background: #F5F5F5;
  color: #666;
}

.badge-ratio { color: #333; font-weight: 600; }
.badge-pctb { color: #2962FF; }
.badge-rsi { color: #333; font-weight: 600; }
.badge-diff { color: #333; font-weight: 600; }

.info-btn {
  background: none;
  border: 1px solid #E8E8E8;
  padding: 4px 8px;
  border-radius: 5px;
  cursor: pointer;
  color: #AAA;
  display: flex;
  align-items: center;
  transition: all 0.15s;
}

.info-btn:hover {
  color: #666;
  border-color: #CCC;
  background: #FAFAFA;
}

.chart-box {
  width: 100%;
  height: 280px;
  touch-action: none;
  will-change: transform;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: #999;
  font-size: 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.loading-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #2962FF;
  animation: dotBounce 1.2s infinite ease-in-out;
}

.loading-dot:nth-child(2) { animation-delay: 0.15s; }
.loading-dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1.2); opacity: 1; }
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
  backdrop-filter: blur(2px);
}

.modal-panel {
  background: #fff;
  border-radius: 12px;
  max-width: 480px;
  width: 100%;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 18px 24px;
  border-bottom: 1px solid #F0F0F0;
}

.modal-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1A1A1A;
}

.modal-close {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: #AAA;
  line-height: 1;
  padding: 0;
}

.modal-close:hover { color: #333; }

.modal-body {
  padding: 20px 24px 24px;
}

.modal-section {
  margin-bottom: 18px;
}

.modal-section:last-child { margin-bottom: 0; }

.modal-section h4 {
  font-size: 13px;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0 0 10px;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.modal-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.modal-list li {
  font-size: 13px;
  color: #555;
  padding: 3px 0;
  line-height: 1.6;
}

.modal-tip {
  margin-top: 8px;
  color: #888;
  font-size: 12px;
  line-height: 1.6;
}

.formula-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.formula-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #555;
  background: #F8F9FA;
  padding: 6px 10px;
  border-radius: 5px;
}

.f-label {
  font-weight: 600;
  color: #333;
  min-width: 40px;
}

.f-eq {
  color: #AAA;
  font-size: 12px;
}

.modal-section p {
  font-size: 13px;
  color: #555;
  line-height: 1.7;
  margin: 0;
}

@media (max-width: 768px) {
  .hongli-header { padding: 14px 16px; }
  .header-inner { flex-direction: column; align-items: flex-start; }
  .header-title { font-size: 17px; }
  .hongli-main { padding: 12px 16px; }
  .chart-box { height: 220px; }
  .charts-grid { gap: 10px; }
  .chart-card { padding: 14px 16px 12px; }
}
</style>