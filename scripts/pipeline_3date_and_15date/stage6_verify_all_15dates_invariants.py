#!/usr/bin/env python3
"""
STAGE 6: Complete Mechanical Invariant Verification across ALL 15-Date Deliverables
+ Copy Forensic Markdown Report to Artifact Directory for Artifact Registration!
"""
import csv, json, shutil
from pathlib import Path

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
ART_DIR = Path(r"C:\Users\Administrator\.gemini\antigravity\brain\ef94cd2a-0982-41cb-9b2e-62eba3745324")

NEW_12 = [
    ("D01", "2022-12-30"), ("D02", "2024-04-09"), ("D03", "2024-09-10"), ("D04", "2024-11-22"),
    ("D05", "2025-01-24"), ("D06", "2025-04-08"), ("D07", "2025-09-19"), ("D08", "2025-10-07"),
    ("D09", "2025-12-26"), ("D10", "2026-01-15"), ("D11", "2026-02-13"), ("D12", "2026-05-12"),
]

# 1. Verify all 12 individual 500-coin cohort CSVs
print("=== [1] VERIFYING 12 INDIVIDUAL COHORT CSVs (500 UNIQUE PURE COINS EACH) ===")
BANNED_SYMS = {"USDT", "USDC", "DAI", "BUSD", "TUSD", "USDE", "SUSDE", "USDS", "WBTC", "WETH", "STETH", "WSTETH", "MSOL", "DPI", "VNDC", "EDGT", "PAXG", "XAUT", "FTT", "LUNC", "USTC"}
for code, dt in NEW_12:
    p = BASE / f"coorte_pure500_{code}_{dt}.csv"
    assert p.exists(), f"Missing {p}"
    with open(p, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 500, f"{p.name}: expected 500 rows, got {len(rows)}"
    cids = {r["cmc_id"] for r in rows}
    assert len(cids) == 500, f"{p.name}: duplicate cmc_id!"
    bad_syms = [r["symbol"] for r in rows if r["symbol"].upper() in BANNED_SYMS]
    assert not bad_syms, f"{p.name}: banned symbol(s) found: {bad_syms}"
    min_vol = min(float(r["vol24h_usd"]) for r in rows)
    assert min_vol >= 100_000.0, f"{p.name}: min volume {min_vol} < 100k!"
    min_p = min(float(r["price_usd"]) for r in rows)
    assert min_p > 0, f"{p.name}: zero/negative price!"
print("  [PASS] All 12 per-date cohort CSVs: 500/500 unique coins, 0 banned symbols, all vol >= 100k USD, all prices > 0!")

# 2. Verify Vista A & Vista B 7,500-row Long Panels + Vista B 500-row Wide CSV/JSON
for fn, expected in [
    ("panel_vistaA_15coorti_7500_righe.csv", 7500),
    ("panel_vistaB_jul1_500_su_15date_7500_righe.csv", 7500),
    ("storico_15date_vistaB_500_crypto.csv", 500),
    ("backtest_matrice_14x15_5eur.csv", 105),
]:
    p = BASE / fn
    with open(p, encoding="utf-8-sig") as f:
        n = sum(1 for _ in csv.DictReader(f))
    assert n == expected, f"{fn}: expected {expected} rows, got {n}"
    print(f"  [PASS] {fn}: exact {n} rows")

# 3. Verify Tranches CSV
with open(BASE / "backtest_tranche_50_to_500_tutte_date.csv", encoding="utf-8-sig") as f:
    ntr = sum(1 for _ in csv.DictReader(f))
assert ntr >= 900, f"Unexpected tranche rows: {ntr}"
print(f"  [PASS] backtest_tranche_50_to_500_tutte_date.csv: {ntr} cumulative & marginal tranche rows")

# 4. Copy Markdown report to Artifact directory
src_md = BASE / "report_15date_2022_2026_completo.md"
dst_md = ART_DIR / "report_15date_2022_2026_completo.md"
shutil.copy2(src_md, dst_md)
print(f"  [PASS] Copied report to Artifact path -> {dst_md}")

# 5. Print key highlights for final executive check (D01..D14 best/worst + factor highlights)
bt = json.loads((BASE / "backtest_15date_completo.json").read_text(encoding="utf-8"))
mat = bt["matrix_14x15"]
best5 = sorted(mat, key=lambda x: x["ret_eur_cons_pct"], reverse=True)[:5]
worst5 = sorted(mat, key=lambda x: x["ret_eur_cons_pct"])[:5]
print("\nTOP 5 ENTRY->EXIT WINDOWS (TOP 500, 2,500 EUR CONSERVATIVE):")
for r in best5:
    print(f"  {r['entry_code']}({r['entry_date']})->{r['exit_code']}({r['exit_date']}): {r['final_eur_cons']:,.2f} EUR ({r['ret_eur_cons_pct']:+.2f}% EUR | BTC={r['btc_bench_ret_eur_pct']:+.2f}% | Alpha={r['alpha_vs_btc_pp']:+.2f}pp)")
print("\nWORST 5 ENTRY->EXIT WINDOWS (TOP 500, 2,500 EUR CONSERVATIVE):")
for r in worst5:
    print(f"  {r['entry_code']}({r['entry_date']})->{r['exit_code']}({r['exit_date']}): {r['final_eur_cons']:,.2f} EUR ({r['ret_eur_cons_pct']:+.2f}% EUR | BTC={r['btc_bench_ret_eur_pct']:+.2f}% | Alpha={r['alpha_vs_btc_pp']:+.2f}pp)")
print("\nFACTOR HIGHLIGHTS (D01->D08 Bear-to-Peak & D08->D15 Peak-to-Bear):")
for w in ("D01_to_D08_BearToPeak", "D01_to_D15_Full4YrHold", "D08_to_D15_PeakToBearNov26"):
    print(f"  [{w}]")
    for fk in ("unlock_overhang", "hist_top10", "hist_eoa_whale"):
        parts = [f"{k}: n={v['n']} med={v['median_eur_pct']:+.1f}% mean={v['mean_eur_pct']:+.1f}%" for k, v in bt["factor_backtests"][w][fk].items() if v["n"] > 0]
        print(f"    {fk:16s} -> " + " | ".join(parts))
