#!/usr/bin/env python3
"""
STAGE 4A (runs in parallel with Stage 1):
1. CoinMetrics Community API v4 — ALL supported catalog assets with AdrBalCnt across 2022-12-28..2026-11-22 (ALL 15 DATES!)
2. CoinCarp Daily Historical Richlist API (type=all + type=1y) across major L1s/tokens back to 2022-2026!
3. Quick probe of CMC dapi total-holder-historical max supported range (1y vs 2y/3y/5y/all/max).
"""
import datetime, json, ssl, time, urllib.request, urllib.error
from pathlib import Path

BASE = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026\multidate_15_2022_2026")
RAW = BASE / "raw"
RAW.mkdir(parents=True, exist_ok=True)
CTX = ssl._create_unverified_context()
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", "Accept": "application/json"}

ALL_15_DATES = [
    ("D01", "2022-12-30"), ("D02", "2024-04-09"), ("D03", "2024-09-10"), ("D04", "2024-11-22"),
    ("D05", "2025-01-24"), ("D06", "2025-04-08"), ("D07", "2025-09-19"), ("D08", "2025-10-07"),
    ("D09", "2025-12-26"), ("D10", "2026-01-15"), ("D11", "2026-02-13"), ("D12", "2026-05-12"),
    ("D13", "2026-07-01"), ("D14", "2026-10-01"), ("D15", "2026-11-21"),
]

def http_json(url, headers=None, timeout=25):
    h = dict(HDR)
    if headers: h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
        return json.loads(r.read().decode("utf-8", errors="replace"))

