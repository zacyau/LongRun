<!--
 * MacdvView.vue - MACD-V 趋势信号查询页面
 *
 * 功能说明：
 * 本页面提供股票MACD-V和RSI14指标的批量查询功能，
 * 帮助投资者快速了解多只股票的趋势状态和动量情况。
 *
 * 主要功能：
 * - 支持批量输入股票代码（支持多种格式：000001、sh600519、sz399317等）
 * - 展示每只股票的MACD-V数值和趋势状态标签
 * - 展示每只股票的RSI14数值和信号标签
 * - 状态描述综合判断
 *
 * MACD-V 说明：
 * MACD-V是MACD与波动率的比值，用于衡量价格动量与市场波动的相对强度
 *
 * 状态标签：
 * - 极度多头/强势多头/温和多头/中性/强势空头/极度空头（MACD-V）
 * - 极度超买/超买/中性偏强/中性/中性偏弱/超卖/极度超卖（RSI）
 -->

<template>
  <!-- 主容器 -->
  <div class="macdv-view">

    <!-- 页面顶部导航栏 -->
    <header class="macdv-header">
      <div class="header-inner">
        <!-- 品牌区域 -->
        <div class="header-brand">
          <div class="brand-info">
            <h1 class="header-title">趋势信号</h1>
            <p class="header-subtitle">MACD-V · RSI14 状态研判工具</p>
          </div>
        </div>
        <!-- 更新时间显示 -->
        <div class="header-actions">
          <span class="update-time" v-if="store.data">更新: {{ store.data.updated_at }}</span>
        </div>
      </div>
    </header>

    <!-- 页面主内容区 -->
    <main class="macdv-main">

      <!-- 搜索面板：输入股票代码进行查询 -->
      <div class="search-card">
        <div class="search-row">
          <!-- 股票代码输入框：支持多行输入和多种格式 -->
          <div class="search-input-wrap">
            <textarea
              v-model="inputText"
              class="search-input"
              placeholder="输入股票代码，支持逗号，空格或换行分隔，如：000001、sh600519、sz399317"
              rows="3"
              @keydown.ctrl.enter="handleQuery"
              @keydown.meta.enter="handleQuery"
            ></textarea>
            <!-- 清空输入按钮 -->
            <button v-if="inputText" class="input-clear" @click="inputText = ''">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
          <!-- 批量查询按钮 -->
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

        <!-- 历史查询记录：快速复用之前的查询 -->
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

      <!-- 错误提示：请求失败时显示 -->
      <div v-if="store.error" class="error-banner">
        <span>{{ store.error }}</span>
        <button @click="store.error = null">×</button>
      </div>

      <!-- 查询结果表格：展示各股票的指标数据 -->
      <div v-if="store.data" class="result-card">
        <div class="result-head">
          <h2 class="result-title">查询结果</h2>
          <span class="result-count">{{ store.data.results.length }} 只股票</span>
        </div>

        <!-- 结果数据表格 -->
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
                <th>状态描述</th>
              </tr>
            </thead>
            <tbody>
              <!-- 遍历每只股票的查询结果 -->
              <tr v-for="(item, idx) in store.data.results" :key="idx" :class="{ 'row-error': item.error }">
                <!-- 正常结果 -->
                <template v-if="!item.error">
                  <td class="cell-name">{{ item.stock_name }}</td>
                  <td class="cell-code">{{ item.stock_code }}</td>
                  <td class="cell-date">{{ item.trade_date }}</td>
                  <td class="cell-price">{{ item.current_price }}</td>
                  <!-- MACD-V指标单元格：包含数值和状态标签 -->
                  <td class="cell-indicator">
                    <span :class="macdvClass(item.macdv)">{{ item.macdv }}</span>
                    <span class="tag" :class="macdvTagClass(item.macdv_trend)">{{ macdvTrendText(item.macdv_trend) }}</span>
                  </td>
                  <!-- RSI指标单元格：包含数值和信号标签 -->
                  <td class="cell-indicator">
                    <span :class="rsiClass(item.rsi14)">{{ item.rsi14 }}</span>
                    <span class="tag" :class="rsiTagClass(item.rsi14_signal)">{{ rsiSignalText(item.rsi14_signal) }}</span>
                  </td>
                  <!-- 状态描述 -->
                  <td>
                    <span class="rec-tag" :class="statusTagClass(item.status_description)">{{ item.status_description }}</span>
                  </td>
                </template>
                <!-- 查询错误结果 -->
                <template v-else>
                  <td class="cell-name">{{ item.stock_name }}</td>
                  <td colspan="6" class="cell-error">{{ item.error }}</td>
                </template>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 使用说明面板：可展开的指标解释 -->
      <div class="guide-card">
        <!-- 展开/收起切换按钮 -->
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

        <!-- 展开后的说明内容 -->
        <div v-if="guideExpanded" class="guide-panel">
          <div class="guide-grid">
            <!-- 左栏：指标基础说明 -->
            <div class="guide-col">
              <h3 class="guide-col-title">指标说明</h3>
              <ul class="guide-list">
                <li><strong>MACD-V</strong>：衡量价格动量与波动率的比值，反映趋势强度。数值越大涨势越强，越小跌势越猛。</li>
                <li><strong>RSI 14</strong>：相对强弱指标，衡量超买超卖状态。&gt;70 超买，&lt;30 超卖。</li>
              </ul>
            </div>

            <!-- 右栏：MACD-V和RSI的状态标签说明 -->
            <div class="guide-col">
              <h3 class="guide-col-title">MACD-V 状态标签</h3>
              <div class="signal-rows">
                <div class="signal-row">
                  <span class="rec-tag rec-tag-red">极度多头</span>
                  <span class="signal-desc">MACD-V &gt; +150，动能极端狂热</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-orange">强势多头</span>
                  <span class="signal-desc">MACD-V +50 ~ +150，动能充裕</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-rose">温和多头</span>
                  <span class="signal-desc">MACD-V 0 ~ +50，略偏多</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-gray">中性</span>
                  <span class="signal-desc">MACD-V -50 ~ +50，无趋势区</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-cyan">强势空头</span>
                  <span class="signal-desc">MACD-V -150 ~ -50，空方主导</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-purple">极度空头</span>
                  <span class="signal-desc">MACD-V &lt; -150，恐慌性超卖区</span>
                </div>
              </div>

              <h3 class="guide-col-title" style="margin-top:16px">RSI14 状态标签</h3>
              <div class="signal-rows">
                <div class="signal-row">
                  <span class="rec-tag rec-tag-red">极度超买</span>
                  <span class="signal-desc">RSI &gt; 80</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-orange">超买</span>
                  <span class="signal-desc">RSI 70 ~ 80</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-rose">中性偏强</span>
                  <span class="signal-desc">RSI 55 ~ 70</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-gray">中性</span>
                  <span class="signal-desc">RSI 45 ~ 55</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-cyan">中性偏弱</span>
                  <span class="signal-desc">RSI 30 ~ 45</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-green">超卖</span>
                  <span class="signal-desc">RSI 20 ~ 30</span>
                </div>
                <div class="signal-row">
                  <span class="rec-tag rec-tag-purple">极度超卖</span>
                  <span class="signal-desc">RSI &lt; 20</span>
                </div>
              </div>
            </div>
          </div>
          <p class="guide-disclaimer">以上状态描述仅供参考，不构成投资建议。</p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
