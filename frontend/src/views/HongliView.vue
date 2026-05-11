<!--
 * HongliView.vue - 中证红利/国证A股 轮动分析页面
 *
 * 功能说明：
 * 本页面对比分析中证红利全收益指数与国证A股全收益指数的相对表现，
 * 帮助投资者了解红利策略在A股市场的超额收益情况。
 *
 * 包含四个核心图表：
 * 1. 收益走势对比：两只指数的价格走势叠加对比
 * 2. 红利/国证比值布林线：分析比值的波动区间和位置
 * 3. 40日收益差：短期超额收益分析
 * 4. RSI14动能指标：比值的RSI动量分析
 *
 * 交互功能：
 * - 时间范围切换（1年/3年/5年/全部/自定义）
 * - 刷新数据
 * - 各图表的说明弹窗
 -->

<template>
  <!-- 主容器：整体页面采用深色主题背景 -->
  <div class="hongli-view">

    <!-- 页面顶部导航栏 -->
    <header class="hongli-header">
      <div class="header-inner">
        <!-- 品牌区域：页面标题和分析主题描述 -->
        <div class="header-brand">
          <div class="brand-info">
            <!-- 主标题：对比两只指数 -->
            <h1 class="header-title">中证红利 <span class="title-sep">/</span> 国证A股</h1>
            <!-- 副标题：说明分析方法和目的 -->
            <p class="header-subtitle">轮动三棱镜 · 中证红利相对国证A股的超额收益分析</p>
          </div>
        </div>

        <!-- 右上角操作区：时间范围选择器 -->
        <div class="header-actions">
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

    <!-- 页面主内容区 -->
    <main class="hongli-main">

      <!-- 错误提示条：请求失败时显示在顶部 -->
      <div v-if="store.error" class="error-banner">
        <span>{{ store.error }}</span>
        <button @click="store.error = null">×</button>
      </div>

      <!-- 图表网格容器：纵向排列四个图表卡片 -->
      <div v-if="store.data" class="charts-grid">

        <!-- 图表卡片1：收益走势对比 -->
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
          <v-chart ref="vChart1Ref" class="chart-box" :option="chart1Option" :update-options="{ notMerge: false, replaceMerge: ['series'] }" />
        </div>

        <!-- 图表卡片2：红利/国证比值布林线 -->
        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">红利/国证 比值布林线</h3>
              <span class="card-desc">242日 ±2σ 通道</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-neutral">比值 {{ store.data.chart2.ratio[store.data.chart2.ratio.length - 1]?.toFixed(4) }}</span>
                <span class="badge badge-blue">%B {{ store.data.chart2.pctB }}</span>
              </div>
              <button class="info-btn" @click="showModal2 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <v-chart ref="vChart2Ref" class="chart-box" :option="chart2Option" :update-options="{ notMerge: false, replaceMerge: ['series'] }" />
        </div>

        <!-- 图表卡片3：40日收益差 -->
        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">40日收益差</h3>
              <span class="card-desc">中证红利 − 国证A股（MA242）</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-neutral">差值 {{ store.data.chart3.diff[store.data.chart3.diff.length - 1]?.toFixed(2) }}%</span>
              </div>
              <button class="info-btn" @click="showModal3 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <v-chart ref="vChart3Ref" class="chart-box" :option="chart3Option" :update-options="{ notMerge: false, replaceMerge: ['series'] }" />
        </div>

        <!-- 图表卡片4：RSI14动能指标 -->
        <div class="chart-card">
          <div class="card-meta">
            <div class="card-title-group">
              <h3 class="card-title">RSI14 动能指标</h3>
              <span class="card-desc">比值 RSI（MA242）</span>
            </div>
            <div class="card-actions">
              <div class="card-badges" v-if="store.data">
                <span class="badge badge-neutral">RSI {{ store.data.chart4.latest_rsi }}</span>
              </div>
              <button class="info-btn" @click="showModal4 = true">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>
              </button>
            </div>
          </div>
          <v-chart ref="vChart4Ref" class="chart-box" :option="chart4Option" :update-options="{ notMerge: false, replaceMerge: ['series'] }" />
        </div>
      </div>

      <!-- 加载状态：数据请求中显示动画 -->
      <div v-else-if="store.loading" class="loading-state">
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
        <span class="loading-dot"></span>
        <p>加载图表数据...</p>
      </div>

      <!-- 空状态：无数据且未加载时显示 -->
      <div v-else class="empty-state">
        <p>暂无数据</p>
      </div>
    </main>

    <!-- 弹窗区域：使用Teleport传送到body层 -->

    <!-- 布林线说明弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
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
      </Transition>
    </Teleport>

    <!-- 收益差说明弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
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
      </Transition>
    </Teleport>

    <!-- RSI说明弹窗 -->
    <Teleport to="body">
      <Transition name="modal">
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
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
/*
 * HongliView 组件逻辑
 *
 * ECharts 配置说明：
 * - 使用 vue-echarts 封装库，配置基于 ECharts 5.x
 * - 支持响应式resize，监听窗口变化自动调整图表尺寸
 *
 * 状态管理：
 * - store: 使用hongliStore管理数据获取和状态
 * - showModal2/3/4: 分别控制三个图表说明弹窗的显示状态
 * - isMobile: 检测是否为移动端设备，用于调整图表X轴标签密度
 *
 * 图表配置：
 * - chart1Option: 收益走势对比图 - 两条折线叠加
 * - chart2Option: 布林线图 - 上轨、下轨、MA242、比值线和布林带填充
 * - chart3Option: 收益差图 - 差值线和MA242均线
 * - chart4Option: RSI图 - RSI线和MA242均线
 */
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, CustomChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useHongliStore } from '@/stores/hongliStore'
import { CHART_COLORS } from '@/utils/chartTheme'
import type { TimeRangeOption } from '@/types/anchor'
import TimeRangeSelector from '@/components/anchor/TimeRangeSelector.vue'

