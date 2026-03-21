# What2Do

AI-powered event finder and activity planner for Dallas, TX.

What2Do aggregates events, restaurants, concerts, nightlife, sports, and seasonal activities from local Dallas sources and social media. Claude AI curates daily recommendations and powers a chatbot that answers "What should I do tonight?"

## Features

- **Daily AI Picks** — Claude analyzes upcoming events and curates personalized top picks with blurbs
- **8 Pages** — Home dashboard, Concerts & Music, Restaurants, Activities, Sports, Nightlife, Weekend Planner, AI Chat
- **Smart Filters** — Filter by venue, genre, cuisine, neighborhood, price, date range
- **Calendar View** — See what's happening on any date
- **RAG Chatbot** — Ask "What should I do tonight?" and get recommendations grounded in real events
- **Refresh Button** — Fetch the latest events on demand per category
- **Multi-City Ready** — Designed to expand beyond Dallas

## Data Sources

All data comes from local web scrapers and social media (no generic third-party APIs):

| Source | Type | Content |
|--------|------|---------|
| dallasites101.com | Web scraper | Events, restaurants, seasonal activities |
| Dallas Observer | Web scraper | Structured event listings |
| Silo Shows | Web scraper | Live music, concerts |
| Visit Dallas | Web scraper | Official tourism events |
| X/Twitter | Social monitoring | 20-50 curated Dallas influencer accounts |
| Sports schedules | Web scraper | Mavericks, Cowboys, Stars, Rangers, FC Dallas |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Next.js 15 (App Router), React 19, TypeScript, Tailwind CSS 4, shadcn/ui |
| Backend | Python 3.12, FastAPI, SQLAlchemy async, Alembic |
| Database | PostgreSQL 16 + pgvector |
| Background Jobs | Celery + Redis (Beat scheduler) |
| AI | Anthropic Claude (curation + RAG chatbot) |
| Infrastructure | Docker Compose |

## Getting Started

### Prerequisites

- Docker & Docker Compose
- Node.js 20+ (for frontend dev)
- Python 3.12+ (for backend dev)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/amin-hamidi/what2do.git
   cd what2do
   ```

2. **Set up environment variables**
   ```bash
   cp backend/.env.example backend/.env
   # Edit backend/.env with your API keys:
   # - ANTHROPIC_API_KEY (for AI curation + chatbot)
   # - X_BEARER_TOKEN (for social media monitoring)
   ```

3. **Start all services**
   ```bash
   docker compose up
   ```

4. **Run database migrations and seed data**
   ```bash
   docker compose exec backend alembic upgrade head
   docker compose exec backend python -m app.db.seed
   ```

5. **Access the app**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/docs
   - Health check: http://localhost:8000/health

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## API Endpoints

All endpoints are prefixed with `/api/v1/{city_slug}`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{city}/events` | Paginated, filterable events |
| GET | `/{city}/events/calendar` | Events grouped by date |
| GET | `/{city}/categories` | Categories with event counts |
| GET | `/{city}/venues` | Venues with event counts |
| GET | `/{city}/picks` | Today's AI-curated picks |
| GET | `/{city}/picks/{date}` | Picks for a specific date |
| POST | `/{city}/chat` | RAG chatbot (SSE stream) |
| POST | `/{city}/sync/{source}` | Trigger on-demand scrape |
| GET | `/{city}/sync/status` | Recent sync logs |
| GET | `/health` | Health check |

## Project Structure

```
what2do/
├── frontend/               # Next.js 15 app
│   └── src/
│       ├── app/[city]/     # Pages (home, concerts, restaurants, etc.)
│       ├── components/     # Reusable UI (event-card, sidebar, chat)
│       └── lib/            # API client, types, utilities
├── backend/
│   ├── app/
│   │   ├── api/routes/     # FastAPI endpoints
│   │   ├── db/models/      # SQLAlchemy models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Scrapers, AI, deduplication
│   │   └── tasks/          # Celery tasks
│   └── alembic/            # Database migrations
├── docker/                 # Dockerfiles
├── docker-compose.yml      # Full stack orchestration
└── CLAUDE.md               # Project context for AI assistants
```

## Background Jobs

Celery Beat runs these on a schedule:

| Task | Schedule | Description |
|------|----------|-------------|
| `scrape_all` | Every 4 hours | Run all active scrapers |
| `curate_daily_picks` | 5:00 AM CST | AI generates daily recommendations |
| `cleanup_expired` | 2:00 AM CST | Archive past events |

## Design

Dark mode glassmorphism UI with purple (#8B5CF6) and cyan (#06B6D4) accent colors. Frosted glass cards, mesh gradient backgrounds, and glow effects.

## Roadmap

- [x] Phase 1: Foundation — project setup, models, first scraper, basic UI
- [ ] Phase 2: More scrapers, filters, infinite scroll, calendar view
- [ ] Phase 3: AI curation, RAG chatbot, dashboard widgets
- [ ] Phase 4: Polish, deploy, SEO, mobile optimization
- [ ] Multi-city expansion (Austin, Houston, etc.)

## License

MIT
