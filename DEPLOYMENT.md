# Deployment Guide: Google Photos AI Discovery Engine

This repository is architected for dual-cloud production deployment:
* **Frontend:** Next.js 16 (Turbopack, App Router) deployed on **Vercel**.
* **Backend:** FastAPI RAG & Vector Intelligence Service deployed on **Railway**.

---

## Architecture Overview

```
[User Browser]
       │
       ▼
[Vercel Global Edge CDN]
  • Next.js 16 App Router (dashboard/)
  • 17 Static Prerendered Routes (SSG) for sub-second delivery
  • /api/ask Proxy with Automatic Offline Fallback
       │
       ▼ (HTTPS REST / JSON)
[Railway Production Container]
  • Python / Uvicorn Server (pipeline.rag.server:app)
  • Scikit-Learn TF-IDF + Cosine Vector Engine
  • Gemini 3.7 / 3.6 Flash LLM Synthesis with Groq Fallback
  • 2,223 Classified Voice-of-Customer Review Corpus
```

---

## 1. Backend Deployment on Railway

### Prerequisites
* A [Railway](https://railway.app) account.
* A [Google AI Studio](https://aistudio.google.com/) API Key (`GEMINI_API_KEY`).
* *(Optional)* A [Groq](https://console.groq.com/) API Key (`GROQ_API_KEY`) for secondary fallback.

### Step-by-Step Instructions

1. **Log in to Railway** and click **New Project**.
2. Select **Deploy from GitHub repo** and choose your repository.
3. Railway will automatically detect the configuration files in the root:
   * [`railway.toml`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/railway.toml): Defines the Nixpacks build, healthcheck path, and restart policies.
   * [`Procfile`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/Procfile): Defines the web start command:
     ```bash
     web: python -m uvicorn pipeline.rag.server:app --host 0.0.0.0 --port ${PORT:-8000}
     ```
   * [`requirements.txt`](file:///c:/Users/THARUN/Videos/AI%20DISCOVERY%20ENGINE%20GOOGLE%20PHOTOS/requirements.txt): Installs FastAPI, Uvicorn, Scikit-Learn, Google Generative AI, etc.

4. **Configure Environment Variables** in Railway:
   Navigate to **Variables** in your Railway service and add:

   | Variable | Value | Required | Description |
   | :--- | :--- | :---: | :--- |
   | `GEMINI_API_KEY` | `AIzaSy...` | **Yes** | Primary LLM synthesis |
   | `GROQ_API_KEY` | `gsk_...` | Optional | Automatic backup if Gemini quota limits |
   | `ALLOWED_ORIGINS` | `*` | Optional | CORS whitelist (set to Vercel URL or `*`) |
   | `PYTHONUNBUFFERED` | `1` | Recommended | Ensures immediate real-time logging |

5. **Generate a Public Domain**:
   * Go to **Settings** $\to$ **Networking** $\to$ Click **Generate Domain**.
   * Note the URL generated (e.g. `https://google-photos-discovery-production.up.railway.app`).

6. **Verify Backend Health**:
   Open in your browser or curl:
   ```bash
   curl https://<your-railway-domain>.up.railway.app/health
   ```
   Expected response:
   ```json
   {
     "status": "ok",
     "vectors": 2223,
     "model": "gemini-3.7-flash + vector-store"
   }
   ```

---

## 2. Frontend Deployment on Vercel

### Prerequisites
* A [Vercel](https://vercel.com) account connected to your GitHub account.
* The public Railway URL from Section 1.

### Step-by-Step Instructions

1. **Log in to Vercel** and click **Add New** $\to$ **Project**.
2. Select and import your GitHub repository.
3. **Configure Project Settings (CRITICAL)**:
   * **Root Directory:** Click **Edit** and change it from `./` to **`dashboard`**.
     *(Since Next.js is located in the `dashboard/` subfolder, setting this ensures Vercel installs dependencies and builds from the correct directory).*
   * **Framework Preset:** `Next.js` (automatically detected).
   * **Build Command:** `next build` (default).
   * **Output Directory:** `.next` (default).

4. **Configure Environment Variables** in Vercel:
   Add the following variables:

   | Variable | Value | Description |
   | :--- | :--- | :--- |
   | `RAG_API_URL` | `https://<your-railway-domain>.up.railway.app` | Backend URL used by Next.js server route |
   | `NEXT_PUBLIC_RAG_API_URL` | `https://<your-railway-domain>.up.railway.app` | Client-accessible backend URL fallback |

   > **Note:** Do not worry about trailing slashes (`/`). The API proxy automatically sanitizes the URL to prevent double slashes.

5. Click **Deploy**.
   * Vercel will run `npm run build` and generate static pages for all 17 routes.
   * Once finished, you will receive your live `.vercel.app` URL.

---

## 3. Local Development & Verification

To run both services locally before deploying:

### Start Backend (Terminal 1)
```bash
# In repository root
pip install -r requirements.txt
python -m uvicorn pipeline.rag.server:app --host 0.0.0.0 --port 8000 --reload
```
Healthcheck: `http://localhost:8000/health`

### Start Frontend (Terminal 2)
```bash
cd dashboard
npm install
npm run dev
```
Open: `http://localhost:3000`

---

## 4. High-Availability & Resilience Architecture

1. **Zero-Downtime Fallback**:
   If the Railway backend is cold-starting or temporarily asleep, the Next.js frontend route (`/api/ask`) catches the timeout after 8 seconds and automatically switches to the built-in offline intelligence engine. It returns grounded answers using the pre-compiled review corpus and JSON exports without crashing or showing a 500 error to users or evaluators.

2. **Edge Pre-rendering (SSG)**:
   All 10 strategic inquiry pages (`/questions/1` through `/questions/10`), the Executive Summary (`/`), and Systemic Gaps (`/gaps`) are compiled into static HTML at build time. Visitors experience instant sub-100ms page transitions globally via Vercel's Edge Network.

3. **No Third-Party Extension Collisions**:
   The application includes inline pre-hydration cleanup that strips third-party antivirus/extension attributes (`bis_skin_checked="1"`), preventing React hydration mismatches on client browsers.

---

## 5. Deployment Verification Checklist

- [ ] Railway service reports status `Active` with green deployment indicator.
- [ ] `https://<railway-domain>/health` returns `{"status": "ok", "vectors": 2223}`.
- [ ] Vercel deployment completes with **Exit Code 0** across all 17 static routes.
- [ ] Navigating between `/`, `/questions/1`, `/gaps`, and `/ask` is fast and responsive.
- [ ] Dark Mode and Light Mode toggle seamlessly using the top-right controls.
- [ ] In `/ask`, submitting a query returns answers with clickable review citations and source badges.
