# Long Run 项目整合规划文档

> 将 `Anchor-5Y`（五年之锚）与 `hongli`（红利之美）两个项目整合为统一网站，通过横向导航栏切换模块。

---

## 一、项目定位

- **网站名称**：Long Run
- **项目一导航名**：五年之锚
- **项目二导航名**：红利之美
- **整体风格**：参考「有知有行」youzyuouxing.cn 的现代简约白色 UI + 参考「老錢日談」laoqianritan-create-github-io.pages.dev 的图表配色风格

---

## 二、项目结构（整合后）

```
long_run/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                      # FastAPI 统一入口，挂载两个模块的路由
│   │   ├── config.py                    # 统一配置管理（Pydantic Settings）
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── anchor.py                # 五年之锚 API 路由  /api/v1/anchor/
│   │   │   └── hongli.py                # 红利之美 API 路由  /api/v1/hongli/
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── baostock_service.py      # baostock 数据获取（共用）
│   │   │   ├── indicator_service.py     # 五年之锚指标计算（SMA/RSI/回撤）
│   │   │   ├── hongli_service.py        # 红利之美指标计算
│   │   │   └── cache_service.py         # SQLite 缓存服务（共用）
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── anchor_schemas.py        # 五年之锚 Pydantic 响应模型
│   │   │   └── hongli_schemas.py        # 红利之美 Pydantic 响应模型
│   │   └── tasks/
│   │       ├── __init__.py
│   │       └── scheduler.py             # APScheduler 定时任务（统一调度）
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   │   └── favicon.ico
│   ├── src/
│   │   ├── App.vue                      # 根组件：顶栏导航 + 路由视图
│   │   ├── main.ts                      # 入口，注册路由/Pinia
│   │   ├── api/
│   │   │   ├── anchor.ts                # 五年之锚 Axios API
│   │   │   └── hongli.ts                # 红利之美 Axios API
│   │   ├── types/
│   │   │   ├── anchor.ts                # 五年之锚 TS 类型
│   │   │   └── hongli.ts                # 红利之美 TS 类型
│   │   ├── stores/
│   │   │   ├── anchorStore.ts           # 五年之锚 Pinia Store（原 chartStore.ts）
│   │   │   └── hongliStore.ts           # 红利之美 Pinia Store（原 hongli.js → TS）
│   │   ├── router/
│   │   │   └── index.ts                 # Vue Router：/anchor 和 /hongli
│   │   ├── views/
│   │   │   ├── AnchorView.vue           # 五年之锚主页面（原 Dashboard.vue）
│   │   │   └── HongliView.vue           # 红利之美主页面（原 HomeView.vue）
│   │   ├── components/
│   │   │   ├── anchor/
│   │   │   │   ├── MainChart.vue        # 五年之锚主图（SMA1210 包络线）
│   │   │   │   ├── RsiChart.vue         # RSI 周线图
│   │   │   │   ├── DrawdownChart.vue    # 滚动最大回撤图
│   │   │   │   └── TimeRangeSelector.vue
│   │   │   ├── hongli/
│   │   │   │   └── ...                  # 红利之美相关图表组件
│   │   │   ├── layout/
│   │   │   │   └── NavBar.vue           # 横向导航栏组件
│   │   │   └── common/
│   │   │       └── LoadingOverlay.vue   # 通用加载遮罩
│   │   └── assets/
│   │       └── styles/
│   │           └── main.css             # 全局样式（Tailwind 基础上统一图表色调）
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
│
└── README.md                            # 整合后统一说明
```

---

## 三、后端整合方案

### 3.1 统一入口 `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import anchor, hongli
from app.tasks.scheduler import start_scheduler

app = FastAPI(title="Long Run", version="1.0.0")

# CORS 配置
app.add_middleware(CORSMiddleware, allow_origins=["*"], ...)

# 注册路由
app.include_router(anchor.router, prefix="/api/v1/anchor", tags=["五年之锚"])
app.include_router(hongli.router, prefix="/api/v1/hongli", tags=["红利之美"])

@app.on_event("startup")
async def startup():
    start_scheduler()  # 统一定时任务
