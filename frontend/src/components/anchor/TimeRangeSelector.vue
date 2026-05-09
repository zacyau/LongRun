<template>
  <div class="time-range-selector">
    <div class="range-buttons">
      <button
        v-for="option in rangeOptions"
        :key="option.value"
        :class="['range-btn', { active: modelValue === option.value }]"
        @click="selectRange(option.value)"
      >
        {{ option.label }}
      </button>
    </div>

    <div v-if="modelValue === 'custom'" class="custom-range">
      <input
        type="date"
        :value="customStart"
        @input="updateStartDate(($event.target as HTMLInputElement).value)"
        class="date-input"
      />
      <span class="range-separator">至</span>
      <input
        type="date"
        :value="customEnd"
        @input="updateEndDate(($event.target as HTMLInputElement).value)"
        class="date-input"
      />
      <button class="apply-btn" @click="applyCustomRange">应用</button>
    </div>

    <button class="refresh-btn" @click="openPasswordModal" :disabled="loading">
      <span class="refresh-icon" :class="{ spinning: loading }">↻</span>
      刷新
    </button>

    <!-- 密码验证弹窗 -->
    <Teleport to="body">
      <Transition name="modal-fade">
        <div v-if="showPasswordModal" class="pwd-backdrop" @click.self="cancelPassword">
          <div class="pwd-modal">
            <div class="pwd-header">
              <span class="pwd-title">请输入管理员密码</span>
              <button class="pwd-close" @click="cancelPassword">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 4L12 12M12 4L4 12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
            <div class="pwd-body">
              <input
                ref="passwordInputRef"
                v-model="passwordInput"
                type="password"
                class="pwd-input"
                placeholder="请输入密码"
                @keydown.enter="confirmPassword"
                @keydown.esc="cancelPassword"
              />
              <p v-if="pwdError" class="pwd-error">{{ pwdError }}</p>
            </div>
            <div class="pwd-footer">
              <button class="pwd-cancel-btn" @click="cancelPassword">取消</button>
              <button class="pwd-confirm-btn" @click="confirmPassword">确认</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick, onMounted, onUnmounted } from 'vue'
import type { TimeRangeOption } from '@/types/anchor'

const ADMIN_PASSWORD = '8730'

interface Props {
  modelValue: TimeRangeOption
  customStart: string | null
  customEnd: string | null
  loading: boolean
}

const props = defineProps<Props>()
const emit = defineEmits(['update:modelValue', 'update:customStart', 'update:customEnd', 'change', 'refresh'])

const rangeOptions = [
  { value: 'all' as TimeRangeOption, label: '全部' },
  { value: '5y' as TimeRangeOption, label: '5年' },
  { value: '3y' as TimeRangeOption, label: '3年' },
  { value: '1y' as TimeRangeOption, label: '1年' },
  { value: 'custom' as TimeRangeOption, label: '自定义' },
]

const localStart = ref(props.customStart)
const localEnd = ref(props.customEnd)

const showPasswordModal = ref(false)
const passwordInput = ref('')
const pwdError = ref('')
const passwordInputRef = ref<HTMLInputElement | null>(null)

function selectRange(value: TimeRangeOption) {
  emit('update:modelValue', value)
  if (value !== 'custom') {
    emit('change', value)
  }
}

function updateStartDate(value: string) {
  localStart.value = value || null
  emit('update:customStart', localStart.value)
}

function updateEndDate(value: string) {
  localEnd.value = value || null
  emit('update:customEnd', localEnd.value)
}

function applyCustomRange() {
  emit('change', 'custom')
}

async function openPasswordModal() {
  if (props.loading) return
  passwordInput.value = ''
  pwdError.value = ''
  showPasswordModal.value = true
  await nextTick()
  passwordInputRef.value?.focus()
}

function cancelPassword() {
  showPasswordModal.value = false
  passwordInput.value = ''
  pwdError.value = ''
}

function confirmPassword() {
  if (passwordInput.value === ADMIN_PASSWORD) {
    showPasswordModal.value = false
    passwordInput.value = ''
    pwdError.value = ''
    emit('refresh')
  } else {
    pwdError.value = '密码错误，请重新输入'
    passwordInput.value = ''
  }
}

function handleKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape' && showPasswordModal.value) {
    cancelPassword()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped>
.time-range-selector {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  flex-wrap: wrap;
}

.range-buttons {
  display: flex;
  gap: var(--space-1);
  background: var(--color-bg-hover);
  padding: var(--space-1);
  border-radius: var(--radius-md);
}

