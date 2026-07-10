import json
import os
from typing import List, Dict, Set
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


def _extract_course(ftype: str, rid: str) -> str | None:
    """Extract course code from record_id based on fraud type."""
    parts = rid.split("_")
    if ftype == "Grade Inflation" and len(parts) >= 1:
        return parts[0]
    if ftype == "CLO Inconsistency" and len(parts) >= 2:
        return parts[1]
    if ftype == "CO Completion Rate" and len(parts) >= 1:
        return parts[0]
    return None


def _find_correlations(flags: list) -> List[str]:
    correlations: List[str] = []

    # 1. STUDENT CROSS-TYPE — same student ID across different fraud types
    student_map: Dict[str, Set[str]] = {}
    for f in flags:
        ftype = f.get("fraud_type", "")
        rid = f.get("record_id", "")
        for part in rid.split("_"):
            if part.startswith("STU"):
                student_map.setdefault(part, set()).add(ftype)
    for sid in sorted(student_map):
        ftypes = student_map[sid]
        if len(ftypes) > 1:
            correlations.append(
                f"Cross-type student: {sid} flagged in {len(ftypes)} fraud types"
                f" ({', '.join(sorted(ftypes))})"
            )

    # 2. COURSE CROSS-TYPE — same course flagged across different fraud types
    course_map: Dict[str, Set[str]] = {}
    for f in flags:
        ftype = f.get("fraud_type", "")
        rid = f.get("record_id", "")
        course = _extract_course(ftype, rid)
        if course:
            course_map.setdefault(course, set()).add(ftype)
    for cid in sorted(course_map):
        ftypes = course_map[cid]
        if len(ftypes) > 1:
            correlations.append(
                f"Multi-flagged course: {cid} flagged in {len(ftypes)} fraud types"
                f" ({', '.join(sorted(ftypes))})"
            )

    # 3. DENSE ASSIGNMENT CLUSTERS — assignments with many clustered pairs
    assign_map: Dict[str, int] = {}
    for f in flags:
        if f.get("fraud_type") == "Submission Clustering":
            rid = f.get("record_id", "")
            assign_id = rid.split("_")[0]
            assign_map[assign_id] = assign_map.get(assign_id, 0) + 1
    for aid in sorted(assign_map, key=lambda x: -assign_map[x]):
        count = assign_map[aid]
        if count >= 3:
            correlations.append(
                f"Dense cluster assignment: {aid} has {count} flagged submission pairs"
            )

    # 4. STUDENTS IN MULTIPLE CLUSTERS — appearing across different assignments
    student_cluster_map: Dict[str, Set[str]] = {}
    for f in flags:
        if f.get("fraud_type") == "Submission Clustering":
            rid = f.get("record_id", "")
            parts = rid.split("_")
            assign_id = parts[0]
            for p in parts:
                if p.startswith("STU"):
                    student_cluster_map.setdefault(p, set()).add(assign_id)
    for sid in sorted(student_cluster_map):
        assignments = student_cluster_map[sid]
        if len(assignments) >= 2:
            correlations.append(
                f"Cross-assignment student: {sid} appears in clusters across"
                f" {len(assignments)} different assignments"
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


def _mock_report_md(flags: list) -> str:
    """Build a structured markdown-format report in mock mode."""
    lines = [
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
        lines.append(f"{ftype} ({len(f_list)}):")
        for i, f in enumerate(f_list, 1):
            lines.append(f"  {i}. Record: {f.get('record_id', 'N/A')}")
        lines.append("")

    correlations = _find_correlations(flags)
    if correlations:
        lines.append("Correlations Identified:")
        for c in correlations:
            lines.append(f"  - {c}")
        lines.append("")
    else:
        lines.append("Correlations Identified: None")
        lines.append("")

    clo_impact = _estimate_clo_impact(flags)
    lines.append(f"Estimated Impact on CLO Attainment: {clo_impact}")
    lines.append("")
    severity = _compute_severity(flags)
    lines.append(f"Overall Severity: {severity}")
    lines.append("")

    lines.append("Recommended Actions:")
    if len(flags) == 0:
        lines.append("  1. No action required.")
    else:
        lines.append("  1. Review flagged records for potential academic misconduct.")
        flag_types = {f.get("fraud_type") for f in flags}
        if "Grade Inflation" in flag_types:
            lines.append("  2. Investigate grade anomalies in identified courses.")
        if "Submission Clustering" in flag_types:
            lines.append("  3. Examine submission timelines for potential collusion.")
        if "CLO Inconsistency" in flag_types:
            lines.append("  4. Verify CLO assessments and exam scores for discrepancies.")
        if "CO Completion Rate" in flag_types:
            lines.append("  5. Audit cohort attainment rates for possible data errors.")
    return "\n".join(lines)


def synthesizer_node(state: ARIAState) -> ARIAState:
    flags = state.get("flags", [])
    if not flags:
        state["report"] = "No flags detected. No report generated."
        return state

    if os.getenv("ARIA_USE_MOCK_LLM") == "1":
        state["report"] = _mock_report_md(flags)
    else:
        state["report"] = call_llm(_build_prompt(flags))
    return state