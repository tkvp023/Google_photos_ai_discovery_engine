# Quick Start Guide: Google Photos AI Discovery Engine

Build, compile, and run the Google Photos AI Discovery Engine.

## Prerequisites

- **Python 3.10+** with `pip`
- **Node.js 18+** with `npm`
- **API Keys** (Free tier available):
  - [Google Gemini API Key](https://aistudio.google.com/apikey) (Primary LLM classification)
  - [Groq API Key](https://console.groq.com/) (High-speed fallback LLM)
  - [YouTube Data API](https://console.cloud.google.com/) (For YouTube comments/video search)
  - [Apify / Reddit API](https://apify.com/) (For Reddit discussions)

---

## Step 1: Configuration

The discovery configuration has already been tailored for Google Photos in:
`ai-discovery-engine-template/ai-discovery-engine-template/discovery_config.yaml`

It defines:
* 5 active data sources (Play Store, App Store, Reddit, YouTube, Trustpilot)
* The 10 Strategic Discovery Questions (memory decay, retrieval failure stages, clutter, workarounds)
* 21 granular retrieval friction tags and 8 core product factors.

---

## Step 2: Compile the Engine Code

Run the setup generator to compile all domain-specific pipeline scrapers, prompts, schemas, and dashboard constants:

```bash
cd ai-discovery-engine-template/ai-discovery-engine-template

# Validate the configuration
python setup_engine.py --validate

# Generate domain code
python setup_engine.py
```

This compiles:
* `pipeline/scrapers/config.py` — Target package IDs, subreddits, query lists
* `pipeline/classification/prompts.py` — Few-shot memory retrieval classification prompts
* `pipeline/classification/schema.py` — Pydantic validation models
* `pipeline/classification/keyword_tagger.py` — Regex fallback patterns
* `pipeline/cleaning/relevance_filter.py` — Google Photos domain keyword filtering
* `pipeline/quantification/question_mapper.py` — Mapping tags to the 10 questions
* `dashboard/lib/constants.ts` — Frontend question colors and metadata

---

## Step 3: Set Up Environment & Dependencies

```bash
# In the template root directory
cp .env.example .env
# Edit .env with your Gemini, Groq, Reddit, and YouTube keys

# Install Python dependencies
pip install -r requirements.txt

# Install Dashboard dependencies
cd dashboard
npm install
cd ..
```

---

## Step 4: Run the Pipeline

```bash
cd pipeline

# 1. Initialize SQLite database schema
python run_pipeline.py --mode init-db

# 2. Scrape data (test with --limit 50 first)
python run_pipeline.py --mode scrape --limit 50

# 3. Clean & filter relevance
python run_pipeline.py --mode clean

# 4. Classify via LLM (extract friction reasons, intent, quotes)
python run_pipeline.py --mode classify

# 5. Export quantified metrics to dashboard
python run_pipeline.py --mode export
```

---

## Step 5: Start the RAG Service & Dashboard

### Launch RAG Semantic Server:
```bash
cd pipeline
python run_pipeline.py --mode rag-server
# Runs FastAPI on http://localhost:8000
```

### Launch Interactive Decision Dashboard:
```bash
cd dashboard
npm run dev
# Open http://localhost:3000 in your browser
```
