#!/usr/bin/env python3
"""
Tranche Analysis (steps of 50: 50, 100, ..., 500):
- Analysis 1: Slice ORIGINAL Global Top 500 into 50-coin tranches (#1-50, ..., #451-500) and cumulative (Top 50..500),
              then REMOVE all excluded assets (Non-Pure + Points 1-3) inside each tranche/cumulative.
- Analysis 2: Take PURE/CLEAN coins packed into FULL tranches of 50 (#1-50, #51-100, ..., up to K surviving from Orig 500,
              AND continuing up to 350, 400, 450, 500 from Clean Pure 500).
- Analysis 3: Best-performing tranche and best cumulative portfolio (with & without Bitway BTW outlier + median/win-rate).
"""

import csv
import json
import os
import statistics

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"

with open(os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
    orig500 = json.load(f)["cryptocurrencies"]

with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
    clean_doc = json.load(f)
clean500 = clean_doc["cryptocurrencies"]
clean_ids = {r["cmc_id"] for r in clean500}
excl_above_500 = {e["cmc_id"]: e["reason"] for e in clean_doc["excluded_above_cutoff"]}

with open(os.path.join(PROJ_DIR, "simulazione_5eur_summary.json"), encoding="utf-8") as f:
    fx_meta = json.load(f)

FX_JUL = fx_meta["fx_eur_usd_jul1"]
FX_OCT = fx_meta["fx_eur_usd_oct1"]
FX_FACTOR = FX_JUL / FX_OCT
STAKE = 5.0

# Verify exact count of clean coins inside Original Top 500!
# Also check how many survived ONLY Base Non-Pure filter (without Points 1-3) just to understand the "349" number!
orig_in_clean = [r for r in orig500 if r["cmc_id"] in clean_ids]
orig_excl_base = [r for r in orig500 if excl_above_500.get(r["cmc_id"]) in ("STABLECOIN", "WRAPPED_LST_LRT_RECEIPT", "TOKENIZED_ETF_STOCK_RWA_COMMODITY")]
orig_excl_p123 = [r for r in orig500 if excl_above_500.get(r["cmc_id"]) in ("PUNTO_1_ILLIQUIDI_VOL_LT_100K", "PUNTO_2_ZOMBIE_FALLITI_CHIUSI", "PUNTO_3_SUBNET_E_GAS_SECONDARI")]

print(f"Original Top 500 count: {len(orig500)}")
print(f"  Excluded by Base Non-Pure inside Orig 500: {len(orig_excl_base)} -> Remaining after Base only: {500 - len(orig_excl_base)}")
print(f"  Excluded by Points 1-3 inside Orig 500:    {len(orig_excl_p123)}")
print(f"  Total Clean surviving inside Orig 500 (K): {len(orig_in_clean)} (check: 500 - {len(orig_excl_base)} - {len(orig_excl_p123)} = {500 - len(orig_excl_base) - len(orig_excl_p123)})")

def eval_basket(items, stake=5.0, fx_factor=FX_FACTOR):
    n = len(items)
    if n == 0:
        return {}
    inv = n * stake
    vals_real = []
    vals_const = []
    vals_real_nobtw = []
    for r in items:
        pj = r["price_jul1_usd"]
        po = r["price_oct1_usd"]
        if po is not None:
            vc = stake * (po / pj)
            vr = vc * fx_factor
        else:
            vc = 0.0
            vr = 0.0
        vals_const.append(vc)
        vals_real.append(vr)
        if r["cmc_id"] != 39158:  # Bitway BTW
            vals_real_nobtw.append(vr)

    tot_real = sum(vals_real)
    tot_const = sum(vals_const)
    pnl_real = tot_real - inv
    pnl_const = tot_const - inv
    pct_real = (tot_real / inv - 1) * 100.0
    pct_const = (tot_const / inv - 1) * 100.0
    med_real = statistics.median(vals_real)
    med_pct_real = (med_real / stake - 1) * 100.0
    wins = sum(1 for v in vals_real if v > stake)
    losses = sum(1 for v in vals_real if v < stake)

    has_btw = len(vals_real_nobtw) < n
    if has_btw and len(vals_real_nobtw) > 0:
        inv_nb = len(vals_real_nobtw) * stake
        pct_real_nobtw = (sum(vals_real_nobtw) / inv_nb - 1) * 100.0
    else:
        pct_real_nobtw = pct_real

    best = max(zip(items, vals_real), key=lambda t: t[1])
    worst = min(zip(items, vals_real), key=lambda t: t[1])

    return {
        "n_coins": n,
        "invested_eur": round(inv, 2),
        "final_eur_real": round(tot_real, 2),
        "pnl_eur_real": round(pnl_real, 2),
        "pct_real": round(pct_real, 2),
        "final_eur_const": round(tot_const, 2),
        "pnl_eur_const": round(pnl_const, 2),
        "pct_const": round(pct_const, 2),
        "median_ticket_eur": round(med_real, 2),
        "median_pct_real": round(med_pct_real, 2),
        "winners": wins,
        "losers": losses,
        "win_rate_pct": round(wins / n * 100.0, 1),
        "has_btw": has_btw,
        "pct_real_ex_btw": round(pct_real_nobtw, 2),
        "best_coin": f"{best[0]['symbol']} (€{best[1]:.2f})",
        "worst_coin": f"{worst[0]['symbol']} (€{worst[1]:.2f})",
    }

# ==============================================================================
# ANALYSIS 1: Slice ORIGINAL Top 500 into 50s, then REMOVE excluded inside each slice
# ==============================================================================
a1_cumulative = []
a1_blocks = []

for end_r in range(50, 501, 50):
    start_r = end_r - 49
    # Cumulative #1..end_r in original 500, filtered to clean_ids
    cum_orig = orig500[:end_r]
    cum_clean = [r for r in cum_orig if r["cmc_id"] in clean_ids]
    res_c = eval_basket(cum_clean)
    res_c["label"] = f"Prime {end_r} orig."
    res_c["orig_count"] = end_r
    res_c["removed_count"] = end_r - len(cum_clean)
    a1_cumulative.append(res_c)

    # Disjoint block start_r..end_r in original 500, filtered to clean_ids
    blk_orig = orig500[start_r - 1 : end_r]
    blk_clean = [r for r in blk_orig if r["cmc_id"] in clean_ids]
    res_b = eval_basket(blk_clean)
    res_b["label"] = f"#{start_r:03d}-#{end_r:03d} orig."
    res_b["orig_count"] = 50
    res_b["removed_count"] = 50 - len(blk_clean)
    a1_blocks.append(res_b)

# ==============================================================================
# ANALYSIS 2: Full Clean Tranches of 50 (packed without gaps!)
# Both: (2A) strictly within the K clean coins surviving from Orig 500 (50, 100, ..., 300, K)
# AND   (2B) continuing cleanly up to 350, 400, 450, 500 from Clean Pure 500!
# Note: Since orig_in_clean is strictly a prefix of clean500 (verified below!), 50..300 are IDENTICAL!
# ==============================================================================
K = len(orig_in_clean)
assert [r["cmc_id"] for r in orig_in_clean] == [r["cmc_id"] for r in clean500[:K]], "Prefix invariant check!"
print(f"Prefix invariant VERIFIED: the {K} clean coins inside Original 500 are EXACTLY clean500[:{K}]!")

a2_cumulative = []
a2_blocks = []

# Cumulative points: 50, 100, 150, 200, 250, 300, K (exact end of Orig 500), 350, 400, 450, 500
cum_cutoffs = [50, 100, 150, 200, 250, 300, K, 350, 400, 450, 500]
for c in cum_cutoffs:
    res = eval_basket(clean500[:c])
    res["label"] = f"Prime {c} pulite" + (" (fine Orig 500)" if c == K else "")
    res["is_orig500_cap"] = (c == K)
    a2_cumulative.append(res)

# Disjoint clean blocks: #1-50, #51-100, ..., #251-300, #301-K (tail of Orig 500), AND full #301-350, #351-400, #401-450, #451-500
for end_r in range(50, 501, 50):
    start_r = end_r - 49
    res = eval_basket(clean500[start_r - 1 : end_r])
    res["label"] = f"#{start_r:03d}-#{end_r:03d} pulite"
    a2_blocks.append(res)

# Also compute exact residual tail block inside Orig 500: #301..#K
res_tail_k = eval_basket(clean500[300:K])
res_tail_k["label"] = f"#301-#{K} pulite (residuo Orig 500)"

# Print concise tables for inspection
def show_table(title, rows_list, extra_col=None):
    print(f"\n=== {title} ===")
    for x in rows_list:
        rem = f" (tolte {x['removed_count']:3d})" if extra_col else ""
        btw_note = f" [ex-BTW: {x['pct_real_ex_btw']:+.2f}%]" if x["has_btw"] else ""
        print(
            f"  {x['label']:32s} | N={x['n_coins']:3d}{rem} | Inv=€{x['invested_eur']:7.2f} -> €{x['final_eur_real']:7.2f} "
            f"| PnL=€{x['pnl_eur_real']:+7.2f} ({x['pct_real']:+6.2f}% EUR / {x['pct_const']:+6.2f}% USD) "
            f"| Med={x['median_pct_real']:+6.2f}% | Win={x['win_rate_pct']:5.1f}%{btw_note} | Best={x['best_coin']}"
        )

show_table("ANALISI 1A — CUMULATIVE ORIGINALI (50..500) DEPURATE", a1_cumulative, extra_col=True)
show_table("ANALISI 1B — SINGOLE TRANCHE DA 50 ORIGINALI DEPURATE", a1_blocks, extra_col=True)
show_table(f"ANALISI 2A — CUMULATIVE PIENE PULITE (50..{K}..500)", a2_cumulative)
show_table("ANALISI 2B — SINGOLE TRANCHE PIENE DA 50 PULITE (#1-50 .. #451-500)", a2_blocks + [res_tail_k])

# Save full JSON and CSV tables to project dir!
out_json = os.path.join(PROJ_DIR, "analisi_tranche_50_comparativa.json")
with open(out_json, "w", encoding="utf-8") as f:
    json.dump({
        "meta": {
            "stake_per_coin_eur": STAKE,
            "fx_eur_usd_jul1": FX_JUL,
            "fx_eur_usd_oct1": FX_OCT,
            "fx_impact_pct": round((FX_FACTOR - 1) * 100, 4),
            "orig500_surviving_after_base_only": 500 - len(orig_excl_base),
            "orig500_surviving_after_base_and_p123_K": K,
        },
        "analisi_1_cumulative_orig_depurate": a1_cumulative,
        "analisi_1_tranche_50_orig_depurate": a1_blocks,
        "analisi_2_cumulative_piene_pulite": a2_cumulative,
        "analisi_2_tranche_50_piene_pulite": a2_blocks,
        "analisi_2_residuo_301_K": res_tail_k,
    }, f, indent=2, ensure_ascii=False)

csv_out = os.path.join(PROJ_DIR, "analisi_tranche_50_comparativa.csv")
all_csv = []
for grp, lst in [
    ("A1_Cumulativa_Orig_Depurata", a1_cumulative),
    ("A1_Tranche50_Orig_Depurata", a1_blocks),
    ("A2_Cumulativa_Piena_Pulita", a2_cumulative),
    ("A2_Tranche50_Piena_Pulita", a2_blocks + [res_tail_k]),
]:
    for row in lst:
        r2 = {"gruppo": grp}
        r2.update(row)
        all_csv.append(r2)

keys = ["gruppo", "label", "n_coins", "orig_count", "removed_count", "invested_eur", "final_eur_real", "pnl_eur_real", "pct_real", "final_eur_const", "pnl_eur_const", "pct_const", "median_ticket_eur", "median_pct_real", "winners", "losers", "win_rate_pct", "has_btw", "pct_real_ex_btw", "best_coin", "worst_coin"]
with open(csv_out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
    w.writeheader()
    w.writerows(all_csv)

print(f"\nSaved {out_json} and {csv_out}")
