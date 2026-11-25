import json, ssl, time, urllib.request
from pathlib import Path

RAW = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026\multidate_15_2022_2026\raw")
CTX = ssl._create_unverified_context()
HDR = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}

fxm = json.loads((RAW / "fx_and_snapshots_manifest_12dates.json").read_text(encoding="utf-8"))

for dt in ["2024-11-22", "2025-01-24", "2025-04-08"]:
    p = RAW / f"cmc_snap_{dt}.json"
    doc = json.loads(p.read_text(encoding="utf-8"))
    coins = doc["data"]
    seen = {int(c["id"]) for c in coins}
    added = 0
    for start in (10001, 15001):
        u = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date={dt}&start={start}&limit=5000&convertId=2781"
        j = json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=HDR), timeout=35, context=CTX).read())
        chunk = j.get("data") or []
        for item in chunk:
            cid = int(item["id"])
            if cid in seen: continue
            seen.add(cid)
            q = (item.get("quotes") or [{}])[0]
            coins.append({
                "id": cid, "name": item.get("name"), "symbol": item.get("symbol"), "slug": item.get("slug"),
                "cmcRank": item.get("cmcRank"), "numMarketPairs": item.get("numMarketPairs"),
                "circulatingSupply": item.get("circulatingSupply"), "totalSupply": item.get("totalSupply"),
                "maxSupply": item.get("maxSupply"), "isActive": item.get("isActive"),
                "tags": item.get("tags") or [], "lastUpdated": item.get("lastUpdated"),
                "price": q.get("price"), "volume24h": q.get("volume24h"), "marketCap": q.get("marketCap"),
                "fullyDiluttedMarketCap": q.get("fullyDiluttedMarketCap") or q.get("fullyDilutedMarketCap"),
                "percentChange24h": q.get("percentChange24h"),
            })
            added += 1
        if len(chunk) < 4900: break
        time.sleep(0.3)
    doc["data"] = coins
    doc["count"] = len(coins)
    p.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
    fxm[dt]["total_coins_in_snapshot"] = len(coins)
    new_high = sorted([c for c in coins[len(coins)-added:] if (c.get("marketCap") or 0) > 1e8], key=lambda x: -x["marketCap"])[:10] if added else []
    print(f"{dt}: +{added} coins -> total={len(coins)} | top newly captured Tier-2 (>100M): {[(c['symbol'], round(c['marketCap']/1e9, 2)) for c in new_high]}")

(RAW / "fx_and_snapshots_manifest_12dates.json").write_text(json.dumps(fxm, indent=2, ensure_ascii=False), encoding="utf-8")
