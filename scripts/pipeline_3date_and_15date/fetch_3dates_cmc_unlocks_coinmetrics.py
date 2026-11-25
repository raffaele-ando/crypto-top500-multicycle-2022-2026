#!/usr/bin/env python3
"""
Script 1: Fetch ALL Point-in-Time Historical Data for the 3 Measurement Dates
  T1 = 2026-07-01 23:59:59 UTC (already in raw/cmc_full_2026-07-01.json)
  T2 = 2026-10-01 23:59:59 UTC (already in raw/cmc_full_2026-10-01.json)
  T3 = 2026-11-21 05:30 CET / 04:30 UTC (fetch cmc_full_2026-11-20.json & cmc_full_2026-11-21.json + existing intraday nov21_0530!)

Also fetches:
  - CMC Official Historical Token Unlocks timeline (v3/token-unlock/historical?cryptoId={cid}&range=All) for all 258 vesting coins
  - CoinMetrics Community API v4 daily historical AdrBalCnt, AdrActCnt, SplyCur, SplyExNtv on T1, T2, T3
  - CoinCarp daily historical Top 10/20/50/100 & holderCount (his/coin/chainsummary?code={code}&type=1y) for major L1s
"""

import datetime
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")

with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
    clean500 = json.load(f)["cryptocurrencies"]
with open(os.path.join(RAW_DIR, "cmc_tokenomics_holders_clean500.json"), encoding="utf-8") as f:
    details = json.load(f)


def get_json(url, retries=3, timeout=20, headers=None):
    hdrs = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
        "Accept": "application/json",
    }
    if headers:
        hdrs.update(headers)
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=hdrs)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            time.sleep(0.5 * (attempt + 1))
    raise last_err


# --- 1. Fetch FULL CMC listings/historical for 2026-11-20 & 2026-11-21 ---
def fetch_cmc_full_date(date_str):
    out_p = os.path.join(RAW_DIR, f"cmc_full_{date_str}.json")
    if os.path.exists(out_p):
        with open(out_p, encoding="utf-8") as f:
            d = json.load(f)
        print(f"  [CACHED] cmc_full_{date_str}.json ({len(d)} coins)")
        return d
    all_rows = []
    start = 1
    limit = 5000
    while True:
        u = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date={date_str}&start={start}&limit={limit}&convertId=2781"
        res = get_json(u, timeout=25)
        batch = res.get("data") or []
        all_rows.extend(batch)
        if len(batch) < limit:
            break
        start += limit
        time.sleep(0.2)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(all_rows, f, ensure_ascii=False)
    print(f"  [OK] cmc_full_{date_str}.json ({len(all_rows)} coins)")
    return all_rows


print("[1] Fetching FULL CMC Historical Snapshots for 2026-11-20 and 2026-11-21...")
fetch_cmc_full_date("2026-11-20")
fetch_cmc_full_date("2026-11-21")

# --- 2. Fetch CMC Official Historical Token Unlocks for ALL 258 coins with tokenUnlockLatest ---
ul_cids = [
    r["cmc_id"] for r in clean500
    if (details[str(r["cmc_id"])].get("tokenUnlockLatest") or {}).get("tokenUnlockedAmount") is not None
]
print(f"\n[2] Fetching CMC v3/token-unlock/historical for {len(ul_cids)} official vesting coins (10 threads)...")

def fetch_ul_hist(cid):
    try:
        res = get_json(f"https://api.coinmarketcap.com/data-api/v3/token-unlock/historical?cryptoId={cid}&range=All", retries=2, timeout=15)
        th = (res.get("data") or {}).get("tokenHistory") or []
        if not th:
            return str(cid), None
        # Aggregate cumulative unlocked amount by date YYYY-MM-DD
        by_date = {}
        for row in th:
            dt = str(row.get("time") or "")[:10]
            if dt:
                by_date[dt] = by_date.get(dt, 0.0) + float(row.get("amount") or 0.0)
        dates = sorted(by_date.keys())
        def val_at(target):
            le = [d for d in dates if d <= target]
            return {"date": le[-1], "unlocked": round(by_date[le[-1]], 4)} if le else {"date": None, "unlocked": 0.0}
        return str(cid), {
            "n_points": len(dates),
            "min_date": dates[0],
            "max_date": dates[-1],
            "at_2026_07_01": val_at("2026-07-01"),
            "at_2026_10_01": val_at("2026-10-01"),
            "at_2026_11_21": val_at("2026-11-21"),
            "at_2026_11_24": val_at("2026-11-24"),
        }
    except Exception:
        return str(cid), None

