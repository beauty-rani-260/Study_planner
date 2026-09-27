import json
import os
from datetime import datetime, date

PLAN_FILE = "study_plan.json"


def calculate_priority(subjects):
    """
    Tool 1: Calculates a priority score for each subject.
    Priority is higher when:
    - the exam is sooner
    - the subject is marked as difficult/weak
    - less progress has been made

    'subjects' is a list of dicts, e.g.:
    [{"name": "Physics", "exam_date": "2026-10-01", "difficulty": "high", "progress": 20}]
    """
    today = date.today()
    results = []

    for subj in subjects:
        exam_date = datetime.strptime(subj["exam_date"], "%Y-%m-%d").date()
        days_left = max((exam_date - today).days, 0)

        # Fewer days left = higher urgency score
        urgency_score = 100 / (days_left + 1)

        # Difficulty adds weight
        difficulty_weight = {"low": 1, "medium": 1.5, "high": 2}.get(
            subj.get("difficulty", "medium"), 1.5
        )

        # Less progress = more priority needed
        progress = subj.get("progress", 0)
        progress_factor = (100 - progress) / 100

        priority_score = urgency_score * difficulty_weight * progress_factor

        results.append({
            "name": subj["name"],
            "exam_date": subj["exam_date"],
            "days_left": days_left,
            "difficulty": subj.get("difficulty", "medium"),
            "progress": progress,
            "topics": subj.get("topics", "General revision"),
            "priority_score": round(priority_score, 2)
        })

    # Sort by priority score, highest first
    results.sort(key=lambda x: x["priority_score"], reverse=True)
    return results


def generate_schedule(prioritized_subjects, available_hours):
    """
    Tool 2: Distributes available_hours across subjects based on priority score.
    Higher priority subjects get more time.
    """
    total_score = sum(s["priority_score"] for s in prioritized_subjects) or 1

    schedule = []
    for subj in prioritized_subjects:
        share = subj["priority_score"] / total_score
        hours = round(share * available_hours, 2)
        schedule.append({
            "subject": subj["name"],
            "hours_allocated": hours,
            "topics": subj.get("topics", "General revision"),
            "reason": f"Exam in {subj['days_left']} day(s), difficulty: {subj['difficulty']}, progress: {subj['progress']}%"
        })

    return schedule


def save_plan(schedule, subjects_data):
    """
    Tool 3: Saves the current study plan to a local JSON file.
    """
    plan = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "subjects": subjects_data,
        "schedule": schedule
    }
    with open(PLAN_FILE, "w") as f:
        json.dump(plan, f, indent=2)
    return "Plan saved successfully."


def load_plan():
    """
    Helper: Loads the saved plan if it exists.
    """
    if os.path.exists(PLAN_FILE):
        with open(PLAN_FILE, "r") as f:
            return json.load(f)
    return None


def update_plan(actual_hours_studied, planned_hours):
    """
    Tool 4: Reorganizes the plan when the student's situation changes
    (e.g., they studied less/more than planned).
    Redistributes the REMAINING hours across subjects using the same
    priority logic, so higher-priority subjects still get more time.
    """
    plan = load_plan()
    if not plan:
        return "No existing plan found. Please create a plan first."

    subjects_data = plan["subjects"]
    prioritized = calculate_priority(subjects_data)

    # Remaining hours = whatever wasn't studied yet (simple beginner-friendly logic)
    remaining_hours = max(planned_hours - actual_hours_studied, 0)

    if remaining_hours == 0:
        return "No remaining hours to reorganize — you completed your planned study time!"

    new_schedule = generate_schedule(prioritized, remaining_hours)
    save_plan(new_schedule, subjects_data)

    return new_schedule