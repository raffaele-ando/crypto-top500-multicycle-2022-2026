#!/usr/bin/env python3
"""
Audit ALL vanishing coins across D01..D12 vs D13/D14/D15 full CMC snapshots so we distinguish:
  (A) Official Token Rebrands / Migrations / Mergers (with exact verified swap ratios!)
  (B) True Delistings / Dead Projects / Rug-Pulls (0 EUR / -100% Conservative Survival-Adjusted!)
"""
import json
from pathlib import Path

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
RAW = PROJ / "multidate_15_2022_2026" / "raw"

st2 = json.loads((RAW / "stage2_cohorts_12dates_pre_audit.json").read_text(encoding="utf-8"))
fx_m = json.loads((RAW / "fx_and_snapshots_manifest_12dates.json").read_text(encoding="utf-8"))

def load_snap_any(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        if "data" in raw and isinstance(raw["data"], list):
            arr = raw["data"]
        elif "cryptocurrencies" in raw and isinstance(raw["cryptocurrencies"], list):
            arr = raw["cryptocurrencies"]
        else:
            return {int(k): v for k, v in raw.items() if str(k).isdigit()}
    else:
        arr = raw
    return {int(c["id"]): c for c in arr}

def get_price(c):
    if c.get("price") is not None:
        return float(c["price"])
    qs = c.get("quotes")
    if isinstance(qs, list) and qs:
        return float(qs[0].get("price") or 0)
    if isinstance(qs, dict):
        q = qs.get("USD") or qs.get("2781") or next(iter(qs.values()), {})
        return float(q.get("price") or 0)
    return 0.0

snap13 = load_snap_any(PROJ / "raw" / "cmc_full_2026-07-01.json")
snap14 = load_snap_any(PROJ / "raw" / "cmc_full_2026-10-01.json")
snap15 = load_snap_any(PROJ / "raw" / "cmc_full_2026-11-21.json")

# Also map every coin in all 12 dates -> best rank ever achieved + metadata + last date seen!
all_snaps = {}
for dt in fx_m.keys():
    all_snaps[dt] = {int(c["id"]): c for c in json.loads((RAW / f"cmc_snap_{dt}.json").read_text(encoding="utf-8"))["data"]}
all_snaps["2026-07-01"] = snap13
all_snaps["2026-10-01"] = snap14
all_snaps["2026-11-21"] = snap15

missing_at_d15 = {}
for dt, cids in st2["cohort_ids_by_date"].items():
    for rk, cid in enumerate(cids, 1):
        if cid not in snap15 or get_price(snap15[cid]) <= 0:
            c = all_snaps[dt][cid]
            rec = missing_at_d15.get(cid)
            if not rec or rk < rec["best_rk"]:
                missing_at_d15[cid] = {
                    "cid": cid, "sym": c["symbol"], "name": c["name"],
                    "best_rk": rk, "best_dt": dt, "mcap_m": round(float(c["marketCap"]) / 1e6, 1),
                    "in_d13": cid in snap13, "in_d14": cid in snap14, "in_d15": cid in snap15,
                }

print(f"Total unique pure cohort coins absent/zero-price in D15 (2026-11-21) full snapshot: {len(missing_at_d15)}")
top_vanished = sorted(missing_at_d15.values(), key=lambda x: x["best_rk"])
print("\nTOP 70 VANISHED COINS BY BEST CLEAN RANK (to identify official migrations/rebrands!):")
for v in top_vanished[:70]:
    # find last snapshot where it appeared
    last_dt = max((d for d, s in all_snaps.items() if v["cid"] in s), default="?")
    print(f"  Best#{v['best_rk']:03d} ({v['best_dt']}) | cid={v['cid']:5d} | {v['sym']:12s} | {v['name'][:30]:30s} | MCap=${v['mcap_m']:7.1f}M | last_seen={last_dt}")

# Also inspect D15 coins with matching symbols/names for quick migration ID lookup!
sym_d15 = {}
for cid, c in snap15.items():
    sym_d15.setdefault(str(c.get("symbol") or "").upper(), []).append((cid, c.get("name"), c.get("cmcRank")))
print("\nKEY TARGET MIGRATION IDS IN D15 (2026-11-21):")
for s in ["POL", "S", "SKY", "A", "KAIA", "FET", "SATS", "BABYDOGE", "G", "BEAM", "VANRY", "PDA", "LUMIA", "HEI", "SLF", "D", "SYNT", "RENDER", "OMNI", "BMT", "XCN", "AI16Z", "ELIZAOS", "ZETA", "BICO", "FORM", "FOUR", "A47", "UXLINK", "BERA", "NFP", "USUAL", "PNUT", "ACT"]:
    if s in sym_d15:
        print(f"  {s:10s} -> {sorted(sym_d15[s], key=lambda x: x[2] or 99999)[:3]}")
