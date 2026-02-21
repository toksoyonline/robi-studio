from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import (
    EnrollmentUpdateRequest,
    LessonCreateRequest,
    PremiumUpdateRequest,
    SimulationRequest,
)
from app.services.simulation import run_performance_simulation

router = APIRouter(prefix="/api")


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/students/{student_id}/dashboard")
def student_dashboard(student_id: int) -> dict:
    with get_connection() as conn:
        student = conn.execute(
            "SELECT id, name, email FROM users WHERE id = ? AND role = 'student'",
            (student_id,),
        ).fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")

        lessons = conn.execute(
            """
            SELECT l.id, l.title, l.is_premium, l.difficulty,
                   COALESCE(e.progress, 0) as progress,
                   COALESCE(e.score, 0) as score
            FROM lessons l
            LEFT JOIN enrollments e ON e.lesson_id = l.id AND e.student_id = ?
            ORDER BY l.id ASC
            """,
            (student_id,),
        ).fetchall()

        premium = conn.execute(
            "SELECT active, plan_name, renewed_at FROM premium_subscriptions WHERE student_id = ?",
            (student_id,),
        ).fetchone()

    return {
        "student": dict(student),
        "premium": dict(premium) if premium else {"active": 0, "plan_name": None, "renewed_at": None},
        "lessons": [dict(row) for row in lessons],
    }


@router.get("/parents/{parent_id}/overview")
def parent_overview(parent_id: int) -> dict:
    with get_connection() as conn:
        parent = conn.execute(
            "SELECT id, name FROM users WHERE id = ? AND role = 'parent'", (parent_id,)
        ).fetchone()
        if not parent:
            raise HTTPException(status_code=404, detail="Parent not found")

        student_progress = conn.execute(
            """
            SELECT u.name as student_name,
                   AVG(e.progress) as avg_progress,
                   AVG(e.score) as avg_score
            FROM users u
            LEFT JOIN enrollments e ON e.student_id = u.id
            WHERE u.role = 'student'
            GROUP BY u.id
            """
        ).fetchall()

    return {
        "parent": dict(parent),
        "students": [
            {
                **dict(row),
                "avg_progress": round(row["avg_progress"] or 0, 1),
                "avg_score": round(row["avg_score"] or 0, 1),
            }
            for row in student_progress
        ],
    }


@router.get("/admin/overview")
def admin_overview() -> dict:
    with get_connection() as conn:
        user_counts = conn.execute(
            "SELECT role, COUNT(*) as total FROM users GROUP BY role"
        ).fetchall()
        lesson_stats = conn.execute(
            "SELECT COUNT(*) as total_lessons, SUM(is_premium) as premium_lessons FROM lessons"
        ).fetchone()
        simulation_count = conn.execute(
            "SELECT COUNT(*) as runs FROM simulation_runs"
        ).fetchone()["runs"]

    return {
        "users": [dict(row) for row in user_counts],
        "lessons": dict(lesson_stats),
        "simulation_runs": simulation_count,
    }


@router.post("/simulation/run")
def run_simulation(payload: SimulationRequest) -> dict:
    result = run_performance_simulation(payload.input_score, payload.scenario)
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO simulation_runs (student_id, scenario, input_score, simulated_score, feedback, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload.student_id,
                payload.scenario,
                payload.input_score,
                result["simulated_score"],
                result["feedback"],
                result["created_at"],
            ),
        )
        conn.commit()

    return result


@router.post("/premium/update")
def update_premium(payload: PremiumUpdateRequest) -> dict:
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT student_id FROM premium_subscriptions WHERE student_id = ?", (payload.student_id,)
        ).fetchone()

        if existing:
            conn.execute(
                """
                UPDATE premium_subscriptions
                SET active = ?, plan_name = ?, renewed_at = datetime('now')
                WHERE student_id = ?
                """,
                (int(payload.active), payload.plan_name, payload.student_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO premium_subscriptions (student_id, active, plan_name, renewed_at)
                VALUES (?, ?, ?, datetime('now'))
                """,
                (payload.student_id, int(payload.active), payload.plan_name),
            )
        conn.commit()

    return {"message": "Premium status updated"}


@router.post("/enrollments/update")
def update_enrollment(payload: EnrollmentUpdateRequest) -> dict:
    with get_connection() as conn:
        enrollment = conn.execute(
            "SELECT id FROM enrollments WHERE student_id = ? AND lesson_id = ?",
            (payload.student_id, payload.lesson_id),
        ).fetchone()

        if enrollment:
            conn.execute(
                """
                UPDATE enrollments
                SET progress = ?, score = ?
                WHERE id = ?
                """,
                (payload.progress, payload.score, enrollment["id"]),
            )
        else:
            conn.execute(
                """
                INSERT INTO enrollments (student_id, lesson_id, progress, score)
                VALUES (?, ?, ?, ?)
                """,
                (payload.student_id, payload.lesson_id, payload.progress, payload.score),
            )
        conn.commit()

    return {"message": "Enrollment updated"}


@router.post("/lessons")
def create_lesson(payload: LessonCreateRequest) -> dict:
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO lessons (title, description, is_premium, difficulty)
            VALUES (?, ?, ?, ?)
            """,
            (payload.title, payload.description, int(payload.is_premium), payload.difficulty),
        )
        conn.commit()

    return {"id": cursor.lastrowid, "message": "Lesson created"}
