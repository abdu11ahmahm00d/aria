import json
import os
from .state import ARIAState
from .llm_client import call_llm


def _compute_severity(flags: list) -> str:
    total = len(flags)
    types = {f.get("fraud_type") for f in flags}
    if total == 0:
        return "NONE"
    if total >= 3 or ("Grade Inflation" in types and "Submission Clustering" in types):
        return "HIGH"
    if total >= 2:
        return "MEDIUM"
    return "LOW"


def _find_correlations(flags: list) -> list[str]:
    correlations = []
    student_map: dict[str, list[str]] = {}
    for f in flags:
        ev = f.get("evidence", {})
        sids = ev.get("student_ids", [])
        rid = f.get("record_id", "")
        for part in rid.split("_"):
            if part.startswith("S-") or part.startswith("S"):
                if part not in student_map:
                    student_map[part] = []
                student_map[part].append(f.get("fraud_type", ""))
        for sid in sids:
            if sid not in student_map:
                student_map[sid] = []
            student_map[sid].append(f.get("fraud_type", ""))

    for sid, ftypes in student_map.items():
        if len(set(ftypes)) > 1:
            correlations.append(
                f"Student {sid} appears in multiple fraud types: {', '.join(set(ftypes))}"
            )
    return correlations


def _estimate_clo_impact(flags: list) -> str:
    co_flags = [f for f in flags if f.get("fraud_type") == "CO Completion Rate"]
    if not co_flags:
        return "No CO Completion Rate flags; impact on CLO attainment cannot be estimated from current flags."
    return (
        f"{len(co_flags)} CO Completion Rate flag(s) detected. "
        "Exclusion of these records may reduce cohort attainment rates; "
        "requires recomputation of CO attainment without flagged records."
    )


def _build_prompt(flags: list) -> str:
    flags_by_type: dict[str, list[dict]] = {}
    for f in flags:
        ftype = f.get("fraud_type", "Unknown")
        flags_by_type.setdefault(ftype, []).append(f)

    flags_text = ""
    for ftype, f_list in flags_by_type.items():
        flags_text += f"\n{ftype} ({len(f_list)}):\n"
        for i, f in enumerate(f_list, 1):
            flags_text += f"  {i}. Record: {f.get('record_id', 'N/A')}, Evidence: {json.dumps(f.get('evidence', {}))}\n"

    severity = _compute_severity(flags)
    correlations = _find_correlations(flags)
    clo_impact = _estimate_clo_impact(flags)

    prompt = f"""You are an expert academic integrity auditor. Analyze the following fraud detection flags from the ARIA system and produce a comprehensive audit report.

FLAGS DETECTED:
{flags_text}

ANALYSIS:
- Severity: {severity}
- Correlations identified: {chr(10).join(correlations) if correlations else "None"}
- Estimated impact on CLO attainment: {clo_impact}

TASK:
Write a clear, structured audit report that includes:
1. Acknowledge all flags and group them by fraud type.
2. Identify correlations — flags that point to the same student, course, or instructor.
3. Estimate the impact on CLO attainment if flagged records were excluded.
4. Assign an overall severity (HIGH / MEDIUM / LOW) with justification.
5. List recommended actions, numbered, specific, actionable.

Write in a professional tone suitable for university administrators. Be concise but thorough.
"""
    return prompt


def synthesizer_node(state: ARIAState) -> ARIAState:
    flags = state.get("flags", [])
    if not flags:
        state["report"] = "No flags detected. No report generated."
        return state

    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        report_lines = [
            "ACADEMIC INTEGRITY AND OBE ANALYTICS REPORT",
            "=============================================",
            "",
            f"Total Flags Detected: {len(flags)}",
            "",
        ]
        flags_by_type: dict[str, list[dict]] = {}
        for f in flags:
            ftype = f.get("fraud_type", "Unknown")
            flags_by_type.setdefault(ftype, []).append(f)
        for ftype, f_list in flags_by_type.items():
            report_lines.append(f"{ftype} ({len(f_list)}):")
            for i, f in enumerate(f_list, 1):
                report_lines.append(f"  {i}. Record: {f.get('record_id', 'N/A')}")
            report_lines.append("")
        correlations = _find_correlations(flags)
        if correlations:
            report_lines.append("Correlations Identified:")
            for c in correlations:
                report_lines.append(f"  - {c}")
            report_lines.append("")
        else:
            report_lines.append("Correlations Identified: None")
            report_lines.append("")
        clo_impact = _estimate_clo_impact(flags)
        report_lines.append(f"Estimated Impact on CLO Attainment: {clo_impact}")
        report_lines.append("")
        severity = _compute_severity(flags)
        report_lines.append(f"Overall Severity: {severity}")
        report_lines.append("")
        report_lines.append("Recommended Actions:")
        if len(flags) == 0:
            report_lines.append("  1. No action required.")
        else:
            report_lines.append(
                "  1. Review flagged records for potential academic misconduct."
            )
            if "Grade Inflation" in [f.get("fraud_type") for f in flags]:
                report_lines.append(
                    "  2. Investigate grade anomalies in identified courses."
                )
            if "Submission Clustering" in [f.get("fraud_type") for f in flags]:
                report_lines.append(
                    "  3. Examine submission timelines for potential collusion."
                )
            if "CLO Inconsistency" in [f.get("fraud_type") for f in flags]:
                report_lines.append(
                    "  4. Verify CLO assessments and exam scores for discrepancies."
                )
            if "CO Completion Rate" in [f.get("fraud_type") for f in flags]:
                report_lines.append(
                    "  5. Audit cohort attainment rates for possible data errors."
                )
        report = "\n".join(report_lines)
    else:
        report = call_llm(_build_prompt(flags))
    state["report"] = report
    return state
