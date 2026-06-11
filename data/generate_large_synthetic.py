import csv
import random
import os
import argparse
from datetime import datetime, timedelta, timezone

random.seed(42)

ALL_COURSES = [
    "CS101",
    "CS102",
    "CS201",
    "MATH201",
    "MATH301",
    "ENG101",
    "ENG201",
    "EEE101",
    "MEC101",
    "PHY101",
    "CHM101",
    "BUS101",
]
ALL_INSTRUCTORS = [f"INST{i:03d}" for i in range(1, 51)]
ALL_SEMESTERS = ["Fall2023", "Spring2024", "Fall2024", "Spring2025"]

ANOMALY_RATE = 0.06


def gen_grade_rows(courses, sections, semesters):
    rows = []
    for cid in courses:
        for sec in sections:
            for sem in semesters:
                hm = round(random.uniform(62, 80), 1)
                hs = round(random.uniform(3.5, 7.5), 1)
                ag = round(random.uniform(hm - 3, hm + 5), 1)
                rows.append(
                    {
                        "course_id": cid,
                        "section_id": sec,
                        "instructor_id": random.choice(ALL_INSTRUCTORS),
                        "semester": sem,
                        "avg_grade": ag,
                        "historical_mean": hm,
                        "historical_std": hs,
                    }
                )
    flagged = random.sample(rows, max(1, int(len(rows) * ANOMALY_RATE * 0.6)))
    for r in flagged:
        r["avg_grade"] = round(
            r["historical_mean"] + random.uniform(1.6, 3.5) * r["historical_std"], 1
        )
    return rows


def gen_student_rows(student_count, courses, semesters):
    sids = [f"STU{i:03d}" for i in range(1, student_count + 1)]
    rows = []

    for sid in sids:
        exam = round(random.uniform(30, 95), 1)
        co = round(random.uniform(max(30, exam - 15), min(100, exam + 15)), 1)
        rows.append(
            {
                "student_id": sid,
                "course_id": random.choice(courses),
                "semester": random.choice(semesters),
                "exam_score": exam,
                "co_score": co,
                "co_attainment_rate": round(random.uniform(0.4, 0.95), 2),
            }
        )

    flagged_clo = random.sample(rows, int(len(rows) * ANOMALY_RATE * 0.35))
    for r in flagged_clo:
        gap = random.uniform(22, 40)
        r["co_score"] = round(min(100, r["exam_score"] + gap), 1)

    used_ids = {r["student_id"] for r in flagged_clo}
    cohort_course = random.choice(courses)
    cohort_sem = random.choice(semesters)
    co_count = 0
    for r in rows:
        if r["course_id"] == cohort_course and r["semester"] == cohort_sem:
            r["co_attainment_rate"] = 1.0
            co_count += 1

    if co_count < 8:
        need = 12 - co_count
        for _ in range(need):
            sid = f"STU{random.randint(1, student_count):03d}"
            if sid not in used_ids:
                used_ids.add(sid)
                rows.append(
                    {
                        "student_id": sid,
                        "course_id": cohort_course,
                        "semester": cohort_sem,
                        "exam_score": round(random.uniform(30, 70), 1),
                        "co_score": round(random.uniform(65, 95), 1),
                        "co_attainment_rate": 1.0,
                    }
                )

    return rows


def gen_submission_rows(student_count, assignments):
    rows = []
    base_date = datetime(2023, 10, 15, 8, 0, 0, tzinfo=timezone.utc)

    pool = [f"STU{i:03d}" for i in range(1, student_count + 1)]
    for i, assn in enumerate(assignments):
        max_n = min(30, student_count)
        n = random.randint(min(8, max_n), max_n)
        students = random.sample(pool, n)
        base = base_date + timedelta(days=i * 7 + random.randint(0, 5))
        for j, sid in enumerate(students):
            ts = base + timedelta(minutes=j * random.randint(5, 25))
            sim = round(random.uniform(0.2, 0.6), 2)
            rows.append(
                {
                    "submission_id": f"SUB{i * 50 + j + 1:04d}",
                    "student_id": sid,
                    "assignment_id": assn,
                    "timestamp": ts.isoformat(),
                    "similarity_score": sim,
                }
            )

    cluster_size = max(1, int(len(assignments) * 0.3))
    cluster_assignments = random.sample(assignments, cluster_size)
    for assn in cluster_assignments:
        batch = [r for r in rows if r["assignment_id"] == assn]
        if len(batch) < 3:
            continue
        n_colluders = random.randint(2, min(4, len(batch)))
        colluders = random.sample(batch, n_colluders)
        base_ts = datetime.fromisoformat(colluders[0]["timestamp"])
        for k, c in enumerate(colluders):
            c["timestamp"] = (
                base_ts + timedelta(seconds=k * random.randint(10, 40))
            ).isoformat()
            c["similarity_score"] = round(random.uniform(0.76, 0.95), 2)

    return rows


GRADE_FIELDS = [
    "course_id",
    "section_id",
    "instructor_id",
    "semester",
    "avg_grade",
    "historical_mean",
    "historical_std",
]
STUDENT_FIELDS = [
    "student_id",
    "course_id",
    "semester",
    "exam_score",
    "co_score",
    "co_attainment_rate",
]
SUBMISSION_FIELDS = [
    "submission_id",
    "student_id",
    "assignment_id",
    "timestamp",
    "similarity_score",
]


def write_csv(path, fields, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(data)


def _scale_lists(student_count):
    if student_count >= 300:
        return (ALL_COURSES, ["001", "002", "003"], ALL_SEMESTERS, 50)
    if student_count >= 100:
        return (ALL_COURSES[:6], ["001", "002"], ALL_SEMESTERS[:2], 15)
    return (ALL_COURSES[:4], ["001"], ALL_SEMESTERS[:2], 8)


def generate(student_count: int, output_dir: str):
    courses, sections, semesters, num_assignments = _scale_lists(student_count)
    assignments = [f"ASSIGN{i:03d}" for i in range(1, num_assignments + 1)]

    grades = gen_grade_rows(courses, sections, semesters)
    students = gen_student_rows(student_count, courses, semesters)
    submissions = gen_submission_rows(student_count, assignments)

    write_csv(os.path.join(output_dir, "grades.csv"), GRADE_FIELDS, grades)
    write_csv(os.path.join(output_dir, "students.csv"), STUDENT_FIELDS, students)
    write_csv(
        os.path.join(output_dir, "submissions.csv"), SUBMISSION_FIELDS, submissions
    )

    print(f"{output_dir}/grades.csv: {len(grades)} records")
    print(f"{output_dir}/students.csv: {len(students)} records")
    print(f"{output_dir}/submissions.csv: {len(submissions)} records")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic ARIA datasets")
    parser.add_argument("--students", type=int, default=600, help="Number of students")
    parser.add_argument(
        "--output-dir", default="data/synthetic", help="Output directory"
    )
    args = parser.parse_args()
    generate(args.students, args.output_dir)


if __name__ == "__main__":
    main()