// 注册ECharts必要的组件
use([
  CanvasRenderer,
  LineChart,
  CustomChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  MarkLineComponent,
])

/*
 * 组件状态定义
 * - showModal2/3/4: 控制三个图表说明弹窗的显示状态
 * - isMobile: 标识当前是否为移动端视口
 * - vChart1/2/3/4Ref: ECharts图表实例引用，用于响应式调整
 */
const store = useHongliStore()
const showModal2 = ref(false)
const showModal3 = ref(false)
const showModal4 = ref(false)

const isMobile = ref(false)
const vChart1Ref = ref()
const vChart2Ref = ref()
const vChart3Ref = ref()
const vChart4Ref = ref()

/*
 * handleResize - 处理窗口大小变化
 * 功能：
 * 1. 检测是否为移动端（宽度<=768px）
 * 2. 触发所有ECharts图表的resize方法以适应新尺寸
 */
function handleResize() {
  isMobile.value = window.innerWidth <= 768
  vChart1Ref.value?.chart?.resize()
  vChart2Ref.value?.chart?.resize()
  vChart3Ref.value?.chart?.resize()
  vChart4Ref.value?.chart?.resize()
}

/*
 * 生命周期钩子
 * - onMounted: 组件挂载时初始化，获取数据，添加窗口resize监听
 * - onUnmounted: 组件卸载时移除监听，防止内存泄漏
 */
onMounted(() => {
  handleResize()
  window.addEventListener('resize', handleResize, { passive: true })
  store.fetchData()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

/*
 * handleRangeChange - 处理时间范围变更
 * @param range: 新的时间范围选项
 * 功能：调用store获取新时间范围的图表数据
 */
function handleRangeChange(range: TimeRangeOption) {
  store.fetchData(range)
}

/*
 * 图表颜色配置对象
 * 为不同数据系列定义颜色，用于视觉区分
 */
const COLORS = {
  hongli: CHART_COLORS.hongli,
  guozheng: CHART_COLORS.guozheng,
  ratio: CHART_COLORS.ratio,
  ma242: CHART_COLORS.hongli,
  bollinger: CHART_COLORS.bollinger,
  bollingerFill: CHART_COLORS.bollingerFill,
  diff: CHART_COLORS.diff,
  diffMa: CHART_COLORS.hongli,
  rsi: CHART_COLORS.ratio,
  rsiMa: CHART_COLORS.hongli,
  grid: CHART_COLORS.splitLine,
}

/*
 * 基础提示框配置
 * 统一所有图表的tooltip样式
 */
const tooltipBase = {
  trigger: 'axis' as const,
  confine: true,
  backgroundColor: CHART_COLORS.tooltipBg,
  borderColor: CHART_COLORS.tooltipBorder,
  borderWidth: 1,
  padding: [8, 12] as [number, number],
  textStyle: { color: CHART_COLORS.tooltipText, fontSize: 12 },
  axisPointer: { type: 'cross' as const, lineStyle: { color: CHART_COLORS.crosshair, type: 'dashed' as const } },
}

// 基础网格配置：控制图表边距
const gridBase = { left: 52, right: 20, top: 24, bottom: 24 }

/*
 * chart1Option - 收益走势对比图表配置
 * 计算属性依赖store.data，当数据变化时自动更新
 * 展示中证红利和国证A股两条收益率曲线的叠加
 */
const chart1Option = computed(() => {
  if (!store.data) return {}
  const d = store.data.chart1
  return {
    animation: false,
    tooltip: tooltipBase,
    legend: { show: false },
    grid: gridBase,
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, interval: isMobile.value ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, formatter: (v: number) => v.toFixed(0) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '中证红利', type: 'line', data: d.hongli, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.hongli } },
      { name: '国证A股', type: 'line', data: d.guozheng, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.guozheng } },
    ],
  }
})