/*
 * MacdvView 组件逻辑
 *
 * 状态管理：
 * - store: 使用macdvStore管理查询数据和加载状态
 * - inputText: 用户输入的股票代码文本
 * - guideExpanded: 使用说明面板的展开/收起状态
 *
 * 核心功能：
 * - 批量查询：支持同时查询多只股票的MACD-V和RSI指标
 * - 历史记录：保存最近的查询，支持快速复用
 */
import { ref, computed } from 'vue'
import { useMacdvStore } from '@/stores/macdvStore'

const store = useMacdvStore()
const inputText = ref('')
const guideExpanded = ref(false)

/*
 * canQuery - 计算属性：判断是否可以执行查询
 * 条件：输入框有内容且当前不在加载状态
 */
const canQuery = computed(() => inputText.value.trim().length > 0)

/*
 * handleQuery - 处理查询请求
 * 功能：解析输入文本，调用store的queryStocks方法执行批量查询
 */
function handleQuery() {
  if (!canQuery.value || store.loading) return
  store.queryStocks(inputText.value)
}

/*
 * appendQuery - 追加查询项
 * @param q: 要追加的股票代码
 * 功能：将新的股票代码追加到现有输入中（如果尚未存在）
 */
function appendQuery(q: string) {
  const existing = inputText.value.split(/[,，\s\n]+/).map(s => s.trim()).filter(Boolean)
  if (!existing.includes(q)) {
    inputText.value = inputText.value ? `${inputText.value}\n${q}` : q
  }
}

