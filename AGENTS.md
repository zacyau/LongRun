# AGENTS.md

This file provides guidance to the AI agent when working with code in this repository.

## Project

Long Run (量化投资分析工具集) — FastAPI backend + Vue 3 frontend. Three modules: 五年之锚 (Anchor), 红利之美 (Hongli), 趋势信号 (MACD-V).

## Commands

### Backend
```bash
cd backend
./venv/bin/python -m uvicorn app.main:app --reload   # dev
./venv/bin/python -m uvicorn app.main:app --host 0.0.0.0 --port 8000  # prod
```
Always use `./venv/bin/python` — the venv is at `backend/venv/`.

### Frontend
```bash
cd frontend
npm run dev       # dev server :5173, proxies /api → localhost:8000
npm run build     # vue-tsc type-check then vite build
```

No test runner exists for either backend or frontend.

## Key Gotchas

- **Index code mapping**: BaoStock-style codes (`sz.399317`) are converted to Sina-style (`sz399317`) inside `sina_service.py`.
- **SQLite cache** (`long_run_data.db`): Uses raw `sqlite3` (no ORM), WAL mode, 24h TTL. Unique constraint on `(index_code, date)` with `ON CONFLICT DO UPDATE` upsert.
- **ECharts dual pattern**: Anchor charts use `vue-echarts` with tree-shaken `echarts/core` imports. Hongli charts use raw `echarts` with manual `init()`/`dispose()`. Do not unify these patterns without a deliberate reason.
- **Scheduler**: APScheduler runs daily at 20:00 (configurable via `data_update_hour`/`data_update_minute`). Updates 3 anchor indices + 2 hongli indices.

## API Routes

All under `/api/v1/`: `anchor/`, `hongli/`, `macdv/`. Each module has `GET /data`, `GET /health`, `POST /refresh` (macdv has `POST /batch_query` instead).

## Style Conventions

- UI language is Chinese (导航、标题、标签均为中文)
- Chart colors: no gradients, flat colors only. White `#FFFFFF` backgrounds. Specific color values defined in `PLAN.md`.
- Tailwind CSS for styling; follow existing spacing/sizing conventions (`max-w-7xl`, `px-6`, `p-6`, etc.)
- Pinia stores use Composition API style

## Environment

Backend supports `.env` file via pydantic-settings. Key vars: `cache_ttl_hours`, `data_update_hour`, `data_update_minute`, `cors_origins`. No required secrets — `bs_username`/`bs_password` are unused (Sina API needs no auth).