/*
 * chart2Option - 布林线图表配置
 * 展示红利/国证比值及其布林带通道
 * 使用CustomChart渲染布林带填充区域
 */
const chart2Option = computed(() => {
  if (!store.data) return {}
  const d = store.data.chart2
  const dates = d.dates as string[]
  const upper = d.upper as (number | null)[]
  const lower = d.lower as (number | null)[]
  const N = dates.length
  // 处理空值：将null值替换为对应位置的另一轨值
  const upperValid: number[] = upper.map((v, i) => v ?? (lower[i] ?? 0))
  const lowerValid: number[] = lower.map((v, i) => v ?? (upper[i] ?? 0))

  return {
    animation: false,
    tooltip: tooltipBase,
    legend: { show: false },
    grid: gridBase,
    xAxis: { type: 'category', data: dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, interval: isMobile.value ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, formatter: (v: number) => v.toFixed(2) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '上轨', type: 'line', data: d.upper, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dotted', color: COLORS.bollinger }, z: 3 },
      // 布林带填充区域：使用CustomChart自定义渲染
      {
        name: '布林带填充',
        type: 'custom',
        renderItem: (_params: any, api: any) => {
          if (N === 0) return null
          const pts: [number, number][] = new Array(N * 2)
          // 上轨：从左到右
          for (let i = 0; i < N; i++) {
            const x = api.coord([i, upperValid[i]])[0]
            const yUp = api.coord([i, upperValid[i]])[1]
            pts[i] = [x, yUp]
          }
          // 下轨：从右到左闭合多边形
          for (let i = N - 1; i >= 0; i--) {
            const x = api.coord([i, lowerValid[i]])[0]
            const yDown = api.coord([i, lowerValid[i]])[1]
            pts[N + (N - 1 - i)] = [x, yDown]
          }
          return { type: 'polygon', shape: { points: pts }, style: { fill: COLORS.bollingerFill, stroke: 'none' }, z: 0 }
        },
        data: [0],
        z: 0,
        silent: true,
      },
      { name: '下轨', type: 'line', data: d.lower, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dotted', color: COLORS.bollinger }, z: 2 },
      { name: 'MA242', type: 'line', data: d.ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.ma242 } },
      { name: '比值', type: 'line', data: d.ratio, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.ratio } },
    ],
  }
})

/*
 * chart3Option - 40日收益差图表配置
 * 展示中证红利与国证A股的40日累计收益差及其均线
 */
const chart3Option = computed(() => {
  if (!store.data) return {}
  const d = store.data.chart3
  return {
    animation: false,
    tooltip: tooltipBase,
    legend: { show: false },
    grid: gridBase,
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, interval: isMobile.value ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, formatter: (v: number) => `${v.toFixed(1)}%` }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: '收益差', type: 'line', data: d.diff, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.diff } },
      { name: 'MA242', type: 'line', data: d.diff_ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.diffMa } },
    ],
  }
})

/*
 * chart4Option - RSI14动能指标图表配置
 * 展示比值的RSI指标及其中期均线
 */
