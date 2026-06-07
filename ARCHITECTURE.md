# Architecture

ARIA (Academic Integrity and OBE Analytics via Multi-Agent LLM Orchestration) detects suspicious patterns in university grade data, student assessment records, and assignment submissions. It replaces a manual audit process that takes 40-60 hours per department per semester and that no university ever staffed.

## Bird's Eye View

Three CSV files enter a LangGraph state machine with three sequential nodes. The Collector loads and validates the data, computing derived signals (z-scores, CLO-exam gaps). The Detector runs four independent fraud checkers over those signals, each in either deterministic mock mode or LLM-augmented mode. The Synthesizer takes the resulting list of flags and produces a human-readable audit report with severity assessment, correlations, and recommendations.

Every node has an error escape hatch -- any node that sets `state["error"]` halts the pipeline before downstream nodes execute. This prevents cascading failures from invalid input.

## Code Map

This section describes the high-level structure of the codebase. Pay attention to **Boundary** and **Invariant** callouts.

### `aria/` -- Pipeline agents

The core of the system. Seven files, each with a single responsibility. This directory IS the application.

**Boundary:** `main.py` and `pipeline.py` are the only files outside `aria/` that import from this directory. No file inside `aria/` imports from outside `aria/` except `requests`, `pandas`, standard library, and LangGraph/LangChain.

**Invariant:** No file in `aria/` does I/O except `collector.py` (reads CSVs), `llm_client.py` (HTTP to LLM APIs), and `synthesizer.py` (implicitly none -- it writes nothing, just builds a string). The Detector and Prompts modules are pure data transformation.

#### `aria/state.py` -- The data contract

Defines `ARIAState`, a TypedDict with seven fields: three file paths, `normalized_data`, `flags`, `report`, and `error`. Every pipeline node reads from and writes to this type. The field order matches pipeline execution order.

Key types: `ARIAState`

#### `aria/collector.py` -- Input stage

Reads three CSV files via pandas, validates column schemas against `GRADES_COLS`, `STUDENTS_COLS`, and `SUBMISSIONS_COLS`, computes derived fields (z-scores for Grade Inflation, CLO-exam gaps for CLO Inconsistency, datetime parsing for Submission Clustering), and serializes everything to JSON-safe dicts.

**Boundary:** This is the only node that touches the filesystem for input. The Detector never sees raw CSV data or file paths.

**Invariant:** No pandas DataFrame leaves this module. Output is always `Dict[str, List[Dict]]`.

#### `aria/detector.py` -- Detection logic

Four independent functions, one per fraud type: `check_grade_inflation`, `check_clo_inconsistency`, `check_submission_clustering`, `check_co_completion_rate`. Each iterates over its slice of `normalized_data`, applies either a mock rule or an LLM prompt, and returns a list of flag dicts. The master node `detector_node` concatenates all four results.

Key types: `_is_mock()`, `_mock_flag()`

**Invariant:** Fraud types are independent. No checker reads another's output. The LLM path and mock path are mutually exclusive per run -- mock mode sets `ARIA_USE_MOCK_LLM=1` and every function checks this first, skipping the LLM path entirely.

#### `aria/prompts.py` -- Few-shot LLM prompts

Four template strings: `GRADE_INFLATION_PROMPT`, `CLO_INCONSISTENCY_PROMPT`, `SUBMISSION_CLUSTERING_PROMPT`, `CO_COMPLETION_PROMPT`. Each follows the same structure: role definition, fraud type definition, record schema with format variables, few-shot examples (flagged and not flagged), step-by-step reasoning instructions, strict JSON output template.

**Invariant:** These are the only files that contain LLM-facing natural language. Changing detection criteria means changing these prompts, not the detector logic.

#### `aria/llm_client.py` -- LLM failover

Two functions: `call_llm` (returns raw text) and `call_llm_json` (strips code fences, parses JSON, returns dict or None). Three-tier failover: local Firman gateway on port 18789, Gemini 2.5 Flash via Google AI Studio with exponential backoff (2^attempt seconds, 10 retries), and fallback to a mock response when `ARIA_USE_MOCK_LLM=1`.

**Invariant:** Neither `call_llm` nor `call_llm_json` ever crashes the pipeline. Network failures, timeouts, non-200 responses, and malformed JSON all produce logged warnings and return `None`. The caller decides what to do.

#### `aria/synthesizer.py` -- Report generation

Takes the flat flag list from the Detector. Groups by fraud type. Computes severity (NONE/LOW/MEDIUM/HIGH) via `_compute_severity`. Finds cross-flag correlations via `_find_correlations`. Estimates CLO attainment impact via `_estimate_clo_impact`. Generates numbered recommendations. In mock mode, builds the report from string templates. In LLM mode, sends all flags to the LLM with a structured prompt requesting a professional audit narrative.

**Boundary:** The Synthesizer receives flags as a flat list and knows nothing about the original CSV data or the Collector's internals. This separation exists because the Synthesizer was added after the Collector and Detector were already stable.

