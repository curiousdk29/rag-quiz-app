# database.py

import sqlite3
from datetime import datetime

DB_PATH = "quiz_results.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quiz_attempts (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            collection      TEXT NOT NULL,
            question        TEXT NOT NULL,
            topic           TEXT,
            user_answer     TEXT NOT NULL,
            correct_answer  TEXT NOT NULL,
            is_correct      INTEGER NOT NULL,
            timestamp       TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_attempt(collection: str, question: str, topic: str,
                 user_answer: str, correct_answer: str, is_correct: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quiz_attempts
            (collection, question, topic, user_answer, correct_answer, is_correct, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        collection,
        question,
        topic,
        user_answer,
        correct_answer,
        1 if is_correct else 0,
        datetime.now().isoformat()
    ))
    conn.commit()
    conn.close()


def get_weak_areas(collection: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            topic,
            COUNT(*) as total_attempts,
            SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) as wrong_count,
            ROUND(
                100.0 * SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) / COUNT(*),
                1
            ) as error_rate
        FROM quiz_attempts
        WHERE topic IS NOT NULL AND collection = ?
        GROUP BY topic
        HAVING total_attempts >= 1 AND error_rate >= 30
        ORDER BY error_rate DESC
    """, (collection,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "topic": row[0],
            "total_attempts": row[1],
            "wrong_count": row[2],
            "error_rate": row[3]
        }
        for row in rows
    ]


def get_all_stats(collection: str) -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            topic,
            COUNT(*) as total,
            SUM(is_correct) as correct,
            ROUND(100.0 * SUM(is_correct) / COUNT(*), 1) as accuracy
        FROM quiz_attempts
        WHERE topic IS NOT NULL AND collection = ?
        GROUP BY topic
        ORDER BY accuracy ASC
    """, (collection,))
    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "topic": row[0],
            "total": row[1],
            "correct": row[2],
            "accuracy": row[3]
        }
        for row in rows
    ]