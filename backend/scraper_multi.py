import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2

DATABASE_URL = os.getenv("DATABASE_URL")

SUPERMARKETS = [
    "https://www.tigotà.it/offerte",
    "https://www.todis.it/offerte",
    "https://www.iperal.it/volantino",
    "https://www.despar.it/volantino",
    "https://www.pam.it/offerte/",
    "https://www.conad.it/volantini.html",
    "https://www.coop.it/volantino",
    "https://www.lidl.it/volantino",
    "https://www.mdspa.it/volantino/",
    "https://www.eurospin.it/volantino/"
]

def scrape_offers():
    offers = []

    for url in SUPERMARKETS:
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                text = soup.get_text(" ", strip=True)
                offers.append({
                    "supermarket": url.split("//")[1].split("/")[0],
                    "offer_preview": text[:150],
                    "timestamp": datetime.utcnow()
                })
        except Exception as e:
            offers.append({
                "supermarket": url,
                "offer_preview": f"Errore: {e}",
                "timestamp": datetime.utcnow()
            })

    return offers

def save_to_db(data):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS offers (
            id SERIAL PRIMARY KEY,
            supermarket TEXT,
            offer_preview TEXT,
            timestamp TIMESTAMP
        );
    """)
    for d in data:
        cur.execute(
            "INSERT INTO offers (supermarket, offer_preview, timestamp) VALUES (%s, %s, %s)",
            (d["supermarket"], d["offer_preview"], d["timestamp"])
        )
    conn.commit()
    cur.close()
    conn.close()

if __name__ == "__main__":
    offers = scrape_offers()
    save_to_db(offers)
    print("✅ Offerte salvate nel database")