.range-btn {
  padding: 6px 12px;
  border: none;
  background: transparent;
  color: var(--color-text-tertiary);
  font-size: var(--text-base);
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: all var(--transition-base);
}

.range-btn:hover {
  background: rgba(13, 27, 42, 0.05);
}

.range-btn.active {
  background: var(--color-bg-card);
  color: var(--color-text-primary);
  font-weight: 500;
  box-shadow: 0 1px 3px rgba(13, 27, 42, 0.1);
}

.custom-range {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.date-input {
  padding: 6px 10px;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-sm);
  font-size: var(--text-base);
  color: var(--color-text-primary);
  background: var(--color-bg-card);
}

.range-separator {
  color: var(--color-text-tertiary);
  font-size: var(--text-base);
}

.apply-btn {
  padding: 6px 12px;
  background: var(--color-primary-accent);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  cursor: pointer;
  transition: background var(--transition-base);
}

.apply-btn:hover {
  background: #1a4fd0;
}

.refresh-btn {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  padding: 6px 12px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  font-size: var(--text-base);
  color: var(--color-text-tertiary);
  cursor: pointer;
  transition: all var(--transition-base);
  margin-left: auto;
}

.refresh-btn:hover:not(:disabled) {
  background: var(--color-bg-hover);
  border-color: var(--color-text-tertiary);
  color: var(--color-text-secondary);
}

.refresh-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.refresh-icon {
  display: inline-block;
  font-size: var(--text-md);
}

.refresh-icon.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 密码弹窗 */
.pwd-backdrop {
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

.pwd-modal {
  background: var(--color-bg-elevated);
  border-radius: var(--radius-xl);
  width: 100%;
  max-width: 360px;
  box-shadow: var(--shadow-modal);
  overflow: hidden;
}

.pwd-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--color-border-light);
}

.pwd-title {
  font-size: var(--text-md);
  font-weight: 600;
  color: var(--color-text-primary);
}

.pwd-close {
  background: none;
  border: none;
  cursor: pointer;
  padding: var(--space-1);
  border-radius: var(--radius-sm);
  color: var(--color-text-tertiary);
  display: flex;
  align-items: center;
  transition: all var(--transition-fast);
}

.pwd-close:hover {
  background: var(--color-bg-hover);
  color: var(--color-text-secondary);
}

.pwd-body {
  padding: var(--space-5);
}

.pwd-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  font-size: var(--text-md);
  color: var(--color-text-primary);
  box-sizing: border-box;
  outline: none;
  transition: border-color var(--transition-base), box-shadow var(--transition-base);
  background: var(--color-bg-input);
}

.pwd-input:focus {
  border-color: var(--color-border-focus);
  box-shadow: 0 0 0 3px rgba(41, 98, 255, 0.1);
  background: var(--color-bg-input-focus);
}

.pwd-error {
  margin: var(--space-2) 0 0;
  font-size: var(--text-sm);
  color: var(--color-danger);
}

.pwd-footer {
  display: flex;
  gap: 10px;
  padding: var(--space-3) var(--space-5) var(--space-4);
  justify-content: flex-end;
}

.pwd-cancel-btn {
  padding: 8px 20px;
  border: 1px solid var(--color-border-default);
  border-radius: var(--radius-md);
  background: var(--color-bg-card);
  color: var(--color-text-secondary);
  font-size: var(--text-base);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.pwd-cancel-btn:hover {
  background: var(--color-bg-hover);
}

.pwd-confirm-btn {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary-accent);
  color: white;
  font-size: var(--text-base);
  cursor: pointer;
  transition: background var(--transition-base);
}

.pwd-confirm-btn:hover {
  background: #1a4fd0;
}

/* 弹窗动画 */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.2s ease;
}

.modal-fade-enter-active .pwd-modal,
.modal-fade-leave-active .pwd-modal {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}

.modal-fade-enter-from .pwd-modal {
  transform: scale(0.95) translateY(-8px);
  opacity: 0;
}

.modal-fade-leave-to .pwd-modal {
  transform: scale(0.95) translateY(-8px);
  opacity: 0;
}

@media (max-width: 768px) {
  .time-range-selector {
    flex-direction: column;
    align-items: stretch;
    touch-action: manipulation;
  }

  .range-buttons {
    justify-content: center;
    touch-action: manipulation;
  }

  .range-btn {
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
  }

  .custom-range {
    justify-content: center;
  }

  .date-input {
    touch-action: manipulation;
  }

  .refresh-btn {
    margin-left: 0;
    justify-content: center;
    touch-action: manipulation;
    -webkit-tap-highlight-color: transparent;
  }
}
</style>
