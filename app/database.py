from pathlib import Path
import sqlite3

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "robi_studio.db"


def get_connection() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'parent', 'admin'))
            );

            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                is_premium INTEGER NOT NULL DEFAULT 0,
                difficulty TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS enrollments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                lesson_id INTEGER NOT NULL,
                progress INTEGER NOT NULL DEFAULT 0,
                score INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY(student_id) REFERENCES users(id),
                FOREIGN KEY(lesson_id) REFERENCES lessons(id)
            );

            CREATE TABLE IF NOT EXISTS premium_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL UNIQUE,
                active INTEGER NOT NULL DEFAULT 0,
                plan_name TEXT,
                renewed_at TEXT,
                FOREIGN KEY(student_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS simulation_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                scenario TEXT NOT NULL,
                input_score INTEGER NOT NULL,
                simulated_score INTEGER NOT NULL,
                feedback TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY(student_id) REFERENCES users(id)
            );
            """
        )
        conn.commit()

        cursor.execute("SELECT COUNT(*) as count FROM users")
        if cursor.fetchone()["count"] == 0:
            cursor.executemany(
                "INSERT INTO users (name, email, role) VALUES (?, ?, ?)",
                [
                    ("Aarav Student", "student@robi.local", "student"),
                    ("Neha Parent", "parent@robi.local", "parent"),
                    ("Sana Admin", "admin@robi.local", "admin"),
                ],
            )

        cursor.execute("SELECT COUNT(*) as count FROM lessons")
        if cursor.fetchone()["count"] == 0:
            cursor.executemany(
                "INSERT INTO lessons (title, description, is_premium, difficulty) VALUES (?, ?, ?, ?)",
                [
                    ("Foundations of Robotics", "Build your first bot with sensors.", 0, "Beginner"),
                    ("AI Navigation", "Learn pathfinding and autonomous movement.", 1, "Intermediate"),
                    ("Computer Vision Lab", "Detect objects with camera input.", 1, "Advanced"),
                ],
            )

            cursor.execute(
                "INSERT INTO enrollments (student_id, lesson_id, progress, score) VALUES (1, 1, 75, 82)"
            )
            cursor.execute(
                "INSERT INTO premium_subscriptions (student_id, active, plan_name, renewed_at) VALUES (1, 1, 'Pro Annual', date('now'))"
            )

        conn.commit()
