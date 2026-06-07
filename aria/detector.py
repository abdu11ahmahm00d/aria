import os
from typing import List, Dict, Any
import pandas as pd
from .state import ARIAState
from .llm_client import call_llm_json
from .prompts import (
    GRADE_INFLATION_PROMPT,
    CLO_INCONSISTENCY_PROMPT,
    SUBMISSION_CLUSTERING_PROMPT,
    CO_COMPLETION_PROMPT,
)


def _is_mock() -> bool:
    return os.getenv("ARIA_USE_MOCK_LLM") == "1"


def _mock_flag(fraud_type: str, record_id: str, reason: str, evidence: dict) -> dict:
    return {
        "flagged": True,
        "fraud_type": fraud_type,
        "record_id": record_id,
        "confidence": 0.95,
        "reason": reason,
        "evidence": evidence,
    }


def check_grade_inflation(grades: List[Dict]) -> List[Dict]:
    flags = []
    for record in grades:
        z = record.get("z_score", 0)
        if _is_mock():
            if z > 1.5:
                flags.append(
                    _mock_flag(
                        "Grade Inflation",
                        f"{record['course_id']}_{record['section_id']}",
                        f"z-score {z:.2f} exceeds threshold of 1.5",
                        {
                            "z_score": z,
                            "avg_grade": record.get("avg_grade"),
                            "historical_mean": record.get("historical_mean"),
                        },
                    )
                )
            continue

        prompt = GRADE_INFLATION_PROMPT.format(
            course_id=record["course_id"],
            section_id=record["section_id"],
            instructor_id=record["instructor_id"],
            semester=record["semester"],
            avg_grade=record["avg_grade"],
            historical_mean=record["historical_mean"],
            historical_std=record["historical_std"],
            z_score=z,
        )
        result = call_llm_json(prompt)
        if result is None:
            print(
                f"[WARN] JSON parse failed for {record['course_id']}_{record['section_id']}"
            )
            continue
        if result.get("flagged"):
            flags.append(result)
    return flags


def check_clo_inconsistency(students: List[Dict]) -> List[Dict]:
    flags = []
    for record in students:
        gap = record.get("co_exam_gap", 0)
        if _is_mock():
            if gap > 20:
                flags.append(
                    _mock_flag(
                        "CLO Inconsistency",
                        f"{record['student_id']}_{record['course_id']}",
                        f"CLO score {gap}pts above exam exceeds 20pt threshold",
                        {
                            "exam_score": record.get("exam_score"),
                            "co_score": record.get("co_score"),
                            "co_exam_gap": gap,
                        },
                    )
                )
            continue

        prompt = CLO_INCONSISTENCY_PROMPT.format(
            student_id=record["student_id"],
            course_id=record["course_id"],
            semester=record["semester"],
            exam_score=record["exam_score"],
            co_score=record["co_score"],
            co_exam_gap=gap,
        )
        result = call_llm_json(prompt)
        if result is None:
            print(
                f"[WARN] JSON parse failed for {record['student_id']}_{record['course_id']}"
            )
            continue
        if result.get("flagged"):
            flags.append(result)
    return flags


def check_submission_clustering(submissions: List[Dict]) -> List[Dict]:
    flags = []
    submissions_by_assignment = {}
    for sub in submissions:
        assignment_id = sub["assignment_id"]
        if assignment_id not in submissions_by_assignment:
            submissions_by_assignment[assignment_id] = []
        submissions_by_assignment[assignment_id].append(sub)

    for assignment_id, assignment_subs in submissions_by_assignment.items():
        sorted_subs = sorted(assignment_subs, key=lambda x: x["timestamp"])

        for i in range(len(sorted_subs)):
            for j in range(i + 1, len(sorted_subs)):
                sub1 = sorted_subs[i]
                sub2 = sorted_subs[j]

                try:
                    time1 = pd.to_datetime(sub1["timestamp"])
                    time2 = pd.to_datetime(sub2["timestamp"])
                    time_diff_seconds = abs((time2 - time1).total_seconds())
                except:
                    continue

                if time_diff_seconds <= 120:
                    sim1 = float(sub1.get("similarity_score", 0))
                    sim2 = float(sub2.get("similarity_score", 0))
                    avg_similarity = (sim1 + sim2) / 2.0

                    if _is_mock():
                        if avg_similarity > 0.75:
                            flags.append(
                                _mock_flag(
                                    "Submission Clustering",
                                    f"{assignment_id}_{sub1['student_id']}_{sub2['student_id']}",
                                    f"Submissions {int(time_diff_seconds)}s apart with {avg_similarity:.2f} avg similarity",
                                    {
                                        "time_diff_seconds": int(time_diff_seconds),
                                        "similarity_score": avg_similarity,
                                    },
                                )
                            )
                        continue

                    prompt = SUBMISSION_CLUSTERING_PROMPT.format(
                        assignment_id=assignment_id,
                        student_id_1=sub1["student_id"],
                        student_id_2=sub2["student_id"],
                        timestamp_1=sub1["timestamp"],
                        timestamp_2=sub2["timestamp"],
                        time_diff_seconds=int(time_diff_seconds),
                        similarity_score=avg_similarity,
                    )
                    result = call_llm_json(prompt)
                    if result is None:
                        print(
                            f"[WARN] JSON parse failed for submission pair {sub1['student_id']}-{sub2['student_id']}"
                        )
                        continue
                    if result.get("flagged"):
                        flags.append(result)

    return flags


def check_co_completion_rate(students: List[Dict]) -> List[Dict]:
    flags = []
    course_semester_groups = {}
    for student in students:
        key = (student["course_id"], student["semester"])
        if key not in course_semester_groups:
            course_semester_groups[key] = []
        course_semester_groups[key].append(student)

    for (course_id, semester), group_students in course_semester_groups.items():
        student_count = len(group_students)

        if student_count < 8:
            continue

        all_perfect = all(
            student.get("co_attainment_rate", 0) == 1.0 for student in group_students
        )

        if all_perfect:
            if _is_mock():
                flags.append(
                    _mock_flag(
                        "CO Completion Rate",
                        f"{course_id}_{semester}",
                        f"100% attainment in cohort of {student_count} students is implausible",
                        {
                            "student_count": student_count,
                            "co_attainment_rate": 1.0,
                        },
                    )
                )
                continue

            rep_student = group_students[0]
            prompt = CO_COMPLETION_PROMPT.format(
                course_id=course_id,
                semester=semester,
                student_count=student_count,
                co_attainment_rate=1.0,
            )
            result = call_llm_json(prompt)
            if result is None:
                print(
                    f"[WARN] JSON parse failed for course {course_id} semester {semester}"
                )
                continue
            if result.get("flagged"):
                flags.append(result)

    return flags


def detector_node(state: ARIAState) -> dict:
    if state.get("error"):
        return {}

    data = state["normalized_data"]
    flags = []
    flags += check_grade_inflation(data.get("grades", []))
    flags += check_clo_inconsistency(data.get("students", []))
    flags += check_submission_clustering(data.get("submissions", []))
    flags += check_co_completion_rate(data.get("students", []))
    return {"flags": flags}
