# User Research Guide & Protocol — Google Photos Vague Retrieval (Part 3)

## 1. Research Objectives & Methodology

### Objectives:
1. **Validate Discovery Engine Hypotheses:** Verify if the friction points surfaced from thousands of scraped reviews (scrolling fatigue, screenshot clutter, lexical query mismatch) mirror real user lived experiences.
2. **Understand Mental Recall Models:** Unpack what clues users *actually* recall when thinking of past photos (sensory, relative time, companions, feelings) versus what they forget (dates, GPS tags, filenames).
3. **Map the Retrieval Breakdown Journey:** Observe firsthand where retrieval breaks down in real-time when users search on their personal devices.
4. **Uncover Compensatory Workarounds:** Document what users do when Google Photos fails (e.g., checking WhatsApp media galleries, searching Instagram archives, asking friends).

### Methodology:
* **Format:** 45–60 minute **Semi-Structured In-Depth Interview (IDI)** combined with a **Think-Aloud Live Retrieval Exercise**.
* **Sample Size:** **5–6 participants** meeting strict segment screening criteria.
* **Setting:** Remote (Google Meet/Zoom) with participant screen sharing their smartphone screen during the live retrieval exercise.

---

## 2. Participant Screening & Segmentation Matrix

To ensure balanced qualitative insights across diverse user archetypes, recruit **5–6 participants** across 3 distinct segments:

| Persona Segment | Characteristics | Target N | Key Research Focus |
| :--- | :--- | :--- | :--- |
| **Segment A: The Memory Custodian (Parents / Family Archivists)** | 10,000+ photos, backs up every family event, frequent nostalgia searches, heavy user of albums & face grouping. | **2 Participants** | Facial recognition failures, chronological confusion over years, emotional memory retrieval. |
| **Segment B: The Visual Utility Searcher (Young Professionals / Students)** | Uses camera as an external memory bank (receipts, medicine prescriptions, whiteboard notes, parking tickets, gym logs). | **2 Participants** | OCR text search breakdown, clutter interference, inability to locate critical documents quickly. |
| **Segment C: The Social & Event Capturer (Gen Z / Millennials)** | Frequent group trips, heavy WhatsApp/Instagram photo exchanges, screenshots, memes, candid social moments. | **2 Participants** | Relative time memory (*"summer before college"*), screenshot clutter pollution, WhatsApp workarounds. |

### Screener Questions:
1. Do you have at least 1,000+ photos backed up on Google Photos? *(Must be Yes)*
2. In the past 3 months, have you experienced a time where you remembered a photo existed but couldn't find it easily? *(Must be Yes)*
3. Are you willing to share your phone screen and perform a 5-minute search during the interview? *(Must be Yes)*

---

## 3. Step-by-Step Interview Protocol (45 Minutes)

### Part 1: Warm-Up & Photo Habits (5 mins)
* *"How often do you take photos, and what kind of photos make up most of your camera roll?"*
* *"When was the last time you opened Google Photos, and what was your primary goal?"*
* *"How organized is your library? Do you create albums, or is it one big timeline?"*

---

### Part 2: Critical Incident Recall (Deep-Dive into Recent Failure) (15 mins)
* *"Think back to the last time you spent 5–10 minutes looking for a specific photo and struggled to find it. What was the photo?"*
* **Unpack the Mental Image:**
  * *"When you pictured the photo in your head, what details stood out to you first?"*
  * *"Did you remember roughly when it happened? What kind of time anchor did you use (e.g. month, season, life event)?"*
  * *"Did you remember where it happened, who was with you, or what colors stood out?"*
* **Unpack the Forgotten Details:**
  * *"What details were fuzzy or completely missing (exact date, location name, restaurant name)?"*
* **Unpack the Search Action:**
  * *"What were the exact words or filters you typed into the search bar first?"*
  * *"What did Google Photos show you in response?"*
  * *"How did you feel when you saw those results?"*

---

### Part 3: Live Think-Aloud Retrieval Exercise (15 mins)
Ask the participant to share their phone screen and attempt two real retrieval tasks:

* **Task 1 (Episodic Memory):**  
  *"Please find a photo from a memorable trip or social gathering from 1 to 3 years ago that you haven't looked at recently. As you search, please say out loud everything you are thinking, typing, and looking for."*
* **Task 2 (Utility / Document):**  
  *"Please find a photo of a document, receipt, medicine bottle, or piece of text you snapped in the past year. Talk aloud as you try to locate it."*

