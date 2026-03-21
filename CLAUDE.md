# CLAUDE.md

## Project Overview

**What2Do** is an AI-powered event finder and activity planner for Dallas, TX (with planned multi-city expansion). It aggregates events from local web sources and social media, uses Claude AI for daily curation and a RAG chatbot, and presents everything in a glassmorphism dark UI.

## Architecture

- **Frontend**: Next.js 15 (App Router) + TypeScript + Tailwind CSS 4 + shadcn/ui
- **Backend**: Python 3.12 + FastAPI + SQLAlchemy async + Alembic
- **Database**: PostgreSQL 16 with pgvector extension
- **Background Jobs**: Celery + Redis (Beat for scheduling)
- **AI**: Claude API for daily curation + RAG chatbot
- **Deployment**: Docker Compose (VPS)

## Data Sources

All data comes from web scrapers and social media monitoring (no third-party event APIs):
1. **dallasites101.com** — local events, restaurants, seasonal activities
2. **Dallas Observer** — structured event listings
3. **Silo Shows** — live music/concerts
4. **Visit Dallas** — official tourism events
5. **X/Twitter** — curated Dallas influencer/food/event accounts
6. **Sports schedules** — Mavericks, Cowboys, Stars, Rangers, FC Dallas

## Core Features

1. **Home Dashboard** — AI-curated daily picks, widgets (Tonight, Weekend, Happening Now, New Restaurants), calendar toggle
2. **Category Pages** — Concerts, Restaurants, Activities, Sports, Nightlife, Weekend Planner with filters and infinite scroll
3. **AI Curation** — Claude generates daily top picks and category recommendations
4. **RAG Chatbot** — "What should I do tonight?" powered by Claude + pgvector similarity search
5. **Refresh Button** — On-demand scraping per category via Celery tasks

## Design Principles

- **Glassmorphism dark theme** — Purple/cyan palette, frosted glass effects, mesh gradients
- **Every event links to source** — source_url is required, every card links to original post/page
- **Multi-city ready** — All models have city_id, routes use /[city]/ parameter
- **Scraper-first** — Unique local content over generic API data

## Project Structure

```
what2do/
├── .claude/agents/       # Specialized subagents
├── frontend/             # Next.js 15 app
│   └── src/
│       ├── app/[city]/   # All pages (concerts, restaurants, etc.)
│       ├── components/   # Reusable UI components
│       └── lib/          # API client, types, utilities
├── backend/
│   ├── app/
│   │   ├── api/routes/   # FastAPI endpoints
│   │   ├── core/         # Config, dependencies
│   │   ├── db/models/    # SQLAlchemy models (City, Event, Venue, etc.)
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Scrapers, AI, deduplication
│   │   ├── tasks/        # Celery tasks (scrape, curate, cleanup)
│   │   └── utils/        # Timezone, text helpers
│   └── alembic/          # Database migrations
├── docker/               # Dockerfiles
└── docker-compose.yml    # Full stack orchestration
```

## Key Commands

```bash
# Development
docker compose up          # Start all services
docker compose up -d       # Start detached

# Frontend only
cd frontend && npm run dev

# Backend only
cd backend && uvicorn app.main:app --reload

# Database
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "description"
cd backend && python -m app.db.seed  # Seed Dallas data

# Celery
celery -A app.worker worker --loglevel=info
celery -A app.worker beat --loglevel=info
```

## Conventions

- Backend routes: `/api/v1/{city_slug}/...`
- All datetimes stored UTC, displayed in city timezone (America/Chicago)
- Event dedup via content_hash (SHA256 of title + date + venue)
- Environment variables in `.env` files (never committed)
- Commit messages: imperative mood, concise
