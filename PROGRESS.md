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
- ~~Alembic migration files not generated yet~~ — DONE (Phase 2)
- ~~Seed data not run yet~~ — DONE (Phase 2)
- ~~npm install not run in frontend yet~~ — DONE (Phase 2)
- ~~Docker hasn't been tested yet~~ — DONE (Phase 2)

### Port Mappings (from Phase 2):
Host ports were remapped to avoid conflicts with other Docker projects:
- Frontend: `localhost:3001` → container:3000
- Backend: `localhost:8001` → container:8000
- PostgreSQL: `localhost:5433` → container:5432
- Redis: `localhost:6380` → container:6379

---

## Phase 2: Scrapers + Filters — COMPLETED (2026-03-22)

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

### What was built in Phase 2:

**Backend — 5 new scrapers + fixes:**
- `dallas_observer.py` — scrapes dallasobserver.com event listings (found 2 events on first run)
- `silo_shows.py` — scrapes siloshows.com for concerts
- `visit_dallas.py` — scrapes visitdallas.com tourism events (found 8 events)
- `x_social.py` — monitors curated Dallas X accounts via async XClient (needs X_BEARER_TOKEN)
- `sports_schedules.py` — scrapes team schedule pages (found 21 events — full Cowboys schedule!)
- All registered in SCRAPER_REGISTRY, sports_schedules source added to seed
- Fixed scrape task: combined scraper + dedup into single asyncio.run() with fresh engine per task
- Fixed scrape task: added city_slug parameter, removed source_type filter

**Frontend — 3 new components + 7 page rewrites:**
- `event-filters.tsx` — reusable filter bar with search, dropdown selects, URL param sync, clear all
- `event-feed.tsx` — infinite scroll feed with cursor pagination, skeleton loading, empty state
- `event-calendar.tsx` — month grid calendar with event dots, date selection, event detail view
- All 6 category pages rewritten with real EventFilters + EventFeed (concerts, restaurants, activities, sports, nightlife, weekend)
- Home page updated: feed/calendar toggle, real EventFeed, wired refresh button via triggerSync()
- Fixed API client paths and types to match backend schemas

**Infrastructure:**
- Docker Compose ports remapped (3001, 8001, 5433, 6380) to avoid conflicts
- frontend.Dockerfile: npm ci → npm install (no lock file)
- Added alembic/script.py.mako template
- Initial Alembic migration generated and applied
- Seed data run: Dallas city, 6 categories, 6 sources, 9 venues, 5 sports teams
- 31 real events scraped and stored across 4 categories

---

## Phase 3: AI Features — COMPLETED (2026-03-22)

### What was built in Phase 3:

**Backend — AI Services:**
- `embedder.py` — sentence-transformers (all-MiniLM-L6-v2, 384-dim) for event embeddings
  - Auto-embeds new events after each scrape (hooked into scrape task)
  - 11 events embedded successfully on first run
- `ai_curator.py` — Claude-powered daily curation service
  - Queries upcoming events, sends to Claude for ranking
  - Creates AIPick entries (top_pick + category picks with blurbs)
  - Wired into Celery Beat (5am CST daily)
- `ai_chat.py` — RAG chatbot with vector search
  - Embeds user query → pgvector cosine similarity search → Claude response
  - Falls back to text search if no embeddings exist
  - Falls back to event list if no API key configured
  - Passes matched events as context to Claude

**Database:**
- Added pgvector extension (`CREATE EXTENSION vector`)
- Added `embedding Vector(384)` column to events table
- New Alembic migration applied

**Frontend:**
- Home page: HeroPick section shows real AI pick data (title, blurb, image, link)
- Home page: Widget cards wired with real data (Tonight, This Weekend, New Restaurants counts)
- Chat page: Wired to real `POST /{city}/chat` API
- Chat page: Shows matched events as EventCards below assistant messages
- Chat page: Passes conversation history for multi-turn conversations
- Updated types.ts: AIPick, DailyPicks, ChatResponse aligned with backend schemas

**Status:** All AI features functional. Requires `ANTHROPIC_API_KEY` in .env for Claude-powered responses. Without it, falls back to event listing mode.

### What remains for later:
- Category Summaries — Claude-generated, cached in Redis (4hr TTL)

## Phase 4: Polish + Deploy — COMPLETED (2026-03-22)

### What was built in Phase 4:

**Error Resilience:**
- Exponential backoff between scraper retries (2^attempt seconds, max 10s)
- SyncLog now records city_id so sync status endpoint works
- Celery tasks: autoretry_for with 60s backoff, max 2 retries
- Claude API calls: 30s timeout (chat), 60s timeout (curation)

**Mobile Responsiveness:**
- Safe-area insets for notched phones (iOS)
- Filter bar: horizontal scroll on mobile with hidden scrollbar
- Chat: `100dvh` for dynamic viewport height (handles mobile keyboard)
- Bottom nav: safe-area padding

**SEO:**
- Root layout: title template, Open Graph, Twitter cards, keywords, robots
- City layout: server/client split for `generateMetadata`
- 7 category layouts with page-specific titles: "Concerts & Music in Dallas | What2Do"
- next.config: `output: "standalone"`, `images.remotePatterns` for all scraper domains, security headers

**Redis Caching:**
- `backend/app/core/cache.py` — async cache utility (get/set/invalidate)
- Categories endpoint: 5min TTL
- Picks endpoint: 15min TTL
- Cache invalidation support for pattern matching

**Production Deployment:**
- `docker/Caddyfile` — reverse proxy with auto-HTTPS, gzip, security headers
- `docker-compose.prod.yml` — production override with Caddy, no exposed internal ports
- `docker/frontend.prod.Dockerfile` — multi-stage build (standalone output)
- `docker/backend.prod.Dockerfile` — gunicorn with 4 uvicorn workers

**Weekend Planner:**
- `curate_weekend_plan()` in ai_curator — Claude generates Saturday/Sunday itineraries
- Weekend page: fetches AI picks, displays Morning/Afternoon/Evening slots for each day
- Glassmorphism Saturday (purple glow) / Sunday (cyan glow) cards

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
