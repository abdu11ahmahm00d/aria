<div align="center">

# ARIA

**Academic Integrity and OBE Analytics via Multi-Agent LLM Orchestration**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)]()
[![LangGraph](https://img.shields.io/badge/LangGraph-StateMachine-green.svg)]()
[![Svelte](https://img.shields.io/badge/GUI-Svelte_5-orange.svg)]()
[![Gemini](https://img.shields.io/badge/LLM-Gemini_2.5_Flash-purple.svg)]()
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)]()

</div>

**ARIA** is an AI-powered audit system that detects suspicious patterns in university grade data, student assessment records, and assignment submissions — replacing a manual review process that takes **40–60 hours per department per semester**.

---

## What It Does

ARIA analyzes **three CSV files** (grades, students, submissions) across **four independent fraud dimensions** using a LangGraph state machine with LLM-augmented reasoning:

| Fraud Type | What It Detects | Signal |
|------------|----------------|--------|
| **Grade Inflation** | Course averages deviating from historical norms | z-score > 1.5 |
| **CLO Inconsistency** | Mismatch between exam scores and Course Learning Outcome attainment | gap > 20% |
| **Submission Clustering** | Suspicious assignment submission patterns (same answers, short time window) | Δt ≤ 2min, similarity > 0.75 |
| **CO Completion Rate** | Anomalously perfect attainment rates across cohorts | 100% rate in ≥8 student cohorts |

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                         StateGraph                               │
│  ┌──────────┐     ┌──────────┐     ┌────────────┐               │
│  │Collector │────▶│ Detector │────▶│Synthesizer │────▶ Report    │
│  │ (CSV in) │     │ (4 flags)│     │ (Summary)  │               │
│  └────┬─────┘     └────┬─────┘     └──────┬──────┘               │
│       │                │                  │                      │
│       └─── error ─→ END└─── error ─→ END  └─── error ─→ END     │
└──────────────────────────────────────────────────────────────────┘
```

Three sequential LangGraph nodes with error escapes at every stage:

1. **Collector** — Loads & validates CSVs, computes derived signals (z-scores, CLO-exam gaps)
2. **Detector** — Runs 4 parallel fraud checkers (mock or LLM-augmented)
3. **Synthesizer** — Produces a severity-assessed audit report with correlations & recommendations

---

## Results

On the synthetic benchmark dataset (144 grades, 600 students, 986 submissions):

| Metric | Value |
|--------|-------|
| Total Flags Detected | 63 |
| Runtime (Mock Mode) | ~16s |
| Runtime (LLM Mode) | ~5 min |
| Fraud Types Covered | 4 / 4 |
| LLM Failover Tiers | 3 (Gateway → Gemini → Mock) |

---

## Getting Started

### Prerequisites

- Python 3.11+
- Google Gemini API key (optional — mock mode works without one)

### Setup

```bash
git clone https://github.com/abdu11ahmahm00d/aria.git
cd aria
pip install -r requirements.txt
cp .env.example .env  # Add your GEMINI_API_KEY (optional)
```

### Run

```bash
python main.py \
  --grades data/synthetic/grades.csv \
  --students data/synthetic/students.csv \
  --submissions data/synthetic/submissions.csv \
  --output output/
```

Output: `output/flags.json` (machine-readable) + `output/report.txt` (audit-ready)

### Web GUI (Svelte 5)

```bash
cd aria-gui
npm install
npm run dev
```

Deployed at: [aria-decypher.vercel.app](https://aria-decypher.vercel.app)

---

## Key Design Decisions

- **Mock mode as specification** — deterministic fraud rules define ground truth; LLM output is validated against them
- **Error isolation** — every node has an escape hatch; no cascading failures
- **Zero pandas leakage** — DataFrames never leave the Collector; the Detector works on JSON-safe dicts
- **LLM failover** — 3 tiers (local gateway → Gemini 2.5 Flash → mock), never crashes
- **GUI is client-side only** — no backend server, no API keys in the frontend

---

## Repository Structure

```
aria/
├── aria/                    # Pipeline agents
│   ├── state.py             # TypedDict data contract
│   ├── collector.py         # CSV input & validation
│   ├── detector.py          # 4 fraud checkers
│   ├── prompts.py           # Few-shot LLM templates
│   ├── llm_client.py        # Gemini with 3-tier failover
│   ├── synthesizer.py       # Audit report generation
│   └── _fix_langchain.py    # Compatibility shim
├── aria-gui/                # Svelte 5 web frontend
├── data/synthetic/          # Benchmark datasets
├── pipeline.py              # LangGraph graph construction
├── main.py                  # CLI entry point
└── ARCHITECTURE.md          # Full architecture docs
```

---

## Citation

```bibtex
@software{mahmood2025aria,
  title={ARIA: Academic Integrity and OBE Analytics via Multi-Agent LLM Orchestration},
  author={Mahmood, Abdullah},
  year={2025}
}
```

---

<div align="center">
<i>40 hours per department → 16 seconds.</i>
</div>