ul_hist_map = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = [ex.submit(fetch_ul_hist, cid) for cid in ul_cids]
    done = 0
    for fut in as_completed(futs):
        cid_s, val = fut.result()
        done += 1
        if val:
            ul_hist_map[cid_s] = val
        if done % 65 == 0 or done == len(ul_cids):
            print(f"  Unlocks hist [{done}/{len(ul_cids)}] ({time.time()-t0:.1f}s) | ok={len(ul_hist_map)}")

with open(os.path.join(RAW_DIR, "cmc_token_unlock_historical_258.json"), "w", encoding="utf-8") as f:
    json.dump(ul_hist_map, f, indent=2, ensure_ascii=False)

# --- 3. CoinMetrics Community API v4 for ALL matching coins in Clean 500 ---
print("\n[3] Querying CoinMetrics Community API v4 for historical AdrBalCnt / AdrActCnt / SplyCur on T1, T2, T3...")
cm_cat = get_json("https://community-api.coinmetrics.io/v4/catalog/assets", timeout=20).get("data") or []
cm_by_sym = {}
for a in cm_cat:
    sym_l = (a.get("asset") or "").lower()
    mset = {m.get("metric") for m in (a.get("metrics") or [])}
    if "AdrBalCnt" in mset:
        cm_by_sym[sym_l] = mset

# Match Clean 500 coins by symbol (careful: avoid symbol collisions by matching known genuine symbols!)
# For symbols that exist on CoinMetrics Community, match exact lower symbol (and handle known aliases)
cm_matches = []
seen_cm = set()
for r in clean500:
    sl = r["symbol"].lower()
    if sl == "pol" and "matic" in cm_by_sym:
        sl_cm = "matic"
    elif sl in cm_by_sym:
        sl_cm = sl
    else:
        continue
    # Avoid duplicate symbol collision (keep highest-ranked Clean 500 coin)
    if sl_cm in seen_cm:
        continue
    seen_cm.add(sl_cm)
    cm_matches.append((r, sl_cm))

print(f"  Matched {len(cm_matches)} Clean 500 coins on CoinMetrics with historical AdrBalCnt!")
cm_out = {}
# Query in batches of 10 assets cleanly
for i in range(0, len(cm_matches), 10):
    batch = cm_matches[i:i+10]
    assets_str = ",".join(sl_cm for _, sl_cm in batch)
    sl_to_r = {sl_cm: r for r, sl_cm in batch}
    try:
        u = (
            f"https://community-api.coinmetrics.io/v4/timeseries/asset-metrics"
            f"?assets={assets_str}&metrics=AdrBalCnt,AdrActCnt,SplyCur"
            f"&start_time=2026-06-28&end_time=2026-11-22&frequency=1d&page_size=10000"
        )
        res = get_json(u, timeout=20)
        by_a = {}
        for row in (res.get("data") or []):
            a = row["asset"]
            dt = row["time"][:10]
            by_a.setdefault(a, {})[dt] = row
        for sl_cm, r in sl_to_r.items():
            dmap = by_a.get(sl_cm) or {}
            if not dmap:
                continue
            dates = sorted(dmap.keys())
            def pick_cm(target):
                # Prefer exact date, else nearest within +-3 days <= target
                le = [d for d in dates if d <= target]
                if not le:
                    return None
                d_use = le[-1]
                row = dmap[d_use]
                return {
                    "date": d_use,
                    "holders_cnt": int(float(row["AdrBalCnt"])) if row.get("AdrBalCnt") else None,
                    "active_addrs": int(float(row["AdrActCnt"])) if row.get("AdrActCnt") else None,
                    "sply_cur": float(row["SplyCur"]) if row.get("SplyCur") else None,
                }
            cm_out[str(r["cmc_id"])] = {
                "symbol": r["symbol"],
                "cm_asset": sl_cm,
                "jul1": pick_cm("2026-07-01"),
                "oct1": pick_cm("2026-10-01"),
                "nov21": pick_cm("2026-11-21"),
            }
    except Exception as e:
        print(f"  CoinMetrics batch {i} ERR: {e}")
    time.sleep(0.25)