```

### 3.2 路由设计

| 模块 | 路径 | 说明 |
|------|------|------|
| 五年之锚 | `GET /api/v1/anchor/data` | 获取指数技术分析数据 |
| 五年之锚 | `GET /api/v1/anchor/health` | 健康检查 |
| 五年之锚 | `POST /api/v1/anchor/refresh` | 手动刷新数据 |
| 红利之美 | `GET /api/v1/hongli/data` | 获取红利相关数据 |
| 红利之美 | `GET /api/v1/hongli/health` | 健康检查 |
| 红利之美 | `POST /api/v1/hongli/refresh` | 手动刷新数据 |

### 3.3 共用服务

- **baostock_service.py**：两个模块共用 baostock 数据源
- **cache_service.py**：两个模块共用 SQLite 缓存机制（不同表/不同数据库文件）
- **scheduler.py**：统一 APScheduler 定时刷新两个模块的数据

### 3.4 依赖整合

```
# requirements.txt
fastapi==0.115.0
uvicorn==0.30.6
baostock==0.8.8
pandas==2.2.2
numpy==1.26.4
pydantic==2.9.2
pydantic-settings==2.5.2
apscheduler==3.10.4
httpx==0.27.2
```

---

## 四、前端整合方案

### 4.1 导航架构

- **横向导航栏**：固定在页面顶部，白色背景，底部细线分隔
- 左侧显示网站名称 **"Long Run"**（加粗深色字体）
- 右侧两个导航按钮：**"五年之锚"** | **"红利之美"**
- 当前激活的导航项有下划线指示器（参考有知有行风格）
- 使用 Vue Router 实现：`/anchor` 和 `/hongli` 两个路由

### 4.2 NavBar 组件设计

```vue
<!-- components/layout/NavBar.vue -->
<template>
  <nav class="fixed top-0 left-0 right-0 z-50 bg-white border-b border-gray-100">
    <div class="max-w-7xl mx-auto px-6 h-14 flex items-center justify-between">
      <router-link to="/" class="text-lg font-semibold text-gray-900 tracking-wide">
        Long Run
      </router-link>
      <div class="flex items-center gap-8">
        <router-link to="/anchor" class="nav-link">五年之锚</router-link>
        <router-link to="/hongli" class="nav-link">红利之美</router-link>
      </div>
    </div>
  </nav>
</template>
```

### 4.3 路由配置

```typescript
// router/index.ts
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/anchor' },
  { path: '/anchor', name: 'anchor', component: () => import('@/views/AnchorView.vue') },
  { path: '/hongli', name: 'hongli', component: () => import('@/views/HongliView.vue') },
]

export default createRouter({ history: createWebHistory(), routes })
```

### 4.4 App.vue 结构

```vue
<template>
  <div class="min-h-screen bg-white">
    <NavBar />
    <main class="pt-14">  <!-- 留出导航栏高度 -->
      <router-view />
    </main>
  </div>
</template>
```

---

## 五、UI/UX 设计规范

### 5.1 整体配色方案

| 用途 | 颜色 | 色值 |
|------|------|------|
| 页面背景 | 纯白 | `#FFFFFF` |
| 卡片/面板背景 | 白色 | `#FFFFFF` |
| 导航栏背景 | 白色 | `#FFFFFF` |
| 导航栏底部边框 | 浅灰 | `#F0F0F0` 或 `#E5E5E5` |
| 主文字色 | 深灰/黑 | `#1A1A1A` 或 `#333333` |
| 次要文字色 | 中灰 | `#666666` 或 `#999999` |
| 导航激活指示 | 深色 | `#1A1A1A`（下划线） |
| 导航悬停色 | 中灰 | `#555555` |
| 卡片阴影 | 极淡阴影 | `box-shadow: 0 1px 3px rgba(0,0,0,0.04)` |

### 5.2 图表统一色调

参考 laoqianritan 图表风格，关键原则：
- **不使用渐变色**，采用扁平纯色
- 白色/浅灰背景的图表画布
- 细网格线（淡灰色 `#E8E8E8` 或 `#F0F0F0`）
- 坐标轴标签使用中性灰色

