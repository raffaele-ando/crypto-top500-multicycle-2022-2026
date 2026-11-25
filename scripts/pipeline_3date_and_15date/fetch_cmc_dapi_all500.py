#!/usr/bin/env python3
"""
Phase 1: Query newly discovered CMC dapi.coinmarketcap.com/dex-stats/v3/dexer/ endpoints
across ALL 500 Clean Pure Cryptocurrencies (10 threads, ~25-35s total!):
  1. crypto-holder-data?cryptoId={cid} -> Top Holders with publicName, percent, fgp/sgp/others, explorerUrl
  2. cdp-holder/total-holder-historical?cryptoId={cid}&range=1y -> Daily/Weekly historical holderCount covering Jul 1, Oct 1, Nov 21!
Saves to raw/cmc_dapi_holders_all500.json
"""

import datetime
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")
OUT_PATH = os.path.join(RAW_DIR, "cmc_dapi_holders_all500.json")

clean500 = json.load(open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8"))["cryptocurrencies"]
audit = {r["cmc_id"]: r for r in json.load(open(os.path.join(PROJ_DIR, "audit_forense_500_crypto.json"), encoding="utf-8"))["cryptocurrencies"]}

HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://coinmarketcap.com",
    "Referer": "https://coinmarketcap.com/",
}


def get_json(url, retries=2, timeout=14):
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception:
            time.sleep(0.4 * (attempt + 1))
    return None


def pick_hist_point(pts, target_iso, max_days=14):
    t_d = datetime.date.fromisoformat(target_iso)
    best, best_diff = None, 9999
    for p in pts:
        try:
            ms = int(p["date"])
            d_obj = datetime.datetime.fromtimestamp(ms / 1000.0, tz=datetime.timezone.utc).date()
            diff = abs((t_d - d_obj).days)
            if diff < best_diff:
                best_diff = diff
                best = {"date": d_obj.isoformat(), "holderCount": int(float(p["holderCount"]))}
        except Exception:
            pass
    return best if (best and best_diff <= max_days) else None


def fetch_one(r):
    cid = r["cmc_id"]
    rec = {"cmc_id": cid, "symbol": r["symbol"], "holder_data": None, "hist_holders": None}

    # 1. crypto-holder-data
    d1 = get_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/crypto-holder-data?cryptoId={cid}")
    if d1 and isinstance(d1.get("data"), dict):
        data = d1["data"]
        hl = data.get("holders") or []
        if hl:
            wallets = []
            for h in hl:
                wallets.append({
                    "address": h.get("address") or "",
                    "balance": float(h.get("balance") or 0),
                    "pct": round(float(h.get("percent") or 0), 4),
                    "label": (h.get("publicName") or "").strip() or None,
                    "explorer": h.get("addressExplorerUrl") or "",
                    "platform_id": h.get("platformId"),
                })
            wallets.sort(key=lambda x: x["pct"], reverse=True)
            t10 = round(min(100.0, sum(w["pct"] for w in wallets[:10])), 2)
            t20 = round(min(100.0, sum(w["pct"] for w in wallets[:20])), 2) if len(wallets) >= 20 else None
            t50 = round(min(100.0, sum(w["pct"] for w in wallets[:50])), 2) if len(wallets) >= 50 else None
            t100 = round(min(100.0, sum(w["pct"] for w in wallets[:100])), 2) if len(wallets) >= 100 else None
            rec["holder_data"] = {
                "n_holders_list": len(wallets),
                "fgp": float(data.get("fgp") or 0),
                "sgp": float(data.get("sgp") or 0),
                "others": float(data.get("others") or 0),
                "top10_pct": t10,
                "top20_pct": t20,
                "top50_pct": t50,
                "top100_pct": t100,
                "explorer": wallets[0]["explorer"] if wallets else "",
                "wallets": wallets[:50],
            }

    # 2. cdp-holder/total-holder-historical (1y + 30d for exact nov21!)
    d2 = get_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/cdp-holder/total-holder-historical?cryptoId={cid}&range=1y")
    pts = []
    if d2 and isinstance(d2.get("data"), dict):
        pts = d2["data"].get("points") or []
    elif d2 and isinstance(d2.get("data"), list):
        pts = d2["data"]
    # Also fetch 30d for daily exact Nov 21 if 1y existed (or if 1y was empty, try 30d alone)
    d3 = get_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/cdp-holder/total-holder-historical?cryptoId={cid}&range=30d")
    pts30 = []
    if d3 and isinstance(d3.get("data"), dict):
        pts30 = d3["data"].get("points") or []
    elif d3 and isinstance(d3.get("data"), list):
        pts30 = d3["data"]

    all_pts = pts + pts30
    if all_pts:
        # Sort by timestamp
        all_pts_clean = [p for p in all_pts if p.get("date") and p.get("holderCount") is not None]
        all_pts_clean.sort(key=lambda p: int(p["date"]))
        if all_pts_clean:
            last_cnt = int(float(all_pts_clean[-1]["holderCount"]))
            rec["hist_holders"] = {
                "n_points": len(all_pts_clean),
                "min_date": datetime.datetime.fromtimestamp(int(all_pts_clean[0]["date"]) / 1000.0, tz=datetime.timezone.utc).strftime("%Y-%m-%d"),
                "max_date": datetime.datetime.fromtimestamp(int(all_pts_clean[-1]["date"]) / 1000.0, tz=datetime.timezone.utc).strftime("%Y-%m-%d"),
                "latest_count": last_cnt,
                "jul1": pick_hist_point(all_pts_clean, "2026-07-01"),
                "oct1": pick_hist_point(all_pts_clean, "2026-10-01"),
                "nov21": pick_hist_point(all_pts_clean, "2026-11-21"),
            }
    return str(cid), rec