const chart4Option = computed(() => {
  if (!store.data) return {}
  const d = store.data.chart4
  return {
    animation: false,
    tooltip: tooltipBase,
    legend: { show: false },
    grid: gridBase,
    xAxis: { type: 'category', data: d.dates, boundaryGap: false, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, interval: isMobile.value ? 1400 : 400 }, splitLine: { show: false } },
    yAxis: { type: 'value', min: 0, max: 100, axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: CHART_COLORS.axisLabel, fontSize: 10, formatter: (v: number) => v.toFixed(0) }, splitLine: { lineStyle: { color: COLORS.grid, width: 1 } } },
    series: [
      { name: 'RSI14', type: 'line', data: d.rsi, smooth: false, symbol: 'none', lineStyle: { width: 1.5, color: COLORS.rsi } },
      { name: 'MA242', type: 'line', data: d.rsi_ma242, smooth: false, symbol: 'none', lineStyle: { width: 1.5, type: 'dashed', color: COLORS.rsiMa } },
    ],
  }
})
</script>

<style scoped>
.hongli-view {
  min-height: calc(100vh - var(--header-height));
  background: var(--color-bg-page);
  touch-action: manipulation;
}

.hongli-header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-default);
  padding: var(--space-5) var(--page-padding);
  touch-action: manipulation;
}

.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-5);
}

.header-brand {
  display: flex;
  align-items: flex-start;
}

.header-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

.title-sep {
  color: var(--color-border-default);
  font-weight: 400;
  margin: 0 2px;
}

.header-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-tertiary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.hongli-main {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--page-padding);
  touch-action: manipulation;
}

.error-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--color-bg-danger);
  border: 1px solid #FECACA;
  color: var(--color-danger);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  margin-bottom: var(--space-4);
  font-size: var(--text-md);
}

.error-banner button {
  background: none;
  border: none;
  color: var(--color-danger);
  font-size: var(--text-xl);
  cursor: pointer;
  padding: 0;
  line-height: 1;
}

.charts-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.chart-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6) var(--space-4);
  box-shadow: var(--shadow-card);
  transition: box-shadow var(--transition-base);
}

.chart-card:hover {
  box-shadow: var(--shadow-card-hover);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.card-title-group {
  display: flex;
  align-items: baseline;
  gap: 10px;
}

.card-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.card-desc {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

.card-legend {
  display: flex;
  gap: 14px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
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
  gap: var(--space-2);
}

.card-badges {
  display: flex;
  gap: 6px;
}

.info-btn {
  background: none;
  border: 1px solid var(--color-border-default);
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-sm);
  cursor: pointer;
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  transition: all var(--transition-fast);
}

.info-btn:hover {
  color: var(--color-text-secondary);
  border-color: var(--color-text-tertiary);
  background: var(--color-bg-hover);
}

.chart-box {
  width: 100%;
  height: 280px;
  touch-action: pan-y;
}

.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--color-text-tertiary);
  font-size: var(--text-md);
}

.loading-state {
  text-align: center;
  padding: 60px;
  color: var(--color-text-tertiary);
  font-size: var(--text-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
}

.loading-dot {
  display: inline-block;
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--color-primary-accent);
  animation: dotBounce 1.2s infinite ease-in-out;
}

.loading-dot:nth-child(2) { animation-delay: 0.15s; }
.loading-dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1.2); opacity: 1; }
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(13, 27, 42, 0.5);
  backdrop-filter: blur(4px);
  -webkit-backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--space-5);
}

.modal-panel {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  max-width: 480px;
  width: 100%;
  overflow: hidden;
  box-shadow: var(--shadow-modal);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6);
  border-bottom: 1px solid var(--color-border-light);
}

.modal-header h3 {
  margin: 0;
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
}

.modal-close {
  background: none;
  border: none;
  font-size: 22px;
  cursor: pointer;
  color: var(--color-text-tertiary);
  line-height: 1;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.modal-close:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-hover);
}

.modal-body {
  padding: var(--space-5) var(--space-6) var(--space-6);
}

.modal-section {
  margin-bottom: 18px;
}

.modal-section:last-child { margin-bottom: 0; }

.modal-section h4 {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
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
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  padding: 3px 0;
  line-height: var(--leading-relaxed);
}

.modal-tip {
  margin-top: var(--space-2);
  color: var(--color-text-tertiary);
  font-size: var(--text-sm);
  line-height: var(--leading-relaxed);
}

.modal-section p {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .hongli-header { padding: var(--space-3) var(--page-padding-mobile); }
  .header-inner { flex-direction: column; align-items: flex-start; }
  .header-title { font-size: var(--text-xl); }
  .hongli-main { padding: var(--space-3) var(--page-padding-mobile); }
  .charts-grid {
    gap: 10px;
  }
  .chart-card { padding: var(--space-3) var(--space-4) var(--space-3); }
  .chart-box { height: 220px; }
}
</style>
