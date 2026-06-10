from typing import TypedDict, Optional, List, Dict, Any


class ARIAState(TypedDict):
    grades_path: str
    students_path: str
    submissions_path: str
    normalized_data: Dict[str, Any]
    flags: List[Dict[str, Any]]
    report: str
    error: Optional[str]