# 1. Probe CMC DAPI range options (using LINK=1975 which has cdp-holder)
print("=== [1] PROBE CMC DAPI MAX RANGE ===")
for rng in ("1y", "2y", "3y", "5y", "all", "max", "ytd"):
    try:
        j = http_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/cdp-holder/total-holder-historical?cryptoId=1975&range={rng}", timeout=10)
        pts = (j.get("data") or {}).get("points") or []
        if pts:
            d0 = datetime.datetime.fromtimestamp(int(pts[0]["timestamp"])/1000 if int(pts[0]["timestamp"])>1e12 else int(pts[0]["timestamp"]), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            d1 = datetime.datetime.fromtimestamp(int(pts[-1]["timestamp"])/1000 if int(pts[-1]["timestamp"])>1e12 else int(pts[-1]["timestamp"]), tz=datetime.timezone.utc).strftime("%Y-%m-%d")
            print(f"  range={rng:4s} -> n={len(pts):4d} ({d0} .. {d1})")
        else:
            print(f"  range={rng:4s} -> empty")
    except Exception as e:
        print(f"  range={rng:4s} -> ERR: {str(e)[:50]}")

# 2. CoinMetrics Community API v4 — ALL assets supporting AdrBalCnt across ALL 15 DATES!
print("\n=== [2] COINMETRICS COMMUNITY V4: ALL AdrBalCnt ASSETS ACROSS 15 DATES ===")
cat = http_json("https://community-api.coinmetrics.io/v4/catalog/assets", timeout=25)
adr_assets = []
for a in (cat.get("data") or []):
    aid = a.get("asset")
    mets = {m.get("metric") for m in (a.get("metrics") or [])}
    if "AdrBalCnt" in mets:
        adr_assets.append(aid)
print(f"  Found {len(adr_assets)} CoinMetrics assets with AdrBalCnt: {adr_assets[:25]} ...")

# Query ONLY the exact 15 target dates (plus +-1 day fallback) in chunks of 12 assets to keep responses tiny & fast!
cm_all = {}  # asset_lower -> {date_str: {holders_cnt, active_addrs, sply_cur}}
for i in range(0, len(adr_assets), 12):
    batch = adr_assets[i:i+12]
    astr = ",".join(batch)
    # Query per-date windows (or full range? Full range for 12 assets x 1425 days = 17k rows -> better query each of the 15 dates +-1 day? No, 15 calls total for ALL assets at once!!)
    pass

# Even smarter: query EACH of the 15 dates (start=dt-1d, end=dt) for batches of 40 assets! Only ~30 tiny HTTP calls total!
for code, dt in ALL_15_DATES:
    d_obj = datetime.date.fromisoformat(dt)
    d_prev = (d_obj - datetime.timedelta(days=2)).isoformat()
    for i in range(0, len(adr_assets), 35):
        batch = adr_assets[i:i+35]
        u = f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={','.join(batch)}&metrics=AdrBalCnt&start_time={d_prev}&end_time={dt}&frequency=1d&page_size=1000"
        try:
            j = http_json(u, timeout=25)
            for row in (j.get("data") or []):
                a = row["asset"].lower()
                t = row["time"][:10]
                v = row.get("AdrBalCnt")
                if v is not None:
                    cm_all.setdefault(a, {})[dt] = {"date_matched": t, "holders_cnt": int(float(v))}
        except Exception as e:
            # fallback one-by-one if a single asset fails
            for a in batch:
                try:
                    j2 = http_json(f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics?assets={a}&metrics=AdrBalCnt&start_time={d_prev}&end_time={dt}&frequency=1d", timeout=12)
                    for row in (j2.get("data") or []):
                        if row.get("AdrBalCnt") is not None:
                            cm_all.setdefault(a.lower(), {})[dt] = {"date_matched": row["time"][:10], "holders_cnt": int(float(row["AdrBalCnt"]))}
                except Exception:
                    pass
    n_cov = sum(1 for a, dmap in cm_all.items() if dt in dmap)
    print(f"  [CM] {code} {dt} -> {n_cov} assets with exact AdrBalCnt")
    time.sleep(0.15)

(RAW / "coinmetrics_15dates_all.json").write_text(json.dumps(cm_all, indent=2), encoding="utf-8")
print(f"  Saved {len(cm_all)} CoinMetrics assets across 15 dates -> coinmetrics_15dates_all.json")

# 3. CoinCarp Daily Historical Richlists (type=all / 1y) across top major L1s!
print("\n=== [3] COINCARD DAILY HISTORICAL RICHLISTS (type=all & type=1y) ===")
CC_CODES = [
    (1, "BTC", "bitcoin"), (1027, "ETH", "ethereum"), (52, "XRP", "ripple"),
    (1839, "BNB", "binance-coin"), (5426, "SOL", "solana"), (74, "DOGE", "dogecoin"),
    (1958, "TRX", "tron"), (2010, "ADA", "cardano"), (11419, "TON", "gram"),
    (2, "LTC", "litecoin"), (1831, "BCH", "bitcoin-cash"), (512, "XLM", "stellar"),
    (1975, "LINK", "chainlink"), (5994, "SHIB", "shiba-inu"), (24478, "PEPE", "pepe"),
    (6636, "DOT", "polkadot100"), (3794, "ATOM", "cosmos"), (5805, "AVAX", "avalanche"),
    (1321, "ETC", "ethereum-classic"), (3077, "VET", "vechaincom"), (2777, "IOST", "iostoken"),
    (7083, "UNI", "uniswap"), (7278, "AAVE", "aave"), (2011, "XTZ", "tezos"),
]
cc_out = {}
for cid, sym, code_slug in CC_CODES:
    pts_map = {}
    for tp in ("all", "1y"):
        try:
            j = http_json(f"https://sapi.coincarp.com/api/v1/his/coin/chainsummary?code={code_slug}&type={tp}", headers={"Referer": "https://www.coincarp.com/"}, timeout=14)
            arr = j.get("data") or []
            for row in arr:
                if isinstance(row, list) and len(row) >= 6:
                    ts = int(row[0])
                    if ts > 1e12: ts //= 1000
                    dstr = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                    pts_map[dstr] = {
                        "date": dstr,
                        "holders": int(row[1]) if row[1] else None,
                        "top10": round(float(row[2]), 2) if row[2] else None,
                        "top20": round(float(row[3]), 2) if row[3] else None,
                        "top50": round(float(row[4]), 2) if row[4] else None,
                        "top100": round(float(row[5]), 2) if row[5] else None,
                    }
        except Exception:
            pass
        time.sleep(0.35)
    if pts_map:
        all_ds = sorted(pts_map.keys())
        matched = {}
        for _, dt in ALL_15_DATES:
            # Find nearest date within +-5 days
            d_obj = datetime.date.fromisoformat(dt)
            best_d = None
            best_diff = 999
            for k in all_ds:
                diff = abs((datetime.date.fromisoformat(k) - d_obj).days)
                if diff <= 5 and diff < best_diff:
                    best_diff = diff
                    best_d = k
            if best_d:
                matched[dt] = pts_map[best_d]
        cc_out[str(cid)] = {"cmc_id": cid, "symbol": sym, "code": code_slug, "min_date": all_ds[0], "max_date": all_ds[-1], "n_days": len(all_ds), "dates": matched}
        print(f"  [CC-OK] {sym:6s} | {all_ds[0]}..{all_ds[-1]} ({len(all_ds):4d}d) | matched {len(matched):2d}/15 dates")

(RAW / "coincarp_his_15dates.json").write_text(json.dumps(cc_out, indent=2), encoding="utf-8")
print(f"\n=== STAGE 4A COMPLETE: CoinMetrics ({len(cm_all)}) + CoinCarp ({len(cc_out)}) SAVED ===")
