import re
import requests
from bs4 import BeautifulSoup
from database import get_connection

def scrape_latest_gospel_charts():
    url = "https://blackgospelradio.net/music/charts/billboard-gospel-airplay-charts/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Chart fetch error: {e}. Utilizing cached database entries.")
        return

    soup = BeautifulSoup(response.text, "html.parser")
    entries = []

    for article in soup.find_all(["h2", "h3", "a"]):
        text = article.get_text().strip()
        match = re.search(r"“([^”]+)”\s+by\s+([^–\n]+)", text)
        if match:
            title = match.group(1).strip()
            artist = match.group(2).strip()
            entries.append((title, artist))

    conn = get_connection()
    cursor = conn.cursor()
    new_added = 0
    for title, artist in entries:
        cursor.execute("""
            INSERT OR IGNORE INTO songs (title, artist, category, ensemble_type, tempo)
            VALUES (?, ?, 'contemporary', 'both', 'medium')
        """, (title, artist))
        if cursor.rowcount > 0:
            new_added += 1

    conn.commit()
    conn.close()
    print(f"Chart sync complete. {new_added} new contemporary titles ingested.")