#### Researcher Observation Checklist:
* [ ] What did the user type as their first query? Was it literal or contextual?
* [ ] Did search return 0 results, unrelated photos, or the target?
* [ ] How many times did the user reformulate their query?
* [ ] At what point did the user abandon search and start scrolling the timeline manually?
* [ ] How deep into the timeline did they scroll? (1 month, 6 months, 2 years?)
* [ ] Did screenshots or memes distract or disrupt their scanning?

---

### Part 4: Workarounds & Competitor Comparisons (10 mins)
* *"When Google Photos search failed, what did you do next? Did you give up, or did you try another app?"*
* *"Have you ever gone into WhatsApp, Instagram, or Apple Photos to find a photo because it was faster than Google Photos? Walk me through how you did that."*
* *"Have you ever texted a friend and asked: 'Hey, do you have that picture of us from...?'"*

---

### Part 5: Debrief & Solution Concept Exploration (5 mins)
* *"If you could talk to Google Photos like a human friend who was with you on that trip, how would you describe that photo to them?"*
* *"If Google Photos could automatically separate your family memories from random receipts and memes, how would that change your experience?"*

---

## 4. Qualitative Data Capture Template

Use this sheet to record observations for each participant during the session:

```markdown
### Participant ID: [P1 - P6]
- **Segment:** [Memory Custodian / Visual Utility / Social Capturer]
- **Device & OS:** [Pixel / Samsung / iPhone]
- **Library Size:** [e.g. 18,000 photos]

#### 1. Target Memory Attempted:
- Described as: __________________________________________________
- Retained Clues: [ ] Relative Time  [ ] Companion  [ ] Landmark  [ ] Color  [ ] Emotion
- Forgotten Clues: [ ] Exact Date  [ ] Exact Location  [ ] Album

#### 2. Query Formulation Progression:
- Query 1: "____________________" ──► Result: [0 Results / Irrelevant / Found]
- Query 2: "____________________" ──► Result: [0 Results / Irrelevant / Found]
- Query 3: "____________________" ──► Result: [0 Results / Irrelevant / Found]

#### 3. Behavioral Observations:
- Time Spent Searching: _______ seconds
- Switched to Manual Timeline Scrolling: [Yes / No]
- Number of Months Scrolled: _______
- Clutter Encountered: [Receipts / Screenshots / Memes / Duplicate Bursts]
- Outcome: [Found Target / Abandoned / Used WhatsApp Workaround]

#### 4. Verbatim User Quotes (Gold for Slide Deck):
- Quote 1 (Expression): "________________________________________________________"
- Quote 2 (Frustration): "________________________________________________________"
- Quote 3 (Workaround): "________________________________________________________"
```

---

## 5. Synthesis & Cross-Interview Comparison Matrix

After completing the 5–6 interviews, populate this matrix to feed directly into **Part 4 (Problem Definition)** and **Slide 5 of the Deck**:

| User ID | Segment | Target Retrieval Task | Initial Query | Point of Breakdown | Workaround Used | Task Success? |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **P1** | Parent / Custodian | Kid's 3rd birthday cake | *"Leo birthday cake"* | Missing face tag, flooded with 200 random cakes | Manually scrolled back to Sept 2022 | ✅ Succeeded after 8 mins |
| **P2** | Parent / Custodian | Family trip to beach | *"Goa sunset beach"* | Returned 400 sunsets across 5 different vacations | Gave up, asked spouse on WhatsApp | ❌ Abandoned |
| **P3** | Utility Searcher | Dog's ear medicine prescription | *"Ear drops medicine"* | Zero results; OCR missed curved bottle text | Searched Amazon order history instead | ❌ Abandoned in app |
| **P4** | Utility Searcher | Car insurance policy slip | *"Insurance car document"* | Overwhelmed by WhatsApp meme screenshots | Found original PDF in Gmail search | ❌ Switched apps |
| **P5** | Social / Gen Z | Paella at beach restaurant | *"Spain seafood paella"* | Paella photos returned without user's friends | Scrolled Instagram archived stories for date | ✅ Found via IG workaround |
| **P6** | Social / Gen Z | Group selfie at music fest | *"Me and Alex concert"* | User's face wasn't in photo (held camera) | Checked WhatsApp group chat media | ✅ Found in WhatsApp |
