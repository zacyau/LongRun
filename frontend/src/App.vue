<template>
  <div class="app-root">
    <NavBar />
    <main class="app-main">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
import NavBar from '@/components/layout/NavBar.vue'
</script>

<style>
*, *::before, *::after {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  -webkit-overflow-scrolling: touch;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'PingFang SC', 'Microsoft YaHei', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #1A1A1A;
  background: #F7F8FA;
  line-height: 1.5;
  overflow-x: hidden;
}

#app {
  min-height: 100vh;
  min-height: 100dvh;
}

.app-root {
  min-height: 100vh;
  min-height: 100dvh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding-top: 56px;
  -webkit-overflow-scrolling: touch;
}

@media (max-width: 768px) {
  html, body {
    overscroll-behavior-y: none;
  }
}

::selection {
  background: rgba(26, 26, 26, 0.12);
}

::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: transparent;
}

::-webkit-scrollbar-thumb {
  background: #DDD;
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #CCC;
}
</style>