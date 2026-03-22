# Deploying What2Do to Railway

## Overview

What2Do runs as 4 services on Railway + 2 managed plugins:
- **PostgreSQL** (Railway plugin — managed, free tier)
- **Redis** (Railway plugin — managed, free tier)
- **Backend** (FastAPI + Uvicorn)
- **Worker** (Celery worker for scraping + AI)
- **Beat** (Celery Beat scheduler)
- **Frontend** (Next.js)

**Domain**: `what2do.aminhamidi.com`

## Step-by-Step Setup

### 1. Push code to GitHub

```bash
cd /Users/aminhamidi/Desktop/Files/Code/what2do
git add -A
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. Create Railway project

1. Go to [railway.app](https://railway.app) and sign in with GitHub
2. Click **New Project** → **Empty Project**
3. Name it `what2do`

### 3. Add PostgreSQL plugin

1. In the project, click **+ New** → **Database** → **PostgreSQL**
2. Railway auto-creates the database and sets `DATABASE_URL`
3. After it's created, click on the PostgreSQL service → **Connect** tab
4. Note: Railway provides `DATABASE_URL` automatically to linked services

**Enable pgvector**: Click the PostgreSQL service → **Settings** → **Deploy** section. Railway's Postgres 16 image includes pgvector. If you need to manually enable it, connect via the provided connection string and run:
```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 4. Add Redis plugin

1. Click **+ New** → **Database** → **Redis**
2. Railway auto-creates Redis and sets `REDIS_URL`

### 5. Add Backend service

1. Click **+ New** → **GitHub Repo** → select `what2do`
2. Railway will detect the repo. Configure:
   - **Root Directory**: `backend`
   - **Builder**: Dockerfile
   - **Dockerfile Path**: `../docker/backend.Dockerfile` (or set to Nixpacks and it'll auto-detect Python)
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. Go to **Variables** tab and add:
   ```
   ANTHROPIC_API_KEY=sk-ant-api03-...
   X_BEARER_TOKEN=AAAAAAA...
   CORS_ORIGINS=["https://what2do.aminhamidi.com"]
   PORT=8000
   ```
   Railway auto-injects `DATABASE_URL` and `REDIS_URL` from the plugins.
4. Go to **Settings** → **Networking** → **Generate Domain** (for health checks)

### 6. Add Worker service

1. Click **+ New** → **GitHub Repo** → select `what2do` again
2. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `celery -A app.worker worker --loglevel=info --concurrency=2`
3. **Variables**: Same as backend (Railway lets you reference shared variables)
4. **No domain needed** (worker doesn't serve HTTP)

### 7. Add Beat service

1. Click **+ New** → **GitHub Repo** → select `what2do` again
2. Configure:
   - **Root Directory**: `backend`
   - **Start Command**: `celery -A app.worker beat --loglevel=info`
3. **Variables**: Same as backend
4. **No domain needed**

### 8. Add Frontend service

1. Click **+ New** → **GitHub Repo** → select `what2do` again
2. Configure:
   - **Root Directory**: `frontend`
   - **Builder**: Nixpacks (auto-detects Next.js)
3. **Variables**:
   ```
   NEXT_PUBLIC_API_URL=https://what2do-backend.up.railway.app/api/v1
   ```
   (Replace with the actual backend domain from step 5)
4. Go to **Settings** → **Networking** → **Custom Domain** → add `what2do.aminhamidi.com`

### 9. Configure DNS at Namecheap

1. Log in to [namecheap.com](https://namecheap.com)
2. Go to **Domain List** → `aminhamidi.com` → **Manage** → **Advanced DNS**
3. Add a new record:
   ```
   Type:  CNAME
   Host:  what2do
   Value: <your-frontend-railway-domain>.up.railway.app
   TTL:   Automatic
   ```
   (Railway gives you the target domain when you add a custom domain)
4. Wait for DNS propagation (usually 5-15 min)

### 10. Run migrations + seed

After all services are running:

1. In Railway, click on the **Backend** service
2. Go to **Settings** → **Deploy** → click **Open Shell** (or use Railway CLI)
3. Run:
   ```bash
   alembic upgrade head
   python -m app.db.seed
   ```

Or use Railway CLI locally:
```bash
npm install -g @railway/cli
railway login
railway link  # select the what2do project
railway run -s backend -- alembic upgrade head
railway run -s backend -- python -m app.db.seed
```

### 11. Verify

- `https://what2do.aminhamidi.com` → frontend loads
- `https://what2do-backend.up.railway.app/health` → `{"status":"healthy"}`
- `https://what2do-backend.up.railway.app/api/v1/dallas/categories` → 6 categories

## Ongoing

- **Auto-deploys**: Every push to `main` triggers redeploy on all services
- **Scraping**: Celery Beat runs scrapers every 4h, curation at 5am CST
- **Logs**: Railway dashboard → service → **Logs** tab
- **Costs**: $5 free credit/mo. Monitor usage in Railway dashboard → **Usage**

## Cost Optimization

To stay within the $5 free tier:
- Worker and Beat are the most expensive (always running). Consider combining them into one service with a supervisor process if needed.
- The sentence-transformers model uses ~500MB RAM on first load. If this blows the memory budget, you can disable embeddings and rely on text search for chat.