#### `aria/_fix_langchain.py` -- Compatibility shim

Monkey-patches `langchain_core.globals.get_debug` to read from `LANGCHAIN_DEBUG` environment variable instead of accessing `langchain.debug` (which was removed in LangChain 1.2.10). Pre-registers a synthetic `langchain` module in `sys.modules` with `debug = False` if the real module is not yet imported.

**Invariant:** Must be imported before `langgraph` or `langchain`. This is enforced by `main.py` importing it as the very first statement.

### `pipeline.py` -- LangGraph graph construction

Creates a `StateGraph(ARIAState)`, adds three nodes, connects them with conditional edges via `_halt_on_error`. The topology is: START -> collector -> detector -> synthesizer -> END, with error escapes at every node.

Key types: `aria_pipeline` (compiled graph singleton)

### `main.py` -- Entry point

Imports `_fix_langchain` first (non-negotiable). Parses CLI args. Builds initial `ARIAState` with file paths and empty containers. Calls `aria_pipeline.invoke(initial_state)`. Saves `flags.json` (machine-readable) and `report.txt` (human-readable) to the output directory.

### `infrastructure/` -- Supporting services

#### `infrastructure/firman_port.py`

FastAPI server that exposes an OpenAI-compatible `/v1/chat/completions` endpoint. This was the intended local LLM gateway during development. The endpoint was added manually after the original server only had `/health` and `/collect` routes.

**Invariant:** The pipeline never depends on this server being available. If it is down, the LLM client falls through to Gemini 2.5 Flash, then to mock mode.

### `data/` -- Synthetic datasets

#### `data/synthetic/grades.csv` -- 8 records

Course section averages with historical means and standard deviations. Three flagged sections (z > 1.5): CS101_001 (z=2.31), CS102_001 (z=1.73), MATH201_001 (z=1.52).

#### `data/synthetic/students.csv` -- 22 records

Student exam scores, CO scores, and attainment rates across 5 courses. CS201 has 11 students with 100% attainment (triggers CO Completion Rate). 10 students across CS101, CS102, and CS201 have CLO-exam gaps exceeding 20 points.

#### `data/synthetic/submissions.csv` -- 8 records

Assignment submission timestamps and similarity scores. Three pairs within 120 seconds with similarity > 0.75: ASSIGN001 (two pairs, 45s and 90s), ASSIGN002 (one pair, 90s). ASSIGN003 pair at 300s is not flagged.

### `test_*.py` -- Test scripts (6 files)

Standalone scripts with independent LangChain workarounds and API key configurations. No shared fixtures or test runner. Each covers one aspect: pipeline smoke test, synthesizer isolated test, full pipeline with report output, Gemini API connectivity, Gemma API responses, LLM client unit test.

**Invariant:** No test file is importable as a module. Each is designed to be run directly with `python test_*.py`. There is no `tests/__init__.py`.

## Cross-Cutting Concerns

### Error Handling

Every node function is wrapped in a try/except that returns `{"error": str(e)}` on failure. The conditional edge `_halt_on_error` checks this field and routes to END. The LLM client never raises exceptions to its caller -- it returns `None` for JSON parse failures, empty strings for network failures, and relies on the caller's `if result is None: continue` pattern.

### LLM Reliability

The LLM client implements three tiers of failover (local gateway -> Gemini 2.5 Flash -> mock). When the mock is active, the entire pipeline runs without any network access or API keys. The max_tokens parameter was increased from 600 to 2000 after a truncation bug caused silent flag drops. The temperature is 0.1 across all calls to minimize creative variation.

### Fraud Type Name Discipline

The four fraud type strings ("Grade Inflation", "CLO Inconsistency", "Submission Clustering", "CO Completion Rate") must be identical across three locations: the prompt JSON templates in `prompts.py`, the mock flag construction in `detector.py`, and the grouping logic in `synthesizer.py`. A previous mismatch between "CLO Attainment Inconsistency" (prompts) and "CLO Inconsistency" (detector/synthesizer) caused silent flag drops for an entire fraud type.

### Mock Mode as Specification

The mock rules (`z > 1.5`, `gap > 20`, `time <= 120s and avg_sim > 0.75`, `cohort >= 8 and 100% attainment`) define what constitutes fraud. If the LLM disagrees with a mock rule, the prompt is wrong, not the rule. This enables CI/CD without API keys and provides deterministic ground truth for testing.

### Testing Strategy

Tests are ad-hoc standalone scripts, not a structured suite. There is no test runner, no fixtures, no assertion framework beyond print statements. The mock LLM mode is the primary testing tool -- it produces deterministic output that can be verified by inspection. Integration tests require a real Gemini API key or the mock flag.

### Dataset Size Gap

The proposal specified 200/500/80 records. The current dataset is 22/8/8. The small dataset enables sub-second iteration during development but does not support statistically meaningful precision/recall evaluation. Scaling the dataset is mechanical: generate more records with the same anomaly injection patterns. The detection logic does not change.
