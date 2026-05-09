<template>
  <Teleport to="body">
    <Transition name="modal-fade">
      <div
        v-if="visible"
        class="modal-backdrop"
        @click.self="handleClose"
      >
        <div class="modal-container" role="dialog" aria-modal="true" aria-labelledby="modal-title">
          <div class="modal-header">
            <h2 id="modal-title" class="modal-title">普通基民投资框架使用说明</h2>
            <button
              class="modal-close-btn"
              @click="handleClose"
              aria-label="关闭"
              title="关闭"
            >
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M5 5L15 15M15 5L5 15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
              </svg>
            </button>
          </div>

          <div class="modal-body">
            <div class="disclaimer-box">
              <strong>【声明】</strong>本内容仅作为投资策略参考，不构成任何具体的投资建议。投资者应根据自身风险承受能力、投资目标和财务状况做出独立的投资决策。
            </div>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">一</span>
                定投策略执行规则
              </h3>
              <ol class="rule-list">
                <li>
                  当指数点位在五年均线的包络线上下轨<strong>之间</strong>时：执行<strong>正常定投</strong>计划，按预设标准金额进行定期投资
                </li>
                <li>
                  当指数点位<strong>高于</strong>五年均线+15%时：<strong>暂停定投</strong>或者<strong>根据自行情况减仓</strong>操作，将原定投资资金暂时配置于货币市场基金或短期债券型基金等低风险产品
                </li>
                <li>
                  当指数点位从高于五年均线+15%的状态<strong>回落至</strong>五年均线以内时：<strong>恢复正常</strong>定投计划
                </li>
                <li>
                  当指数点位<strong>低于</strong>五年均线-15%时：按预设标准金额执行<strong>加倍定投</strong>
                </li>
              </ol>
            </section>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">二</span>
                资产配置与动态平衡策略
              </h3>
              <ol class="rule-list">
                <li>
                  <strong>固定周期再平衡</strong>，如一年一次、或半年一次
                </li>
                <li>
                  当指数点位<strong>显著高于</strong>五年均线+15%以上时：执行<strong>减仓</strong>操作，降低股票类资产配置比例，相应增加债券类资产配置，以降低整体权益风险敞口
                </li>
                <li>
                  当指数点位<strong>显著低于</strong>五年均线-15%以下时：执行<strong>加仓</strong>操作，提高股票类资产配置比例，相应减少债券类资产配置，以增加权益类资产仓位
                </li>
                <li>
                  当指数点位<strong>回归至</strong>五年均线附近（±5%区间内）时：执行一次<strong>完整的资产配置比例重置</strong>，将各类资产比例恢复至预设的目标配置比例
                </li>
              </ol>
            </section>

            <section class="guide-section">
              <h3 class="section-title">
                <span class="section-number">三</span>
                辅助判断工具
              </h3>
              <p class="section-text">
                在执行上述策略时，可结合 <strong>RSI</strong>（相对强弱指数）等技术指标的超买超卖信号进行综合判断，以提高策略执行的准确性和有效性。
              </p>
            </section>
          </div>

          <div class="modal-footer">
            <button class="modal-confirm-btn" @click="handleClose">
              我了解了
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch, onMounted, onUnmounted } from 'vue'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  close: []
}>()

function handleClose() {
  emit('close')
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && props.visible) {
    handleClose()
  }
}

watch(() => props.visible, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.modal-backdrop {
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

.modal-container {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 640px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: var(--shadow-modal);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-5) var(--space-6) var(--space-4);
  border-bottom: 1px solid var(--color-border-light);
  flex-shrink: 0;
}

.modal-title {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0;
}

.modal-close-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-md);
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
  flex-shrink: 0;
}

.modal-close-btn:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

.modal-body {
  padding: var(--space-5) var(--space-6);
  overflow-y: auto;
  flex: 1;
  -webkit-overflow-scrolling: touch;
}

.disclaimer-box {
  background: var(--color-bg-warning);
  border: 1px solid #FDE68A;
  border-radius: var(--radius-lg);
  padding: var(--space-3) var(--space-4);
  font-size: var(--text-base);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin-bottom: var(--space-5);
}

.disclaimer-box strong {
  color: #92400E;
}

.guide-section {
  margin-bottom: var(--space-5);
}

.guide-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
  margin: 0 0 var(--space-3);
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.section-number {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--color-primary-accent);
  color: white;
  font-size: var(--text-sm);
  font-weight: 600;
  flex-shrink: 0;
}

.rule-list {
  counter-reset: rule-counter;
  list-style: none;
  padding: 0;
  margin: 0;
}

.rule-list > li {
  font-size: var(--text-md);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  padding: var(--space-2) 0 var(--space-2) 28px;
  position: relative;
  border-left: 2px solid var(--color-border-default);
}

.rule-list > li::before {
  counter-increment: rule-counter;
  content: counter(rule-counter);
  position: absolute;
  left: 0;
  top: var(--space-2);
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--color-primary-accent);
  color: white;
  font-size: var(--text-xs);
  font-weight: 600;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.rule-list strong {
  color: var(--color-text-primary);
}

.section-text {
  font-size: var(--text-md);
  color: var(--color-text-secondary);
  line-height: var(--leading-relaxed);
  margin: 0;
}

.modal-footer {
  padding: var(--space-4) var(--space-6);
  border-top: 1px solid var(--color-border-light);
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.modal-confirm-btn {
  background: var(--color-primary-accent);
  color: white;
  border: none;
  padding: 10px 40px;
  border-radius: var(--radius-lg);
  font-size: var(--text-md);
  font-weight: 500;
  cursor: pointer;
  transition: background var(--transition-base), transform 0.1s;
}

.modal-confirm-btn:hover {
  background: #1a4fd0;
}

.modal-confirm-btn:active {
  transform: scale(0.97);
}

/* Transition */
.modal-fade-enter-active {
  transition: opacity 0.25s ease;
}

.modal-fade-enter-active .modal-container {
  transition: transform 0.25s ease, opacity 0.25s ease;
}

.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-leave-active .modal-container {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from {
  opacity: 0;
}

.modal-fade-enter-from .modal-container {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-leave-to .modal-container {
  transform: scale(0.95) translateY(10px);
  opacity: 0;
}

/* 响应式 */
@media (max-width: 768px) {
  .modal-backdrop {
    padding: 0;
    align-items: flex-end;
  }

  .modal-container {
    max-width: 100%;
    max-height: 90vh;
    border-radius: var(--radius-2xl) var(--radius-2xl) 0 0;
  }

  .modal-header {
    padding: var(--space-4) var(--space-4) var(--space-3);
  }

  .modal-title {
    font-size: var(--text-md);
  }

  .modal-body {
    padding: var(--space-4);
  }

  .modal-footer {
    padding: var(--space-3) var(--space-4);
  }

  .modal-confirm-btn {
    width: 100%;
  }
}
</style>
