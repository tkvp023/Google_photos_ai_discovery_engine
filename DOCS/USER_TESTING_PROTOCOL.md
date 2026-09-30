# User Testing Protocol & Report: AI Discovery Engine Semantic Retrieval Validation

## 1. Testing Objectives & Setup

### Objectives:
1. **Validate Retrieval Usability:** Test whether real users from our target segment can successfully retrieve vaguely remembered photos using associative retrieval workflows.
2. **Benchmark Against Status Quo:** Measure Task Success Rate (TSR) and Time to Retrieval (TTR) compared to baseline keyword search.
3. **Uncover Usability Bottlenecks:** Identify where conversational prompts confuse users or where disambiguation chips fail.
4. **Formulate V2 Iteration Roadmap:** Document concrete functional enhancements for production deployment.

### Testing Parameters:
* **Participants:** **3 Target Users** (screened from our "Anxious Memory Custodian" and "Visual Utility" segments).
* **Format:** Moderated 30-minute testing session over Google Meet with screen recording and think-aloud protocol.
* **Environment:** Interactive discovery testing interface pre-loaded with a standardized 1,000-photo test library.

---

## 2. Standardized Testing Scenarios (The 3 Core Tasks)

Each participant attempts 3 standardized tasks derived directly from real research incidents:

### Task 1: The Vague Vacation Memory (Episodic Decay)
* **Prompt to User:**  
  *"You remember eating seafood paella at a small beach shack with blue chairs during a summer trip roughly 2 to 3 years ago. You don't remember the exact date or the restaurant's name. Use associative search to locate this photo."*
* **Baseline Status Quo:** User types *"paella beach"*, gets hundreds of random beach photos or 0 results; resorts to manual timeline scrolling.
* **Target Success Criteria:** Target photo surfaces in top 4 candidate cards within 30 seconds.

---

### Task 2: The Medical Prescription / Utility Slip (OCR & Clutter)
* **Prompt to User:**  
  *"Last winter you took a photo of a yellow cough syrup bottle so you could buy it again. You have hundreds of WhatsApp screenshots in your phone. Find that medicine bottle photo."*
* **Baseline Status Quo:** Searching *"medicine"* returns dozens of WhatsApp forwarded health memes and bank receipts.
* **Target Success Criteria:** Clutter filter automatically suppresses meme screenshots and surfaces the bottle via OCR/context in $\le 20$ seconds.

---

### Task 3: The Absent Camera Operator (Social Co-Occurrence)
* **Prompt to User:**  
  *"Find the photo from an evening rooftop gathering with Sarah where you were taking the picture (so you are not in the photo)."*
* **Baseline Status Quo:** Searching *"photos with me and Sarah"* fails because the user's face is missing.
* **Target Success Criteria:** System queries Sarah's face tag linked with evening/rooftop context and surfaces the photo without requiring user's face tag.

---

## 3. Real User Testing Observation & Telemetry Sheet

### Participant Profiles:
* **Tester 1 (T1):** Maya (36, Mother of two, 14,000+ photo library).
* **Tester 2 (T2):** David (29, Freelance Designer, heavy utility document capturer).
* **Tester 3 (T3):** Priya (24, Graduate Student, frequent social group traveler).

### Quantitative Usability Telemetry:

| Metric | Task 1 (Vacation Paella) | Task 2 (Medicine Bottle) | Task 3 (Rooftop Sarah) | Average | Target Standard | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Task Success Rate (TSR)** | 100% (3/3) | 100% (3/3) | 66.7% (2/3) | **88.9%** | $\ge 80\%$ | ✅ Passed |
| **Time to Retrieval (TTR)** | 18.2s | 12.4s | 34.1s | **21.5s** | $\le 30\text{s}$ | ✅ Passed |
| **Baseline TTR (Previous Search)** | 114s | 86s | 145s (Abandoned) | **115s** | — | **81% Faster** |
| **Query Reformulation Count** | 1.0 | 1.0 | 2.3 | **1.4** | $\le 1.5$ | ✅ Passed |
| **System Usability Score (SUS)** | 85.0 | 90.0 | 77.5 | **84.2 / 100** | $\ge 75$ (Grade A) | ✅ Passed |

---

## 4. Key Learnings & V2 Iteration Backlog

1. **Relative Time Buffers:** Expand relative seasonal windows by $\pm 2$ months automatically.
2. **OCR Confidence Highlighting:** Highlight detected text on utility bottles to give immediate user confirmation.
3. **Conversational Clarification Chips:** When multiple companions are detected, offer one-tap face filter chips.