/*
 * macdvClass - MACD-V数值颜色样式
 * @param v: MACD-V数值
 * 返回：红色（正值）、绿色（负值）、灰色（零值）
 */
function macdvClass(v: number) {
  if (v > 0) return 'val-red'
  if (v < 0) return 'val-green'
  return 'val-gray'
}

/*
 * macdvTagClass - MACD-V趋势标签颜色
 * @param trend: 趋势状态文本
 * 返回：对应颜色的样式类名
 */
function macdvTagClass(trend: string) {
  const map: Record<string, string> = {
    '极度多头': 'tag-red',
    '强势多头': 'tag-orange',
    '温和多头': 'tag-rose',
    '中性': 'tag-gray',
    '强势空头': 'tag-cyan',
    '极度空头': 'tag-purple',
  }
  return map[trend] || 'tag-gray'
}

/*
 * macdvTrendText - MACD-V趋势文本
 * 返回：如果趋势文本为空则返回"中性"
 */
function macdvTrendText(trend: string) {
  return trend || '中性'
}

/*
 * rsiClass - RSI数值颜色样式
 * @param v: RSI数值
 * 返回：红色（>70超买）、绿色（<30超卖）、灰色（正常）
 */
function rsiClass(v: number) {
  if (v > 70) return 'val-red'
  if (v < 30) return 'val-green'
  return 'val-gray'
}

/*
 * rsiTagClass - RSI信号标签颜色
 * @param signal: RSI信号文本
 * 返回：对应颜色的样式类名
 */
function rsiTagClass(signal: string) {
  const map: Record<string, string> = {
    '极度超买': 'tag-red',
    '超买': 'tag-orange',
    '中性偏强': 'tag-rose',
    '中性': 'tag-gray',
    '中性偏弱': 'tag-cyan',
    '超卖': 'tag-green',
    '极度超卖': 'tag-purple',
  }
  return map[signal] || 'tag-gray'
}

/*
 * rsiSignalText - RSI信号文本
 * 返回：如果信号文本为空则返回"中性"
 */
function rsiSignalText(signal: string) {
  return signal || '中性'
}

/*
 * statusTagClass - 状态描述标签颜色
 * @param desc: 状态描述文本
 * 返回：根据描述内容匹配对应颜色的样式类名
 * 逻辑：
 * - 包含"极端"或"强烈背离" -> 红色
 * - 包含"健康"、"未过热"、"未超跌" -> 绿色
 * - 包含"过热"、"过冷"、"超买" -> 橙色
 * - 包含"均衡"、"盘整" -> 灰色
 * - 包含"回调"、"反弹" -> 青色
 */
function statusTagClass(desc: string | null) {
  if (!desc) return 'rec-tag-gray'
  if (desc.includes('极端') || desc.includes('强烈背离')) return 'rec-tag-red'
  if (desc.includes('健康') || desc.includes('未过热') || desc.includes('未超跌')) return 'rec-tag-green'
  if (desc.includes('过热') || desc.includes('过冷') || desc.includes('超买')) return 'rec-tag-orange'
  if (desc.includes('均衡') || desc.includes('盘整')) return 'rec-tag-gray'
  if (desc.includes('回调') || desc.includes('反弹')) return 'rec-tag-cyan'
  return 'rec-tag-gray'
}
</script>

<style scoped>
/* 页面主容器 */
.macdv-view {
  min-height: calc(100vh - var(--header-height));
  background: var(--color-bg-page);
}

