from fastapi import FastAPI, Query
import os, psycopg2
from math import radians, sin, cos, sqrt, atan2

app = FastAPI()
DB = os.getenv("DATABASE_URL")

def get_conn():
    return psycopg2.connect(DB)

def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = radians(lat2-lat1); dlon = radians(lon2-lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1))*cos(radians(lat2))*sin(dlon/2)**2
    return R * 2 * atan2(sqrt(a), sqrt(1-a))

@app.get("/health")
def health():
    return {"status":"ok"}

@app.get("/offers")
def offers(q: str = "", sort: str = "price", max_price: float = None, 
           user_lat: float = 41.9028, user_lon: float = 12.4964, max_distance: float = 50):
    conn = get_conn()
    cur = conn.cursor()
    sql = """SELECT o.id, s.name, s.lat, s.lon, o.product_name_raw, o.price, o.old_price, o.price_per_unit, o.discount_percent, o.source_url
             FROM offers o JOIN supermarkets s ON s.id = o.supermarket_id
             WHERE (coalesce(o.normalized_name, o.product_name_raw) ILIKE %s)"""
    param = f"%{q}%"
    cur.execute(sql, (param,))
    rows = cur.fetchall()
    res = []
    for r in rows:
        id_, sname, slat, slon, pname, price, old_price, ppu, disc, url = r
        # fallback coordinates
        lat = slat if slat is not None else user_lat
        lon = slon if slon is not None else user_lon
        distance = haversine(user_lat, user_lon, lat, lon)
        if max_price and price and price > max_price:
            continue
        if distance > max_distance:
            continue
        res.append({"id": id_, "supermarket": sname, "product": pname, "price": float(price) if price else None,
                    "old_price": float(old_price) if old_price else None, "discount": float(disc) if disc else None,
                    "price_per_unit": float(ppu) if ppu else None, "distance_km": round(distance,2), "url": url})
    conn.close()
    if sort == "price":
        res.sort(key=lambda x: (x['price'] is None, x['price']))
    elif sort == "distance":
        res.sort(key=lambda x: x['distance_km'])
    elif sort == "discount":
        res.sort(key=lambda x: (x['discount'] is None, -x['discount'] if x['discount'] else 0))
    return {"count": len(res), "offers": res}
