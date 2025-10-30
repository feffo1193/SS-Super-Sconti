import { useEffect, useState } from "react";

export default function App(){
  const [q, setQ] = useState("");
  const [offers, setOffers] = useState([]);
  const [coords, setCoords] = useState({lat:41.9028, lon:12.4964});
  const [loading, setLoading] = useState(false);

  useEffect(()=>{ fetchOffers(); }, []);

  const fetchOffers = async () => {
    setLoading(true);
    try{
      const res = await fetch(`https://api-PLACEHOLDER.example.com/offers?q=${encodeURIComponent(q)}&user_lat=${coords.lat}&user_lon=${coords.lon}`);
      const data = await res.json();
      setOffers(data.offers || []);
    }catch(e){
      console.error(e);
      setOffers([]);
    }finally{ setLoading(false); }
  };

  const refresh = () => fetchOffers();

  const geoLocate = () => {
    if(navigator.geolocation) navigator.geolocation.getCurrentPosition(p => { setCoords({lat:p.coords.latitude, lon:p.coords.longitude}); fetchOffers(); });
  };

  return (
    <div style={{padding:16,fontFamily:"system-ui"}}>
      <h1 style={{fontSize:20,fontWeight:700}}>SS Super Sconti</h1>
      <div style={{display:"flex",gap:8,marginTop:12}}>
        <input value={q} onChange={e=>setQ(e.target.value)} placeholder="Cerca prodotto" style={{flex:1,padding:8,border:"1px solid #ddd",borderRadius:6}}/>
        <button onClick={fetchOffers} style={{padding:"8px 12px",background:"#2563eb",color:"white",borderRadius:6}}>Cerca</button>
        <button onClick={refresh} style={{padding:"8px 12px",background:"#16a34a",color:"white",borderRadius:6}}>Refresh</button>
        <button onClick={geoLocate} style={{padding:"8px 12px",background:"#6b7280",color:"white",borderRadius:6}}>Posizione</button>
      </div>
      <div style={{marginTop:16}}>
        {loading ? <div>Caricamento...</div> : (
          <ul style={{listStyle:"none",padding:0,margin:0,display:"grid",gap:8}}>
            {offers.map(o=>(
              <li key={o.id} style={{border:"1px solid #eee",padding:12,display:"flex",justifyContent:"space-between",borderRadius:8}}>
                <div>
                  <div style={{fontWeight:600}}>{o.product}</div>
                  <div style={{fontSize:12,color:"#6b7280"}}>{o.supermarket}</div>
                </div>
                <div style={{textAlign:"right"}}>
                  <div style={{fontWeight:700}}>€{o.price}</div>
                  <div style={{fontSize:12}}>{o.discount ? `${o.discount}%` : ""}</div>
                  <div style={{fontSize:12,color:"#6b7280"}}>{o.distance_km} km</div>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
