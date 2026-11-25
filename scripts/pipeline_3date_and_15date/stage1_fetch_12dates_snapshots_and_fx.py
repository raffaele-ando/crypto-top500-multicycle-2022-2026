#!/usr/bin/env python3
"""
STAGE 1: Download FULL CMC Historical Snapshots (up to 10,000 coins per date) + Exact EUR/USD FX
for ALL 12 requested cycle checkpoints (all aligned to exact YYYY-MM-DD 00:00:00 UTC):
  D01: 2022-12-30 00:00:00 UTC (30 Dic 2022 01:00 CET)
  D02: 2024-04-09 00:00:00 UTC (9 Apr 2024 02:00 CEST)
  D03: 2024-09-10 00:00:00 UTC (10 Set 2024 02:00 CEST)
  D04: 2024-11-22 00:00:00 UTC (22 Nov 2024 01:00 CET)
  D05: 2025-01-24 00:00:00 UTC (24 Gen 2025 01:00 CET)
  D06: 2025-04-08 00:00:00 UTC (8 Apr 2025 02:00 CEST)
  D07: 2025-09-19 00:00:00 UTC (19 Set 2025 02:00 CEST)
  D08: 2025-10-07 00:00:00 UTC (7 Ott 2025 02:00 CEST)
  D09: 2025-12-26 00:00:00 UTC (26 Dic 2025 01:00 CET)
  D10: 2026-01-15 00:00:00 UTC (15 Gen 2026 01:00 CET)
  D11: 2026-02-13 00:00:00 UTC (13 Feb 2026 01:00 CET)
  D12: 2026-05-12 00:00:00 UTC (12 Mag 2026 02:00 CEST)
"""
import json, os, ssl, statistics, time, urllib.request
from pathlib import Path

BASE = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026\multidate_15_2022_2026")
RAW = BASE / "raw"
RAW.mkdir(parents=True, exist_ok=True)

DATES_12 = [
    ("D01", "2022-12-30", "30 Dic 2022 01:00 CET"),
    ("D02", "2024-04-09", "9 Apr 2024 02:00 CEST"),
    ("D03", "2024-09-10", "10 Set 2024 02:00 CEST"),
    ("D04", "2024-11-22", "22 Nov 2024 01:00 CET"),
    ("D05", "2025-01-24", "24 Gen 2025 01:00 CET"),
    ("D06", "2025-04-08", "8 Apr 2025 02:00 CEST"),
    ("D07", "2025-09-19", "19 Set 2025 02:00 CEST"),
    ("D08", "2025-10-07", "7 Ott 2025 02:00 CEST"),
    ("D09", "2025-12-26", "26 Dic 2025 01:00 CET"),
    ("D10", "2026-01-15", "15 Gen 2026 01:00 CET"),
    ("D11", "2026-02-13", "13 Feb 2026 01:00 CET"),
    ("D12", "2026-05-12", "12 Mag 2026 02:00 CEST"),
]

CTX = ssl._create_unverified_context()
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

def http_json(url, retries=3, timeout=28):
    for att in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception as e:
            if att == retries - 1:
                raise
            time.sleep(1.5 * (att + 1))

fx_manifest = {}

