# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

Long Run (量化投资分析工具集) — a quantitative investment analysis platform with three modules:
- **五年之锚 (Anchor)**: Technical analysis of Guozheng A-Share Index (sz.399317) with SMA1210 envelope bands, RSI14, and rolling 5-year max drawdown
- **红利之美 (Hongli)**: Comparative excess-return analysis of CSI Dividend Index (sh515180) vs Guozheng A-Share (sz399317) with Bollinger Bands, 40-day return difference, and RSI14 momentum
- **趋势信号 (MACD-V)**: Batch stock screener using MACD-V (MACD normalized by ATR) + RSI14 to generate buy/sell signals

## Commands

### Backend (Python/FastAPI)
```bash
cd backend
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000   # production
./venv/bin/python -m uvicorn app.main:app --reload                      # dev with auto-reload
```

### Frontend (Vue 3/TypeScript)
```bash
cd frontend
npm install
npm run dev       # dev server on :5173, proxies /api to localhost:8000
npm run build     # type-check with vue-tsc then vite build
npm run preview   # preview production build
```

No test runner is configured for either backend or frontend.

## Architecture

```
long_run/
├── backend/app/
│   ├── main.py              # FastAPI app: CORS, router mounts, scheduler lifecycle
│   ├── config.py            # Pydantic Settings (.env supported): cache TTL, scheduler time, CORS origins
│   ├── routers/             # One router per module, prefix /api/v1/{anchor,hongli,macdv}
│   ├── services/            # Business logic + data fetching
│   ├── models/              # Pydantic response schemas
│   └── tasks/scheduler.py   # APScheduler: daily 20:00 refresh for anchor (3 indices) + hongli (2 indices)
├── frontend/src/
│   ├── api/                 # Axios clients (one per module, baseURL /api/v1)
│   ├── stores/              # Pinia stores (Composition API style, one per module)
│   ├── views/               # Page components mapped 1:1 to routes
│   ├── components/
│   │   ├── anchor/          # MainChart, RsiChart, DrawdownChart (vue-echarts), TimeRangeSelector, UsageGuideModal
│   │   ├── layout/          # NavBar
│   │   └── common/          # LoadingOverlay
│   ├── types/               # TypeScript interfaces per module
│   └── router/              # Vue Router: / → /anchor, /anchor, /hongli, /macdv
└── backend/long_run_data.db # SQLite cache (WAL mode, 24h TTL)
```

### Backend Data Flow

All data comes from **Sina Finance** APIs (`money.finance.sina.com.cn`, `hq.sinajs.cn`, `suggest3.sinajs.cn`). Despite the filename `baostock_service.py`, no BaoStock library is used — it fetches from Sina.

1. **Request hits router** → service checks `CacheService.is_cache_valid()` (compares last update against 24h TTL)
2. **Cache valid** → return cached data from SQLite
3. **Cache expired/missing** → fetch from Sina API → save to SQLite via upsert (`ON CONFLICT DO UPDATE`) → return data

`CacheService` uses raw `sqlite3` (no ORM) with two tables: `stock_data` (OHLCV per index/date, unique on `index_code + date`) and `cache_meta` (key-value metadata for last-update timestamps).

### Frontend ECharts Patterns

Two different integration patterns exist:

- **Anchor charts** (MainChart, RsiChart, DrawdownChart): Use `vue-echarts` (`VChart` component) with tree-shaken imports from `echarts/core`. Options are computed properties reacting to props.
- **Hongli charts**: Use raw `echarts` with manual `echarts.init()` / `dispose()` lifecycle. Imports the full `echarts` bundle.

### API Endpoints

| Module | Method | Path | Description |
|--------|--------|------|-------------|
| Anchor | GET | `/api/v1/anchor/data` | Chart data (query: `index_code`, `start_date`, `end_date`) |
| Anchor | GET | `/api/v1/anchor/health` | Cache status |
| Anchor | POST | `/api/v1/anchor/refresh` | Force refresh from Sina |
| Hongli | GET | `/api/v1/hongli/data` | Comparative data (query: `start_date`, `end_date`) |
| Hongli | GET | `/api/v1/hongli/health` | Cache status |
| Hongli | POST | `/api/v1/hongli/refresh` | Force refresh from Sina |
| MACD-V | POST | `/api/v1/macdv/batch_query` | Batch query (body: string[], rate-limited 10 req/60s per IP) |
| MACD-V | GET | `/api/v1/macdv/health` | Health check |

### Key Technical Details

- **Index code mapping**: `baostock_service.py` maps BaoStock-style codes (`sz.399317`) to Sina-style codes (`sz399317`). The `macdv_service.py` `_normalize()` function resolves stock names/abbreviations to Sina codes, with fallback to Sina Suggest API.
- **MACD-V calculation**: `(EMA12 - EMA26) / ATR(26) * 100` — normalizes MACD by volatility. Trend zones: >150 momentum_peak, >50 strong_up, ≥-50 oscillation, ≥-150 strong_down, <-150 momentum_decay.
- **Scheduler**: Both `daily_anchor_update` (3 indices) and `daily_hongli_update` (2 indices) run at 20:00 daily via APScheduler `CronTrigger`.
- **Vite proxy**: `/api` requests are proxied to `http://localhost:8000` in dev mode.
- **Config**: Settings via `pydantic-settings`, supports `.env` file. Key settings: `cache_ttl_hours` (default 24), `data_update_hour`/`data_update_minute` (default 20:00), `cors_origins`.