print("Fetching CMC dapi dex-stats holder-data + total-holder-historical for ALL 500 coins (10 threads)...")
results = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = [ex.submit(fetch_one, r) for r in clean500]
    done = 0
    for fut in as_completed(futs):
        cid_s, rec = fut.result()
        done += 1
        if rec["holder_data"] or rec["hist_holders"]:
            results[cid_s] = rec
        if done % 100 == 0 or done == 500:
            hd_cnt = sum(1 for v in results.values() if v["holder_data"])
            hh_cnt = sum(1 for v in results.values() if v["hist_holders"])
            print(f"  Progress [{done}/500] ({time.time()-t0:.1f}s) | with_holder_data={hd_cnt} | with_hist_counts={hh_cnt}")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

# Print exact recoveries among our 76 previously missing coins!
prev_missing = [r for r in clean500 if audit[r["cmc_id"]]["top10_holders_pct"] is None]
rec_missing = []
for r in prev_missing:
    v = results.get(str(r["cmc_id"]))
    if v and (v["holder_data"] or v["hist_holders"]):
        rec_missing.append((r, v))

print(f"\n=== PHASE 1 CMC DAPI RESULTS ===")
print(f"  Total coins with crypto-holder-data (Top Holders): {sum(1 for v in results.values() if v['holder_data'])}")
print(f"  Total coins with total-holder-historical (3-date): {sum(1 for v in results.values() if v['hist_holders'])}")
print(f"    - covering Jul 1:  {sum(1 for v in results.values() if v['hist_holders'] and v['hist_holders']['jul1'])}")
print(f"    - covering Oct 1:  {sum(1 for v in results.values() if v['hist_holders'] and v['hist_holders']['oct1'])}")
print(f"    - covering Nov 21: {sum(1 for v in results.values() if v['hist_holders'] and v['hist_holders']['nov21'])}")
print(f"  Previously-missing (76) coins newly hit by CMC dapi: {len(rec_missing)}")
for r, v in rec_missing:
    hd = v["holder_data"]
    hh = v["hist_holders"]
    print(f"    #{r['rank_clean_jul1']:03d} {r['symbol']:10s} | top10={hd['top10_pct'] if hd else None}% exp={hd['explorer'][:32] if hd else ''} | hist_cnt={hh['latest_count'] if hh else None} (j={hh['jul1']['holderCount'] if (hh and hh['jul1']) else None})")