print(f"  CoinMetrics historical holder counts saved: {len(cm_out)} coins!")
with open(os.path.join(RAW_DIR, "coinmetrics_3dates.json"), "w", encoding="utf-8") as f:
    json.dump(cm_out, f, indent=2, ensure_ascii=False)

# --- 4. CoinCarp Historical Holders (his/coin/chainsummary) paced gently for major Native L1s ---
print("\n[4] Querying CoinCarp Historical Holders (paced 0.45s) for major L1s...")
L1_CC = [
    ("BTC", "bitcoin"), ("DOGE", "dogecoin"), ("GRAM", "toncoin"), ("BCH", "bitcoin-cash"),
    ("ZEC", "zcash"), ("BSV", "bitcoin-sv"), ("LTC", "litecoin"), ("ETH", "ethereum"),
    ("BNB", "binance-coin"), ("SOL", "solana"), ("XRP", "ripple"), ("TRX", "tron"),
    ("ADA", "cardano"), ("KAS", "kaspa"), ("ATOM", "cosmos"), ("DASH", "dash"),
    ("DGB", "digibyte"), ("XTZ", "tezos"), ("AVAX", "avalanche"), ("APT", "aptos"),
    ("ICP", "dfinity"), ("ALGO", "algorand"), ("CRO", "crypto-com-chain"), ("XDC", "xinfin"),
    ("CORE", "core-dao"), ("ONT", "ont"), ("IOST", "iost"), ("ORDI", "ordi"),
]
sym_to_cid = {r["symbol"]: str(r["cmc_id"]) for r in clean500}
cc_his_out = {}
for sym, code in L1_CC:
    if sym not in sym_to_cid:
        continue
    time.sleep(0.45)
    try:
        res = get_json(
            f"https://sapi.coincarp.com/api/v1/his/coin/chainsummary?code={code}&type=1y",
            retries=1, timeout=12, headers={"Referer": "https://www.coincarp.com/"}
        )
        arr = res.get("data") or []
        if arr:
            pts = []
            for p in arr:
                dt = datetime.datetime.fromtimestamp(p[0], tz=datetime.timezone.utc).strftime("%Y-%m-%d")
                pts.append({"date": dt, "holders": int(p[1]) if p[1] else None, "top10": float(p[2]), "top20": float(p[3]), "top50": float(p[4]), "top100": float(p[5])})
            def nearest_pt(target, max_days=14):
                t_dt = datetime.date.fromisoformat(target)
                best = None
                best_diff = 9999
                for pt in pts:
                    p_dt = datetime.date.fromisoformat(pt["date"])
                    diff = abs((t_dt - p_dt).days)
                    if diff < best_diff:
                        best_diff = diff
                        best = pt
                return best if (best and best_diff <= max_days) else None
            rec = {
                "symbol": sym, "code": code, "min_date": pts[0]["date"], "max_date": pts[-1]["date"],
                "jul1": nearest_pt("2026-07-01"),
                "oct1": nearest_pt("2026-10-01"),
                "nov21": nearest_pt("2026-11-21"),
            }
            if rec["jul1"] or rec["oct1"] or rec["nov21"]:
                cc_his_out[sym_to_cid[sym]] = rec
                print(f"  [OK] CC-His {sym:5s}: range={pts[0]['date']}..{pts[-1]['date']} | jul1={rec['jul1']['top10'] if rec['jul1'] else None}% oct1={rec['oct1']['top10'] if rec['oct1'] else None}% nov21={rec['nov21']['top10'] if rec['nov21'] else None}%")
    except Exception as e:
        print(f"  [ERR] CC-His {sym:5s}: {str(e)[:60]}")

with open(os.path.join(RAW_DIR, "coincarp_his_l1.json"), "w", encoding="utf-8") as f:
    json.dump(cc_his_out, f, indent=2, ensure_ascii=False)

print(f"\n=== SCRIPT 1 COMPLETE ===")
print(f"  CMC Historical Unlocks: {len(ul_hist_map)} / {len(ul_cids)}")
print(f"  CoinMetrics 3-Date Holders: {len(cm_out)}")
print(f"  CoinCarp Historical L1 Richlists: {len(cc_his_out)}")
