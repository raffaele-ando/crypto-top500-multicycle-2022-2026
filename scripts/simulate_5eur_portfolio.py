#!/usr/bin/env python3
"""
Exact Backtest Simulation: €5 invested in each of the 500 Clean Pure Cryptocurrencies
from 1 July 2026 (23:59:59 UTC) to 1 October 2026 (23:59:59 UTC).
Cross-verifies EUR/USD exchange rate across CMC (convertId=2790), ECB/Frankfurter, Binance EURUSDT, and EURC.
"""

import csv
import datetime
import json
import os
import statistics
import urllib.request

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


# 1. Fetch exact EUR/USD on 2026-07-01 and 2026-10-01 from 4 independent sources!
print("=== 1. EUR/USD HISTORICAL FX RATE CROSS-VERIFICATION ===")

# Source A: CMC implied EUR/USD from BTC in USD (2781) vs EUR (2790) at exact snapshot timestamp!
cmc_btc_j = fetch_json("https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date=2026-07-01&start=1&limit=1&convertId=2781,2790")["data"][0]["quotes"]
cmc_btc_o = fetch_json("https://api.coinmarketcap.com/data-api/v3/cryptocurrency/listings/historical?date=2026-10-01&start=1&limit=1&convertId=2781,2790")["data"][0]["quotes"]
q_j = {q["name"]: q["price"] for q in cmc_btc_j}
q_o = {q["name"]: q["price"] for q in cmc_btc_o}
fx_cmc_jul = q_j["2781"] / q_j["2790"]
fx_cmc_oct = q_o["2781"] / q_o["2790"]
print(f"CMC Official Snapshot FX (EUR/USD): Jul 1 = {fx_cmc_jul:.6f} | Oct 1 = {fx_cmc_oct:.6f} (EUR vs USD: {(fx_cmc_oct/fx_cmc_jul - 1)*100:+.4f}%)")

# Source B: ECB / Frankfurter API
try:
    ecb_j = fetch_json("https://api.frankfurter.app/2026-07-01?from=EUR&to=USD")
    ecb_o = fetch_json("https://api.frankfurter.app/2026-10-01?from=EUR&to=USD")
    print(f"ECB Frankfurter FX (EUR/USD):       Jul 1 ({ecb_j['date']}) = {ecb_j['rates']['USD']:.6f} | Oct 1 ({ecb_o['date']}) = {ecb_o['rates']['USD']:.6f}")
except Exception as e:
    print("ECB Frankfurter err:", e)

