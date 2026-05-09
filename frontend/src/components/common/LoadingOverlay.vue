<template>
  <div v-if="loading" class="loading-overlay">
    <div class="loading-content">
      <div class="loading-ring">
        <div class="ring-dot"></div>
        <div class="ring-dot"></div>
        <div class="ring-dot"></div>
      </div>
      <p class="loading-text">{{ message }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading: boolean
  message?: string
}

withDefaults(defineProps<Props>(), {
  message: '数据加载中...'
})
</script>

<style scoped>
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  border-radius: inherit;
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

.loading-ring {
  display: flex;
  gap: 6px;
  align-items: center;
}

.ring-dot {
  width: 6px;
  height: 6px;
  background: #1A1A1A;
  border-radius: 50%;
  animation: bounce 1.2s ease-in-out infinite;
}

.ring-dot:nth-child(2) { animation-delay: 0.15s; }
.ring-dot:nth-child(3) { animation-delay: 0.3s; }

@keyframes bounce {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40% { transform: scale(1); opacity: 1; }
}

.loading-text {
  color: #999;
  font-size: 13px;
  letter-spacing: 0.02em;
}
</style>