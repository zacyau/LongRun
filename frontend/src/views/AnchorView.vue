<!--
 * AnchorView.vue - 国证A股指数"五年之锚"分析页面
 *
 * 功能说明：
 * 本页面展示国证A股指数（SZ.399317）的技术分析图表，主要包含：
 * 1. 主图表：显示价格走势与SMA1210±15%包络线
 * 2. RSI图表：展示RSI周期指标
 * 3. 回撤图表：展示滚动最大回撤
 *
 * 主要交互：
 * - 时间范围选择（1年/3年/5年/全部/自定义）
 * - 刷新数据功能
 * - 使用指南弹窗
 -->

<template>
  <!-- 主容器：整体页面布局 -->
  <div class="anchor-view">

    <!-- 页面顶部导航栏 -->
    <header class="anchor-header">
      <div class="header-inner">
        <!-- 品牌信息区域：标题和副标题 -->
        <div class="header-brand">
          <div class="brand-info">
            <!-- 主标题：指数名称和分析主题 -->
            <h1 class="header-title">国证A股指数 <span class="title-sep">·</span> 五年之锚</h1>
            <!-- 副标题：使用的技术指标说明 -->
            <p class="header-subtitle">SMA1210 ±15% 包络线 · RSI 周期 · 滚动最大回撤</p>
          </div>
        </div>

        <!-- 右上角操作按钮区域 -->
        <div class="header-actions">
          <!-- 时间范围选择器组件：支持预设范围和自定义日期 -->
          <TimeRangeSelector
            v-model="store.selectedRange"
            v-model:customStart="store.customStartDate"
            v-model:customEnd="store.customEndDate"
            :loading="store.loading"
            @change="handleRangeChange"
            @refresh="handleRefresh"
          />
          <!-- 使用指南按钮：点击后弹出说明弹窗 -->
          <button class="guide-btn" @click="showGuide = true">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <!-- 页面主内容区域 -->
    <main class="anchor-main">

      <!-- 图表容器：当数据加载成功时显示 -->
      <div v-if="store.data" class="charts-container">
        <!-- 主图表区域：显示价格、包络线等核心数据 -->
        <div class="chart-section main-chart-section">
          <MainChart :data="store.data" />
        </div>

        <!-- 副图表区域：包含RSI和回撤两个子图表 -->
        <div class="sub-charts">
          <!-- RSI图表：展示RSI周期指标 -->
          <div class="chart-section">
            <RsiChart :data="store.data" />
          </div>
          <!-- 回撤图表：展示滚动最大回撤 -->
          <div class="chart-section">
            <DrawdownChart :data="store.data" />
          </div>
        </div>
      </div>

      <!-- 加载状态：数据请求进行中时显示 -->
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

    <!-- 错误提示：请求失败时显示的错误提示条 -->
    <div v-if="store.error" class="error-toast">
      <span>{{ store.error }}</span>
      <button class="error-close" @click="store.error = null">×</button>
    </div>

    <!-- 使用指南弹窗组件 -->
    <UsageGuideModal :visible="showGuide" @close="showGuide = false" />
  </div>
</template>

<script setup lang="ts">
/*
 * AnchorView 组件逻辑
 *
 * 状态管理：
 * - store: 使用anchorStore管理全局状态，包括图表数据、加载状态、错误信息、时间范围选择
 * - showGuide: 控制使用指南弹窗的显示/隐藏
 *
 * 生命周期：
 * - onMounted: 组件挂载时自动获取"全部"时间范围的图表数据
 *
 * 事件处理：
 * - handleRangeChange: 处理时间范围变更，重新获取对应范围的图表数据
 * - handleRefresh: 刷新数据，先调用后端刷新接口，再重新获取图表数据
 */
import { onMounted, ref } from 'vue'
import { useAnchorStore } from '@/stores/anchorStore'
import type { TimeRangeOption } from '@/types/anchor'

import MainChart from '@/components/anchor/MainChart.vue'
import RsiChart from '@/components/anchor/RsiChart.vue'
import DrawdownChart from '@/components/anchor/DrawdownChart.vue'
import TimeRangeSelector from '@/components/anchor/TimeRangeSelector.vue'
import UsageGuideModal from '@/components/anchor/UsageGuideModal.vue'

