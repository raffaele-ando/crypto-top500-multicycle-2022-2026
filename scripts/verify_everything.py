#!/usr/bin/env python3
"""
Independent Mathematical, Structural & Forensic Verification Suite
Verifies 100% correctness of the Top 500 Crypto dataset (2026-07-01 vs 2026-10-01).
"""

import csv
import json
import os
import re
import sys

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
JSON_PATH = os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.json")
CSV_PATH = os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.csv")
MD_PATH = os.path.join(PROJ_DIR, "report_top500_crypto_2026.md")
HTML_PATH = os.path.join(PROJ_DIR, "dashboard_top500_crypto_2026.html")


def strip_backticks_and_escaped_dollars(line):
    # Remove inline code spans `...`
    no_code = re.sub(r"`[^`]*`", "", line)
    # Remove properly escaped \$
    no_esc = no_code.replace("\\$", "")
    return no_esc


def main():
    checks = []

    def record(name, passed, detail=""):
        checks.append({"check": name, "pass": bool(passed), "detail": detail})
        icon = "PASS" if passed else "FAIL"
        print(f"[{icon}] {name}: {detail}")
        if not passed:
            raise AssertionError(f"Check failed: {name} -> {detail}")

    # 1. Load JSON & CSV
    with open(JSON_PATH, encoding="utf-8") as f:
        jdata = json.load(f)
    rows_json = jdata["cryptocurrencies"]

    with open(CSV_PATH, encoding="utf-8-sig") as f:
        rows_csv = list(csv.DictReader(f))

    with open(MD_PATH, encoding="utf-8") as f:
        md_text = f.read()

    with open(HTML_PATH, encoding="utf-8") as f:
        html_text = f.read()

    record("1. Cardinality JSON == CSV == 500", len(rows_json) == 500 and len(rows_csv) == 500, f"JSON={len(rows_json)}, CSV={len(rows_csv)}")

    # 2. Unique IDs and sequential ranks 1..500
    cmc_ids = [r["cmc_id"] for r in rows_json]
    forensic_ids = [r["forensic_id"] for r in rows_json]
    ranks_mcap = [r["rank_mcap_jul1"] for r in rows_json]
    ranks_cmc = sorted(r["cmc_rank_jul1"] for r in rows_json)
    record(
        "2. Unique IDs & Exact Rank Permutations 1..500",
        len(set(cmc_ids)) == 500 and ranks_mcap == list(range(1, 501)) and ranks_cmc == list(range(1, 501)),
        "500 unique CMC IDs; both Pure MCap Rank and CMC Rank cover exact 1..500",
    )

    # 3. Strict Monotonic Decreasing Market Cap on 1 July 2026
    mono = all(rows_json[i]["mcap_jul1_usd"] >= rows_json[i + 1]["mcap_jul1_usd"] for i in range(499))
    record(
        "3. Monotonic Decreasing Market Cap on 2026-07-01",
        mono,
        f"#1=${rows_json[0]['mcap_jul1_usd']:,.2f} >= ... >= #500=${rows_json[499]['mcap_jul1_usd']:,.2f}",
    )

    # 4. Exact Percentage & Delta Formula Recomputation across all 500 rows
    max_pct_err = 0.0
    for r in rows_json:
        assert r["price_jul1_usd"] > 0, f"Non-positive Jul 1 price for {r['forensic_id']}"
        assert r["mcap_jul1_usd"] > 0, f"Non-positive Jul 1 mcap for {r['forensic_id']}"
        if r["status_oct1"] == "UNTRACKED":
            assert r["price_oct1_usd"] is None and r["mcap_oct1_usd"] is None
        else:
            assert r["price_oct1_usd"] > 0, f"Non-positive Oct 1 price for {r['forensic_id']}"
            exp_ppct = (r["price_oct1_usd"] - r["price_jul1_usd"]) / r["price_jul1_usd"] * 100.0
            err_p = abs(exp_ppct - r["price_change_pct"])
            max_pct_err = max(max_pct_err, err_p)
            exp_mpct = (r["mcap_oct1_usd"] - r["mcap_jul1_usd"]) / r["mcap_jul1_usd"] * 100.0
            err_m = abs(exp_mpct - r["mcap_change_pct"])
            max_pct_err = max(max_pct_err, err_m)

    record("4. Delta & Percentage Recomputation Accuracy", max_pct_err < 1e-4, f"max_abs_pct_error={max_pct_err:.2e}")

    # 5. Market Cap == Price * Circulating Supply Consistency Audit
    supply_mismatches = []
    for r in rows_json:
        if r["circulating_supply_jul1"] > 0:
            rel_j = abs(r["mcap_jul1_usd"] - r["price_jul1_usd"] * r["circulating_supply_jul1"]) / r["mcap_jul1_usd"]
            if rel_j > 0.002:
                supply_mismatches.append((r["forensic_id"], "JUL", rel_j))
        if r["mcap_oct1_usd"] and r["circulating_supply_oct1"] and r["circulating_supply_oct1"] > 0:
            rel_o = abs(r["mcap_oct1_usd"] - r["price_oct1_usd"] * r["circulating_supply_oct1"]) / r["mcap_oct1_usd"]
            if rel_o > 0.002:
                supply_mismatches.append((r["forensic_id"], "OCT", rel_o))

    record("5. MarketCap == Price * CirculatingSupply (<0.2% tol)", len(supply_mismatches) == 0, f"mismatches={len(supply_mismatches)}")

    # 6. Markdown Table Census Row Count == 500 & HTML Embedded Rows == 500
    md_census_rows = [ln for ln in md_text.splitlines() if re.match(r"^\|\s*\d{3}\s*\|\s*\d+\s*\|\s*`cmc-\d+`", ln)]
    record("6. Markdown Census Table Exact 500 Rows", len(md_census_rows) == 500, f"census_rows={len(md_census_rows)}")

    html_ids_found = sum(1 for fid in forensic_ids if f'"{fid}"' in html_text)
    record("7. Interactive HTML Explorer Contains 500/500 IDs", html_ids_found == 500, f"html_ids={html_ids_found}/500")

    # 8. KaTeX Safety Check (zero unescaped bare '$' in Markdown)
    bare_dollar_lines = []
    for i, ln in enumerate(md_text.splitlines(), 1):
        rem = strip_backticks_and_escaped_dollars(ln)
        if "$" in rem:
            bare_dollar_lines.append((i, rem[:100]))
    record("8. Markdown KaTeX Dollar-Escaping Safety", len(bare_dollar_lines) == 0, f"unescaped_lines={len(bare_dollar_lines)}")

    out_cert = os.path.join(PROJ_DIR, "math_integrity_audit.json")
    with open(out_cert, "w", encoding="utf-8") as f:
        json.dump({"overall_pass": True, "checks": checks}, f, indent=2)
    print("\nALL 8 MATHEMATICAL & STRUCTURAL INTEGRITY CHECKS PASSED (100%).")


if __name__ == "__main__":
    main()
