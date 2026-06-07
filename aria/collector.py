import pandas as pd
from .state import ARIAState

GRADES_COLS = [
    "course_id", "section_id", "instructor_id", "semester",
    "avg_grade", "historical_mean", "historical_std"
]
STUDENTS_COLS = [
    "student_id", "course_id", "semester",
    "exam_score", "co_score", "co_attainment_rate"
]
SUBMISSIONS_COLS = [
    "submission_id", "student_id", "assignment_id",
    "timestamp", "similarity_score"
]


def _validate(df: pd.DataFrame, required: list, name: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"{name} missing columns: {missing}")


def collector_node(state: ARIAState) -> dict:
    try:
        grades = pd.read_csv(state["grades_path"])
        students = pd.read_csv(state["students_path"])
        submissions = pd.read_csv(state["submissions_path"])

        _validate(grades, GRADES_COLS, "grades.csv")
        _validate(students, STUDENTS_COLS, "students.csv")
        _validate(submissions, SUBMISSIONS_COLS, "submissions.csv")

        grades["z_score"] = (
            (grades["avg_grade"] - grades["historical_mean"])
            / grades["historical_std"].replace(0, 1)
        ).round(3)

        students["co_exam_gap"] = (
            students["co_score"] - students["exam_score"]
        ).round(2)

        submissions["timestamp"] = pd.to_datetime(
            submissions["timestamp"], utc=True, errors="coerce"
        )
        submissions = submissions.sort_values(
            ["assignment_id", "timestamp"]
        ).reset_index(drop=True)

        normalized = {
            "grades": grades.to_dict(orient="records"),
            "students": students.to_dict(orient="records"),
            "submissions": submissions.astype(str).to_dict(orient="records")
        }
        return {"normalized_data": normalized, "error": None}

    except Exception as e:
        return {"normalized_data": {}, "error": str(e)}
