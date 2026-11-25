#!/usr/bin/env python3
"""
Fetches full CoinMarketCap detail (supply, circulating/unlocked/locked/max supply,
tokenUnlockLatest vesting data, on-chain holders & Top 10/20/50/100 concentration,
and smart-contract platforms) for ALL 500 Clean Pure Cryptocurrencies.
"""

import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")


def fetch_detail(cid, retries=4):
    url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail?id={cid}"
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=20) as r:
                d = json.loads(r.read().decode("utf-8"))["data"]
                return cid, {
                    "id": cid,
                    "name": d.get("name"),
                    "symbol": d.get("symbol"),
                    "slug": d.get("slug"),
                    "category": d.get("category"),
                    "isInfiniteMaxSupply": d.get("isInfiniteMaxSupply"),
                    "cdpTotalHolder": d.get("cdpTotalHolder"),
                    "statistics": d.get("statistics") or {},
                    "supplyDetails": d.get("supplyDetails") or {},
                    "tokenUnlockLatest": d.get("tokenUnlockLatest") or {},
                    "holders": d.get("holders") or {},
                    "platforms": [
                        {
                            "platform": p.get("contractPlatform"),
                            "chainId": p.get("contractChainId"),
                            "address": p.get("contractAddress"),
                        }
                        for p in (d.get("platforms") or [])
                    ],
                }
        except Exception as e:
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    return cid, {"error": str(last_err)}


def main():
    with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
        clean500 = json.load(f)["cryptocurrencies"]

    cids = [r["cmc_id"] for r in clean500]
    t0 = time.time()
    out = {}
    errs = []

    with ThreadPoolExecutor(max_workers=14) as ex:
        futs = {ex.submit(fetch_detail, cid): cid for cid in cids}
        done = 0
        for fut in as_completed(futs):
            cid, res = fut.result()
            done += 1
            if "error" in res:
                errs.append((cid, res["error"]))
            else:
                out[str(cid)] = res
            if done % 100 == 0 or done == len(cids):
                print(f"  Progress: {done}/{len(cids)} ({time.time()-t0:.1f}s) | ok={len(out)} err={len(errs)}")

    # Compute exact coverage stats
    has_unlock_obj = sum(1 for v in out.values() if v.get("tokenUnlockLatest"))
    has_top10 = sum(1 for v in out.values() if (v.get("holders") or {}).get("topTenHolderRatio") is not None)
    has_holder_cnt = sum(1 for v in out.values() if (v.get("holders") or {}).get("holderCount"))
    missing_holders_with_plat = sum(
        1 for v in out.values()
        if (v.get("holders") or {}).get("topTenHolderRatio") is None and len(v.get("platforms") or []) > 0
    )
    missing_holders_native_l1 = sum(
        1 for v in out.values()
        if (v.get("holders") or {}).get("topTenHolderRatio") is None and len(v.get("platforms") or []) == 0
    )

    print(f"\n=== CMC DETAIL COVERAGE ACROSS 500 CLEAN PURE CRYPTOS ===")
    print(f"  Fetched OK:                      {len(out)} / 500 (errors={len(errs)})")
    print(f"  With official tokenUnlockLatest: {has_unlock_obj} / 500 (others use circulating/total/maxSupply)")
    print(f"  With CMC Top10/20/50/100 ratios: {has_top10} / 500 (holderCount: {has_holder_cnt})")
    print(f"  Missing CMC holders WITH EVM/SOL contract (recoverable via GoPlus/RugCheck!): {missing_holders_with_plat}")
    print(f"  Missing CMC holders NATIVE L1 (no contract; recoverable via explorers/BitInfoCharts): {missing_holders_native_l1}")

    out_path = os.path.join(RAW_DIR, "cmc_tokenomics_holders_clean500.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