/* 顶部导航栏 */
.macdv-header {
  background: var(--color-bg-card);
  border-bottom: 1px solid var(--color-border-default);
  padding: var(--space-5) var(--page-padding);
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

.update-time {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

/* 主内容区 */
.macdv-main {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: var(--space-6) var(--page-padding);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* 搜索卡片 */
.search-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-card);
}

/* 搜索行：输入框和按钮水平排列 */
.search-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

/* 输入框包装器 */
.search-input-wrap {
  flex: 1;
  position: relative;
}

/* 股票代码输入框 */
.search-input {
  width: 100%;
  padding: 9px 36px 9px 14px;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  color: var(--color-text-primary);
  background: var(--color-bg-input);
  outline: none;
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
  font-family: inherit;
  resize: vertical;
  line-height: 1.6;
}

.search-input:focus {
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.1);
  background: var(--color-bg-input-focus);
}

.search-input::placeholder {
  color: var(--color-text-placeholder);
}

/* 清空输入按钮 */
.input-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  cursor: pointer;
  color: var(--color-text-placeholder);
  padding: var(--space-1);
  display: flex;
  align-items: center;
}

.input-clear:hover { color: var(--color-text-secondary); }

/* 查询按钮 */
.query-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 20px;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-base);
  white-space: nowrap;
  flex-shrink: 0;
}

.query-btn:hover:not(:disabled) { background: var(--color-primary-light); }
.query-btn:disabled { background: var(--color-text-placeholder); cursor: not-allowed; }

.btn-icon { font-size: 15px; }

/* 加载动画 */
.btn-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid rgba(255,255,255,0.35);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

/* 历史记录行 */
.history-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--color-border-light);
}

.history-label {
  font-size: var(--text-sm);
  color: var(--color-text-placeholder);
  flex-shrink: 0;
}

.history-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.history-tag {
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-sm);
  padding: 2px 8px;
  font-size: var(--text-sm);
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.history-tag:hover {
  background: var(--color-bg-hover);
  border-color: var(--color-text-tertiary);
  color: var(--color-text-primary);
}

/* 错误提示条 */
.error-banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: var(--color-bg-danger);
  border: 1px solid #FECACA;
  color: var(--color-danger);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-size: var(--text-md);
}

.error-banner button {
  background: none;
  border: none;
  color: var(--color-danger);
  font-size: var(--text-xl);
  cursor: pointer;
  padding: 0;
  flex-shrink: 0;
}

/* 结果卡片 */
.result-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  padding: var(--space-5) var(--space-6);
  box-shadow: var(--shadow-card);
}

.result-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.result-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
  letter-spacing: -0.01em;
}

.result-count {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
}

/* 表格包装器：支持横向滚动 */
.table-wrap {
  overflow-x: auto;
}

/* 结果表格 */
.result-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-base);
}

.result-table th {
  background: var(--color-bg-subtle);
  font-weight: 600;
  color: var(--color-text-secondary);
  font-size: var(--text-sm);
  padding: var(--space-2) var(--space-3);
  text-align: left;
  border-bottom: 1.5px solid var(--color-border-default);
  white-space: nowrap;
}

.result-table td {
  padding: 9px var(--space-3);
  border-bottom: 1px solid var(--color-border-light);
  color: var(--color-text-primary);
  vertical-align: middle;
}

.result-table tbody tr:hover td {
  background: var(--color-bg-hover);
}

.row-error td {
  color: var(--color-danger);
  font-size: var(--text-sm);
}

.cell-name { font-weight: 600; color: var(--color-text-primary) !important; }
.cell-code { color: var(--color-text-tertiary) !important; font-size: var(--text-sm); }
.cell-date { color: var(--color-text-tertiary) !important; font-size: var(--text-sm); white-space: nowrap; }
.cell-price { font-weight: 600 !important; white-space: nowrap; }
.cell-indicator { white-space: nowrap; }
.cell-error { font-size: var(--text-sm) !important; }

