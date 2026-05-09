<template>
  <div class="anchor-view">
    <header class="anchor-header">
      <div class="header-inner">
        <div class="header-brand">
          <div class="brand-info">
            <h1 class="header-title">国证A股指数 <span class="title-sep">·</span> 五年之锚</h1>
            <p class="header-subtitle">SMA1210 ±15% 包络线 · RSI 周期 · 滚动最大回撤</p>
          </div>
        </div>
        <div class="header-actions">
          <TimeRangeSelector
            v-model="store.selectedRange"
            v-model:customStart="store.customStartDate"
            v-model:customEnd="store.customEndDate"
            :loading="store.loading"
            @change="handleRangeChange"
            @refresh="handleRefresh"
          />
          <button class="guide-btn" @click="showGuide = true">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
            </svg>
          </button>
        </div>
      </div>
    </header>

    <main class="anchor-main">
      <div class="charts-container">
        <div class="chart-section main-chart-section">
          <LoadingOverlay :loading="store.loading" />
          <MainChart :data="store.data" />
        </div>
        <div class="sub-charts">
          <div class="chart-section">
            <LoadingOverlay :loading="store.loading" />
            <RsiChart :data="store.data" />
          </div>
          <div class="chart-section">
            <LoadingOverlay :loading="store.loading" />
            <DrawdownChart :data="store.data" />
          </div>
        </div>
      </div>
    </main>

    <div v-if="store.error" class="error-toast">
      <span>{{ store.error }}</span>
      <button class="error-close" @click="store.error = null">×</button>
    </div>

    <UsageGuideModal :visible="showGuide" @close="showGuide = false" />
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useAnchorStore } from '@/stores/anchorStore'
import type { TimeRangeOption } from '@/types/anchor'

import MainChart from '@/components/anchor/MainChart.vue'
import RsiChart from '@/components/anchor/RsiChart.vue'
import DrawdownChart from '@/components/anchor/DrawdownChart.vue'
import TimeRangeSelector from '@/components/anchor/TimeRangeSelector.vue'
import LoadingOverlay from '@/components/common/LoadingOverlay.vue'
import UsageGuideModal from '@/components/anchor/UsageGuideModal.vue'

const store = useAnchorStore()
const showGuide = ref(false)

function handleRangeChange(range: TimeRangeOption) {
  store.fetchData(range)
}

function handleRefresh() {
  store.refreshData()
}

onMounted(() => {
  store.fetchData('all')
})
</script>

<style scoped>
.anchor-view {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  flex-direction: column;
  touch-action: manipulation;
}

.anchor-header {
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
}

.header-subtitle {
  font-size: var(--text-base);
  color: var(--color-text-tertiary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}

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

.anchor-main {
  flex: 1;
  padding: var(--space-6) var(--page-padding);
  background: var(--color-bg-page);
  touch-action: manipulation;
}

.charts-container {
  max-width: var(--max-width);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.sub-charts {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.chart-section {
  position: relative;
  touch-action: manipulation;
}

.main-chart-section {
  min-height: 420px;
}

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

@keyframes slideUp {
  from { opacity: 0; transform: translateX(-50%) translateY(16px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}

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
