#!/usr/bin/env python3
"""
Generates the complete 500/500 ranking of all Clean Pure Cryptocurrencies
sorted strictly from HIGHEST return to LOWEST return (1 July 2026 -> 1 October 2026),
including:
  - Return Rank (#001..#500)
  - Clean Pure Market Cap Rank (#1..#500)
  - Global Market Cap Rank on 1 July 2026 (#1..#774)
  - Official CMC Rank on 1 July 2026 (cmcRank)
  - EUR Real Return %, USD Return %, €5 Ticket Final Value & PnL, Prices, and Jul 1 Market Cap.
"""

import csv
import datetime
import json
import os
import re

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")


def fmt_price(p):
    if p is None:
        return "N/D (Sospesa)"
    ap = abs(p)
    if ap >= 1000:
        return f"${p:,.2f}"
    if ap >= 1:
        return f"${p:,.4f}"
    if ap >= 0.01:
        return f"${p:.6f}"
    if ap >= 0.0001:
        return f"${p:.8f}"
    if ap >= 1e-6:
        return f"${p:.10f}"
    return f"${p:.4e}"


def main():
    with open(os.path.join(RAW_DIR, "cmc_full_2026-07-01.json"), encoding="utf-8") as f:
        jul_all = json.load(f)["data"]
    ranked_global = [r for r in jul_all if r["quotes"][0].get("marketCap", 0) > 0]
    ranked_global.sort(key=lambda r: r["quotes"][0]["marketCap"], reverse=True)
    global_mcap_rank_by_id = {r["id"]: idx for idx, r in enumerate(ranked_global, 1)}

    with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
        clean500 = json.load(f)["cryptocurrencies"]

    with open(os.path.join(PROJ_DIR, "simulazione_5eur_summary.json"), encoding="utf-8") as f:
        fx = json.load(f)
    fx_factor = fx["fx_eur_usd_jul1"] / fx["fx_eur_usd_oct1"]
    stake = 5.0

    enriched = []
    for r in clean500:
        pj = r["price_jul1_usd"]
        po = r["price_oct1_usd"]
        if po is not None:
            pct_usd = (po / pj - 1.0) * 100.0
            val_eur = stake * (po / pj) * fx_factor
            pct_eur = (val_eur / stake - 1.0) * 100.0
        else:
            pct_usd = -100.0
            val_eur = 0.0
            pct_eur = -100.0

        enriched.append({
            "forensic_id": r["forensic_id"],
            "rank_clean_mcap_jul1": r["rank_clean_jul1"],
            "rank_global_mcap_jul1": global_mcap_rank_by_id[r["cmc_id"]],
            "cmc_rank_jul1": r["cmc_rank_jul1"],
            "cmc_id": r["cmc_id"],
            "name": r["name"],
            "symbol": r["symbol"],
            "status_oct1": r["status_oct1"],
            "return_pct_eur": round(pct_eur, 4),
            "return_pct_usd": round(pct_usd, 4),
            "ticket_5eur_final_eur": round(val_eur, 4),
            "ticket_5eur_pnl_eur": round(val_eur - stake, 4),
            "price_jul1_usd": pj,
            "price_oct1_usd": po,
            "mcap_jul1_usd": r["mcap_jul1_usd"],
            "mcap_oct1_usd": r["mcap_oct1_usd"],
        })

    # Sort strictly descending by real EUR return % (tie-breaker: clean mcap rank ascending)
    enriched.sort(key=lambda x: (-x["return_pct_eur"], x["rank_clean_mcap_jul1"]))

    for idx, x in enumerate(enriched, 1):
        x["rank_return"] = idx

    # Reorder keys cleanly
    fieldnames = [
        "rank_return", "forensic_id", "name", "symbol",
        "rank_clean_mcap_jul1", "rank_global_mcap_jul1", "cmc_rank_jul1",
        "return_pct_eur", "return_pct_usd",
        "ticket_5eur_final_eur", "ticket_5eur_pnl_eur",
        "price_jul1_usd", "price_oct1_usd",
        "mcap_jul1_usd", "mcap_oct1_usd", "status_oct1", "cmc_id"
    ]
    ordered = [{k: x[k] for k in fieldnames} for x in enriched]

    assert len(ordered) == 500
    for i in range(499):
        assert ordered[i]["return_pct_eur"] >= ordered[i + 1]["return_pct_eur"]

    csv_path = os.path.join(PROJ_DIR, "classifica_500_per_rendimento_desc.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(ordered)

    json_path = os.path.join(PROJ_DIR, "classifica_500_per_rendimento_desc.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({
            "meta": {
                "sorted_by": "return_pct_eur DESC (1 July 2026 -> 1 October 2026)",
                "total_coins": 500,
                "fx_eur_usd_jul1": fx["fx_eur_usd_jul1"],
                "fx_eur_usd_oct1": fx["fx_eur_usd_oct1"],
            },
            "ranking": ordered,
        }, f, indent=2, ensure_ascii=False)

    # Build Complete 500/500 Markdown Report Artifact (KaTeX-safe, zero truncation)
    md = []
    md.append("# Classifica Integrale per Rendimento (dal Più Alto al Più Basso) — Tutte le 500 Clean Pure Crypto")
    md.append("")
    md.append("> [!IMPORTANT]")
    md.append("> **Ordinamento Integrale 1:1 (`#001` → `#500`) dal Rendimento più Alto al Minore (`1° Luglio 2026 → 1° Ottobre 2026`)**")
    md.append("> Per ogni criptovaluta sono riportati i **3 riferimenti di posizione al 1° luglio 2026**:")
    md.append("> 1. **`# Clean` (`1..500`):** posizione nell'elenco pulito delle 500 criptovalute per capitalizzazione;")
    md.append("> 2. **`# MCap Glob.` (`1..774`):** posizione per pura capitalizzazione nella classifica globale originale (inclusi stablecoin, wrapped, ETF tokenizzati);")
    md.append("> 3. **`CMC #` (`cmcRank`):** numero ufficiale di classifica su CoinMarketCap al 1° luglio 2026.")
    md.append("")
    md.append("**File Generati:**")
    md.append("- Tabella CSV ordinata per rendimento (`500` righe): [classifica_500_per_rendimento_desc.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/classifica_500_per_rendimento_desc.csv)")
    md.append("- Dataset JSON ordinato per rendimento: [classifica_500_per_rendimento_desc.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/classifica_500_per_rendimento_desc.json)")
    md.append("- Certificato di Completezza Forense (`500/500`): [audit_certificate_classifica_rendimento.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/audit_certificate_classifica_rendimento.json)")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## Elenco Completo 1:1 (`#001` → `#500`) — Dal Rendimento Maggiore al Minore")
    md.append("")
    md.append("| # Rend. | Nome (`Ticker`) | ID | # Clean (Cap) | # MCap Glob. | CMC # | Rend. % EUR | Rend. % USD | €5 → Finale | Guadagno €5 | Prezzo 1 Lug | Prezzo 1 Ott | Market Cap 1 Lug |")
    md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for x in ordered:
        nm = x["name"].replace("|", "/").replace("$", "\\$")
        sym = x["symbol"].replace("|", "/")
        st_tag = " *(sospesa 28 set)*" if x["status_oct1"] == "UNTRACKED" else ""
        md.append(
            f"| {x['rank_return']:03d} | **{nm}** (`{sym}`){st_tag} | `{x['forensic_id']}` "
            f"| #{x['rank_clean_mcap_jul1']} | #{x['rank_global_mcap_jul1']} | #{x['cmc_rank_jul1']} "
            f"| **`{x['return_pct_eur']:+.2f}%`** | `{x['return_pct_usd']:+.2f}%` "
            f"| `€{x['ticket_5eur_final_eur']:,.2f}` | `{x['ticket_5eur_pnl_eur']:+,.2f}€` "
            f"| `{fmt_price(x['price_jul1_usd'])}` | `{fmt_price(x['price_oct1_usd'])}` | `${x['mcap_jul1_usd']:,.0f}` |"
        )
    md.append("")

    md_text = "\n".join(md)
    for i, ln in enumerate(md_text.splitlines(), 1):
        rem = re.sub(r"`[^`]*`", "", ln).replace("\\$", "")
        assert "$" not in rem, f"Unescaped '$' at line {i}: {rem}"

    proj_md = os.path.join(PROJ_DIR, "classifica_500_per_rendimento.md")
    with open(proj_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    manifest = {
        "target": "500 Clean Pure Cryptos Ranked by Return Descending",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "expected_counts": {"ranked_500": 500},
        "sources": [
            f"ranking_json={json_path}:ranking:forensic_id",
            f"ranking_csv={csv_path}::forensic_id",
        ],
        "required_files": [json_path, csv_path],
    }
    with open(os.path.join(PROJ_DIR, "manifest_classifica_rendimento.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("Top 20 by return:")
    for x in ordered[:20]:
        print(f"  #{x['rank_return']:03d} {x['name']:24s} ({x['symbol']:8s}) | Clean#{x['rank_clean_mcap_jul1']:03d} | Glob#{x['rank_global_mcap_jul1']:03d} | CMC#{x['cmc_rank_jul1']:03d} | {x['return_pct_eur']:+8.2f}% EUR | €5 -> €{x['ticket_5eur_final_eur']:.2f}")
    print("\nBottom 10 by return:")
    for x in ordered[-10:]:
        print(f"  #{x['rank_return']:03d} {x['name']:24s} ({x['symbol']:8s}) | Clean#{x['rank_clean_mcap_jul1']:03d} | Glob#{x['rank_global_mcap_jul1']:03d} | CMC#{x['cmc_rank_jul1']:03d} | {x['return_pct_eur']:+8.2f}% EUR | €5 -> €{x['ticket_5eur_final_eur']:.2f}")


if __name__ == "__main__":
    main()
