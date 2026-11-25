#!/usr/bin/env python3
"""
Fetches exact intraday Price, Volume, and Market Capitalization at
2026-11-21 05:30:00 CET (2026-11-21 04:30:00 UTC, unix=1795235400)
for ALL 682 unique cryptocurrencies across Original Top 500 and Clean Pure Top 500,
plus exact EUR/USD FX rate and Binance 1m kline verification at 04:30:00 UTC.
"""

import datetime
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")

TS_TARGET = 1795235400  # 2026-11-21 04:30:00 UTC = 2026-11-21 05:30:00 CET (+01:00)
TS_START = TS_TARGET - 1800  # 04:00 UTC
TS_END = TS_TARGET + 1800    # 05:00 UTC


def fetch_json(url, retries=4, timeout=20):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    raise last_err


def extract_closest_point(pts, target_ts=TS_TARGET):
    valid = []
    for k, val in (pts or {}).items():
        if not str(k).isdigit():
            continue
        if isinstance(val, dict):
            arr = val.get("v") or val.get("c")
            if isinstance(arr, list) and len(arr) >= 3 and arr[0] is not None:
                valid.append((abs(int(k) - target_ts), int(k), float(arr[0]), float(arr[1] or 0.0), float(arr[2] or 0.0)))
    if not valid:
        return None
    valid.sort(key=lambda x: x[0])
    diff_s, ts_actual, price, vol, mcap = valid[0]
    return {
        "ts_actual": ts_actual,
        "ts_utc": datetime.datetime.fromtimestamp(ts_actual, tz=datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "offset_sec": ts_actual - target_ts,
        "price_usd": price,
        "volume24h_usd": vol,
        "marketCap_usd": mcap,
    }


def fetch_coin_nov21(cid):
    url = f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={cid}&range={TS_START}~{TS_END}"
    try:
        d = fetch_json(url)
        pts = d.get("data", {}).get("points", {})
        pt = extract_closest_point(pts, TS_TARGET)
        if pt is not None:
            return cid, pt
        # Fallback wider window ±6 hours in case of sparser polling on small caps
        d2 = fetch_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id={cid}&range={TS_TARGET-21600}~{TS_TARGET+21600}")
        pt2 = extract_closest_point(d2.get("data", {}).get("points", {}), TS_TARGET)
        if pt2 is not None:
            pt2["wider_window"] = True
            return cid, pt2
        return cid, None
    except Exception as e:
        return cid, {"error": str(e)}


def main():
    with open(os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
        orig500 = json.load(f)["cryptocurrencies"]
    with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
        clean500 = json.load(f)["cryptocurrencies"]

    all_ids = sorted({r["cmc_id"] for r in orig500} | {r["cmc_id"] for r in clean500})
    print(f"Total unique coins across Original 500 U Clean 500: {len(all_ids)}")

    # 1. Exact EUR/USD FX at 2026-11-21 04:30:00 UTC (05:30:00 CET)
    btc_usd_d = fetch_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=1&range={TS_START}~{TS_END}&convertId=2781")
    btc_eur_d = fetch_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/detail/chart?id=1&range={TS_START}~{TS_END}&convertId=2790")
    p_btc_usd = extract_closest_point(btc_usd_d["data"]["points"])
    p_btc_eur = extract_closest_point(btc_eur_d["data"]["points"])
    fx_cmc_nov21 = p_btc_usd["price_usd"] / p_btc_eur["price_usd"]

    kb_eur = fetch_json(f"https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1m&startTime={TS_TARGET*1000}&endTime={TS_TARGET*1000}")
    fx_bin_nov21 = float(kb_eur[0][4]) if kb_eur else None

    ecb_nov20 = fetch_json("https://api.frankfurter.app/2026-11-21?from=EUR&to=USD")  # Saturday -> Friday ECB close
    print(f"EUR/USD at 2026-11-21 05:30 CET (04:30 UTC):")
    print(f"  CMC Official convertId=2790: {fx_cmc_nov21:.6f}")
    print(f"  Binance EURUSDT 1m close:    {fx_bin_nov21}")
    print(f"  ECB Frankfurter ({ecb_nov20['date']}):  {ecb_nov20['rates']['USD']}")

    # 2. Fetch all 682 coins concurrently (14 workers — fast & respectful)
    results = {}
    errors = []
    missing = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=14) as ex:
        futs = {ex.submit(fetch_coin_nov21, cid): cid for cid in all_ids}
        done = 0
        for fut in as_completed(futs):
            cid, pt = fut.result()
            done += 1
            if pt is None:
                missing.append(cid)
            elif "error" in pt:
                errors.append((cid, pt["error"]))
            else:
                results[str(cid)] = pt
            if done % 150 == 0 or done == len(all_ids):
                print(f"  Progress: {done}/{len(all_ids)} ({time.time()-t0:.1f}s) | ok={len(results)} missing={len(missing)} err={len(errors)}")

    # 3. Cross-verify top 20 Binance pairs at exact 2026-11-21 04:30:00 UTC 1m kline!
    bin_check = []
    for cid, sym in [(1, "BTC"), (1027, "ETH"), (1839, "BNB"), (5426, "SOL"), (52, "XRP"), (74, "DOGE"), (2010, "ADA"), (1958, "TRX"), (5805, "AVAX"), (1975, "LINK"), (7083, "UNI"), (1437, "ZEC"), (30171, "ENA"), (6535, "NEAR"), (24478, "PEPE")]:
        try:
            k = fetch_json(f"https://api.binance.com/api/v3/klines?symbol={sym}USDT&interval=1m&startTime={TS_TARGET*1000}&endTime={TS_TARGET*1000}")
            if k and str(cid) in results:
                bp = float(k[0][1])  # Open of 04:30:00 UTC minute = exact 04:30:00 UTC!
                cp = results[str(cid)]["price_usd"]
                diff_pct = abs(bp - cp) / cp * 100.0
                bin_check.append({"symbol": sym, "cmc": cp, "binance_0430_open": bp, "diff_pct": round(diff_pct, 4)})
        except Exception:
            pass

    med_bin = sorted(x["diff_pct"] for x in bin_check)[len(bin_check)//2] if bin_check else 0
    print(f"\nBinance 1m exact 2026-11-21 04:30:00 UTC verification ({len(bin_check)} pairs): median diff = {med_bin:.4f}%")
    for x in bin_check[:8]:
        print(f"  {x['symbol']:6s}: CMC=${x['cmc']:.6g} vs Binance_0430=${x['binance_0430_open']:.6g} (diff={x['diff_pct']:.4f}%)")

    # Inspect exact offset distribution
    exact_0s = sum(1 for v in results.values() if v["offset_sec"] == 0)
    within_5m = sum(1 for v in results.values() if abs(v["offset_sec"]) <= 300)
    print(f"\nTimestamp precision: exact 04:30:00 UTC (0s offset) = {exact_0s}/{len(results)} | within ±5 min = {within_5m}/{len(results)}")
    print(f"Missing ({len(missing)}): {missing}")
    print(f"Errors ({len(errors)}): {errors}")

    out_path = os.path.join(RAW_DIR, "cmc_nov21_0530cet_all682.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({
            "target_local": "2026-11-21T05:30:00+01:00",
            "target_utc": "2026-11-21T04:30:00Z",
            "target_unix": TS_TARGET,
            "fx_eur_usd_cmc": round(fx_cmc_nov21, 6),
            "fx_eur_usd_binance": fx_bin_nov21,
            "fx_eur_usd_ecb_prev_close": ecb_nov20["rates"]["USD"],
            "binance_verification": bin_check,
            "missing_ids": missing,
            "errors": errors,
            "coins": results,
        }, f, indent=2)
    print(f"Saved {out_path}")


if __name__ == "__main__":
    main()
