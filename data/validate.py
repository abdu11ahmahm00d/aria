import pandas as pd
import sys

dir = sys.argv[1] if len(sys.argv) > 1 else "data/synthetic/large"

grades = pd.read_csv(f"{dir}/grades.csv")
students = pd.read_csv(f"{dir}/students.csv")
subs = pd.read_csv(f"{dir}/submissions.csv")

print(f"=== {dir} ===")
print(f"Grades: {len(grades)} rows, {grades['course_id'].nunique()} courses")
print(
    f"Students: {len(students)} rows, {students['student_id'].nunique()} unique students"
)
print(f"  Avg courses per student: {students.groupby('student_id').size().mean():.1f}")
print(
    f"Submissions: {len(subs)} rows, {subs['student_id'].nunique()} unique students, {subs['assignment_id'].nunique()} assignments"
)

sub_students = set(subs["student_id"])
stu_students = set(students["student_id"])
print(f"Students with 0 submissions: {len(stu_students - sub_students)}")
print(f"Submitters not in students: {len(sub_students - stu_students)}")