# Source C: Binance EURUSDT 1d close
try:
    ts_j = int(datetime.datetime(2026, 7, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    ts_o = int(datetime.datetime(2026, 10, 1, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    bj = float(fetch_json(f"https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1d&startTime={ts_j}&endTime={ts_j}")[0][4])
    bo = float(fetch_json(f"https://api.binance.com/api/v3/klines?symbol=EURUSDT&interval=1d&startTime={ts_o}&endTime={ts_o}")[0][4])
    print(f"Binance EURUSDT 1d Close:           Jul 1 = {bj:.6f} | Oct 1 = {bo:.6f}")
except Exception as e:
    print("Binance EURUSDT err:", e)

# Source D: EURC in our raw snapshots
with open(os.path.join(RAW_DIR, "cmc_full_2026-07-01.json"), encoding="utf-8") as f:
    eurc_j = [r["quotes"][0]["price"] for r in json.load(f)["data"] if r["id"] == 20641][0]
with open(os.path.join(RAW_DIR, "cmc_full_2026-10-01.json"), encoding="utf-8") as f:
    eurc_o = [r["quotes"][0]["price"] for r in json.load(f)["data"] if r["id"] == 20641][0]
print(f"CMC EURC Stablecoin (ID=20641):     Jul 1 = {eurc_j:.6f} | Oct 1 = {eurc_o:.6f}")

# 2. Load Clean 500 dataset and simulate €5.00 per cryptocurrency!
with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
    rows = json.load(f)["cryptocurrencies"]

assert len(rows) == 500
STAKE_EUR = 5.0
TOTAL_INVESTED_EUR = STAKE_EUR * len(rows)  # €2,500.00
STAKE_USD_JUL = STAKE_EUR * fx_cmc_jul
TOTAL_INVESTED_USD = STAKE_USD_JUL * len(rows)
FX_FACTOR_EUR = fx_cmc_jul / fx_cmc_oct  # USD return multiplied by EURUSD_jul / EURUSD_oct = EUR return!

sim_rows = []
for r in rows:
    pj = r["price_jul1_usd"]
    po = r["price_oct1_usd"]
    qty = STAKE_USD_JUL / pj

    # Conservative: UNTRACKED ISIKC = 0
    if po is not None:
        mult_usd = po / pj
        val_const_fx_eur = STAKE_EUR * mult_usd
        val_real_eur = val_const_fx_eur * FX_FACTOR_EUR
        val_usd = STAKE_USD_JUL * mult_usd
        val_real_eur_lastprice = val_real_eur
        val_const_fx_lastprice = val_const_fx_eur
    else:
        # ISIKC (cmc-5468): last price on 2026-09-28 was $0.2309414359
        val_const_fx_eur = 0.0
        val_real_eur = 0.0
        val_usd = 0.0
        mult_last = 0.2309414359 / pj if r["cmc_id"] == 5468 else 0.0
        val_const_fx_lastprice = STAKE_EUR * mult_last
        val_real_eur_lastprice = val_const_fx_lastprice * FX_FACTOR_EUR

    sim_rows.append({
        "rank_clean_jul1": r["rank_clean_jul1"],
        "forensic_id": r["forensic_id"],
        "name": r["name"],
        "symbol": r["symbol"],
        "status_oct1": r["status_oct1"],
        "price_jul1_usd": pj,
        "price_oct1_usd": po,
        "invested_eur": STAKE_EUR,
        "qty_bought": qty,
        "value_oct1_eur_real_fx": round(val_real_eur, 4),
        "pnl_eur_real_fx": round(val_real_eur - STAKE_EUR, 4),
        "return_pct_eur_real_fx": round((val_real_eur / STAKE_EUR - 1) * 100.0, 4),
        "value_oct1_eur_const_fx": round(val_const_fx_eur, 4),
        "pnl_eur_const_fx": round(val_const_fx_eur - STAKE_EUR, 4),
        "return_pct_usd": round((val_const_fx_eur / STAKE_EUR - 1) * 100.0, 4),
        "value_oct1_eur_real_fx_lastprice": round(val_real_eur_lastprice, 4),
        "value_oct1_eur_const_fx_lastprice": round(val_const_fx_lastprice, 4),
        "val_real_raw": val_real_eur,
        "val_const_raw": val_const_fx_eur,
        "val_real_lp_raw": val_real_eur_lastprice,
        "val_const_lp_raw": val_const_fx_lastprice,
    })

# Totals (computed from unrounded raw floats for exact precision!)
tot_real_cons = sum(x["val_real_raw"] for x in sim_rows)
tot_const_cons = sum(x["val_const_raw"] for x in sim_rows)
tot_real_lp = sum(x["val_real_lp_raw"] for x in sim_rows)
tot_const_lp = sum(x["val_const_lp_raw"] for x in sim_rows)

# Without single mega-outlier Bitway (BTW, cmc-39158)
tot_real_no_btw = sum(x["val_real_raw"] for x in sim_rows if x["forensic_id"] != "cmc-39158")
tot_const_no_btw = sum(x["val_const_raw"] for x in sim_rows if x["forensic_id"] != "cmc-39158")

# Winners / losers in EUR (real FX) and USD (const FX)
win_real = sum(1 for x in sim_rows if x["val_real_raw"] > STAKE_EUR)
lose_real = sum(1 for x in sim_rows if x["val_real_raw"] < STAKE_EUR)
win_const = sum(1 for x in sim_rows if x["val_const_raw"] > STAKE_EUR)
lose_const = sum(1 for x in sim_rows if x["val_const_raw"] < STAKE_EUR)

# Distribution stats
vals_real = sorted(x["val_real_raw"] for x in sim_rows)
vals_const = sorted(x["val_const_raw"] for x in sim_rows)
med_real = statistics.median(vals_real)
med_const = statistics.median(vals_const)

# Rank tier breakdown (#1-10, #11-50, #51-100, #101-250, #251-500)
tiers = [(1, 10), (11, 50), (51, 100), (101, 250), (251, 500)]
tier_stats = []
for lo, hi in tiers:
    sub = [x for x in sim_rows if lo <= x["rank_clean_jul1"] <= hi]
    inv = STAKE_EUR * len(sub)
    v_r = sum(x["val_real_raw"] for x in sub)
    v_c = sum(x["val_const_raw"] for x in sub)
    tier_stats.append({
        "tier": f"#{lo:03d}-#{hi:03d}",
        "count": len(sub),
        "invested_eur": inv,
        "final_eur_real_fx": round(v_r, 2),
        "pnl_eur_real_fx": round(v_r - inv, 2),
        "pct_eur_real_fx": round((v_r / inv - 1) * 100, 2),
        "final_eur_const_fx": round(v_c, 2),
        "pnl_eur_const_fx": round(v_c - inv, 2),
        "pct_usd": round((v_c / inv - 1) * 100, 2),
    })

# Benchmarks: putting all €2,500 in BTC, ETH, SOL
by_sym = {x["symbol"]: x for x in sim_rows}
benchmarks = {}
for s in ["BTC", "ETH", "SOL", "BNB", "XRP"]:
    x = by_sym[s]
    mult_c = x["val_const_raw"] / STAKE_EUR
    mult_r = x["val_real_raw"] / STAKE_EUR
    benchmarks[s] = {
        "final_eur_real_fx": round(TOTAL_INVESTED_EUR * mult_r, 2),
        "pnl_eur_real_fx": round(TOTAL_INVESTED_EUR * (mult_r - 1), 2),
        "pct_eur_real_fx": round((mult_r - 1) * 100, 2),
        "final_eur_const_fx": round(TOTAL_INVESTED_EUR * mult_c, 2),
        "pnl_eur_const_fx": round(TOTAL_INVESTED_EUR * (mult_c - 1), 2),
        "pct_usd": round((mult_c - 1) * 100, 2),
    }

# Top 10 best & worst €5 tickets
top10_best = sorted(sim_rows, key=lambda x: x["val_real_raw"], reverse=True)[:10]
top10_worst = sorted(sim_rows, key=lambda x: x["val_real_raw"])[:10]

# Save detailed 500-row simulation CSV
csv_out = os.path.join(PROJ_DIR, "simulazione_5eur_x_500_clean_crypto.csv")
csv_fields = [
    "rank_clean_jul1", "forensic_id", "name", "symbol", "status_oct1",
    "price_jul1_usd", "price_oct1_usd", "invested_eur", "qty_bought",
    "value_oct1_eur_real_fx", "pnl_eur_real_fx", "return_pct_eur_real_fx",
    "value_oct1_eur_const_fx", "pnl_eur_const_fx", "return_pct_usd"
]
with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=csv_fields)
    w.writeheader()
    for x in sim_rows:
        w.writerow({k: x[k] for k in csv_fields})

summary = {
    "invested_eur": TOTAL_INVESTED_EUR,
    "fx_eur_usd_jul1": round(fx_cmc_jul, 6),
    "fx_eur_usd_oct1": round(fx_cmc_oct, 6),
    "fx_impact_on_eur_investor_pct": round((FX_FACTOR_EUR - 1) * 100, 4),
    "real_eur_conservative_isikc0": {
        "final_eur": round(tot_real_cons, 2),
        "profit_eur": round(tot_real_cons - TOTAL_INVESTED_EUR, 2),
        "return_pct": round((tot_real_cons / TOTAL_INVESTED_EUR - 1) * 100, 2),
        "winners": win_real,
        "losers": lose_real,
        "median_ticket_eur": round(med_real, 2),
        "mean_ticket_eur": round(tot_real_cons / 500, 2),
    },
    "real_eur_lastprice_isikc": {
        "final_eur": round(tot_real_lp, 2),
        "profit_eur": round(tot_real_lp - TOTAL_INVESTED_EUR, 2),
        "return_pct": round((tot_real_lp / TOTAL_INVESTED_EUR - 1) * 100, 2),
    },
    "const_fx_usd_conservative_isikc0": {
        "final_eur": round(tot_const_cons, 2),
        "profit_eur": round(tot_const_cons - TOTAL_INVESTED_EUR, 2),
        "return_pct": round((tot_const_cons / TOTAL_INVESTED_EUR - 1) * 100, 2),
        "winners": win_const,
        "losers": lose_const,
        "median_ticket_eur": round(med_const, 2),
        "mean_ticket_eur": round(tot_const_cons / 500, 2),
    },
    "const_fx_usd_lastprice_isikc": {
        "final_eur": round(tot_const_lp, 2),
        "profit_eur": round(tot_const_lp - TOTAL_INVESTED_EUR, 2),
        "return_pct": round((tot_const_lp / TOTAL_INVESTED_EUR - 1) * 100, 2),
    },
    "ex_btw_499_coins_real_eur": {
        "invested_eur": 2495.0,
        "final_eur": round(tot_real_no_btw, 2),
        "profit_eur": round(tot_real_no_btw - 2495.0, 2),
        "return_pct": round((tot_real_no_btw / 2495.0 - 1) * 100, 2),
    },
    "ex_btw_499_coins_const_fx": {
        "invested_eur": 2495.0,
        "final_eur": round(tot_const_no_btw, 2),
        "profit_eur": round(tot_const_no_btw - 2495.0, 2),
        "return_pct": round((tot_const_no_btw / 2495.0 - 1) * 100, 2),
    },
    "tier_breakdown": tier_stats,
    "benchmarks_2500eur": benchmarks,
    "top10_best_tickets": [
        {"rank": x["rank_clean_jul1"], "name": x["name"], "symbol": x["symbol"], "val_real_eur": round(x["val_real_raw"], 2), "pnl_real_eur": round(x["val_real_raw"]-5, 2), "pct_real_eur": round((x["val_real_raw"]/5-1)*100, 2), "val_const_eur": round(x["val_const_raw"], 2), "pct_usd": round((x["val_const_raw"]/5-1)*100, 2)}
        for x in top10_best
    ],
    "top10_worst_tickets": [
        {"rank": x["rank_clean_jul1"], "name": x["name"], "symbol": x["symbol"], "val_real_eur": round(x["val_real_raw"], 2), "pnl_real_eur": round(x["val_real_raw"]-5, 2), "pct_real_eur": round((x["val_real_raw"]/5-1)*100, 2), "val_const_eur": round(x["val_const_raw"], 2), "pct_usd": round((x["val_const_raw"]/5-1)*100, 2)}
        for x in top10_worst
    ],
}

with open(os.path.join(PROJ_DIR, "simulazione_5eur_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)

print("\n=== SIMULATION SUMMARY ===")
print(json.dumps(summary, indent=2, ensure_ascii=False))
