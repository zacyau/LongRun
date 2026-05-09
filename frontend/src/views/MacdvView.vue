<template>
  <div class="macdv-view">
    <header class="macdv-header">
      <div class="header-inner">
        <div class="header-brand">
          <div class="brand-tag">量化信号</div>
          <div class="brand-info">
            <h1 class="header-title">趋势信号</h1>
            <p class="header-subtitle">MACD-V · RSI14 买卖信号研判工具</p>
          </div>
        </div>
        <div class="header-actions">
          <span class="update-time" v-if="store.data">更新: {{ store.data.updated_at }}</span>
        </div>
      </div>
    </header>

    <main class="macdv-main">
      <!-- 搜索面板 -->
      <div class="search-card">
        <div class="search-row">
          <div class="search-input-wrap">
            <textarea
              v-model="inputText"
              class="search-input"
              placeholder="输入股票代码，支持逗号，空格或换行分隔，如：000001、sh600519、sz399317"
              rows="3"
              @keydown.ctrl.enter="handleQuery"
              @keydown.meta.enter="handleQuery"
            ></textarea>
            <button v-if="inputText" class="input-clear" @click="inputText = ''">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <button
            class="query-btn"
            :disabled="!canQuery || store.loading"
            @click="handleQuery"
          >
            <span v-if="store.loading" class="btn-spinner"></span>
            <span v-else class="btn-icon">⌕</span>
            {{ store.loading ? '查询中...' : '批量查询' }}
          </button>
        </div>
        <div v-if="store.history.length > 0 && !store.data" class="history-row">
          <span class="history-label">最近:</span>
          <div class="history-tags">
            <button
              v-for="q in store.history.slice(0, 8)"
              :key="q"
              class="history-tag"
              @click="appendQuery(q)"
            >{{ q }}</button>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="store.error" class="error-banner">
        <span>{{ store.error }}</span>
        <button @click="store.error = null">×</button>
      </div>

      <!-- 结果 -->
      <div v-if="store.data" class="result-card">
        <div class="result-head">
          <h2 class="result-title">查询结果</h2>
          <span class="result-count">{{ store.data.results.length }} 只股票</span>
        </div>

        <div class="table-wrap">
          <table class="result-table">
            <thead>
              <tr>
                <th>股票名称</th>
                <th>代码</th>
                <th>日期</th>
                <th>现价</th>
                <th>MACD-V</th>
                <th>RSI 14</th>
                <th>买卖建议</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, idx) in store.data.results" :key="idx" :class="{ 'row-error': item.error }">
                <template v-if="!item.error">
                  <td class="cell-name">{{ item.stock_name }}</td>
                  <td class="cell-code">{{ item.stock_code }}</td>
                  <td class="cell-date">{{ item.trade_date }}</td>
                  <td class="cell-price">{{ item.current_price }}</td>
                  <td class="cell-indicator">
                    <span :class="macdvClass(item.macdv)">{{ item.macdv }}</span>
                    <span class="tag" :class="macdvTagClass(item.macdv_trend)">{{ macdvTrendText(item.macdv_trend) }}</span>
                  </td>
                  <td class="cell-indicator">
                    <span :class="rsiClass(item.rsi14)">{{ item.rsi14 }}</span>
                    <span class="tag" :class="rsiTagClass(item.rsi14_signal)">{{ rsiSignalText(item.rsi14_signal) }}</span>
                  </td>
                  <td>
                    <span class="rec-tag" :class="recTagClass(item.recommendation)">{{ item.recommendation }}</span>
                  </td>
                </template>
                <template v-else>
                  <td class="cell-name">{{ item.stock_name }}</td>
                  <td colspan="6" class="cell-error">{{ item.error }}</td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 使用说明 -->
      <div class="guide-card">
        <button class="guide-toggle" @click="guideExpanded = !guideExpanded">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/>
          </svg>
          <span>使用说明</span>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
               :class="{ 'arrow-open': guideExpanded }" class="toggle-arrow">
            <path d="M19 9l-7 7-7-7"/>
          </svg>
        </button>
        <div v-if="guideExpanded" class="guide-panel">
          <div class="guide-grid">
            <div class="guide-col">
              <h3 class="guide-col-title">指标说明</h3>
              <ul class="guide-list">
                <li><strong>MACD-V</strong>：衡量价格动量与波动率的比值，反映趋势强度。数值越大涨势越强，越小跌势越猛。</li>
                <li><strong>RSI 14</strong>：相对强弱指标，衡量超买超卖状态。&gt;70 超买，&lt;30 超卖。</li>
              </ul>
            </div>
            <div class="guide-col">
              <h3 class="guide-col-title">交易信号</h3>
              <div class="signal-rows">
                <div class="signal-row">
                  <span class="rec-tag rec-tag-blue">右侧买点</span>
                  <span class="signal-desc">MACD-V +50~+150（确认强势）+ RSI &lt; 30（超卖）</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-green">左侧买点</span>
                  <span class="signal-desc">MACD-V &lt; -150（恐慌性超卖）+ RSI &lt; 30（超卖）</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-red">左侧卖点</span>
                  <span class="signal-desc">MACD-V &gt; +150（情绪过热）+ RSI &gt; 70（超买）</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-orange">右侧卖点</span>
                  <span class="signal-desc">MACD-V &lt; +50（趋势转弱）+ RSI &gt; 70（超买）</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-gray">观望</span>
                  <span class="signal-desc">MACD-V 在 -50~+50 区间（无趋势区），无论 RSI 如何</span>
                </div>
              </div>
            </div>
          </div>
          <p class="guide-disclaimer">以上信号仅供参考，不构成投资建议。</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useMacdvStore } from '@/stores/macdvStore'

