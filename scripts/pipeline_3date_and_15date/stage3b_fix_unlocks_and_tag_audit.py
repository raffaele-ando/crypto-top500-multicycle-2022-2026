#!/usr/bin/env python3
"""
STAGE 3B:
1. Audits live CMC detail tags of all 679 newly appearing historical coins (catching any untagged 2022/2024 stablecoins/wrapped/LST/RWA!).
2. Fetches ALL ~497 official CMC v3/token-unlock/historical?range=All vesting curves across ALL 15 dates (D01..D15) using the verified (time, amount) schema!
"""
import json, ssl, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
RAW = BASE / "raw"

CTX = ssl._create_unverified_context()
HDR = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36", "Accept": "application/json"}

ALL_15_DATES = [
    ("D01", "2022-12-30"), ("D02", "2024-04-09"), ("D03", "2024-09-10"), ("D04", "2024-11-22"),
    ("D05", "2025-01-24"), ("D06", "2025-04-08"), ("D07", "2025-09-19"), ("D08", "2025-10-07"),
    ("D09", "2025-12-26"), ("D10", "2026-01-15"), ("D11", "2026-02-13"), ("D12", "2026-05-12"),
    ("D13", "2026-07-01"), ("D14", "2026-10-01"), ("D15", "2026-11-21"),
]

st2 = json.loads((RAW / "stage2_cohorts_12dates_pre_audit.json").read_text(encoding="utf-8"))
union_cids = [int(x) for x in st2["union_cids"]]
old_details = json.loads((PROJ / "raw" / "cmc_tokenomics_holders_clean500.json").read_text(encoding="utf-8"))
new_details = json.loads((RAW / "new679_cmc_details.json").read_text(encoding="utf-8"))

all_details = {}
all_details.update(old_details)
all_details.update(new_details)

# --- 1. LIVE TAG AUDIT ON ALL 679 NEW HISTORICAL COINS ---
BAD_TAGS = {
    "stablecoin", "usd-stablecoin", "eur-stablecoin", "fiat-stablecoin",
    "algorithmic-stablecoin", "asset-backed-stablecoin", "gbp-stablecoin",
    "wrapped-tokens", "liquid-staking-derivatives", "liquid-restaking-tokens",
    "tokenized-stock", "tokenized-gold", "tokenized-etf", "tokenized-treasury-bills",
    "tokenized-real-estate", "tokenized-commodities", "bittensor-subnets", "synthetic-issuer",
}
print("=== [1] AUDITING LIVE CMC DETAIL TAGS ON 679 NEW HISTORICAL COINS ===")
flagged = []
for scid, d in sorted(new_details.items(), key=lambda kv: int(kv[0])):
    tset = set(d.get("tags") or [])
    hits = sorted(tset & BAD_TAGS)
    if hits:
        flagged.append((int(scid), d.get("symbol"), d.get("name"), hits))
print(f"Flagged {len(flagged)} coins among 673 fetched new details:")
for cid, sym, nm, hits in flagged:
    print(f"  cid={cid:6d} | {str(sym):12s} | {str(nm):34s} | tags={hits}")

# Also count EVM Archive candidates among new_details!
ARCHIVE_CHAINS = {"Ethereum", "Base", "Arbitrum", "Optimism", "Avalanche C-Chain"}
evm_new = 0
for scid, d in new_details.items():
    hl = (d.get("holders") or {}).get("holderList") or []
    plats = {p.get("platform") for p in (d.get("platforms") or []) if (p.get("address") or "").startswith("0x")}
    if hl and str(hl[0].get("address", "")).startswith("0x") and (plats & ARCHIVE_CHAINS):
        evm_new += 1
print(f"New historical coins with 0x holderList on Archive EVM chains: {evm_new}")

# --- 2. FETCH ALL OFFICIAL CMC HISTORICAL VESTING CURVES (ALL 15 DATES!) ---
ul_cids = [
    cid for cid in union_cids
    if (all_details.get(str(cid)) or {}).get("tokenUnlockLatest", {}).get("tokenUnlockedAmount") is not None
]
print(f"\n=== [2] FETCHING OFFICIAL CMC VESTING CURVES FOR {len(ul_cids)} COINS ACROSS ALL 15 DATES ===")

def http_json(url, timeout=16, retries=2):
    for att in range(retries):
        try:
            req = urllib.request.Request(url, headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout, context=CTX) as r:
                return json.loads(r.read().decode("utf-8", errors="replace"))
        except Exception:
            if att == retries - 1:
                return None
            time.sleep(0.5 * (att + 1))

def fetch_ul_hist(cid):
    j = http_json(f"https://api.coinmarketcap.com/data-api/v3/token-unlock/historical?cryptoId={cid}&range=All")
    th = ((j or {}).get("data") or {}).get("tokenHistory") or []
    if not th:
        return str(cid), None
    by_date = {}
    for row in th:
        dt = str(row.get("time") or "")[:10]
        if dt:
            by_date[dt] = by_date.get(dt, 0.0) + float(row.get("amount") or 0.0)
    if not by_date:
        return str(cid), None
    dates = sorted(by_date.keys())
    sampled = {}
    for _, target in ALL_15_DATES:
        le = [d for d in dates if d <= target]
        if le:
            sampled[target] = {"curve_date": le[-1], "unlocked": round(by_date[le[-1]], 4)}
        else:
            sampled[target] = {"curve_date": None, "unlocked": 0.0}
    return str(cid), {
        "n_points": len(dates),
        "min_date": dates[0],
        "max_date": dates[-1],
        "dates": sampled,
    }

ul_map = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = [ex.submit(fetch_ul_hist, cid) for cid in ul_cids]
    done = 0
    for f in as_completed(futs):
        scid, val = f.result()
        done += 1
        if val:
            ul_map[scid] = val
        if done % 100 == 0 or done == len(ul_cids):
            print(f"  unlocks [{done}/{len(ul_cids)}] ok={len(ul_map)} ({time.time()-t0:.1f}s)")

out_p = RAW / "unlock_historical_15dates_all.json"
out_p.write_text(json.dumps(ul_map, ensure_ascii=False), encoding="utf-8")
print(f"Saved {len(ul_map)}/{len(ul_cids)} official 15-date vesting curves -> {out_p}")
# Quick coverage check per date (unlocked > 0)
for code, dt in ALL_15_DATES:
    n_pos = sum(1 for v in ul_map.values() if (v["dates"].get(dt) or {}).get("unlocked", 0) > 0)
    print(f"  {code} {dt}: {n_pos} coins with >0 official unlocked amount on curve")