/*
 * 组件状态
 * - showGuide: 布尔值，控制使用指南弹窗的显示状态
 */
const store = useAnchorStore()
const showGuide = ref(false)

/*
 * handleRangeChange - 处理时间范围变更
 * @param range: 新的时间范围选项
 * 功能：调用store的fetchData方法，根据选定的时间范围重新获取图表数据
 */
function handleRangeChange(range: TimeRangeOption) {
  store.fetchData(range)
}

/*
 * handleRefresh - 刷新图表数据
 * 功能：先调用后端API刷新数据缓存，再重新获取最新的图表数据
 */
function handleRefresh() {
  store.refreshData()
}

/*
 * 组件挂载时的初始化逻辑
 * 功能：自动获取"全部"时间范围的图表数据，用于首次加载页面时展示
 */
onMounted(() => {
  store.fetchData('all')
})
</script>

<style scoped>
/* 页面主容器：flex纵向布局，占满视口高度 */
.anchor-view {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

/* 顶部导航栏：卡片背景，底部边框分隔 */
.anchor-header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-default);
  padding: var(--space-5) var(--page-padding);
  touch-action: manipulation;
}

/* 导航栏内部容器：最大宽度限制，水平两端对齐 */
.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-5);
}

/* 品牌区域：向左对齐 */
.header-brand {
  display: flex;
  align-items: flex-start;
}

/* 主标题：大号加粗字体 */
.header-title {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--color-text-primary);
  margin: 0 0 4px;
  letter-spacing: -0.01em;
}

/* 标题分隔符：浅色样式 */
.title-sep {
  color: var(--color-border-default);
  font-weight: 400;
}

/* 副标题：较小字号，浅色文字 */
.header-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-tertiary);
  margin: 0;
}

/* 右上角操作区：水平排列，固定宽度不收缩 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

/* 指南按钮：圆形图标按钮，hover时高亮 */
.guide-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  background: var(--color-bg-subtle);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.guide-btn:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

/* 主内容区：flex占比1填充剩余空间 */
.anchor-main {
  flex: 1;
  padding: var(--space-6) var(--page-padding);
  background: var(--color-bg-page);
  touch-action: manipulation;
}

/* 图表容器：纵向排列，最大宽度限制 */
.charts-container {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 副图表区域：包含RSI和回撤两个子图 */
.sub-charts {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 图表区域：相对定位，支持触摸操作 */
.chart-section {
  position: relative;
  touch-action: manipulation;
}

/* 主图表最小高度：确保主图有足够显示空间 */
.main-chart-section {
  min-height: 420px;
}

/* 错误提示：固定在底部居中，动画滑入效果 */
.error-toast {
  position: fixed;
  bottom: var(--space-6);
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-primary);
  color: white;
  padding: var(--space-3) var(--space-5);
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  gap: var(--space-3);
  box-shadow: var(--shadow-elevated);
  z-index: 100;
  animation: slideUp 0.3s ease;
  font-size: var(--text-md);
}

/* 错误提示关闭按钮 */
.error-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.6);
  font-size: var(--text-xl);
  cursor: pointer;
  padding: 0;
  width: var(--space-6);
  height: var(--space-6);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.error-close:hover {
  color: #fff;
}

/* 滑入动画定义 */
@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(16px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

/* 加载状态：居中显示，弹性列布局 */
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

/* 加载动画圆点：弹性缩放动画 */
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

/* 圆点弹跳动画 */
@keyframes dotBounce {
  0%, 80%, 100% { transform: scale(0.4); opacity: 0.3; }
  40% { transform: scale(1.2); opacity: 1; }
}

/* 空状态：居中灰色文字 */
.empty-state {
  text-align: center;
  padding: 60px;
  color: var(--color-text-tertiary);
  font-size: var(--text-md);
}

/* 移动端响应式布局 */
@media (max-width: 768px) {
  .anchor-header {
    padding: var(--space-3) var(--page-padding-mobile);
  }
  .header-inner {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-title { font-size: var(--text-xl); }
  .header-subtitle { display: none; }
  .anchor-main { padding: var(--space-3) var(--page-padding-mobile); }
  .charts-container { gap: 10px; }
  .sub-charts {
    gap: 10px;
  }
  .main-chart-section { min-height: 280px; }
}
</style>