| 图表元素 | 颜色 | 色值 |
|----------|------|------|
| K线/指数线（上涨） | 红色系 | `#E53935` 或 `#F55555` |
| K线/指数线（下跌） | 绿色系 | `#43A047` 或 `#26A69A` |
| SMA1210 均线 | 深蓝 | `#2962FF` 或 `#448AFF` |
| 包络线上轨 | 浅蓝虚线 | `#90CAF9` |
| 包络线下轨 | 浅蓝虚线 | `#90CAF9` |
| RSI 线 | 橙色 | `#FF7043` |
| RSI 超买线(80) | 红色虚线 | `#EF9A9A` |
| RSI 超卖线(20) | 绿色虚线 | `#A5D6A7` |
| RSI 中线(50) | 灰色虚线 | `#BDBDBD` |
| 回撤面积 | 浅红半透明 | `rgba(229,57,53,0.15)` |
| 红利相关折线 | 深绿 | `#2E7D32` |
| 辅助标注线 | 灰色 | `#9E9E9E` |

### 5.3 排版规范

- 字体：系统默认中文字体栈（PingFang SC, Microsoft YaHei, sans-serif）
- 标题：`font-weight: 600`，深色
- 正文字号：`14px` / `15px`
- 数据指标数字：`font-weight: 600`，较大字号
- 导航文字：`15px`，`font-weight: 500`

### 5.4 布局规范

- 最大内容宽度：`max-w-7xl`（1280px）
- 左右内边距：`px-6`（24px）
- 卡片间距：`gap-6`（24px）
- 卡片内边距：`p-6`（24px）
- 卡片圆角：`rounded-lg`（8px）
- 导航栏高度：`h-14`（56px）

---

## 六、整合实施步骤

### 第 1 步：项目初始化
1. 在 `long_run/` 下创建整合后的目录结构
2. 初始化 frontend（Vue 3 + Vite + TypeScript + Tailwind CSS + Pinia + Vue Router + ECharts）
3. 初始化 backend（FastAPI 项目骨架）
4. 安装所有依赖

### 第 2 步：后端整合
1. 复制 Anchor-5Y 的 `backend/app/` 代码，调整为整合后的目录结构
2. 复制 hongli 的 `backend/` 代码，整合到统一结构
3. 创建统一的 `main.py`，挂载两个模块的路由
4. 整合 `config.py`、`scheduler.py`、`cache_service.py` 等共用模块
5. 测试两个模块的 API 端点

### 第 3 步：前端整合 - 导航
1. 创建 `NavBar.vue` 横向导航组件
2. 创建 `router/index.ts` 路由配置
3. 修改 `App.vue` 为带导航的整体布局
4. 配置 Tailwind 全局样式（白色主题、字体、间距）

### 第 4 步：前端整合 - 五年之锚模块
1. 迁移 Anchor-5Y 的 views/components/stores/api/types 到整合结构
2. 适配路由布局，去掉原项目独立的 header
3. 调整图表配色为统一风格

### 第 5 步：前端整合 - 红利之美模块
1. 迁移 hongli 的 views/components/stores 到整合结构
2. 将 `.js` 文件转换为 `.ts`（TypeScript）
3. 适配路由布局
4. 调整图表配色为统一风格

### 第 6 步：整体调优
1. 全局 UI 细节打磨（间距、阴影、边框一致性）
2. 图表配色统一调优
3. 响应式适配（桌面/平板/移动端）
4. Vite 代理配置统一
5. 整体测试与调试

### 第 7 步：文档与收尾
1. 更新 README.md
2. 确保两个模块的所有功能正常运行

---

## 七、关键注意事项

1. **原有功能不变**：两个模块的指标计算逻辑、数据获取逻辑、缓存策略全部保持不变，仅做结构整合和 UI 统一
2. **TypeScript 统一**：hongli 项目当前使用 `.js`，整合时统一转为 `.ts`
3. **API 路径隔离**：两个模块使用独立的 API 前缀 `/api/v1/anchor/` 和 `/api/v1/hongli/`，互不干扰
4. **缓存隔离**：共用 cache_service 但使用独立的数据库表或独立 SQLite 文件
5. **定时任务统一**：APScheduler 统一调度两个模块的数据刷新
6. **无渐变色**：图表严格使用纯色+透明度，不使用 gradient
7. **白色底色**：全局背景 `#FFFFFF`，无渐变色背景