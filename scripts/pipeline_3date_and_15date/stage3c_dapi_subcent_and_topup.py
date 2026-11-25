#!/usr/bin/env python3
"""
STAGE 3C:
1. Top-up CMC detail + 15-date official vesting unlocks for any newly promoted replacement coins.
2. Fetch CMC dapi (crypto-holder-data + total-holder-historical?range=1y) with exact Origin/Referer & p['date'] schema
   for ALL 680 new historical coins + 310 verified-primary Jul 1 coins (covers D09..D15!).
3. Fetch exact sub-cent (< $0.0001) daily open prices at YYYY-MM-DD 00:00:00 UTC across ALL 12 new dates via v3.1 historical.
"""
import datetime, json, ssl, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
RAW = BASE / "raw"

CTX = ssl._create_unverified_context()
HDR = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Origin": "https://coinmarketcap.com",
    "Referer": "https://coinmarketcap.com/",
}

ALL_15_DATES = [
    ("D01", "2022-12-30"), ("D02", "2024-04-09"), ("D03", "2024-09-10"), ("D04", "2024-11-22"),
    ("D05", "2025-01-24"), ("D06", "2025-04-08"), ("D07", "2025-09-19"), ("D08", "2025-10-07"),
    ("D09", "2025-12-26"), ("D10", "2026-01-15"), ("D11", "2026-02-13"), ("D12", "2026-05-12"),
    ("D13", "2026-07-01"), ("D14", "2026-10-01"), ("D15", "2026-11-21"),
]
NEW_12_DATES = [d for _, d in ALL_15_DATES[:12]]

st2 = json.loads((RAW / "stage2_cohorts_12dates_pre_audit.json").read_text(encoding="utf-8"))
union_cids = [int(x) for x in st2["union_cids"]]
new_cids = [int(x) for x in st2["new_cids_vs_jul1"]]
old_details = json.loads((PROJ / "raw" / "cmc_tokenomics_holders_clean500.json").read_text(encoding="utf-8"))
det_path = RAW / "new679_cmc_details.json"
new_details = json.loads(det_path.read_text(encoding="utf-8"))
ul_path = RAW / "unlock_historical_15dates_all.json"
ul_map = json.loads(ul_path.read_text(encoding="utf-8"))
old_dapi_primary = json.loads((PROJ / "raw" / "holders_hunter_master_consolidated.json").read_text(encoding="utf-8")).get("dapi_verified_primary") or {}

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

# --- 1. TOP-UP ANY MISSING DETAILS + UNLOCKS FOR NEWLY PROMOTED COINS ---
missing_det_cids = [cid for cid in new_cids if str(cid) not in new_details]
print(f"=== [1/3] TOP-UP DETAIL & UNLOCKS FOR {len(missing_det_cids)} MISSING/PROMOTED COINS ===")
added_det = 0
for cid in missing_det_cids:
    j = http_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail?id={cid}")
    d = (j or {}).get("data")
    if not d:
        continue
    h = d.get("holders") or {}
    hl = h.get("holderList") or []
    new_details[str(cid)] = {
        "id": cid, "name": d.get("name"), "symbol": d.get("symbol"), "slug": d.get("slug"),
        "category": d.get("category"), "isInfiniteMaxSupply": d.get("isInfiniteMaxSupply"),
        "tags": [t.get("slug") if isinstance(t, dict) else t for t in (d.get("tags") or [])],
        "statistics": d.get("statistics") or {},
        "tokenUnlockLatest": d.get("tokenUnlockLatest") or {},
        "platforms": [{"platform": p.get("contractPlatform"), "chainId": p.get("contractChainId"), "address": p.get("contractAddress")} for p in (d.get("platforms") or [])],
        "holders": {
            "holderCount": h.get("holderCount"), "topTenHolderRatio": h.get("topTenHolderRatio"),
            "topTwentyHolderRatio": h.get("topTwentyHolderRatio"), "topFiftyHolderRatio": h.get("topFiftyHolderRatio"),
            "topHundredHolderRatio": h.get("topHundredHolderRatio"),
            "holderList": [{"address": w.get("address"), "balance": w.get("balance"), "share": w.get("share")} for w in hl[:30]],
        } if h else {},
    }
    added_det += 1
    if (d.get("tokenUnlockLatest") or {}).get("tokenUnlockedAmount") is not None and str(cid) not in ul_map:
        ju = http_json(f"https://api.coinmarketcap.com/data-api/v3/token-unlock/historical?cryptoId={cid}&range=All")
        th = ((ju or {}).get("data") or {}).get("tokenHistory") or []
        by_date = {}
        for row in th:
            dt = str(row.get("time") or "")[:10]
            if dt:
                by_date[dt] = by_date.get(dt, 0.0) + float(row.get("amount") or 0.0)
        if by_date:
            dates = sorted(by_date.keys())
            sampled = {}
            for _, target in ALL_15_DATES:
                le = [x for x in dates if x <= target]
                sampled[target] = {"curve_date": le[-1], "unlocked": round(by_date[le[-1]], 4)} if le else {"curve_date": None, "unlocked": 0.0}
            ul_map[str(cid)] = {"n_points": len(dates), "min_date": dates[0], "max_date": dates[-1], "dates": sampled}