print("=== STAGE 1: FETCHING 12 FULL CMC HISTORICAL SNAPSHOTS + EXACT EUR/USD FX ===")
for code, dt, lbl in DATES_12:
    out_p = RAW / f"cmc_snap_{dt}.json"
    # 1. Exact EUR/USD FX at YYYY-MM-DD 00:00:00 UTC via CMC USD+EUR dual-quote median (plus Frankfurter ECB cross-check)
    dual = http_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date={dt}&start=1&limit=10&convertId=2781,2790")
    ratios = []
    ts_exact = None
    btc_usd = None
    for c in (dual.get("data") or []):
        if ts_exact is None:
            ts_exact = c.get("lastUpdated")
        qs = {str(q.get("name")): q for q in (c.get("quotes") or [])}
        u_q = qs.get("USD") or qs.get("2781")
        e_q = qs.get("EUR") or qs.get("2790")
        if u_q and e_q and u_q.get("price") and e_q.get("price"):
            ratios.append(float(u_q["price"]) / float(e_q["price"]))
            if c.get("id") == 1:
                btc_usd = float(u_q["price"])
    fx_cmc = round(statistics.median(ratios), 6) if ratios else None
    fx_ecb = None
    try:
        fj = http_json(f"https://api.frankfurter.app/{dt}?from=EUR&to=USD", retries=2, timeout=10)
        fx_ecb = round(float((fj.get("rates") or {}).get("USD")), 6)
    except Exception:
        pass
    fx_used = fx_cmc or fx_ecb

    # 2. Download FULL CMC snapshot (start=1..10000 in 5000-coin pages!)
    if out_p.exists() and out_p.stat().st_size > 1_000_000:
        existing = json.loads(out_p.read_text(encoding="utf-8"))
        all_coins = existing.get("data", existing) if isinstance(existing, dict) else existing
        print(f"  [CACHED] {code} {dt} ({lbl:21s}) | n={len(all_coins):5d} | ts={ts_exact} | BTC={btc_usd:9.2f} | FX_CMC={fx_cmc} FX_ECB={fx_ecb}")
    else:
        all_coins = []
        seen_ids = set()
        for start in (1, 5001):
            u = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date={dt}&start={start}&limit=5000&convertId=2781"
            j = http_json(u, retries=3, timeout=35)
            chunk = j.get("data") or []
            for item in chunk:
                cid = int(item["id"])
                if cid in seen_ids:
                    continue
                seen_ids.add(cid)
                q = (item.get("quotes") or [{}])[0]
                all_coins.append({
                    "id": cid,
                    "name": item.get("name"),
                    "symbol": item.get("symbol"),
                    "slug": item.get("slug"),
                    "cmcRank": item.get("cmcRank"),
                    "numMarketPairs": item.get("numMarketPairs"),
                    "circulatingSupply": item.get("circulatingSupply"),
                    "totalSupply": item.get("totalSupply"),
                    "maxSupply": item.get("maxSupply"),
                    "isActive": item.get("isActive"),
                    "tags": item.get("tags") or [],
                    "lastUpdated": item.get("lastUpdated"),
                    "price": q.get("price"),
                    "volume24h": q.get("volume24h"),
                    "marketCap": q.get("marketCap"),
                    "fullyDiluttedMarketCap": q.get("fullyDiluttedMarketCap") or q.get("fullyDilutedMarketCap"),
                    "percentChange24h": q.get("percentChange24h"),
                })
            if len(chunk) < 4900:
                break
            time.sleep(0.35)
        out_p.write_text(json.dumps({"date": dt, "code": code, "ts_exact": ts_exact, "fx_eur_usd": fx_used, "count": len(all_coins), "data": all_coins}, ensure_ascii=False), encoding="utf-8")
        print(f"  [SAVED ] {code} {dt} ({lbl:21s}) | n={len(all_coins):5d} | ts={ts_exact} | BTC={btc_usd:9.2f} | FX_CMC={fx_cmc} FX_ECB={fx_ecb}")

    fx_manifest[dt] = {
        "code": code, "date": dt, "italian_label": lbl, "ts_exact": ts_exact,
        "fx_eur_usd": fx_used, "fx_cmc": fx_cmc, "fx_ecb": fx_ecb,
        "btc_usd": btc_usd, "total_coins_in_snapshot": len(all_coins),
    }
    time.sleep(0.25)

(RAW / "fx_and_snapshots_manifest_12dates.json").write_text(json.dumps(fx_manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"\n=== STAGE 1 COMPLETE: ALL 12 FULL SNAPSHOTS + EXACT FX SAVED -> {RAW} ===")
