from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import datetime
from typing import List

app = FastAPI()

# MySQL Database Initialization
def initialize_database():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password=""
    )
    cursor = db.cursor()
    
    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS memotime")
    cursor.execute("USE memotime")

    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_notes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tbl_timers (
        id INT AUTO_INCREMENT PRIMARY KEY,
        task_name VARCHAR(255) NOT NULL,
        start_time DATETIME,
        end_time DATETIME,
        duration INT
    )
    """)

    cursor.close()
    db.close()

# Initialize the database when the app starts
initialize_database()

# Database Connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="password",
        database="memotime"
    )

# Models for Pydantic
class Note(BaseModel):
    title: str
    content: str

class Timer(BaseModel):
    task_name: str
    start_time: datetime
    end_time: datetime

# Notes Management

@app.post("/notes/")
def create_note(note: Note):
    db = get_db_connection()
    cursor = db.cursor()
    query = "INSERT INTO tbl_notes (title, content, created_at, updated_at) VALUES (%s, %s, NOW(), NOW())"
    cursor.execute(query, (note.title, note.content))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note created successfully"}

@app.get("/notes/")
def get_all_notes():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_notes")
    notes = cursor.fetchall()
    cursor.close()
    db.close()
    return notes

@app.get("/notes/{note_id}")
def get_note_by_id(note_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_notes WHERE id = %s", (note_id,))
    note = cursor.fetchone()
    cursor.close()
    db.close()
    if note:
        return note
    raise HTTPException(status_code=404, detail="Note not found")

@app.put("/notes/{note_id}")
def update_note(note_id: int, note: Note):
    db = get_db_connection()
    cursor = db.cursor()
    query = "UPDATE tbl_notes SET title = %s, content = %s, updated_at = NOW() WHERE id = %s"
    cursor.execute(query, (note.title, note.content, note_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note updated successfully"}

@app.delete("/notes/{note_id}")
def delete_note_by_id(note_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_notes WHERE id = %s", (note_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Note deleted successfully"}

@app.get("/notes/search/")
def search_notes_by_title(title: str):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM tbl_notes WHERE title LIKE %s"
    cursor.execute(query, ('%' + title + '%',))
    notes = cursor.fetchall()
    cursor.close()
    db.close()
    return notes

@app.get("/notes/count/")
def get_note_count():
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM tbl_notes")
    count = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"total_notes": count}

@app.get("/notes/recent/")
def get_recently_updated_notes():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_notes ORDER BY updated_at DESC LIMIT 5")
    notes = cursor.fetchall()
    cursor.close()
    db.close()
    return notes

@app.delete("/notes/bulk-delete/")
def bulk_delete_notes(ids: List[int]):
    db = get_db_connection()
    cursor = db.cursor()
    format_strings = ','.join(['%s'] * len(ids))
    cursor.execute(f"DELETE FROM tbl_notes WHERE id IN ({format_strings})", tuple(ids))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Notes deleted successfully"}

# Timer Management

@app.post("/timers/")
def create_timer(timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = (timer.end_time - timer.start_time).seconds
    query = "INSERT INTO tbl_timers (task_name, start_time, end_time, duration) VALUES (%s, %s, %s, %s)"
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer created successfully"}

@app.get("/timers/")
def get_all_timers():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_timers")
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    return timers

@app.get("/timers/{timer_id}")
def get_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_timers WHERE id = %s", (timer_id,))
    timer = cursor.fetchone()
    cursor.close()
    db.close()
    if timer:
        return timer
    raise HTTPException(status_code=404, detail="Timer not found")

@app.put("/timers/{timer_id}")
def update_timer(timer_id: int, timer: Timer):
    db = get_db_connection()
    cursor = db.cursor()
    duration = (timer.end_time - timer.start_time).seconds
    query = "UPDATE tbl_timers SET task_name = %s, start_time = %s, end_time = %s, duration = %s WHERE id = %s"
    cursor.execute(query, (timer.task_name, timer.start_time, timer.end_time, duration, timer_id))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer updated successfully"}

@app.delete("/timers/{timer_id}")
def delete_timer_by_id(timer_id: int):
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("DELETE FROM tbl_timers WHERE id = %s", (timer_id,))
    db.commit()
    cursor.close()
    db.close()
    return {"message": "Timer deleted successfully"}

@app.get("/timers/active/")
def get_active_timers():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tbl_timers WHERE end_time IS NULL")
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    return timers

@app.get("/timers/duration/")
def calculate_total_time(task_name: str):
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT SUM(duration) AS total_duration FROM tbl_timers WHERE task_name = %s"
    cursor.execute(query, (task_name,))
    total_duration = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"total_duration_seconds": total_duration}

@app.get("/timers/average-duration/")
def get_average_duration():
    db = get_db_connection()
    cursor = db.cursor()
    query = "SELECT AVG(duration) AS average_duration FROM tbl_timers"
    cursor.execute(query)
    avg_duration = cursor.fetchone()[0]
    cursor.close()
    db.close()
    return {"average_duration_seconds": avg_duration}

@app.get("/timers/range/")
def get_timers_in_range(start: datetime, end: datetime):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)
    query = "SELECT * FROM tbl_timers WHERE start_time BETWEEN %s AND %s"
    cursor.execute(query, (start, end))
    timers = cursor.fetchall()
    cursor.close()
    db.close()
    return timers
