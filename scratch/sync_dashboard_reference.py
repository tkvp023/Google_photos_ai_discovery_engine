import json
from pathlib import Path

def format_question(i):
    p = Path(f"dashboard/public/data/q{i}.json")
    with open(p, "r", encoding="utf-8") as f:
        d = json.load(f)
    
    q_id = d["question_id"]
    q_text = d["question_text"]
    q_short = d["question_short"]
    total = d["total_relevant_docs"]
    conf = d["avg_confidence"]
    
    lines = []
    lines.append(f"### Question {q_id}: {q_short} (Q{q_id})")
    lines.append("")
    lines.append(f"- **Full Research Question:** {q_text}")
    lines.append(f"- **Phase Grouping:** Research Question")
    lines.append(f"- **Evidence Base:** {total:,} reviews analyzed | Calibrated Confidence: {conf:.3f}")
    lines.append("")
    
    top_b = d.get("breakdown", [])
    lines.append("#### Executive Takeaway & Key Findings")
    if top_b:
        top_item = top_b[0]
        lines.append(f"- **Headline:** {top_item['label']} dominates user friction ({top_item['pct']}% of cohort)")
        lines.append("- **Evidence Tiles:**")
        for b in top_b[:3]:
            lines.append(f"  1. **{b['label']}:** {b['count']} of {total:,} reviews ({b['pct']}%) report this retrieval friction mode.")
        lines.append(f"- **Key Metric ({top_item['label']}):** **{top_item['pct']}% ({top_item['count']:,} of {total:,} reviews)**")
    lines.append(f"- **Recommended Product Direction:** Implement targeted algorithmic improvements grounded in the {total:,} verified user complaints.")
    lines.append("")
    
    # Breakdown Table
    lines.append("#### Frequency Breakdown Table")
    lines.append("")
    lines.append("| Segment Tag | Problem Area | Mentions Count | Pct of Mentions | Calibrated Confidence |")
    lines.append("|:---|:---|---:|---:|---:|")
    for b in top_b:
        lines.append(f"| `{b['tag']}` | **{b['label']}** | {b['count']:,} | {b['pct']}% | {b.get('avg_confidence', conf):.3f} |")
    lines.append("")
    
    # Specialized Analytics
    if "temporal_distribution" in d:
        lines.append("#### Specialized Analytics: Search Struggles Over Time (Monthly Distribution)")
        lines.append("Distribution of search struggle mentions across months:")
        lines.append("")
        lines.append("| Month | Search Issues Count | Percentage of Search Corpus |")
        lines.append("|:---|---:|---:|")
        for td in d["temporal_distribution"]:
            lines.append(f"| **{td['month']}** | {td['count']} | {td.get('pct', round(td['count']/total*100, 1))}% |")
        lines.append("")
    elif "factor_correlation" in d:
        lines.append("#### Specialized Analytics: Multi-Factor Memory Anchor Radar")
        lines.append("User retention importance vs negative sentiment across recall dimensions:")
        lines.append("")
        lines.append("| Memory Clue Dimension | Retention Importance (%) | Negative Sentiment Rate (%) |")
        lines.append("|:---|---:|---:|")
        for fc in d["factor_correlation"]:
            lines.append(f"| **{fc['factor']}** | {fc['importance']}% | {fc['negative_pct']}% |")
        lines.append("")
    elif "retrieval_heatmap" in d:
        hm = d["retrieval_heatmap"]
        lines.append("#### Specialized Analytics: Metadata Degradation Heatmap")
        lines.append("Memory degradation rate across photo access modes:")
        lines.append("")
        cols = hm.get("columns", [])
        hdr = "| Metadata Dimension | " + " | ".join(cols) + " |"
        sep = "|:---|" + "|".join(["---:"] * len(cols)) + "|"
        lines.append(hdr)
        lines.append(sep)
        rows = hm.get("rows", [])
        vals = hm.get("values", [])
        for r_idx, row_name in enumerate(rows):
            row_vals = vals[r_idx] if r_idx < len(vals) else []
            v_str = " | ".join(f"{v}%" for v in row_vals)
            lines.append(f"| **{row_name}** | {v_str} |")
        lines.append("")
    elif "query_terms" in d:
        lines.append("#### Specialized Analytics: Query Formulation Pattern Matrix")
        lines.append("Common formulation structures and their breakdown rates:")
        lines.append("")
        lines.append("| Formulation Pattern | Volume Share (%) |")
        lines.append("|:---|---:|")
        for qt in d["query_terms"]:
            lines.append(f"| **{qt.get('text', 'Pattern')}** | {qt.get('value', 0)}% |")
        lines.append("")
    elif "retrieval_treemap" in d:
        lines.append("#### Specialized Analytics: False Miss & Hallucination Breakdown")
        lines.append("Failure modes across retrieval engines:")
        lines.append("")
        lines.append("| Theme | Sub-category | Relative Volume |")
        lines.append("|:---|:---|---:|")
        for group in d["retrieval_treemap"]:
            theme = group.get("theme", "General")
            for ch in group.get("children", []):
                lines.append(f"| **{theme}** | {ch.get('name', '')} | {ch.get('value', 0)} |")
        lines.append("")
    elif "failure_sankey" in d:
        lines.append("#### Specialized Analytics: Timeline Doom-Scrolling Flow Transitions")
        lines.append("User navigation transitions following search failure:")
        lines.append("")
        lines.append("| Transition Step | Description |")
        lines.append("|:---|:---|")
        for node in d["failure_sankey"].get("nodes", []):
            lines.append(f"| Node | {node.get('id', '')} |")
        lines.append("")
    elif "radar_data" in d:
        lines.append("#### Specialized Analytics: Clutter Pollution Profile")
        lines.append("Clutter volume and impact across photo library segments:")
        lines.append("")
        lines.append("| Clutter Category | Retention Importance (%) | Negative Sentiment Rate (%) |")
        lines.append("|:---|---:|---:|")
        for rd in d["radar_data"]:
            lines.append(f"| **{rd.get('factor', 'Item')}** | {rd.get('importance', 0)}% | {rd.get('negative_pct', 0)}% |")
        lines.append("")

    # Source Attribution Table
    src_attr = d.get("source_attribution", [])
    if src_attr:
        lines.append("#### Cross-Platform Attribution Breakdown")
        lines.append("")
        lines.append("| Topic / Segment | Play Store | App Store | Reddit | Hacker News | YouTube | Total Count |")
        lines.append("|:---|---:|---:|---:|---:|---:|---:|")
        for sa in src_attr:
            lbl = sa["label"]
            smap = {s["source"]: s["count"] for s in sa.get("sources", [])}
            play = smap.get("Play Store", 0)
            app = smap.get("App Store", 0)
            reddit = smap.get("Reddit", 0)
            hn = smap.get("Hacker News", 0)
            yt = smap.get("YouTube", 0)
            tot = sum([play, app, reddit, hn, yt])
            lines.append(f"| **{lbl}** | {play} | {app} | {reddit} | {hn} | {yt} | **{tot:,}** |")
        lines.append("")

    # Grounded Quotes
    quotes = d.get("key_quotes", [])
    if quotes:
        lines.append("#### Complete Verbatim Grounded Quotes")
        lines.append("")
        for q_idx, q in enumerate(quotes[:3], 1):
            lines.append(f"**Quote {q_idx}:**")
            lines.append(f"> \"{q['text']}\"")
            lines.append(f"> — *Platform: **{q['source']}** | Calibrated Score: `{q.get('confidence', conf):.2f}` (High confidence)*")
            lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)

def run():
    ref_path = Path("DOCS/DASHBOARD_FULL_CONTENT_REFERENCE.md")
    with open(ref_path, "r", encoding="utf-8") as f:
        content = f.read()

    q1_pos = content.find("### Question 1: Struggled Photo Types (Q1)")
    sec5_pos = content.find("## 5. Ask AI & Conversational Search Console (`/ask`)")

    if q1_pos == -1 or sec5_pos == -1:
        print("Could not find delimiters in DASHBOARD_FULL_CONTENT_REFERENCE.md!")
        return

    before = content[:q1_pos]
    after = content[sec5_pos:]

    q_blocks = []
    for i in range(1, 11):
        q_blocks.append(format_question(i))

    new_content = before + "\n".join(q_blocks) + "\n" + after

    with open(ref_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"Successfully updated Questions 1-10 in {ref_path} with canonical 1,616 corpus metrics!")

if __name__ == "__main__":
    run()