const store = useMacdvStore()
const inputText = ref('')
const guideExpanded = ref(false)

const canQuery = computed(() => inputText.value.trim().length > 0)

function handleQuery() {
  if (!canQuery.value || store.loading) return
  store.queryStocks(inputText.value)
}

function appendQuery(q: string) {
  const existing = inputText.value.split(/[,，\s\n]+/).map(s => s.trim()).filter(Boolean)
  if (!existing.includes(q)) {
    inputText.value = inputText.value ? `${inputText.value}\n${q}` : q
  }
}

function macdvClass(v: number) {
  if (v > 0) return 'val-red'
  if (v < 0) return 'val-green'
  return 'val-gray'
}

function macdvTagClass(trend: string) {
  const map: Record<string, string> = {
    momentum_peak: 'tag-red',
    strong_up: 'tag-orange',
    oscillation: 'tag-gray',
    strong_down: 'tag-cyan',
    momentum_decay: 'tag-purple',
  }
  return map[trend] || 'tag-gray'
}

function macdvTrendText(trend: string) {
  const map: Record<string, string> = {
    momentum_peak: '动量峰值',
    strong_up: '强劲上涨',
    oscillation: '震荡',
    strong_down: '强劲下跌',
    momentum_decay: '动量衰竭',
  }
  return map[trend] || '震荡'
}

function rsiClass(v: number) {
  if (v > 70) return 'val-red'
  if (v < 30) return 'val-green'
  return 'val-gray'
}

function rsiTagClass(signal: string) {
  if (signal === 'overbought') return 'tag-red'
  if (signal === 'oversold') return 'tag-green'
  return 'tag-gray'
}

function rsiSignalText(signal: string) {
  if (signal === 'overbought') return '超买'
  if (signal === 'oversold') return '超卖'
  return '中性'
}

function recTagClass(rec: string | null) {
  if (rec === '右侧买点') return 'rec-tag-blue'
  if (rec === '左侧买点') return 'rec-tag-green'
  if (rec === '左侧卖点') return 'rec-tag-red'
  if (rec === '右侧卖点') return 'rec-tag-orange'
  return 'rec-tag-gray'
}
</script>

<style scoped>
.macdv-view {
  min-height: calc(100vh - 56px);
  background: #F7F8FA;
}

.macdv-header {
  background: #fff;
  border-bottom: 1px solid #EBEBEB;
  padding: 18px 32px;
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

.update-time {
  font-size: 12px;
  color: #999;
}

.macdv-main {
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 32px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-card {
  background: #fff;
  border-radius: 10px;
  padding: 18px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 0 0 1px rgba(0,0,0,0.03);
}

.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.search-input-wrap {
  flex: 1;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 9px 36px 9px 14px;
  border: 1px solid #E8E8E8;
  border-radius: 7px;
  font-size: 14px;
  color: #1A1A1A;
  background: #FAFAFA;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
}

.search-input:focus {
  border-color: #2962FF;
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.08);
  background: #fff;
}

.search-input::placeholder {
  color: #CCC;
}

.input-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: #AAA;
  padding: 4px;
  display: flex;
  align-items: center;
}

