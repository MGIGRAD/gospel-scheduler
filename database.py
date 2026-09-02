import sqlite3
from datetime import datetime

DB_NAME = "gospel_music.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('contemporary', 'classic_anthem', 'devotional_praise')),
            ensemble_type TEXT NOT NULL CHECK(ensemble_type IN ('praise_team', 'choir', 'both')),
            tempo TEXT CHECK(tempo IN ('fast', 'medium', 'slow')),
            key_signature TEXT,
            last_scheduled DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(title, artist)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_date DATE NOT NULL,
            slot TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            ensemble TEXT NOT NULL,
            FOREIGN KEY(song_id) REFERENCES songs(id)
        )
    """)

    conn.commit()
    conn.close()

def seed_classic_repertoire():
    classics = [
        ("Total Praise", "Richard Smallwood", "classic_anthem", "choir", "slow", "Db"),
        ("Anthem of Praise", "Richard Smallwood", "classic_anthem", "choir", "fast", "Eb"),
        ("He Turned It", "Ricky Dillard", "classic_anthem", "choir", "fast", "Ab"),
        ("Every Praise", "Hezekiah Walker", "devotional_praise", "both", "medium", "Db"),
        ("Souled Out", "Hezekiah Walker", "classic_anthem", "choir", "fast", "Ab"),
        ("You Are Good", "Fred Hammond", "devotional_praise", "both", "fast", "E"),
        ("No Ordinary Worship", "Kelontae Gavin", "devotional_praise", "praise_team", "slow", "G"),
        ("For Every Mountain", "Kurt Carr", "classic_anthem", "choir", "slow", "Eb"),
        ("We Offer Praise", "Rodnie Bryant", "classic_anthem", "choir", "fast", "Bb"),
        ("Open My Eyes", "Ricky Dillard", "classic_anthem", "choir", "medium", "F"),
    ]
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT OR IGNORE INTO songs (title, artist, category, ensemble_type, tempo, key_signature)
        VALUES (?, ?, ?, ?, ?, ?)
    """, classics)
    conn.commit()
    conn.close()