if added_det:
    det_path.write_text(json.dumps(new_details, ensure_ascii=False), encoding="utf-8")
    ul_path.write_text(json.dumps(ul_map, ensure_ascii=False), encoding="utf-8")
print(f"  Added {added_det} promoted details (total new_details={len(new_details)}, total unlocks={len(ul_map)})")

all_details = {}
all_details.update(old_details)
all_details.update(new_details)

# --- 2. FETCH CMC DAPI HOLDERS & 1Y HISTORICAL COUNTS (EXACT SCHEMA!) ---
new_set = set(new_cids)
dapi_targets = sorted(new_set | {int(k) for k in old_dapi_primary.keys()})
print(f"\n=== [2/3] FETCHING CMC DAPI HOLDERS & 1Y HIST COUNTS FOR {len(dapi_targets)} COINS ===")

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
                best = {"date": d_obj.isoformat(), "holders_cnt": int(float(p["holderCount"]))}
        except Exception:
            pass
    return best if (best and best_diff <= max_days) else None

def fetch_dapi_one(cid):
    scid = str(cid)
    out = {"cmc_id": cid}
    if cid in new_set:
        j1 = http_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/crypto-holder-data?cryptoId={cid}", timeout=14)
        hd = (j1 or {}).get("data") if isinstance((j1 or {}).get("data"), dict) else {}
        hl = hd.get("holders") or []
        if hl:
            tot_bal = sum(float(w.get("balance") or 0) for w in hl)
            st = (all_details.get(scid) or {}).get("statistics") or {}
            tot_sup = float(st.get("totalSupply") or st.get("circulatingSupply") or 0)
            ratio = (tot_bal / tot_sup) if (tot_sup > 0 and tot_bal > 0) else None
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
            out["fgp"] = round(float(hd.get("fgp") or t10), 4)
            out["top10_pct"] = t10
            out["others"] = round(float(hd.get("others") or (100.0 - t10)), 4)
            out["supply_ratio"] = round(ratio, 4) if ratio is not None else None
            out["explorer"] = wallets[0]["explorer"] if wallets else ""
            out["wallets"] = wallets[:30]
    else:
        out["supply_ratio"] = 1.0

    # Historical holder counts (1y covers D09..D15!)
    j2 = http_json(f"https://dapi.coinmarketcap.com/dex-stats/v3/dexer/cdp-holder/total-holder-historical?cryptoId={cid}&range=1y", timeout=14)
    pts = []
    if j2 and isinstance(j2.get("data"), dict):
        pts = j2["data"].get("points") or []
    elif j2 and isinstance(j2.get("data"), list):
        pts = j2["data"]
    pts_clean = [p for p in pts if p.get("date") and p.get("holderCount") is not None]
    if pts_clean:
        pts_clean.sort(key=lambda p: int(p["date"]))
        matched = {}
        for _, dt in ALL_15_DATES:
            pt = pick_hist_point(pts_clean, dt, max_days=14)
            if pt:
                matched[dt] = pt
        out["hist_counts"] = matched
        out["latest_count"] = int(float(pts_clean[-1]["holderCount"]))
        out["min_date"] = datetime.datetime.fromtimestamp(int(pts_clean[0]["date"]) / 1000.0, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
        out["max_date"] = datetime.datetime.fromtimestamp(int(pts_clean[-1]["date"]) / 1000.0, tz=datetime.timezone.utc).strftime("%Y-%m-%d")
    return scid, out

dapi_out = {}
t0 = time.time()
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = [ex.submit(fetch_dapi_one, cid) for cid in dapi_targets]
    done = 0
    for f in as_completed(futs):
        scid, val = f.result()
        dapi_out[scid] = val
        done += 1
        if done % 200 == 0 or done == len(dapi_targets):
            n_hc = sum(1 for v in dapi_out.values() if v.get("hist_counts"))
            n_t10 = sum(1 for v in dapi_out.values() if v.get("top10_pct") is not None)
            print(f"  dapi [{done}/{len(dapi_targets)}] hist_counts={n_hc} | new_top10={n_t10} ({time.time()-t0:.1f}s)")

dapi_path = RAW / "dapi_holders_15dates_union.json"
dapi_path.write_text(json.dumps(dapi_out, ensure_ascii=False), encoding="utf-8")
for code, dt in ALL_15_DATES[8:]:
    cnt = sum(1 for v in dapi_out.values() if dt in (v.get("hist_counts") or {}))
    print(f"  DAPI {code} {dt}: {cnt} coins with historical holderCount")

# --- 3. SUB-CENT (< $0.0001) EXACT PRECISION FIX ACROSS ALL 12 NEW DATES ---
print("\n=== [3/3] SUB-CENT (< $0.0001) EXACT PRECISION FIX ACROSS 12 DATES ===")
sub_cids = set()
union_set = set(union_cids)
for dt in NEW_12_DATES:
    snap = json.loads((RAW / f"cmc_snap_{dt}.json").read_text(encoding="utf-8"))["data"]
    for c in snap:
        cid = int(c["id"])
        p = float(c.get("price") or 0)
        if cid in union_set and 0 < p < 0.0001:
            sub_cids.add(cid)

print(f"  Found {len(sub_cids)} unique sub-cent (<$0.0001) coins across 12 dates -> fetching exact v3.1 full-span daily quotes...")
ts_start = int(datetime.datetime(2022, 12, 28, tzinfo=datetime.timezone.utc).timestamp())
ts_end = int(datetime.datetime(2026, 5, 14, tzinfo=datetime.timezone.utc).timestamp())

def fetch_subcent_one(cid):
    u = f"https://api.coinmarketcap.com/data-api/v3.1/cryptocurrency/historical?id={cid}&convertId=2781&timeStart={ts_start}&timeEnd={ts_end}&interval=1d"
    j = http_json(u, timeout=20)
    qs = ((j or {}).get("data") or {}).get("quotes") or []
    by_open = {}
    by_close = {}
    for q in qs:
        t_o = str(q.get("timeOpen") or "")[:10]
        t_c = str(q.get("timeClose") or "")[:10]
        qo = q.get("quote") or {}
        if t_o and qo.get("open"):
            by_open[t_o] = float(qo["open"])
        if t_c and qo.get("close"):
            by_close[t_c] = float(qo["close"])
    matched = {}
    for dt in NEW_12_DATES:
        if dt in by_open:
            matched[dt] = by_open[dt]
        else:
            prev_d = (datetime.date.fromisoformat(dt) - datetime.timedelta(days=1)).isoformat()
            if prev_d in by_close:
                matched[dt] = by_close[prev_d]
    return str(cid), matched

sub_out = {}
with ThreadPoolExecutor(max_workers=14) as ex:
    futs = [ex.submit(fetch_subcent_one, cid) for cid in sorted(sub_cids)]
    for f in as_completed(futs):
        scid, val = f.result()
        if val:
            sub_out[scid] = val

sub_path = RAW / "subcent_exact_12dates.json"
sub_path.write_text(json.dumps(sub_out, indent=2), encoding="utf-8")
print(f"  Saved exact sub-cent quotes for {len(sub_out)}/{len(sub_cids)} coins -> {sub_path}")
print("\n=== STAGE 3C COMPLETE! ===")
