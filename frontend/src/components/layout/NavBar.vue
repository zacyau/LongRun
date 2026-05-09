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
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #EBEBEB;
  height: 56px;
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
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
  font-size: 17px;
  font-weight: 700;
  color: #1A1A1A;
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 4px;
}

.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: #999;
  text-decoration: none;
  padding: 6px 14px;
  border-radius: 6px;
  transition: all 0.15s;
  position: relative;
}

.nav-link:hover {
  color: #555;
  background: #F5F5F5;
}

.nav-link-active {
  color: #1A1A1A;
  background: #F0F0F0;
}

@media (max-width: 640px) {
  .nav-inner {
    padding: 0 16px;
  }
  .nav-link {
    padding: 6px 12px;
    font-size: 13px;
  }
}
</style>