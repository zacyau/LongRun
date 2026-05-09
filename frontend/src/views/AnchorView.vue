<template>
  <div class="anchor-view">
    <header class="anchor-header">
      <div class="header-inner">
        <div class="header-brand">
          <div class="brand-tag">技术分析</div>
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
        <div class="chart-section">
          <LoadingOverlay :loading="store.loading" />
          <RsiChart :data="store.data" />
        </div>
        <div class="chart-section">
          <LoadingOverlay :loading="store.loading" />
          <DrawdownChart :data="store.data" />
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
  min-height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}

.anchor-header {
  background: #ffffff;
  border-bottom: 1px solid #EBEBEB;
  padding: 18px 32px;
  position: sticky;
  top: 56px;
  z-index: 50;
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
}

.header-subtitle {
  font-size: 13px;
  color: #999;
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
  border: 1px solid #E8E8E8;
  border-radius: 7px;
  background: #FAFAFA;
  color: #888;
  cursor: pointer;
  transition: all 0.15s;
  flex-shrink: 0;
}

.guide-btn:hover {
  background: #F0F0F0;
  border-color: #CCC;
  color: #555;
}

.anchor-main {
  flex: 1;
  padding: 24px 32px;
  background: #F7F8FA;
}

.charts-container {
  max-width: 1280px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.chart-section {
  position: relative;
}

.main-chart-section {
  min-height: 420px;
}

.error-toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  background: #1A1A1A;
  color: white;
  padding: 12px 20px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  z-index: 100;
  animation: slideUp 0.3s ease;
  font-size: 14px;
}

.error-close {
  background: none;
  border: none;
  color: rgba(255,255,255,0.6);
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
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
    padding: 12px 16px;
  }
  .header-inner {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-title { font-size: 17px; }
  .header-subtitle { display: none; }
  .anchor-main { padding: 12px 16px; }
  .charts-container { gap: 10px; }
  .main-chart-section { min-height: 280px; }
}
</style>