.input-clear:hover { color: #666; }

.query-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 20px;
  background: #1A1A1A;
  color: #fff;
  border: none;
  border-radius: 7px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.query-btn:hover:not(:disabled) { background: #333; }
.query-btn:disabled { background: #CCC; cursor: not-allowed; }

.btn-icon { font-size: 15px; }

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.history-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid #F0F0F0;
}

.history-label {
  font-size: 12px;
  color: #AAA;
  flex-shrink: 0;
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.history-tag {
  background: #F5F5F5;
  border: 1px solid #E8E8E8;
  border-radius: 4px;
  padding: 2px 8px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.15s;
}

.history-tag:hover {
  background: #F0F0F0;
  border-color: #CCC;
  color: #333;
}

.error-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #FFF2F0;
  border: 1px solid #FFCCC7;
  color: #CF1322;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
}

.error-banner button {
  background: none;
  border: none;
  color: #CF1322;
  font-size: 18px;
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
}

.result-card {
  background: #fff;
  border-radius: 10px;
  padding: 20px 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 0 0 1px rgba(0,0,0,0.03);
}

.result-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.result-title {
  font-size: 15px;
  font-weight: 600;
  color: #1A1A1A;
  margin: 0;
}

.result-count {
  font-size: 12px;
  color: #AAA;
}

.table-wrap {
  overflow-x: auto;
}

.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.result-table th {
  background: #F8F9FA;
  font-weight: 600;
  color: #555;
  font-size: 12px;
  padding: 8px 12px;
  text-align: left;
  border-bottom: 1.5px solid #EBEBEB;
  white-space: nowrap;
}

.result-table td {
  padding: 9px 12px;
  border-bottom: 1px solid #F5F5F5;
  color: #333;
  vertical-align: middle;
}

.result-table tbody tr:hover td {
  background: #FAFAFA;
}

.row-error td {
  color: #CF1322;
  font-size: 12px;
}

.cell-name { font-weight: 600; color: #1A1A1A !important; }
.cell-code { color: #888 !important; font-size: 12px; }
.cell-date { color: #888 !important; font-size: 12px; white-space: nowrap; }
.cell-price { font-weight: 600 !important; white-space: nowrap; }
.cell-indicator { white-space: nowrap; }
.cell-error { font-size: 12px !important; }

.val-red { color: #DC2626; font-weight: 700; }
.val-green { color: #059669; font-weight: 700; }
.val-gray { color: #374151; font-weight: 700; }

.tag {
  display: inline-block;
  margin-left: 5px;
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
}

.tag-red { background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }
.tag-orange { background: #FFF7ED; color: #EA580C; border: 1px solid #FED7AA; }
.tag-gray { background: #F9FAFB; color: #6B7280; border: 1px solid #E5E7EB; }
.tag-cyan { background: #ECFEFF; color: #0891B2; border: 1px solid #A5F3FC; }
.tag-purple { background: #FAF5FF; color: #7C3AED; border: 1px solid #DDD6FE; }
.tag-green { background: #F0FDF4; color: #059669; border: 1px solid #BBF7D0; }

.rec-tag {
  display: inline-block;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.rec-tag-blue { background: #EFF6FF; color: #1D4ED8; border: 1px solid #BFDBFE; }
.rec-tag-green { background: #F0FDF4; color: #047857; border: 1px solid #A7F3D0; }
.rec-tag-red { background: #FEF2F2; color: #B91C1C; border: 1px solid #FECACA; }
.rec-tag-orange { background: #FFF7ED; color: #C2410C; border: 1px solid #FED7AA; }
.rec-tag-gray { background: #F9FAFB; color: #6B7280; border: 1px solid #E5E7EB; }

.guide-card {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 0 0 1px rgba(0,0,0,0.03);
  overflow: hidden;
}

.guide-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border: none;
  background: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: #666;
  width: 100%;
  transition: background 0.15s;
}

.guide-toggle:hover { background: #FAFAFA; }

.toggle-arrow {
  margin-left: auto;
  transition: transform 0.2s;
}

.arrow-open { transform: rotate(180deg); }

.guide-panel {
  border-top: 1px solid #F0F0F0;
  padding: 16px 20px;
}

.guide-grid {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: 24px;
}

.guide-col-title {
  font-size: 12px;
  font-weight: 600;
  color: #1A1A1A;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 10px;
  padding-bottom: 8px;
  border-bottom: 1.5px solid #EBEBEB;
}

.guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-list li {
  font-size: 13px;
  color: #555;
  padding: 4px 0;
  line-height: 1.6;
}

.guide-list strong { color: #1A1A1A; }

.signal-rows {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.signal-desc {
  color: #666;
  line-height: 1.5;
}

.guide-disclaimer {
  font-size: 12px;
  color: #AAA;
  text-align: center;
  margin: 16px 0 0;
  padding-top: 12px;
  border-top: 1px solid #F0F0F0;
}

@media (max-width: 768px) {
  .macdv-header { padding: 14px 16px; }
  .header-inner { flex-direction: column; align-items: flex-start; }
  .header-title { font-size: 17px; }
  .macdv-main { padding: 12px 16px; }
  .search-row { flex-direction: column; }
  .query-btn { width: 100%; justify-content: center; }
  .guide-grid { grid-template-columns: 1fr; gap: 16px; }
  .guide-panel { padding: 14px 16px; }
}
</style>