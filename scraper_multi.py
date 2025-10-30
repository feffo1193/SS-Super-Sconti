import os, re, json, tempfile, time, requests, pdfplumber
from bs4 import BeautifulSoup
from datetime import date
import psycopg2

# Minimal, robust scraper that looks for PDF links or "€" lines in HTML.
SUPERMARKETS = {
    "esselunga": {"name":"Esselunga", "base":"https://www.esselunga.it", "urls":["https://www.esselunga.it/it-it/promozioni/volantini.html"]},
    "carrefour": {"name":"Carrefour", "base":"https://www.carrefour.it", "urls":["https://www.carrefour.it/volantino"]},
    "coop": {"name":"Coop", "base":"https://www.coop.it", "urls":["https://www.coop.it"]},
    "conad": {"name":"Conad", "base":"https://www.conad.it", "urls":["https://www.conad.it/it/volantini.html"]},
    "pam": {"name":"Pam Panorama", "base":"https://www.pampanorama.it", "urls":["https://www.pampanorama.it/volantini"]},
    "todis": {"name":"Todis", "base":"https://www.todis.it", "urls":["https://www.todis.it/volantini"]},
    "md": {"name":"MD Discount", "base":"https://www.mdspa.it", "urls":["https://www.mdspa.it/volantino"]},
    "eurospin": {"name":"Eurospin", "base":"https://www.eurospin.it", "urls":["https://www.eurospin.it/it/volantini"]},
    "penny": {"name":"Penny Market", "base":"https://www.pennymarket.it", "urls":["https://www.pennymarket.it/it/volantini"]},
    "lidl": {"name":"Lidl", "base":"https://www.lidl.it", "urls":["https://www.lidl.it/it/volantino"]}
}

HEADERS = {"User-Agent":"SS-SuperSconti-bot/1.0"}
DB_URL = os.getenv("DATABASE_URL")

def db_conn():
    return psycopg2.connect(DB_URL)

def download(url):
    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()
    return r.content

def extract_text_pdf_bytes(b):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
        f.write(b); path = f.name
    texts = []
    try:
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                t = p.extract_text()
                if t: texts.append(t)
    finally:
        try: os.unlink(path)
        except: pass
    return "\\n".join(texts)

def find_pdfs(html, base):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if href.lower().endswith(".pdf"):
            if href.startswith("http"): links.append(href)
            else: links.append(base.rstrip("/") + "/" + href.lstrip("/"))
    return list(set(links))

def price_lines(text):
    lines = []
    for line in text.splitlines():
        if "€" in line:
            lines.append(line.strip())
    return lines

def save_offer(conn, supermarket_code, name, price_text, url, source_type):
    cur = conn.cursor()
    cur.execute("SELECT id FROM supermarkets WHERE code=%s", (supermarket_code,))
    row = cur.fetchone()
    if not row:
        cur.execute("INSERT INTO supermarkets(code,name,website) VALUES (%s,%s,%s) RETURNING id", (supermarket_code, SUPERMARKETS[supermarket_code]['name'], SUPERMARKETS[supermarket_code]['base']))
        sid = cur.fetchone()[0]; conn.commit()
    else:
        sid = row[0]
    m = re.search(r'(\\d+[\\.,]?\\d*)', price_text)
    price = float(m.group(1).replace(',', '.')) if m else None
    cur.execute(\"\"\"INSERT INTO offers(supermarket_id, product_name_raw, price, source_url, source_type, start_date, scraped_at, raw_metadata)
                   VALUES (%s,%s,%s,%s,%s,%s, now(), %s)\"\"\", (sid, name, price, url, source_type, date.today(), json.dumps({"raw":price_text})))
    conn.commit()

def process_page(conn, code, url):
    try:
        print("GET", url)
        content = download(url)
        html = content.decode(errors='ignore')
    except Exception as e:
        print("download error", e); return
    pdfs = find_pdfs(html, SUPERMARKETS[code]['base'])
    if pdfs:
        for p in pdfs:
            try:
                b = download(p)
                text = extract_text_pdf_bytes(b)
                for ln in price_lines(text):
                    save_offer(conn, code, ln, ln, p, "pdf")
            except Exception as e:
                print("pdf parse err", e)
    else:
        for ln in price_lines(html):
            save_offer(conn, code, ln, ln, url, "html")

def run_all():
    conn = db_conn()
    for code,cfg in SUPERMARKETS.items():
        for u in cfg.get("urls", cfg.get("volantino_pages", [])):
            process_page(conn, code, u)
            time.sleep(2)
    conn.close()

if __name__ == "__main__":
    run_all()
