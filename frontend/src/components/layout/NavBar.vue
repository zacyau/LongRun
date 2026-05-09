<template>
  <nav class="nav-bar">
    <div class="nav-inner">
      <router-link to="/" class="nav-brand">
        <span class="brand-text">Long Run</span>
      </router-link>
      <div class="nav-links">
        <router-link to="/anchor" class="nav-link" active-class="nav-link-active">
          五年之锚
        </router-link>
        <router-link to="/hongli" class="nav-link" active-class="nav-link-active">
          红利之美
        </router-link>
        <router-link to="/macdv" class="nav-link" active-class="nav-link-active">
          趋势信号
        </router-link>
      </div>
    </div>
  </nav>
</template>

<style scoped>
.nav-bar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(12px) saturate(180%);
  -webkit-backdrop-filter: blur(12px) saturate(180%);
  border-bottom: 1px solid var(--color-border-light);
  height: var(--header-height);
  touch-action: manipulation;
  padding: 0 var(--page-padding);
}

.nav-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.nav-brand {
  text-decoration: none;
  display: flex;
  align-items: center;
}

.brand-text {
  font-size: var(--text-xl);
  font-weight: 700;
  color: var(--color-primary);
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: var(--space-1);
}

.nav-link {
  font-size: var(--text-md);
  font-weight: 500;
  color: var(--color-text-tertiary);
  text-decoration: none;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  position: relative;
}

.nav-link:hover {
  color: var(--color-text-secondary);
  background: var(--color-bg-hover);
}

.nav-link-active {
  color: var(--color-text-primary);
  background: transparent;
  font-weight: 600;
}

.nav-link-active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 14px;
  right: 14px;
  height: 2px;
  background: var(--color-primary-accent);
  border-radius: 1px;
}

@media (max-width: 768px) {
  .nav-bar {
    padding: 0 var(--page-padding-mobile);
  }
  .nav-link {
    padding: 6px 12px;
    font-size: var(--text-base);
  }
  .nav-link-active::after {
    left: 12px;
    right: 12px;
  }
}
</style>
