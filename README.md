# Long Run

量化投资分析工具集，包含三个分析模块。

## 模块

### 五年之锚
基于国证A股指数的技术分析工具，提供 SMA1210 包络线、RSI 周期、滚动最大回撤三个视角的图表，帮助判断指数在历史波动区间中的位置。

- 数据来源：新浪财经
- 指数：国证A股（sz.399317）
- 指标：SMA1210 ±15% 包络线、RSI14 周线、滚动 5 年最大回撤

### 红利之美
中证红利相对国证A股的超额收益分析，通过四个图表从不同维度追踪红利策略的相对表现。

- 数据来源：新浪财经
- 指数：中证红利（sh515180）、国证A股（sz399317）
- 图表：收益走势对比、布朗带(%B/带宽)、40日收益差、RSI14 动能

### 趋势信号
MACD-V + RSI14 量化指标批量查询工具，支持同时查询多只股票并给出买卖信号建议。

- 数据来源：新浪财经
- 指标：MACD-V（动量与波动率比值）、RSI14
- 信号：左侧买点、左侧卖点、右侧买点、右侧卖点、观望

## 快速启动

### 后端

```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 前端

```bash
cd frontend
npm install
npm run dev
```

前端运行在 http://localhost:5173，会自动代理后端 API 请求到 http://localhost:8000。

## 技术栈

**后端**
- FastAPI + Uvicorn
- Pandas + NumPy
- APScheduler（定时任务）
- 新浪财经 API（数据源）

**前端**
- Vue 3 + TypeScript
- Vue Router
- Pinia（状态管理）
- ECharts 5（图表）
- Tailwind CSS

## 目录结构

```
long_run/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置
│   │   ├── routers/             # API 路由
│   │   │   ├── anchor.py        # 五年之锚 API
│   │   │   ├── hongli.py        # 红利之美 API
│   │   │   └── macdv.py         # 趋势信号 API
│   │   ├── services/            # 业务逻辑
│   │   │   ├── baostock_service.py
│   │   │   ├── indicator_service.py
│   │   │   ├── cache_service.py
│   │   │   ├── hongli_service.py
│   │   │   └── macdv_service.py
│   │   └── tasks/               # 定时任务
│   │       └── scheduler.py
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── views/                # 页面视图
    │   │   ├── AnchorView.vue
    │   │   ├── HongliView.vue
    │   │   └── MacdvView.vue
    │   ├── components/          # 组件
    │   │   ├── anchor/
    │   │   ├── common/
    │   │   └── layout/
    │   ├── stores/              # Pinia 状态
    │   ├── api/                 # Axios 封装
    │   └── router/             # 路由配置
    └── package.json
```

## 免责声明

本工具仅供个人学习与研究使用，不构成任何投资建议。历史数据不代表未来表现，股票市场存在风险，投资需谨慎。
