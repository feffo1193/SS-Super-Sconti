
# SS Super Sconti - Progetto (scaffold)
Questo archivio contiene un prototipo pronto all'uso per l'app **SS Super Sconti**.
Contenuto: backend scraper (Python), API (FastAPI), frontend (Vite React), GitHub Actions workflow per scraping giornaliero.

## Cosa fare da smartphone (passaggi minimi)
1. Crea un account gratuito su Supabase (https://supabase.com) e crea un progetto Postgres.
2. Nella console SQL di Supabase esegui lo schema DB (tabelle supermarkets, offers) come descritto nel README dettagliato.
3. Crea un nuovo repository su GitHub e carica il contenuto di questa cartella (puoi caricare lo ZIP tramite l'app GitHub o il browser mobile).
4. Vai su GitHub repo -> Settings -> Secrets -> Actions -> aggiungi DATABASE_URL (connection string di Supabase).
5. Collegare il repo a Vercel per il frontend e a Render/Railway per il backend (o usa il deploy Automatico di ciascun servizio).
6. Il workflow GitHub Actions `.github/workflows/scrape-daily.yml` eseguirà lo scraper una volta al giorno e popolerà il DB.

## Disclaimer
- Per costruzione dell'APK Android serve Android Studio (PC). Tuttavia l'app è una PWA installabile su Android come app senza APK.
- Rispetta i robots.txt e le policy dei siti; usa questo progetto per scopi legittimi / prototipazione.
