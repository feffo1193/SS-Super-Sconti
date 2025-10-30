from fastapi import FastAPI
from scraper.scraper_multi import scrape_offers, save_to_db

app = FastAPI()

@app.get("/")
def home():
    return {"status": "ok", "message": "SS Super Sconti backend attivo 🚀"}

@app.get("/aggiorna")
def aggiorna_offerte():
    offers = scrape_offers()
    save_to_db(offers)
    return {"message": f"{len(offers)} offerte aggiornate nel database"}
