# What2Do — Development Progress

> This file documents all context needed to continue development in a new session. Read this first.

## Project Summary

**What2Do** is an AI-powered event finder and activity planner for Dallas, TX. It aggregates events from local web scrapers and social media (intentionally no third-party APIs like Eventbrite/Ticketmaster), uses Claude AI for daily curation, and has a RAG chatbot.

- **GitHub**: https://github.com/amin-hamidi/what2do
- **Domain**: aminhamidi.com/what2do
- **Design**: Dark mode glassmorphism, purple (#8B5CF6) / cyan (#06B6D4) palette

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui, Zustand |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL 16 + pgvector |
| Jobs | Celery + Redis (Beat scheduler) |
| AI | Anthropic Claude (curation + RAG) |
| Infra | Docker Compose (6 services) |

## Architecture Decisions

- **No third-party event APIs** — Amin specifically chose scrapers + social media only for unique local content. Skip Eventbrite/Ticketmaster/Yelp/Google Places entirely.
- **Multi-city via route params** — URL: `/[city]/concerts`. All DB models have `city_id`. Start with Dallas, expand later.
- **Glassmorphism from dj-aide** — CSS theme ported directly from `/Users/aminhamidi/Desktop/Files/Code/dj-aide/frontend/src/app/globals.css`
- **X API client reuse** — The X social scraper should reuse the XClient pattern from `/Users/aminhamidi/Desktop/Files/Code/news_summary/daily_digest_xbot/x_client.py`
- **Every event links to source** — `source_url` is required on all events. Every UI card must link to the original post/page.

## Phase 1: Foundation — COMPLETED (2026-03-21)

### What was built (86 files, 4,893 lines):

**Backend:**
- 8 SQLAlchemy models: City, Category, Venue, Source, Event, AIPick, SportsTeam, SyncLog
- All in `backend/app/db/models/` with UUID PKs, timezone-aware datetimes, proper indexes
- 7 API route modules in `backend/app/api/routes/`: events (paginated + calendar), categories, venues, picks, chat, sync, health
- Scraper architecture: `BaseScraper` ABC + `ScrapedEvent` dataclass in `backend/app/services/scrapers/base.py`
- First scraper: `dallasites101.py` — scrapes dallasites101.com articles
- Deduplication service: `backend/app/services/deduplicator.py` — content hash + fuzzy matching
- 3 Celery tasks: `scrape.py` (all/single source), `curate.py` (placeholder), `cleanup.py` (expire old events)
- Celery Beat schedule in `worker.py`: scrape every 4h, curate at 5am CST, cleanup at 2am CST
- Seed script: `backend/app/db/seed.py` — Dallas city, 6 categories, 5 sources, 9 venues, 5 sports teams
- Pydantic schemas for all endpoints
- Config via pydantic-settings with .env

**Frontend:**
- Root layout with Geist fonts, forced dark mode, bg-mesh background
- `/` redirects to `/dallas`
- `[city]/layout.tsx` — sidebar with glassmorphism nav (8 items with Lucide icons) + mobile bottom nav
- 8 page files: home dashboard, concerts, restaurants, activities, sports, nightlife, weekend, chat
- `EventCard` component with glass styling, image/gradient, source link, category badge
- Typed API client (`lib/api.ts`), TypeScript interfaces (`lib/types.ts`), utilities (`lib/utils.ts`)
- All pages have placeholder UI with filter bars and "Coming soon" cards

**Infrastructure:**
- `docker-compose.yml` — 6 services: frontend, backend, db (pgvector/pgvector:pg16), redis, worker, beat
- Dockerfiles for backend (Python 3.12-slim) and frontend (Node 20-alpine)
- Alembic config + async env.py for migrations
- 10 specialized agents in `.claude/agents/`
- CLAUDE.md, README.md

### What is NOT yet done from Phase 1:
- Alembic migration files not generated yet (need `docker compose up` + `alembic revision --autogenerate`)
- Seed data not run yet (need DB running first)
- `npm install` not run in frontend yet (no node_modules/package-lock.json)
- Docker hasn't been tested yet — first `docker compose up` still needed

---

## Phase 2: Scrapers + Filters — TODO (Next Phase)

### 2.1 Remaining Scrapers
Create these scraper files in `backend/app/services/scrapers/`:

1. **`dallas_observer.py`** — Scrape Dallas Observer events section. More structured data with explicit date/time/venue.
2. **`silo_shows.py`** — Scrape Silo Shows for upcoming concerts/live music in Dallas.
3. **`visit_dallas.py`** — Scrape Visit Dallas official tourism site event listings.
4. **`x_social.py`** — Monitor 20-50 curated Dallas influencer/food/event X accounts. Reuse XClient from `news_summary/daily_digest_xbot/x_client.py`. Use Claude to classify tweets as events and extract structured data.
5. **`sports_schedules.py`** — Scrape team schedule pages for Mavericks, Cowboys, Stars, Rangers, FC Dallas.

After creating each, add to `SCRAPER_REGISTRY` in `backend/app/services/scrapers/__init__.py` and add the source to the seed script.

### 2.2 Wire Up Celery Beat
- Verify Beat schedule works with `docker compose up`
- Test `scrape_all` and `scrape_source` tasks end-to-end
- Verify SyncLog entries are created

### 2.3 Frontend: Event Filters
Build `EventFilters` component in `frontend/src/components/events/event-filters.tsx`:
- Dropdown/select for each filter (varies by category page)
- Sync filter state to URL search params
- Use Zustand store for filter state (`frontend/src/lib/store.ts`)
- Wire filters to the `getEvents()` API call

### 2.4 Frontend: Infinite Scroll Feed
Build `EventFeed` component in `frontend/src/components/events/event-feed.tsx`:
- Use `IntersectionObserver` for infinite scroll
- Cursor-based pagination (API already supports it)
- Loading skeleton cards
- "No events found" empty state

### 2.5 Wire Up Category Pages
Replace placeholder content in all category pages with real `EventFilters` + `EventFeed`:
- Concerts: filters for venue, genre, date, price
- Restaurants: filters for cuisine, neighborhood, price level
- Activities: filters for type, date, indoor/outdoor
- Sports: filters for sport/team, date
- Nightlife: filters for type, neighborhood, vibe
- Weekend: curated weekend view (group by Saturday/Sunday)

### 2.6 Calendar View
Build `EventCalendar` in `frontend/src/components/events/event-calendar.tsx`:
- Toggle between feed and calendar view on home page
- 7-column CSS grid calendar
- Click a date → show events for that day
- Uses `GET /{city}/events/calendar` endpoint

### 2.7 Refresh Button
- Wire the refresh button (already in UI) to `POST /{city}/sync/{source}` endpoint
- Show loading spinner during refresh
- On completion, re-fetch events for the current page

---

## Phase 3: AI Features — TODO (After Phase 2)

1. **Daily Curation** (`backend/app/services/ai_curator.py`):
   - Query upcoming events → send to Claude → get top_pick + category recs with blurbs → store in ai_picks table
   - Wire `curate_daily_picks` Celery task (currently placeholder)

2. **Home Dashboard Widgets**:
   - `HeroPick` component — full-width card for AI top pick of the day
   - `CategoryRecs` — horizontal scroll of AI picks per category
   - Widget cards: "Happening Now", "Tonight", "This Weekend", "New Restaurants"

3. **RAG Chatbot**:
   - Add pgvector extension to DB migration
   - Add embedding column to Event model
   - Generate embeddings with sentence-transformers on scrape
   - `backend/app/services/ai_chat.py` — vector search + Claude response + SSE streaming
   - Wire `POST /{city}/chat` endpoint (currently placeholder)

4. **Category Summaries** — Claude-generated, cached in Redis (4hr TTL)

## Phase 4: Polish + Deploy — TODO (After Phase 3)

- Error resilience, retry logic, sync logs admin UI
- Mobile responsiveness pass
- SEO: generateMetadata, Open Graph, JSON-LD for events
- Weekend Planner: AI-curated itineraries
- VPS deployment with Caddy/Nginx reverse proxy + SSL
- Redis caching for hot endpoints

---

## Key Reference Files (outside this repo)

| File | Purpose |
|------|---------|
| `dj-aide/backend/app/worker.py` | Celery setup pattern (already followed) |
| `dj-aide/frontend/src/app/globals.css` | Glassmorphism theme (already ported) |
| `news_summary/daily_digest_xbot/x_client.py` | **X API v2 client to reuse for x_social scraper** |
| `news_summary/daily_digest_xbot/claude_client.py` | Claude tool-use loop pattern (for AI curation) |
| `dj-aide/backend/app/services/spotify.py` | Service layer pattern (already followed) |
| `agents/*.md` | 10 specialized agents (already copied to .claude/agents/) |

## Environment Variables Needed

```
ANTHROPIC_API_KEY=     # For AI curation + chatbot (Phase 3)
X_BEARER_TOKEN=        # For X social scraper (Phase 2)
DATABASE_URL=postgresql+asyncpg://what2do:what2do@db:5432/what2do
REDIS_URL=redis://redis:6379/0
```

## Database Seed Data (created by `python -m app.db.seed`)

- **City**: Dallas, TX (slug: dallas, tz: America/Chicago)
- **Categories**: concerts, restaurants, activities, sports, nightlife, weekend
- **Sources**: dallasites101, dallas_observer, silo_shows, visit_dallas, x_social
- **Venues**: American Airlines Center, AT&T Stadium, Globe Life Field, Toyota Stadium, The Bomb Factory, Trees, Deep Ellum (area), Kessler Theater, Granada Theater
- **Sports Teams**: Dallas Mavericks (NBA), Dallas Cowboys (NFL), Dallas Stars (NHL), Texas Rangers (MLB), FC Dallas (MLS)