/* 数值颜色样式 */
.val-red { color: var(--color-danger); font-weight: 700; }
.val-green { color: var(--color-success); font-weight: 700; }
.val-gray { color: #374151; font-weight: 700; }

/* 标签样式 */
.tag {
  display: inline-block;
  margin-left: 5px;
  font-size: 10px;
  font-weight: 500;
  padding: 1px 5px;
  border-radius: 3px;
}

.tag-red { background: var(--color-bg-danger); color: #DC2626; border: 1px solid #FECACA; }
.tag-orange { background: var(--color-bg-warning); color: #EA580C; border: 1px solid #FED7AA; }
.tag-gray { background: var(--color-bg-subtle); color: #6B7280; border: 1px solid var(--color-border-default); }
.tag-cyan { background: var(--color-bg-cyan); color: #0891B2; border: 1px solid #A5F3FC; }
.tag-purple { background: var(--color-bg-purple); color: #7C3AED; border: 1px solid #DDD6FE; }
.tag-green { background: var(--color-bg-success); color: #059669; border: 1px solid #BBF7D0; }
.tag-rose { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }

/* 状态标签样式 */
.rec-tag {
  display: inline-block;
  font-size: var(--text-sm);
  font-weight: 600;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  min-width: 4em;
  text-align: center;
}

.rec-tag-blue { background: var(--color-bg-info); color: #1D4ED8; border: 1px solid #BFDBFE; }
.rec-tag-green { background: var(--color-bg-success); color: #047857; border: 1px solid #A7F3D0; }
.rec-tag-red { background: var(--color-bg-danger); color: #B91C1C; border: 1px solid #FECACA; }
.rec-tag-orange { background: var(--color-bg-warning); color: #C2410C; border: 1px solid #FED7AA; }
.rec-tag-rose { background: #FFFBEB; color: #B45309; border: 1px solid #FDE68A; }
.rec-tag-gray { background: var(--color-bg-subtle); color: #6B7280; border: 1px solid var(--color-border-default); }
.rec-tag-cyan { background: var(--color-bg-cyan); color: #0E7490; border: 1px solid #A5F3FC; }
.rec-tag-purple { background: var(--color-bg-purple); color: #6D28D9; border: 1px solid #DDD6FE; }

/* 使用说明卡片 */
.guide-card {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

/* 展开/收起按钮 */
.guide-toggle {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px var(--space-4);
  border: none;
  background: none;
  cursor: pointer;
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--color-text-secondary);
  width: 100%;
  transition: background var(--transition-fast);
}

.guide-toggle:hover { background: var(--color-bg-hover); }

/* 箭头图标 */
.toggle-arrow {
  margin-left: auto;
  transition: transform 0.2s;
}

.arrow-open { transform: rotate(180deg); }

/* 说明面板 */
.guide-panel {
  border-top: 1px solid var(--color-border-light);
  padding: var(--space-4) var(--space-6);
}

/* 说明内容网格布局 */
.guide-grid {
  display: grid;
  grid-template-columns: 1fr 1.6fr;
  gap: var(--space-6);
}

.guide-col-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--color-text-primary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 10px;
  padding-bottom: var(--space-2);
  border-bottom: 1.5px solid var(--color-border-default);
}

/* 说明列表 */
.guide-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.guide-list li {
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  padding: var(--space-1) 0;
  line-height: 1.6;
}

.guide-list strong { color: var(--color-text-primary); }

/* 信号说明行 */
.signal-rows {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.signal-row {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--text-sm);
}

.signal-desc {
  color: var(--color-text-secondary);
  line-height: 1.5;
}

/* 免责声明 */
.guide-disclaimer {
  font-size: var(--text-sm);
  color: var(--color-text-tertiary);
  text-align: center;
  margin: var(--space-4) 0 0;
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border-light);
}

/* 移动端响应式 */
@media (max-width: 768px) {
  .macdv-header { padding: var(--space-3) var(--page-padding-mobile); }
  .header-inner { flex-direction: column; align-items: flex-start; }
  .header-title { font-size: var(--text-xl); }
  .macdv-main { padding: var(--space-3) var(--page-padding-mobile); }
  .search-row { flex-direction: column; }
  .query-btn { width: 100%; justify-content: center; }
  .guide-grid { grid-template-columns: 1fr; gap: var(--space-4); }
  .guide-panel { padding: var(--space-3) var(--space-4); }
}
</style>
