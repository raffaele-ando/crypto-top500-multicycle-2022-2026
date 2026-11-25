#!/usr/bin/env python3
"""
Master Builder & Verifier: Top 500 PURE Cryptocurrencies by Market Capitalization
(Excluding all Stablecoins, Wrapped/Bridged/LST/LRT/Receipt/LP tokens, and Tokenized Stocks/ETFs/RWA/Commodities)
Comparison between 1 July 2026 (2026-07-01 23:59:59 UTC) and 1 October 2026 (2026-10-01 23:59:59 UTC).
"""

import csv
import json
import os
import re
import statistics
from datetime import datetime, timezone

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")
ARTIFACT_DIR = r"C:\Users\Administrator\.gemini\antigravity\brain\ef94cd2a-0982-41cb-9b2e-62eba3745324"


def fmt_price(p):
    if p is None:
        return "N/D (Untracked)"
    if p == 0:
        return "$0.00"
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


def fmt_mcap(m):
    if m is None:
        return "N/D (Untracked)"
    return f"${m:,.0f}"


def fmt_pct(pct):
    if pct is None:
        return "N/D"
    return f"{pct:+.2f}%"


def main():
    with open(os.path.join(RAW_DIR, "cmc_full_2026-07-01.json"), encoding="utf-8") as f:
        jul_all = json.load(f)["data"]
    with open(os.path.join(RAW_DIR, "cmc_full_2026-10-01.json"), encoding="utf-8") as f:
        oct_all = json.load(f)["data"]
    with open(os.path.join(RAW_DIR, "cmc_subcent_exact_v31.json"), encoding="utf-8") as f:
        subcent_v31 = json.load(f)
    with open(os.path.join(RAW_DIR, "excluded_non_pure_above_top500.json"), encoding="utf-8") as f:
        excluded_list = json.load(f)

    oct_by_id = {r["id"]: r for r in oct_all}
    excl_ids = {e["cmc_id"] for e in excluded_list}

    ranked = [r for r in jul_all if r["quotes"][0].get("marketCap", 0) > 0]
    ranked.sort(key=lambda r: r["quotes"][0]["marketCap"], reverse=True)

    pure_raw = []
    for r in ranked:
        if r["id"] not in excl_ids:
            pure_raw.append(r)
            if len(pure_raw) == 500:
                break

    assert len(pure_raw) == 500, f"Expected 500 pure cryptos, got {len(pure_raw)}"

    # Save excluded CSV for full transparency
    excl_csv = os.path.join(PROJ_DIR, "excluded_229_non_pure_assets.csv")
    with open(excl_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(excluded_list[0].keys()))
        w.writeheader()
        w.writerows(excluded_list)

    untracked_meta = {
        33249: {
            "last_date": "2026-07-02",
            "last_price_usd": 4.9922389585,
            "last_mcap_usd": 101770106.02,
            "reason": "Rimosso dal tracking attivo CMC/CG dopo il 2026-07-02 per assenza di volume/liquidità verificabile (\\$0 vol 24h; 0 pool DEX attive).",
        },
        37986: {
            "last_date": "2026-09-14",
            "last_price_usd": 0.1664165984,
            "last_mcap_usd": 116591829.48,
            "reason": "Token Solana Heaven DEX (LiGHt...v777) passato a stato untracked su CMC e CoinGecko dopo il 2026-09-14 per inattività del protocollo (\\$0 vol 24h al 1° lug).",
        },
    }

    CEX_IDS = {1839, 3957, 3635, 3897, 29160, 11092, 2087, 4269, 2694, 4041, 2933, 33849, 3893}
    ZOMBIE_IDS = {4195, 4172, 20314, 11171, 21296, 8049}
    SUBNET_IDS = {36912, 36902, 36901, 36904}
    GAS_DUAL_IDS = {1785, 3822, 3012, 3217}

    records = []
    for idx, rj in enumerate(pure_raw, 1):
        cid = rj["id"]
        scid = str(cid)
        forensic_id = f"cmc-{cid}"
        qj = rj["quotes"][0]
        tags = set(rj.get("tags") or [])

        mcap_jul = float(qj["marketCap"])
        cs_jul = float(rj.get("circulatingSupply") or 0.0)
        vol_jul = float(qj.get("volume24h") or 0.0)
        price_jul = float(qj["price"])
        price_source_jul = "CMC Snapshot"

        if price_jul < 0.01:
            v31_j = subcent_v31.get(scid, {}).get("2026-07-01", {})
            if "close" in v31_j and v31_j["close"] > 0:
                price_jul = float(v31_j["close"])
                price_source_jul = "CMC v3.1 Exact Unrounded"
            elif cs_jul > 0 and mcap_jul > 0:
                price_jul = mcap_jul / cs_jul
                price_source_jul = "CMC Implied Exact (MCap/Supply)"

        ro = oct_by_id.get(cid)
        note = ""
        status_oct = "ACTIVE"
        source_oct = "CMC Snapshot"
        cmc_rank_oct = None
        price_oct = None
        mcap_oct = None
        cs_oct = None
        vol_oct = None

        if ro is not None:
            qo = ro["quotes"][0]
            cmc_rank_oct = ro.get("cmcRank")
            price_oct = float(qo["price"])
            mcap_oct = float(qo["marketCap"])
            cs_oct = float(ro.get("circulatingSupply") or 0.0)
            vol_oct = float(qo.get("volume24h") or 0.0)

            if price_oct < 0.01:
                v31_o = subcent_v31.get(scid, {}).get("2026-10-01", {})
                if "close" in v31_o and v31_o["close"] > 0:
                    price_oct = float(v31_o["close"])
                    source_oct = "CMC v3.1 Exact Unrounded"
                elif cs_oct > 0 and mcap_oct > 0:
                    price_oct = mcap_oct / cs_oct
                    source_oct = "CMC Implied Exact (MCap/Supply)"

            if mcap_oct == 0.0:
                status_oct = "ACTIVE_UNVERIFIED_SUPPLY"
                imp_mcap = cs_jul * price_oct
                note = f"Crollo del prezzo con rimozione della verifica supply su CMC al 2026-10-01 (mcap ufficiale CMC `$0`; mcap implicita a supply costante: `${imp_mcap:,.2f}`)."
        else:
            status_oct = "UNTRACKED"
            source_oct = "Delisted / Untracked pre-2026-10-01"
            mu = untracked_meta.get(cid, {})
            if mu:
                note = f"Untracked prima del 1° ott 2026 (ultimo dato `{mu['last_date']}`: P=`{fmt_price(mu['last_price_usd'])}`, MCap=`{fmt_mcap(mu['last_mcap_usd'])}`). {mu['reason']}"

        price_change_pct = ((price_oct - price_jul) / price_jul * 100.0) if (price_oct is not None and price_jul > 0) else None
        mcap_change_pct = ((mcap_oct - mcap_jul) / mcap_jul * 100.0) if (mcap_oct is not None and mcap_jul > 0) else None

        # Dubious flags for interactive filtering & transparency
        dubious_flags = []
        if vol_jul < 10000:
            dubious_flags.append("GHOST_VOL_LT_10K")
        elif vol_jul < 100000:
            dubious_flags.append("LOW_LIQ_VOL_LT_100K")
        if cid in ZOMBIE_IDS:
            dubious_flags.append("ZOMBIE_BANKRUPT_LEGACY")
        if cid in SUBNET_IDS:
            dubious_flags.append("BITTENSOR_SUBNET_TOKEN")
        if cid in GAS_DUAL_IDS:
            dubious_flags.append("SECONDARY_GAS_TOKEN")
        if cid in CEX_IDS:
            dubious_flags.append("CEX_EXCHANGE_TOKEN")
        if "memes" in tags:
            dubious_flags.append("MEMECOIN")

        records.append({
            "forensic_id": forensic_id,
            "rank_pure_jul1": idx,
            "cmc_rank_jul1": rj["cmcRank"],
            "cmc_id": cid,
            "name": rj["name"].replace("\n", " "),
            "symbol": rj["symbol"],
            "slug": rj["slug"],
            "price_jul1_usd": price_jul,
            "mcap_jul1_usd": mcap_jul,
            "circulating_supply_jul1": cs_jul,
            "volume24h_jul1_usd": vol_jul,
            "price_source_jul1": price_source_jul,
            "status_oct1": status_oct,
            "cmc_rank_oct1": cmc_rank_oct,
            "price_oct1_usd": price_oct,
            "mcap_oct1_usd": mcap_oct,
            "circulating_supply_oct1": cs_oct,
            "volume24h_oct1_usd": vol_oct,
            "source_oct1": source_oct,
            "price_change_pct": round(price_change_pct, 6) if price_change_pct is not None else None,
            "mcap_change_pct": round(mcap_change_pct, 6) if mcap_change_pct is not None else None,
            "dubious_flags": ",".join(dubious_flags),
            "notes": note,
        })

    # Verify strict monotonic decreasing Market Cap on July 1
    for i in range(499):
        assert records[i]["mcap_jul1_usd"] >= records[i + 1]["mcap_jul1_usd"], f"Monotonicity broken at {i}"

    total_mcap_jul1 = sum(r["mcap_jul1_usd"] for r in records)
    active_oct = [r for r in records if r["mcap_oct1_usd"] is not None]
    priced_oct = [r for r in records if r["price_oct1_usd"] is not None]
    total_mcap_oct1_active = sum(r["mcap_oct1_usd"] for r in active_oct)
    total_mcap_jul1_active = sum(r["mcap_jul1_usd"] for r in active_oct)

    price_pcts = [r["price_change_pct"] for r in priced_oct if r["price_change_pct"] is not None]
    mcap_pcts = [r["mcap_change_pct"] for r in active_oct if r["mcap_change_pct"] is not None]
    pos_p = sum(1 for x in price_pcts if x > 0)
    neg_p = sum(1 for x in price_pcts if x < 0)

    excl_counts = {}
    for e in excluded_list:
        excl_counts[e["reason"]] = excl_counts.get(e["reason"], 0) + 1

    summary = {
        "universe_type": "PURE_CRYPTO_TOP_500 (No Stablecoins, No Wrapped/LST/LRT/Receipts, No Tokenized Stocks/ETFs/Commodities)",
        "snapshot_date_start_utc": "2026-07-01T23:59:59.999Z",
        "snapshot_date_end_utc": "2026-10-01T23:59:59.999Z",
        "universe_size": 500,
        "excluded_above_cutoff_total": len(excluded_list),
        "excluded_breakdown": excl_counts,
        "active_priced_on_oct1": len(priced_oct),
        "untracked_delisted_by_oct1": 500 - len(priced_oct),
        "rank1_jul1_mcap_usd": records[0]["mcap_jul1_usd"],
        "rank500_jul1_mcap_usd": records[499]["mcap_jul1_usd"],
        "rank500_coin": f"{records[499]['name']} ({records[499]['symbol']})",
        "total_cohort_mcap_jul1_usd": total_mcap_jul1,
        "total_cohort_mcap_oct1_active_usd": total_mcap_oct1_active,
        "cohort_mcap_growth_active_pct": round((total_mcap_oct1_active - total_mcap_jul1_active) / total_mcap_jul1_active * 100.0, 4),
        "cohort_mcap_growth_conservative_pct": round((total_mcap_oct1_active - total_mcap_jul1) / total_mcap_jul1 * 100.0, 4),
        "median_price_return_pct": round(statistics.median(price_pcts), 4),
        "mean_price_return_pct": round(statistics.mean(price_pcts), 4),
        "median_mcap_return_pct": round(statistics.median(mcap_pcts), 4),
        "winners_price_count": pos_p,
        "losers_price_count": neg_p,
    }

    # Save Pure 500 JSON & CSV
    json_path = os.path.join(PROJ_DIR, "pure500_crypto_2026-07-01_vs_2026-10-01.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump({"metadata": summary, "excluded_above_cutoff": excluded_list, "cryptocurrencies": records}, f, indent=2, ensure_ascii=False)

    csv_path = os.path.join(PROJ_DIR, "pure500_crypto_2026-07-01_vs_2026-10-01.csv")
    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    # Build Markdown Dossier (500/500 Pure Cryptos, KaTeX-safe, Zero Truncation)
    top_gainers = sorted(priced_oct, key=lambda x: x["price_change_pct"], reverse=True)[:15]
    top_losers = sorted(priced_oct, key=lambda x: x["price_change_pct"])[:15]

    md = []
    md.append("# Dossier Pure Crypto Top 500 per Capitalizzazione (1° Luglio 2026 vs 1° Ottobre 2026)")
    md.append("")
    md.append("> [!IMPORTANT]")
    md.append("> **Universo Pure Crypto Point-in-Time (500/500 Criptovalute Native & di Protocollo — Zero Stablecoin, Zero Wrapped/LST/LRT, Zero ETF/Azioni/Materie Prime Tokenizzate)**")
    md.append("> Dalla classifica globale per capitalizzazione del **1° luglio 2026 (`2026-07-01 23:59:59 UTC`)** sono stati filtrati ed esclusi **229 asset non-puri** (`66` Stablecoin, `70` Token Wrapped / Liquid Staking / Restaking / Receipt / LP Basket, `93` Azioni, ETF, Pre-IPO e Materie Prime Tokenizzate), scorrendo la graduatoria fino alla posizione globale `CMC #729` (`Open Campus [EDU]`, `$23,907,077`) così da ottenere esattamente le **prime 500 criptovalute pure per capitalizzazione**.")
    md.append("")
    md.append("**File Dataset & Strumenti Generati (Versione Pure Crypto):**")
    md.append("- Tabella CSV Pure Crypto (500 righe): [pure500_crypto_2026-07-01_vs_2026-10-01.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/pure500_crypto_2026-07-01_vs_2026-10-01.csv)")
    md.append("- Dataset JSON Pure Crypto + Elenco Esclusi: [pure500_crypto_2026-07-01_vs_2026-10-01.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/pure500_crypto_2026-07-01_vs_2026-10-01.json)")
    md.append("- Elenco completo dei 229 asset rimossi con motivazione: [excluded_229_non_pure_assets.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/excluded_229_non_pure_assets.csv)")
    md.append("- Dashboard Interattiva HTML Pure Crypto (con filtri rapidi per i casi dubbi): [dashboard_pure500_crypto_2026.html](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/dashboard_pure500_crypto_2026.html)")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Sintesi Macroeconomica Pure Crypto Top 500 (1° Luglio → 1° Ottobre 2026)")
    md.append("")
    md.append("| Metrica Aggregata Coorte Pure Crypto (500 Asset del 1° Luglio 2026) | Valore Certificato |")
    md.append("| :--- | ---: |")
    md.append(f"| **Asset Non-Puri Rimossi sopra la soglia #500** | **229** (`66` Stablecoin + `70` Wrapped/LST/Receipt + `93` ETF/Stock/Gold Tokenizzati) |")
    md.append(f"| **Criptovalute Pure Censite (1:1)** | **500 / 500** (`100.00%`) |")
    md.append(f"| **Attive al 1° Ottobre 2026 / Delistate pre-1° Ottobre** | **{len(priced_oct)} attive** / **{500 - len(priced_oct)} untracked** (`WIBE`, `LIGHT`) |")
    md.append(f"| **Capitalizzazione #1 al 1° Luglio 2026 (`Bitcoin`)** | **`${records[0]['mcap_jul1_usd']:,.2f}`** (Prezzo: `${records[0]['price_jul1_usd']:,.2f}`) |")
    md.append(f"| **Nuova Soglia #500 Pure Crypto (`Open Campus [EDU]`, `CMC #729`)** | **`${records[499]['mcap_jul1_usd']:,.2f}`** (Prezzo: `${records[499]['price_jul1_usd']:.6f}`) |")
    md.append(f"| **Capitalizzazione Aggregata Pure 500 al 1° Luglio 2026** | **`${total_mcap_jul1:,.2f}`** (`${total_mcap_jul1/1e12:.3f} Trilioni`) |")
    md.append(f"| **Capitalizzazione Aggregata Pure 500 al 1° Ottobre 2026** | **`${total_mcap_oct1_active:,.2f}`** (`${total_mcap_oct1_active/1e12:.3f} Trilioni`) |")
    md.append(f"| **Crescita Capitalizzazione Coorte Pure Crypto (perimetro attivo)** | **{summary['cohort_mcap_growth_active_pct']:+.2f}%** (`+${total_mcap_oct1_active - total_mcap_jul1_active:,.0f}`) |")
    md.append(f"| **Crescita Capitalizzazione Coorte Pure Crypto (prudenziale con 2 untracked = `$0`)** | **{summary['cohort_mcap_growth_conservative_pct']:+.2f}%** (`+${total_mcap_oct1_active - total_mcap_jul1:,.0f}`) |")
    md.append(f"| **Rendimento Mediano di Prezzo (498 asset quotati)** | **{summary['median_price_return_pct']:+.2f}%** |")
    md.append(f"| **Rendimento Medio Equipesato di Prezzo (498 asset quotati)** | **{summary['mean_price_return_pct']:+.2f}%** |")
    md.append(f"| **Variazione Mediana di Market Cap (498 asset quotati)** | **{summary['median_mcap_return_pct']:+.2f}%** |")
    md.append(f"| **Bilancio Performance Prezzo (Rialzo / Ribasso)** | **{pos_p} positivi** (`{pos_p/len(priced_oct)*100:.1f}%`) / **{neg_p} negativi** (`{neg_p/len(priced_oct)*100:.1f}%`) |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Top 15 Maggiori Rialzi e Top 15 Maggiori Ribassi — Universo Pure Crypto")
    md.append("")
    md.append("### Top 15 Performance Positive (Prezzo USD)")
    md.append("")
    md.append("| Rank Pure | ID | Criptovaluta (Ticker) | Prezzo 1 Lug 2026 | Prezzo 1 Ott 2026 | Δ% Prezzo | Market Cap 1 Lug 2026 | Market Cap 1 Ott 2026 | Δ% MCap |")
    md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in top_gainers:
        md.append(
            f"| #{r['rank_pure_jul1']:03d} | `{r['forensic_id']}` | **{r['name']}** (`{r['symbol']}`) | `{fmt_price(r['price_jul1_usd'])}` | `{fmt_price(r['price_oct1_usd'])}` | **{fmt_pct(r['price_change_pct'])}** | `{fmt_mcap(r['mcap_jul1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` | {fmt_pct(r['mcap_change_pct'])} |"
        )
    md.append("")
    md.append("### Top 15 Performance Negative (Prezzo USD, Asset Attivi)")
    md.append("")
    md.append("| Rank Pure | ID | Criptovaluta (Ticker) | Prezzo 1 Lug 2026 | Prezzo 1 Ott 2026 | Δ% Prezzo | Market Cap 1 Lug 2026 | Market Cap 1 Ott 2026 | Δ% MCap |")
    md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in top_losers:
        md.append(
            f"| #{r['rank_pure_jul1']:03d} | `{r['forensic_id']}` | **{r['name']}** (`{r['symbol']}`) | `{fmt_price(r['price_jul1_usd'])}` | `{fmt_price(r['price_oct1_usd'])}` | **{fmt_pct(r['price_change_pct'])}** | `{fmt_mcap(r['mcap_jul1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` | {fmt_pct(r['mcap_change_pct'])} |"
        )
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. Tabella Integrale 1:1 — Tutte le 500 Criptovalute Pure per Capitalizzazione (1° Luglio 2026 vs 1° Ottobre 2026)")
    md.append("")
    md.append("| # Pure | CMC # | ID | Nome | Ticker | Prezzo 1 Lug 2026 | Market Cap 1 Lug 2026 | Prezzo 1 Ott 2026 | Market Cap 1 Ott 2026 | Δ% Prezzo | Δ% MCap | Flag / Note |")
    md.append("| ---: | ---: | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |")
    for r in records:
        safe_name = r["name"].replace("|", "/").replace("$", "\\$")
        safe_sym = r["symbol"].replace("|", "/")
        flag_str = r["dubious_flags"] if r["dubious_flags"] else "—"
        if r["status_oct1"] != "ACTIVE":
            flag_str = f"{r['status_oct1']}" + (f" | {flag_str}" if flag_str != "—" else "")
        md.append(
            f"| {r['rank_pure_jul1']:03d} | {r['cmc_rank_jul1']} | `{r['forensic_id']}` | {safe_name} | `{safe_sym}` "
            f"| `{fmt_price(r['price_jul1_usd'])}` | `{fmt_mcap(r['mcap_jul1_usd'])}` "
            f"| `{fmt_price(r['price_oct1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` "
            f"| {fmt_pct(r['price_change_pct'])} | {fmt_pct(r['mcap_change_pct'])} | {flag_str} |"
        )
    md.append("")

    md_text = "\n".join(md)
    proj_md = os.path.join(PROJ_DIR, "report_pure500_crypto_2026.md")
    with open(proj_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    # Interactive HTML Explorer with Dubious-Category Filter Checkboxes!
    html_path = os.path.join(PROJ_DIR, "dashboard_pure500_crypto_2026.html")
    html_payload = json.dumps({"summary": summary, "rows": records}, ensure_ascii=False)
    html_doc = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Pure Crypto Top 500 — 1 Luglio 2026 vs 1 Ottobre 2026</title>
<style>
  :root {{
    --bg: #0b0f17; --panel: #131a26; --border: #232f42; --text: #e6edf3;
    --muted: #8b9bb4; --accent: #3b82f6; --pos: #10b981; --neg: #ef4444; --warn: #f59e0b;
  }}
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: var(--bg); color: var(--text); }}
  header {{ padding: 24px 32px; border-bottom: 1px solid var(--border); background: #0f1520; }}
  h1 {{ margin: 0 0 8px; font-size: 22px; }}
  .sub {{ color: var(--muted); font-size: 14px; }}
  .kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; padding: 20px 32px; }}
  .kpi {{ background: var(--panel); border: 1px solid var(--border); border-radius: 10px; padding: 14px 16px; }}
  .kpi .lbl {{ font-size: 12px; color: var(--muted); text-transform: uppercase; }}
  .kpi .val {{ font-size: 20px; font-weight: 700; margin-top: 6px; }}
  .controls {{ display: flex; flex-wrap: wrap; gap: 12px; padding: 0 32px 16px; align-items: center; }}
  input[type="text"], select {{ background: var(--panel); color: var(--text); border: 1px solid var(--border); border-radius: 8px; padding: 9px 12px; font-size: 14px; }}
  input[type="text"] {{ min-width: 260px; }}
  .chk {{ display: inline-flex; align-items: center; gap: 6px; font-size: 13px; background: var(--panel); border: 1px solid var(--border); padding: 7px 10px; border-radius: 8px; cursor: pointer; }}
  .count-badge {{ margin-left: auto; color: var(--muted); font-size: 13px; }}
  .table-wrap {{ padding: 0 32px 40px; overflow-x: auto; }}
  table {{ width: 100%; border-collapse: collapse; background: var(--panel); border: 1px solid var(--border); border-radius: 10px; overflow: hidden; font-size: 13px; }}
  th, td {{ padding: 10px 12px; border-bottom: 1px solid var(--border); white-space: nowrap; text-align: right; }}
  th:nth-child(3), th:nth-child(4), td:nth-child(3), td:nth-child(4) {{ text-align: left; }}
  th {{ background: #182232; color: var(--muted); cursor: pointer; user-select: none; position: sticky; top: 0; }}
  tr:hover td {{ background: rgba(59,130,246,0.07); }}
  .pos {{ color: var(--pos); font-weight: 600; }}
  .neg {{ color: var(--neg); font-weight: 600; }}
  .tag {{ font-size: 11px; padding: 2px 6px; border-radius: 4px; background: #1f2b3d; color: var(--muted); }}
  .tag-warn {{ background: rgba(245,158,11,0.16); color: var(--warn); }}
</style>
</head>
<body>
<header>
  <h1>Pure Crypto Top 500: 1° Luglio 2026 vs 1° Ottobre 2026</h1>
  <div class="sub">Rimossi 229 asset non-puri (66 Stablecoin • 70 Wrapped/LST/Receipt • 93 ETF/Azioni/Materie Prime Tokenizzate) • 500/500 Criptovalute Pure</div>
</header>
<div class="kpis" id="kpis"></div>
<div class="controls">
  <input type="text" id="q" placeholder="Cerca nome, ticker o ID (es. BTC, SOL, cmc-1)...">
  <select id="filter">
    <option value="ALL">Tutte le 500 Pure Crypto</option>
    <option value="DUBIOUS_ONLY">Mostra solo Casi Dubbi segnalati</option>
    <option value="GAINERS">Solo in rialzo (Δ% > 0)</option>
    <option value="LOSERS">Solo in ribasso (Δ% < 0)</option>
  </select>
  <label class="chk"><input type="checkbox" id="exGhost"> Nascondi Illiquidi (&lt;$100k vol)</label>
  <label class="chk"><input type="checkbox" id="exZombie"> Nascondi Zombie/Falliti</label>
  <label class="chk"><input type="checkbox" id="exMeme"> Nascondi Memecoin</label>
  <span class="count-badge" id="countBadge"></span>
</div>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th data-k="rank_pure_jul1"># Pure</th>
        <th data-k="cmc_rank_jul1">CMC #</th>
        <th data-k="name">Criptovaluta</th>
        <th data-k="symbol">Ticker</th>
        <th data-k="price_jul1_usd">Prezzo 1 Lug 26</th>
        <th data-k="mcap_jul1_usd">Market Cap 1 Lug 26</th>
        <th data-k="volume24h_jul1_usd">Vol 24h 1 Lug</th>
        <th data-k="price_oct1_usd">Prezzo 1 Ott 26</th>
        <th data-k="mcap_oct1_usd">Market Cap 1 Ott 26</th>
        <th data-k="price_change_pct">Δ% Prezzo</th>
        <th data-k="mcap_change_pct">Δ% MCap</th>
        <th data-k="dubious_flags">Flag</th>
      </tr>
    </thead>
    <tbody id="tb"></tbody>
  </table>
</div>
<script>
const DATA = {html_payload};
let sortKey = 'rank_pure_jul1', sortDir = 1;
function fmtPrice(p) {{
  if (p === null || p === undefined) return 'N/D';
  const ap = Math.abs(p);
  if (ap >= 1000) return '$' + p.toLocaleString('en-US', {{minimumFractionDigits:2, maximumFractionDigits:2}});
  if (ap >= 1) return '$' + p.toLocaleString('en-US', {{minimumFractionDigits:4, maximumFractionDigits:4}});
  if (ap >= 0.01) return '$' + p.toFixed(6);
  if (ap >= 0.0001) return '$' + p.toFixed(8);
  if (ap >= 1e-6) return '$' + p.toFixed(10);
  return '$' + p.toExponential(4);
}}
function fmtMcap(m) {{ return (m === null || m === undefined) ? 'N/D' : '$' + Math.round(m).toLocaleString('en-US'); }}
function fmtPct(v) {{ return (v === null || v === undefined) ? 'N/D' : (v >= 0 ? '+' : '') + v.toFixed(2) + '%'; }}

function render() {{
  const q = document.getElementById('q').value.trim().toLowerCase();
  const f = document.getElementById('filter').value;
  const exG = document.getElementById('exGhost').checked;
  const exZ = document.getElementById('exZombie').checked;
  const exM = document.getElementById('exMeme').checked;
  let rows = DATA.rows.filter(r => {{
    if (q && !(r.name.toLowerCase().includes(q) || r.symbol.toLowerCase().includes(q) || r.forensic_id.toLowerCase().includes(q))) return false;
    if (exG && (r.dubious_flags.includes('GHOST_VOL_LT_10K') || r.dubious_flags.includes('LOW_LIQ_VOL_LT_100K'))) return false;
    if (exZ && r.dubious_flags.includes('ZOMBIE_BANKRUPT_LEGACY')) return false;
    if (exM && r.dubious_flags.includes('MEMECOIN')) return false;
    if (f === 'DUBIOUS_ONLY') return r.dubious_flags !== '';
    if (f === 'GAINERS') return r.price_change_pct !== null && r.price_change_pct > 0;
    if (f === 'LOSERS') return r.price_change_pct !== null && r.price_change_pct < 0;
    return true;
  }});
  const mJul = rows.reduce((s, r) => s + r.mcap_jul1_usd, 0);
  const mOct = rows.reduce((s, r) => s + (r.mcap_oct1_usd || 0), 0);
  const pcts = rows.filter(r => r.price_change_pct !== null).map(r => r.price_change_pct).sort((a,b)=>a-b);
  const med = pcts.length ? pcts[Math.floor(pcts.length/2)] : 0;
  document.getElementById('kpis').innerHTML = `
    <div class="kpi"><div class="lbl">Market Cap 1 Lug (${{rows.length}} asset)</div><div class="val">${{'$' + (mJul/1e12).toFixed(3) + 'T'}}</div></div>
    <div class="kpi"><div class="lbl">Market Cap 1 Ott</div><div class="val">${{'$' + (mOct/1e12).toFixed(3) + 'T'}}</div></div>
    <div class="kpi"><div class="lbl">Δ% Market Cap Aggregata</div><div class="val ${{mOct>=mJul?'pos':'neg'}}">${{fmtPct((mOct-mJul)/mJul*100)}}</div></div>
    <div class="kpi"><div class="lbl">Rendimento Mediano Prezzo</div><div class="val ${{med>=0?'pos':'neg'}}">${{fmtPct(med)}}</div></div>
  `;
  rows.sort((a, b) => {{
    let va = a[sortKey], vb = b[sortKey];
    if (va === null || va === undefined) return 1;
    if (vb === null || vb === undefined) return -1;
    return typeof va === 'string' ? va.localeCompare(vb) * sortDir : (va - vb) * sortDir;
  }});
  document.getElementById('countBadge').textContent = `Visualizzati ${{rows.length}} su 500 asset`;
  document.getElementById('tb').innerHTML = rows.map(r => `
    <tr title="${{r.notes || ''}}">
      <td>${{r.rank_pure_jul1}}</td>
      <td>${{r.cmc_rank_jul1}}</td>
      <td><strong>${{r.name}}</strong> <span class="tag">${{r.forensic_id}}</span></td>
      <td><code>${{r.symbol}}</code></td>
      <td>${{fmtPrice(r.price_jul1_usd)}}</td>
      <td>${{fmtMcap(r.mcap_jul1_usd)}}</td>
      <td>${{fmtMcap(r.volume24h_jul1_usd)}}</td>
      <td>${{fmtPrice(r.price_oct1_usd)}}</td>
      <td>${{fmtMcap(r.mcap_oct1_usd)}}</td>
      <td class="${{r.price_change_pct>0?'pos':(r.price_change_pct<0?'neg':'')}}">${{fmtPct(r.price_change_pct)}}</td>
      <td class="${{r.mcap_change_pct>0?'pos':(r.mcap_change_pct<0?'neg':'')}}">${{fmtPct(r.mcap_change_pct)}}</td>
      <td>${{r.dubious_flags ? `<span class="tag tag-warn">${{r.dubious_flags}}</span>` : '<span class="tag">OK</span>'}}</td>
    </tr>
  `).join('');
}}
['q','filter','exGhost','exZombie','exMeme'].forEach(id => document.getElementById(id).addEventListener('input', render));
document.querySelectorAll('th[data-k]').forEach(th => th.addEventListener('click', () => {{
  if (sortKey === th.dataset.k) sortDir *= -1; else {{ sortKey = th.dataset.k; sortDir = 1; }}
  render();
}}));
render();
</script>
</body>
</html>
"""
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_doc)

    # Manifest for Pure 500 audit gate
    manifest_pure = {
        "target": "Pure Crypto Top 500 (2026-07-01 vs 2026-10-01)",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "expected_counts": {"pure500_cryptos": 500},
        "sources": [
            f"pure500_json={json_path}:cryptocurrencies:forensic_id",
            f"pure500_csv={csv_path}::forensic_id",
        ],
        "required_files": [json_path, csv_path, excl_csv, html_path],
    }
    with open(os.path.join(PROJ_DIR, "manifest_pure500.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_pure, f, indent=2)

    # Verify zero unescaped bare '$' in Markdown
    for i, ln in enumerate(md_text.splitlines(), 1):
        rem = re.sub(r"`[^`]*`", "", ln).replace("\\$", "")
        assert "$" not in rem, f"Unescaped '$' at line {i}: {rem}"

    print("=== PURE 500 BUILD & INTERNAL VERIFICATION COMPLETE ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
