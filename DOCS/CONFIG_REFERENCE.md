# Configuration Reference

Complete reference for `discovery_config.yaml` — the single configuration file that defines your discovery engine.

---

## `project`

| Field | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✅ | Display name for the project |
| `slug` | string | ✅ | Short identifier (lowercase, no spaces, used in file names) |
| `description` | string | ✅ | One-line description of what the engine discovers |

```yaml
project:
  name: "Google Photos AI Discovery Engine"
  slug: "google_photos"
  description: "Analyzing visual memory retrieval friction..."
```

---

## `domain`

| Field | Type | Required | Description |
|---|---|---|---|
| `brand_name` | string | ✅ | The brand/product being analyzed |
| `industry` | string | ✅ | Industry (gives LLM context) |
| `competitors` | list[string] | ✅ | Competitor brand names |

---

## `sources`

Each source has `enabled: true/false` and source-specific settings.

### `playstore`
| Field | Description | Default |
|---|---|---|
| `app_id` | Google Play package name (e.g., `com.google.android.apps.photos`) | — |
| `country` | Country code | `in` / `us` |
| `lang` | Language code | `en` |
| `count` | Max reviews to fetch | `50000` |
| `batch_size` | Reviews per API call | `200` |

### `appstore`
| Field | Description | Default |
|---|---|---|
| `app_id` | Apple App Store numeric ID (e.g., `962194608`) | — |
| `country` | Country code | `in` / `us` |
| `max_pages` | Max RSS pages | `50` |
| `target_count` | Target review count | `10000` |

### `reddit`
| Field | Description | Default |
|---|---|---|
| `subreddits` | List of subreddit names | — |
| `search_queries` | Search queries to run | — |
| `sort` | Sort order | `relevance` |
| `time_filter` | Time filter | `all` |
| `limit_per_query` | Max results per query | `500` |
| `include_comments` | Include comment threads | `true` |
| `comment_depth` | Max comment depth | `5` |
| `min_upvotes` | Minimum upvotes filter | `1` |

### `youtube`
| Field | Description | Default |
|---|---|---|
| `search_queries` | YouTube search queries | — |
| `max_videos_per_query` | Videos per query | `30` |
| `max_comments_per_video` | Comments per video | `200` |
| `order` | Sort order | `relevance` |
| `published_after` | ISO date cutoff | `2022-01-01T00:00:00Z` |
| `region_code` | Region | `US` / `IN` |

### `trustpilot`
| Field | Description | Default |
|---|---|---|
| `url` | Trustpilot company review URL | — |
| `max_pages` | Max pages to scrape | `100` |
| `target_count` | Target review count | `5000` |

### `pissedconsumer`
| Field | Description | Default |
|---|---|---|
| `url` | PissedConsumer company URL | — |
| `max_pages` | Max pages | `50` |
| `target_count` | Target count | `3000` |

### `reviewsio`
| Field | Description | Default |
|---|---|---|
| `url` | Reviews.io company URL | — |
| `max_pages` | Max pages | `20` |
| `target_count` | Target count | `1000` |

---

## `discovery_questions`

List of 1-10 strategic questions the engine will answer.

| Field | Type | Required | Description |
|---|---|---|---|
| `id` | int | ✅ | Question number (1-10) |
| `text` | string | ✅ | Full question text |
| `short` | string | ✅ | Short label (for UI cards) |
| `related_tags` | list[string] | ❌ | Hesitation tags related to this question. Empty = uses other data (intent, factors, etc.) |

---

## `classification`

Defines the classification schema the LLM uses to tag reviews.

### `hesitation_reasons`
List of friction/hesitation categories. These become the core taxonomy.

### `factor_categories`
Key factors analyzed across reviews. Each gets a mentioned/sentiment analysis.

### `intent_types`
User intent categories (e.g. `vague_episodic_recall`, `utility_document_retrieval`, `unknown`).

### `user_segments`
| Field | Description |
|---|---|
| `age_groups` | Age group categories |
| `price_sensitivity` | Price sensitivity levels |
| `engagement_level` | Engagement levels |
| `gender_signals` | Gender signal categories |

### `competitor_platforms`
List of competitor platform IDs for comparison tracking (e.g. `apple_photos`, `whatsapp`, `onedrive`).

### `external_info_types`
Types of external information users seek before purchasing or when troubleshooting.

---

## `relevance`

### `domain_keywords`
Keywords that indicate a review is relevant to your domain. Reviews from Reddit/YouTube without these keywords are filtered out.

### `auto_relevant_sources`
Sources where ALL reviews are inherently relevant (e.g., `playstore`, `appstore` — because they're specifically about your app).

---

## `few_shot_examples`

2-3 example reviews with expected classifications. Helps the LLM understand your domain.
