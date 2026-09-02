import calendar
from datetime import date, timedelta
from database import get_connection

def get_sundays(year: int, month: int):
    cal = calendar.Calendar(firstweekday=calendar.SUNDAY)
    return [d for d in cal.itermonthdates(year, month) if d.month == month and d.weekday() == 6]

def pick_song(cursor, category, ensemble, cooldown_days=45):
    query = """
        SELECT id, title, artist, tempo, key_signature 
        FROM songs 
        WHERE (ensemble_type = ? OR ensemble_type = 'both')
          AND category = ?
          AND (last_scheduled IS NULL OR last_scheduled <= date('now', ?))
        ORDER BY last_scheduled ASC, RANDOM()
        LIMIT 1
    """
    cursor.execute(query, (ensemble, category, f"-{cooldown_days} days"))
    row = cursor.fetchone()

    if not row:
        fallback_query = """
            SELECT id, title, artist, tempo, key_signature 
            FROM songs 
            WHERE category = ?
            ORDER BY RANDOM() LIMIT 1
        """
        cursor.execute(fallback_query, (category,))
        row = cursor.fetchone()
    return row

def generate_monthly_schedule(year: int, month: int):
    sundays = get_sundays(year, month)
    conn = get_connection()
    cursor = conn.cursor()

    monthly_plan = {}

    for sunday in sundays:
        slots = [
            ("Call to Worship", "devotional_praise", "praise_team"),
            ("Praise & Worship", "contemporary", "praise_team"),
            ("Choir Selection", "classic_anthem", "choir")
        ]

        service_order = []
        for slot_name, category, ensemble in slots:
            song = pick_song(cursor, category, ensemble)
            if song:
                song_id, title, artist, tempo, key_sig = song
                cursor.execute("UPDATE songs SET last_scheduled = ? WHERE id = ?", (sunday, song_id))
                cursor.execute("""
                    INSERT INTO schedules (service_date, slot, song_id, ensemble)
                    VALUES (?, ?, ?, ?)
                """, (sunday, slot_name, song_id, ensemble))
                service_order.append({
                    "slot": slot_name,
                    "title": title,
                    "artist": artist,
                    "ensemble": ensemble,
                    "key": key_sig or "N/A"
                })

        monthly_plan[str(sunday)] = service_order

    conn.commit()
    conn.close()
    return monthly_plan
