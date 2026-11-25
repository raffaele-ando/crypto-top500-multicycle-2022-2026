#!/usr/bin/env python3
"""
Enriches ALL complete 500-row lists ("gli elenchi che hanno tutto") with exact
21 November 2026 05:30 CET (2026-11-21 04:30:00 UTC) Price, Market Cap, % Deltas,
and €5 Real-EUR Ticket Values:
  1. Original Global Top 500 (CSV, JSON, MD, HTML)
  2. Clean Pure Crypto Top 500 (CSV, JSON, pure500_*, MD, HTML)
  3. Complete 500 Return Ranking (CSV, JSON, MD)
  4. Complete €5 x 500 Simulation CSV (Jul 1 -> Oct 1 -> Nov 21 05:30 CET)
  5. Complete N=1..500 Marginal Curve (CSV, JSON, MD, HTML)
"""

import csv
import datetime
import json
import os
import re
import statistics

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")
ARTIFACT_DIR = r"C:\Users\Administrator\.gemini\antigravity\brain\ef94cd2a-0982-41cb-9b2e-62eba3745324"


def fmt_price(p):
    if p is None:
        return "N/D"
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
        return "N/D"
    return f"${m:,.0f}"


def fmt_pct(pct):
    if pct is None:
        return "N/D"
    return f"{pct:+.2f}%"


def check_katex_safe(md_text, label):
    for i, ln in enumerate(md_text.splitlines(), 1):
        rem = re.sub(r"`[^`]*`", "", ln).replace("\\$", "")
        assert "$" not in rem, f"[{label}] Unescaped '$' at line {i}: {rem}"


def enrich_nov21_fields(r, nov_map, fx_jul, fx_nov):
    scid = str(r["cmc_id"])
    nv = nov_map.get(scid)
    pj = r["price_jul1_usd"]
    mj = r["mcap_jul1_usd"]
    po = r.get("price_oct1_usd")

    if nv and nv.get("price_usd") is not None:
        pn = float(nv["price_usd"])
        mn = float(nv["marketCap_usd"])
        ts_n = nv.get("ts_utc", "2026-11-21 04:30:00 UTC")
        pct_p_jul_nov = round((pn - pj) / pj * 100.0, 6) if pj > 0 else None
        pct_m_jul_nov = round((mn - mj) / mj * 100.0, 6) if (mj > 0 and mn > 0) else (None if mn == 0 else None)
        if mn == 0.0:
            pct_m_jul_nov = -100.0
        pct_p_oct_nov = round((pn - po) / po * 100.0, 6) if (po is not None and po > 0) else None
        val_5eur_nov = round(5.0 * (pn / pj) * (fx_jul / fx_nov), 4) if pj > 0 else 0.0
        pct_eur_jul_nov = round((val_5eur_nov / 5.0 - 1.0) * 100.0, 4) if pj > 0 else None
        status_n = "ACTIVE" if mn > 0 else "ACTIVE_UNVERIFIED_SUPPLY"
    else:
        pn = None
        mn = None
        ts_n = None
        pct_p_jul_nov = None
        pct_m_jul_nov = None
        pct_p_oct_nov = None
        val_5eur_nov = 0.0
        pct_eur_jul_nov = -100.0
        status_n = "UNTRACKED"

    r["status_nov21_0530"] = status_n
    r["ts_nov21_utc"] = ts_n
    r["price_nov21_0530_usd"] = pn
    r["mcap_nov21_0530_usd"] = mn
    r["price_change_jul_to_nov21_pct"] = pct_p_jul_nov
    r["mcap_change_jul_to_nov21_pct"] = pct_m_jul_nov
    r["price_change_oct_to_nov21_pct"] = pct_p_oct_nov
    r["ticket_5eur_nov21_eur"] = val_5eur_nov
    r["return_jul_to_nov21_eur_pct"] = pct_eur_jul_nov
    return r


def main():
    with open(os.path.join(RAW_DIR, "cmc_nov21_0530cet_all682.json"), encoding="utf-8") as f:
        nov_doc = json.load(f)
    nov_map = nov_doc["coins"]

    # Check if we also have recovered fallbacks file
    rec_path = os.path.join(RAW_DIR, "cmc_nov21_recovered.json")
    if os.path.exists(rec_path):
        with open(rec_path, encoding="utf-8") as f:
            nov_map.update(json.load(f))

    with open(os.path.join(PROJ_DIR, "simulazione_5eur_summary.json"), encoding="utf-8") as f:
        fx_old = json.load(f)

    fx_jul = fx_old["fx_eur_usd_jul1"]
    fx_oct = fx_old["fx_eur_usd_oct1"]
    # CMC detail/chart ignores convertId=2790; use exact 2026-11-21 04:30 UTC Binance EURUSDT 1m close (1.0960, verified vs EURC 1.0957 & ECB 1.0990)
    fx_nov = float(nov_doc["fx_eur_usd_binance"])
    fx_factor_oct = fx_jul / fx_oct
    fx_factor_nov = fx_jul / fx_nov

    # =========================================================================
    # 1. ENRICH ORIGINAL TOP 500 (CSV, JSON, MD, HTML)
    # =========================================================================
    orig_json_path = os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.json")
    with open(orig_json_path, encoding="utf-8") as f:
        orig_doc = json.load(f)
    orig_rows = [enrich_nov21_fields(r, nov_map, fx_jul, fx_nov) for r in orig_doc["cryptocurrencies"]]
    orig_active_nov = [r for r in orig_rows if r["price_nov21_0530_usd"] is not None]
    orig_mcap_nov = sum(r["mcap_nov21_0530_usd"] for r in orig_rows if r["mcap_nov21_0530_usd"] is not None)
    orig_doc["metadata"]["snapshot_date_nov21_local"] = "2026-11-21T05:30:00+01:00"
    orig_doc["metadata"]["snapshot_date_nov21_utc"] = "2026-11-21T04:30:00Z"
    orig_doc["metadata"]["fx_eur_usd_nov21_0530"] = fx_nov
    orig_doc["metadata"]["active_priced_on_nov21_0530"] = len(orig_active_nov)
    orig_doc["metadata"]["total_cohort_mcap_nov21_0530_usd"] = orig_mcap_nov
    orig_doc["cryptocurrencies"] = orig_rows

    with open(orig_json_path, "w", encoding="utf-8") as f:
        json.dump(orig_doc, f, indent=2, ensure_ascii=False)
    orig_csv_path = os.path.join(PROJ_DIR, "top500_crypto_2026-07-01_vs_2026-10-01.csv")
    with open(orig_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(orig_rows[0].keys()))
        w.writeheader()
        w.writerows(orig_rows)

    # Update report_top500_crypto_2026.md (both project & artifact)
    m = orig_doc["metadata"]
    orig_md = []
    orig_md.append("# Dossier Integrale Verificato: Prime 500 Criptovalute per Capitalizzazione (1° Luglio 2026 vs 1° Ottobre 2026 vs 21 Novembre 2026 ore 05:30)")
    orig_md.append("")
    orig_md.append("> [!IMPORTANT]")
    orig_md.append("> **Universo Point-in-Time Completo (`500/500`) su 3 Date Certificate:** `2026-07-01 23:59:59 UTC`, `2026-10-01 23:59:59 UTC` e **`2026-11-21 05:30:00 CET` (`04:30:00 UTC`)** (rilevazione intraday a 5 minuti verificata contro Binance `1m`).")
    orig_md.append("")
    orig_md.append("**File Dataset & Strumenti Generati:**")
    orig_md.append("- Dataset CSV completo (`500` righe, 3 date): [top500_crypto_2026-07-01_vs_2026-10-01.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/top500_crypto_2026-07-01_vs_2026-10-01.csv)")
    orig_md.append("- Dataset JSON completo: [top500_crypto_2026-07-01_vs_2026-10-01.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/top500_crypto_2026-07-01_vs_2026-10-01.json)")
    orig_md.append("- Dashboard HTML interattiva (3 date): [dashboard_top500_crypto_2026.html](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/dashboard_top500_crypto_2026.html)")
    orig_md.append("")
    orig_md.append("## 1. Sintesi Macroeconomica Coorte Globale Top 500 (3 Date)")
    orig_md.append("")
    orig_md.append("| Metrica Coorte Originale (500 Asset del 1° Luglio 2026) | 1° Luglio 2026 | 1° Ottobre 2026 | 21 Nov 2026 `05:30 CET` |")
    orig_md.append("| :--- | ---: | ---: | ---: |")
    orig_md.append(f"| **Asset Attivi / Quotati** | `500 / 500` | `{m['active_priced_on_oct1']} / 500` | `{len(orig_active_nov)} / 500` |")
    orig_md.append(f"| **Market Cap Aggregata Coorte** | `${m['total_cohort_mcap_jul1_usd']:,.0f}` | `${m['total_cohort_mcap_oct1_active_usd']:,.0f}` | `${orig_mcap_nov:,.0f}` |")
    orig_md.append(f"| **Prezzo Bitcoin (`BTC`)** | `{fmt_price(orig_rows[0]['price_jul1_usd'])}` | `{fmt_price(orig_rows[0]['price_oct1_usd'])}` | `{fmt_price(orig_rows[0]['price_nov21_0530_usd'])}` |")
    orig_md.append("")
    orig_md.append("## 2. Tabella Integrale 1:1 — Tutte le 500 Criptovalute Originali (1° Luglio · 1° Ottobre · 21 Novembre `05:30`)")
    orig_md.append("")
    orig_md.append("| # MCap | CMC # | ID | Nome (`Ticker`) | Prezzo 1 Lug | MCap 1 Lug | Prezzo 1 Ott | MCap 1 Ott | Prezzo 21 Nov 05:30 | MCap 21 Nov 05:30 | Δ% Lug→Ott | Δ% Lug→21 Nov | Δ% Ott→21 Nov |")
    orig_md.append("| ---: | ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in orig_rows:
        nm = r["name"].replace("|", "/").replace("$", "\\$")
        sym = r["symbol"].replace("|", "/")
        orig_md.append(
            f"| {r['rank_mcap_jul1']:03d} | {r['cmc_rank_jul1']} | `{r['forensic_id']}` | {nm} (`{sym}`) "
            f"| `{fmt_price(r['price_jul1_usd'])}` | `{fmt_mcap(r['mcap_jul1_usd'])}` "
            f"| `{fmt_price(r['price_oct1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` "
            f"| `{fmt_price(r['price_nov21_0530_usd'])}` | `{fmt_mcap(r['mcap_nov21_0530_usd'])}` "
            f"| {fmt_pct(r['price_change_pct'])} | {fmt_pct(r['price_change_jul_to_nov21_pct'])} | {fmt_pct(r['price_change_oct_to_nov21_pct'])} |"
        )
    orig_md_txt = "\n".join(orig_md) + "\n"
    check_katex_safe(orig_md_txt, "report_top500_crypto_2026.md")
    for p in (os.path.join(PROJ_DIR, "report_top500_crypto_2026.md"), os.path.join(ARTIFACT_DIR, "report_top500_crypto_2026.md")):
        with open(p, "w", encoding="utf-8") as f:
            f.write(orig_md_txt)

    # Update dashboard_top500_crypto_2026.html
    orig_html_data = json.dumps({"summary": orig_doc["metadata"], "rows": orig_rows}, ensure_ascii=False)
    orig_html = f"""<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8"><title>Top 500 Crypto — 1 Lug · 1 Ott · 21 Nov 05:30</title>
<style>body{{margin:0;font-family:-apple-system,Segoe UI,sans-serif;background:#0b0f17;color:#e6edf3}}header{{padding:20px 28px;background:#0f1520;border-bottom:1px solid #232f42}}
.wrap{{padding:18px 28px}}input{{background:#131a26;color:#e6edf3;border:1px solid #232f42;border-radius:8px;padding:8px 12px;min-width:280px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;background:#131a26;font-size:12.5px}}th,td{{padding:8px 10px;border-bottom:1px solid #232f42;text-align:right;white-space:nowrap}}
th:nth-child(3),td:nth-child(3){{text-align:left}}th{{background:#182232;color:#8b9bb4;position:sticky;top:0;cursor:pointer}}.pos{{color:#10b981;font-weight:600}}.neg{{color:#ef4444;font-weight:600}}</style></head>
<body><header><h1 style="margin:0 0 6px;font-size:20px">Top 500 Criptovalute Originali — 1° Luglio · 1° Ottobre · 21 Novembre 2026 (05:30 CET)</h1>
<div style="color:#8b9bb4;font-size:13px">500/500 asset censiti • Clicca sulle intestazioni per ordinare</div></header>
<div class="wrap"><input id="q" placeholder="Cerca nome, ticker o cmc-ID...">
<div style="overflow-x:auto"><table><thead><tr>
<th data-k="rank_mcap_jul1">#</th><th data-k="cmc_rank_jul1">CMC#</th><th data-k="name">Criptovaluta</th>
<th data-k="price_jul1_usd">Prezzo 1 Lug</th><th data-k="mcap_jul1_usd">MCap 1 Lug</th>
<th data-k="price_oct1_usd">Prezzo 1 Ott</th><th data-k="mcap_oct1_usd">MCap 1 Ott</th>
<th data-k="price_nov21_0530_usd">Prezzo 21 Nov 05:30</th><th data-k="mcap_nov21_0530_usd">MCap 21 Nov 05:30</th>
<th data-k="price_change_pct">Δ% Lug→Ott</th><th data-k="price_change_jul_to_nov21_pct">Δ% Lug→21 Nov</th><th data-k="price_change_oct_to_nov21_pct">Δ% Ott→21 Nov</th>
</tr></thead><tbody id="tb"></tbody></table></div></div>
<script>const D={orig_html_data}.rows;let sk='rank_mcap_jul1',sd=1;
const fp=p=>p==null?'N/D':(Math.abs(p)>=1000?'$'+p.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}}):(Math.abs(p)>=1?'$'+p.toFixed(4):(Math.abs(p)>=1e-4?'$'+p.toFixed(6):'$'+p.toExponential(3))));
const fm=m=>m==null?'N/D':'$'+Math.round(m).toLocaleString('en-US');
const fpc=v=>v==null?'N/D':(v>=0?'+':'')+v.toFixed(2)+'%';
function ren(){{const q=document.getElementById('q').value.trim().toLowerCase();
let rs=D.filter(r=>!q||r.name.toLowerCase().includes(q)||r.symbol.toLowerCase().includes(q)||r.forensic_id.includes(q));
rs.sort((a,b)=>{{let va=a[sk],vb=b[sk];if(va==null)return 1;if(vb==null)return -1;return typeof va==='string'?va.localeCompare(vb)*sd:(va-vb)*sd;}});
document.getElementById('tb').innerHTML=rs.map(r=>`<tr><td>${{r.rank_mcap_jul1}}</td><td>${{r.cmc_rank_jul1}}</td><td><strong>${{r.name}}</strong> (<code>${{r.symbol}}</code>) <small style="color:#64748b">${{r.forensic_id}}</small></td><td>${{fp(r.price_jul1_usd)}}</td><td>${{fm(r.mcap_jul1_usd)}}</td><td>${{fp(r.price_oct1_usd)}}</td><td>${{fm(r.mcap_oct1_usd)}}</td><td>${{fp(r.price_nov21_0530_usd)}}</td><td>${{fm(r.mcap_nov21_0530_usd)}}</td><td class="${{r.price_change_pct>0?'pos':'neg'}}">${{fpc(r.price_change_pct)}}</td><td class="${{r.price_change_jul_to_nov21_pct>0?'pos':'neg'}}">${{fpc(r.price_change_jul_to_nov21_pct)}}</td><td class="${{r.price_change_oct_to_nov21_pct>0?'pos':'neg'}}">${{fpc(r.price_change_oct_to_nov21_pct)}}</td></tr>`).join('');}}
document.getElementById('q').addEventListener('input',ren);document.querySelectorAll('th[data-k]').forEach(t=>t.addEventListener('click',()=>{{sk===t.dataset.k?sd*=-1:(sk=t.dataset.k,sd=1);ren();}}));ren();
</script></body></html>"""
    with open(os.path.join(PROJ_DIR, "dashboard_top500_crypto_2026.html"), "w", encoding="utf-8") as f:
        f.write(orig_html)

    # =========================================================================
    # 2. ENRICH CLEAN PURE CRYPTO TOP 500 (CSV, JSON, pure500_*, MD, HTML)
    # =========================================================================
    clean_json_path = os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json")
    with open(clean_json_path, encoding="utf-8") as f:
        clean_doc = json.load(f)
    clean_rows = [enrich_nov21_fields(r, nov_map, fx_jul, fx_nov) for r in clean_doc["cryptocurrencies"]]
    clean_active_nov = [r for r in clean_rows if r["price_nov21_0530_usd"] is not None]
    clean_mcap_nov = sum(r["mcap_nov21_0530_usd"] for r in clean_rows if r["mcap_nov21_0530_usd"] is not None)
    clean_tot_5eur_nov = sum(r["ticket_5eur_nov21_eur"] for r in clean_rows)
    clean_tot_5eur_oct = sum((5.0 * (r["price_oct1_usd"] / r["price_jul1_usd"]) * fx_factor_oct) if r["price_oct1_usd"] else 0.0 for r in clean_rows)
    clean_pcts_jul_nov = [r["return_jul_to_nov21_eur_pct"] for r in clean_rows]

    cm = clean_doc["metadata"]
    cm["snapshot_date_nov21_local"] = "2026-11-21T05:30:00+01:00"
    cm["snapshot_date_nov21_utc"] = "2026-11-21T04:30:00Z"
    cm["fx_eur_usd_nov21_0530"] = fx_nov
    cm["active_priced_on_nov21_0530"] = len(clean_active_nov)
    cm["total_cohort_mcap_nov21_0530_usd"] = clean_mcap_nov
    cm["cohort_mcap_jul_to_nov21_pct"] = round((clean_mcap_nov - cm["total_cohort_mcap_jul1_usd"]) / cm["total_cohort_mcap_jul1_usd"] * 100.0, 4)
    cm["portfolio_2500eur_oct1_eur"] = round(clean_tot_5eur_oct, 2)
    cm["portfolio_2500eur_nov21_0530_eur"] = round(clean_tot_5eur_nov, 2)
    cm["portfolio_2500eur_jul_to_nov21_pct"] = round((clean_tot_5eur_nov / 2500.0 - 1.0) * 100.0, 2)
    cm["median_jul_to_nov21_eur_pct"] = round(statistics.median(clean_pcts_jul_nov), 2)
    clean_doc["cryptocurrencies"] = clean_rows

    for prefix in ("clean500", "pure500"):
        with open(os.path.join(PROJ_DIR, f"{prefix}_crypto_2026-07-01_vs_2026-10-01.json"), "w", encoding="utf-8") as f:
            json.dump(clean_doc, f, indent=2, ensure_ascii=False)
        with open(os.path.join(PROJ_DIR, f"{prefix}_crypto_2026-07-01_vs_2026-10-01.csv"), "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(clean_rows[0].keys()))
            w.writeheader()
            w.writerows(clean_rows)

    # Update report_pure500_crypto_2026.md (both project & artifact)
    clean_md = []
    clean_md.append("# Dossier Definitivo Clean Pure Crypto Top 500 (1° Luglio · 1° Ottobre · 21 Novembre 2026 ore 05:30)")
    clean_md.append("")
    clean_md.append("> [!IMPORTANT]")
    clean_md.append("> **Universo Clean Pure Crypto (`500/500`) aggiornato con il 21 Novembre 2026 alle `05:30 CET` (`04:30 UTC`)**")
    clean_md.append(f"> Esclusi `274` asset (Stablecoin, Wrapped/LST/Receipt, ETF/Azioni/Oro Tokenizzati, Illiquidi `< $100k`, Zombie/Falliti, Subnet & Gas Secondari). Cambio storico EUR/USD: `1,1413` (1° lug) → `1,1327` (1° ott) → **`{fx_nov:.4f}`** (21 nov `05:30 CET`).")
    clean_md.append("")
    clean_md.append("**File Dataset & Strumenti Aggiornati (3 Date):**")
    clean_md.append("- Tabella CSV Clean Pure 500: [clean500_crypto_2026-07-01_vs_2026-10-01.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/clean500_crypto_2026-07-01_vs_2026-10-01.csv)")
    clean_md.append("- Dataset JSON Clean Pure 500: [clean500_crypto_2026-07-01_vs_2026-10-01.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/clean500_crypto_2026-07-01_vs_2026-10-01.json)")
    clean_md.append("- Dashboard HTML Interattiva (3 date): [dashboard_pure500_crypto_2026.html](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/dashboard_pure500_crypto_2026.html)")
    clean_md.append("")
    clean_md.append("## 1. Evoluzione Macroeconomica della Coorte Clean Pure 500 (1° Luglio → 1° Ottobre → 21 Novembre `05:30 CET`)")
    clean_md.append("")
    clean_md.append("| Metrica Coorte Clean Pure 500 | 1° Luglio 2026 | 1° Ottobre 2026 | 21 Nov 2026 `05:30 CET` |")
    clean_md.append("| :--- | ---: | ---: | ---: |")
    clean_md.append(f"| **Asset Attivi / Quotati** | `500 / 500` | `{cm['active_priced_on_oct1']} / 500` | `{len(clean_active_nov)} / 500` |")
    clean_md.append(f"| **Market Cap Aggregata Coorte** | `${cm['total_cohort_mcap_jul1_usd']:,.0f}` | `${cm['total_cohort_mcap_oct1_active_usd']:,.0f}` (`+44,78%`) | `${clean_mcap_nov:,.0f}` (`{cm['cohort_mcap_jul_to_nov21_pct']:+.2f}%` vs Lug) |")
    clean_md.append(f"| **Portafoglio `€5 × 500` (`€2.500,00` investiti, EUR reali)** | `€2.500,00` | `€{clean_tot_5eur_oct:,.2f}` (`{(clean_tot_5eur_oct/2500-1)*100:+.2f}%`) | **`€{clean_tot_5eur_nov:,.2f}`** (**`{(clean_tot_5eur_nov/2500-1)*100:+.2f}%`** vs Lug) |")
    clean_md.append(f"| **Mediana Rendimento EUR (da 1° Luglio)** | `0,00%` | `+24,36%` | **`{cm['median_jul_to_nov21_eur_pct']:+.2f}%`** |")
    clean_md.append(f"| **Prezzo Bitcoin (`BTC`)** | `{fmt_price(clean_rows[0]['price_jul1_usd'])}` | `{fmt_price(clean_rows[0]['price_oct1_usd'])}` | `{fmt_price(clean_rows[0]['price_nov21_0530_usd'])}` |")
    clean_md.append("")
    clean_md.append("## 2. Tabella Integrale 1:1 — Tutte le 500 Clean Pure Crypto (1° Luglio · 1° Ottobre · 21 Novembre `05:30 CET`)")
    clean_md.append("")
    clean_md.append("| # Clean | CMC # | ID | Nome (`Ticker`) | Prezzo 1 Lug | MCap 1 Lug | Prezzo 1 Ott | MCap 1 Ott | Prezzo 21 Nov 05:30 | MCap 21 Nov 05:30 | Δ% Lug→Ott | Δ% Lug→21 Nov | Δ% Ott→21 Nov |")
    clean_md.append("| ---: | ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in clean_rows:
        nm = r["name"].replace("|", "/").replace("$", "\\$")
        sym = r["symbol"].replace("|", "/")
        clean_md.append(
            f"| {r['rank_clean_jul1']:03d} | {r['cmc_rank_jul1']} | `{r['forensic_id']}` | {nm} (`{sym}`) "
            f"| `{fmt_price(r['price_jul1_usd'])}` | `{fmt_mcap(r['mcap_jul1_usd'])}` "
            f"| `{fmt_price(r['price_oct1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` "
            f"| `{fmt_price(r['price_nov21_0530_usd'])}` | `{fmt_mcap(r['mcap_nov21_0530_usd'])}` "
            f"| {fmt_pct(r['price_change_pct'])} | {fmt_pct(r['price_change_jul_to_nov21_pct'])} | {fmt_pct(r['price_change_oct_to_nov21_pct'])} |"
        )
    clean_md_txt = "\n".join(clean_md) + "\n"
    check_katex_safe(clean_md_txt, "report_pure500_crypto_2026.md")
    for p in (os.path.join(PROJ_DIR, "report_pure500_crypto_2026.md"), os.path.join(PROJ_DIR, "report_clean500_crypto_2026.md"), os.path.join(ARTIFACT_DIR, "report_pure500_crypto_2026.md")):
        with open(p, "w", encoding="utf-8") as f:
            f.write(clean_md_txt)

    # Update dashboard_pure500_crypto_2026.html
    clean_html_data = json.dumps({"summary": cm, "rows": clean_rows}, ensure_ascii=False)
    clean_html = f"""<!DOCTYPE html><html lang="it"><head><meta charset="UTF-8"><title>Clean Pure 500 — 1 Lug · 1 Ott · 21 Nov 05:30</title>
<style>body{{margin:0;font-family:-apple-system,Segoe UI,sans-serif;background:#0b0f17;color:#e6edf3}}header{{padding:20px 28px;background:#0f1520;border-bottom:1px solid #232f42}}
.wrap{{padding:18px 28px}}input{{background:#131a26;color:#e6edf3;border:1px solid #232f42;border-radius:8px;padding:8px 12px;min-width:280px;margin-bottom:12px}}
table{{width:100%;border-collapse:collapse;background:#131a26;font-size:12.5px}}th,td{{padding:8px 10px;border-bottom:1px solid #232f42;text-align:right;white-space:nowrap}}
th:nth-child(3),td:nth-child(3){{text-align:left}}th{{background:#182232;color:#8b9bb4;position:sticky;top:0;cursor:pointer}}.pos{{color:#10b981;font-weight:600}}.neg{{color:#ef4444;font-weight:600}}</style></head>
<body><header><h1 style="margin:0 0 6px;font-size:20px">Clean Pure Crypto Top 500 — 1° Luglio · 1° Ottobre · 21 Novembre 2026 (05:30 CET)</h1>
<div style="color:#8b9bb4;font-size:13px">500/500 criptovalute pulite e liquide • €2.500 → €{clean_tot_5eur_oct:,.2f} (1 Ott) → €{clean_tot_5eur_nov:,.2f} (21 Nov 05:30)</div></header>
<div class="wrap"><input id="q" placeholder="Cerca nome, ticker o cmc-ID...">
<div style="overflow-x:auto"><table><thead><tr>
<th data-k="rank_clean_jul1">#</th><th data-k="cmc_rank_jul1">CMC#</th><th data-k="name">Criptovaluta</th>
<th data-k="price_jul1_usd">Prezzo 1 Lug</th><th data-k="mcap_jul1_usd">MCap 1 Lug</th>
<th data-k="price_oct1_usd">Prezzo 1 Ott</th><th data-k="mcap_oct1_usd">MCap 1 Ott</th>
<th data-k="price_nov21_0530_usd">Prezzo 21 Nov 05:30</th><th data-k="mcap_nov21_0530_usd">MCap 21 Nov 05:30</th>
<th data-k="price_change_pct">Δ% Lug→Ott</th><th data-k="price_change_jul_to_nov21_pct">Δ% Lug→21 Nov</th><th data-k="price_change_oct_to_nov21_pct">Δ% Ott→21 Nov</th>
</tr></thead><tbody id="tb"></tbody></table></div></div>
<script>const D={clean_html_data}.rows;let sk='rank_clean_jul1',sd=1;
const fp=p=>p==null?'N/D':(Math.abs(p)>=1000?'$'+p.toLocaleString('en-US',{{minimumFractionDigits:2,maximumFractionDigits:2}}):(Math.abs(p)>=1?'$'+p.toFixed(4):(Math.abs(p)>=1e-4?'$'+p.toFixed(6):'$'+p.toExponential(3))));
const fm=m=>m==null?'N/D':'$'+Math.round(m).toLocaleString('en-US');
const fpc=v=>v==null?'N/D':(v>=0?'+':'')+v.toFixed(2)+'%';
function ren(){{const q=document.getElementById('q').value.trim().toLowerCase();
let rs=D.filter(r=>!q||r.name.toLowerCase().includes(q)||r.symbol.toLowerCase().includes(q)||r.forensic_id.includes(q));
rs.sort((a,b)=>{{let va=a[sk],vb=b[sk];if(va==null)return 1;if(vb==null)return -1;return typeof va==='string'?va.localeCompare(vb)*sd:(va-vb)*sd;}});
document.getElementById('tb').innerHTML=rs.map(r=>`<tr><td>${{r.rank_clean_jul1}}</td><td>${{r.cmc_rank_jul1}}</td><td><strong>${{r.name}}</strong> (<code>${{r.symbol}}</code>) <small style="color:#64748b">${{r.forensic_id}}</small></td><td>${{fp(r.price_jul1_usd)}}</td><td>${{fm(r.mcap_jul1_usd)}}</td><td>${{fp(r.price_oct1_usd)}}</td><td>${{fm(r.mcap_oct1_usd)}}</td><td>${{fp(r.price_nov21_0530_usd)}}</td><td>${{fm(r.mcap_nov21_0530_usd)}}</td><td class="${{r.price_change_pct>0?'pos':'neg'}}">${{fpc(r.price_change_pct)}}</td><td class="${{r.price_change_jul_to_nov21_pct>0?'pos':'neg'}}">${{fpc(r.price_change_jul_to_nov21_pct)}}</td><td class="${{r.price_change_oct_to_nov21_pct>0?'pos':'neg'}}">${{fpc(r.price_change_oct_to_nov21_pct)}}</td></tr>`).join('');}}
document.getElementById('q').addEventListener('input',ren);document.querySelectorAll('th[data-k]').forEach(t=>t.addEventListener('click',()=>{{sk===t.dataset.k?sd*=-1:(sk=t.dataset.k,sd=1);ren();}}));ren();
</script></body></html>"""
    with open(os.path.join(PROJ_DIR, "dashboard_pure500_crypto_2026.html"), "w", encoding="utf-8") as f:
        f.write(clean_html)

    # =========================================================================
    # 3. ENRICH CLASSIFICA 500 PER RENDIMENTO (CSV, JSON, MD)
    # =========================================================================
    rank_json_path = os.path.join(PROJ_DIR, "classifica_500_per_rendimento_desc.json")
    with open(rank_json_path, encoding="utf-8") as f:
        rank_doc = json.load(f)
    clean_by_id = {r["cmc_id"]: r for r in clean_rows}
    rank_rows = []
    for x in rank_doc["ranking"]:
        cr = clean_by_id[x["cmc_id"]]
        x["price_nov21_0530_usd"] = cr["price_nov21_0530_usd"]
        x["mcap_nov21_0530_usd"] = cr["mcap_nov21_0530_usd"]
        x["return_jul_to_nov21_eur_pct"] = cr["return_jul_to_nov21_eur_pct"]
        x["return_oct_to_nov21_usd_pct"] = cr["price_change_oct_to_nov21_pct"]
        x["ticket_5eur_nov21_eur"] = cr["ticket_5eur_nov21_eur"]
        rank_rows.append(x)
    rank_doc["meta"]["snapshot_nov21_local"] = "2026-11-21T05:30:00+01:00"
    rank_doc["meta"]["fx_eur_usd_nov21"] = fx_nov
    rank_doc["ranking"] = rank_rows

    with open(rank_json_path, "w", encoding="utf-8") as f:
        json.dump(rank_doc, f, indent=2, ensure_ascii=False)
    rank_csv_path = os.path.join(PROJ_DIR, "classifica_500_per_rendimento_desc.csv")
    with open(rank_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rank_rows[0].keys()))
        w.writeheader()
        w.writerows(rank_rows)

    rank_md = []
    rank_md.append("# Classifica Integrale per Rendimento (1° Lug → 1° Ott) con Aggiunta Valore del 21 Novembre 2026 ore 05:30")
    rank_md.append("")
    rank_md.append("> [!IMPORTANT]")
    rank_md.append(f"> **Tutte le 500 Clean Pure Crypto ordinate per Rendimento 1° Luglio → 1° Ottobre 2026**, arricchite con il **Prezzo, la Capitalizzazione e il valore della quota da `€5` al 21 Novembre 2026 alle `05:30 CET` (`04:30 UTC`, `EUR/USD = {fx_nov:.4f}`)**.")
    rank_md.append("")
    rank_md.append("**File Aggiornati:** [classifica_500_per_rendimento_desc.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/classifica_500_per_rendimento_desc.csv) · [classifica_500_per_rendimento_desc.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/classifica_500_per_rendimento_desc.json)")
    rank_md.append("")
    rank_md.append("| # Rend. | Nome (`Ticker`) | ID | # Clean | # Glob | CMC # | Rend. % Lug→Ott | €5 → 1 Ott | Prezzo 1 Lug | Prezzo 1 Ott | Prezzo 21 Nov 05:30 | MCap 21 Nov 05:30 | €5 → 21 Nov | Δ% Lug→21 Nov EUR |")
    rank_md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for x in rank_rows:
        nm = x["name"].replace("|", "/").replace("$", "\\$")
        sym = x["symbol"].replace("|", "/")
        rank_md.append(
            f"| {x['rank_return']:03d} | **{nm}** (`{sym}`) | `{x['forensic_id']}` "
            f"| #{x['rank_clean_mcap_jul1']} | #{x['rank_global_mcap_jul1']} | #{x['cmc_rank_jul1']} "
            f"| **`{x['return_pct_eur']:+.2f}%`** | `€{x['ticket_5eur_final_eur']:,.2f}` "
            f"| `{fmt_price(x['price_jul1_usd'])}` | `{fmt_price(x['price_oct1_usd'])}` "
            f"| `{fmt_price(x['price_nov21_0530_usd'])}` | `{fmt_mcap(x['mcap_nov21_0530_usd'])}` "
            f"| `€{x['ticket_5eur_nov21_eur']:,.2f}` | `{fmt_pct(x['return_jul_to_nov21_eur_pct'])}` |"
        )
    rank_md_txt = "\n".join(rank_md) + "\n"
    check_katex_safe(rank_md_txt, "classifica_500_per_rendimento.md")
    for p in (os.path.join(PROJ_DIR, "classifica_500_per_rendimento.md"), os.path.join(ARTIFACT_DIR, "classifica_500_per_rendimento.md")):
        with open(p, "w", encoding="utf-8") as f:
            f.write(rank_md_txt)

    # =========================================================================
    # 4. ENRICH SIMULAZIONE €5 x 500 CSV
    # =========================================================================
    sim_csv_path = os.path.join(PROJ_DIR, "simulazione_5eur_x_500_clean_crypto.csv")
    with open(sim_csv_path, encoding="utf-8-sig") as f:
        sim_rows = list(csv.DictReader(f))
    clean_by_fid = {r["forensic_id"]: r for r in clean_rows}
    for sr in sim_rows:
        cr = clean_by_fid[sr["forensic_id"]]
        sr["price_nov21_0530_usd"] = cr["price_nov21_0530_usd"]
        sr["mcap_nov21_0530_usd"] = cr["mcap_nov21_0530_usd"]
        sr["value_nov21_0530_eur_real_fx"] = cr["ticket_5eur_nov21_eur"]
        sr["pnl_nov21_0530_eur_real_fx"] = round(cr["ticket_5eur_nov21_eur"] - 5.0, 4)
        sr["return_jul_to_nov21_pct_eur"] = cr["return_jul_to_nov21_eur_pct"]
    with open(sim_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(sim_rows[0].keys()))
        w.writeheader()
        w.writerows(sim_rows)

    # =========================================================================
    # 5. ENRICH CURVA CUMULATIVA N = 1..500 (CSV, JSON, MD)
    # =========================================================================
    curva_json_path = os.path.join(PROJ_DIR, "curva_cumulativa_N1_a_N500.json")
    with open(curva_json_path, encoding="utf-8") as f:
        curva_doc = json.load(f)
    cum_nov_eur = 0.0
    for s in curva_doc["steps"]:
        cr = clean_by_fid[s["forensic_id"]]
        v_nov = cr["ticket_5eur_nov21_eur"]
        cum_nov_eur += v_nov
        inv = s["invested_eur"]
        s["added_price_nov21_0530_usd"] = cr["price_nov21_0530_usd"]
        s["added_coin_val_nov21_eur"] = v_nov
        s["added_coin_jul_to_nov21_eur_pct"] = cr["return_jul_to_nov21_eur_pct"]
        s["portfolio_val_nov21_eur_real"] = round(cum_nov_eur, 2)
        s["portfolio_pnl_nov21_eur_real"] = round(cum_nov_eur - inv, 2)
        s["portfolio_pct_nov21_eur_real"] = round((cum_nov_eur / inv - 1.0) * 100.0, 4)

    with open(curva_json_path, "w", encoding="utf-8") as f:
        json.dump(curva_doc, f, indent=2, ensure_ascii=False)
    curva_csv_path = os.path.join(PROJ_DIR, "curva_cumulativa_N1_a_N500.csv")
    with open(curva_csv_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(curva_doc["steps"][0].keys()))
        w.writeheader()
        w.writerows(curva_doc["steps"])

    curva_md = []
    curva_md.append("# Curva di Rendimento Marginale Step-by-Step `N = 1..500` (1° Luglio → 1° Ottobre → 21 Novembre 2026 ore 05:30)")
    curva_md.append("")
    curva_md.append("> [!IMPORTANT]")
    curva_md.append(f"> **Analisi Integrale `500/500` passi (`N = 1..500`)** con confronto del portafoglio `€5 × N` al **1° Ottobre 2026** e al **21 Novembre 2026 ore `05:30 CET` (`04:30 UTC`, `EUR/USD = {fx_nov:.4f}`)**.")
    curva_md.append("")
    curva_md.append("**File Aggiornati:** [curva_cumulativa_N1_a_N500.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/curva_cumulativa_N1_a_N500.csv) · [curva_cumulativa_N1_a_N500.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/curva_cumulativa_N1_a_N500.json)")
    curva_md.append("")
    curva_md.append("| N | Passo ID | Crypto Aggiunta (`Ticker`) | ID | Prezzo 21 Nov 05:30 | Investito (`€`) | Finale 1 Ott (`€`) | Cum. % 1 Ott | Finale 21 Nov (`€`) | Cum. % 21 Nov | Singola % Lug→21 Nov |")
    curva_md.append("| ---: | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |")
    for s in curva_doc["steps"]:
        nm = s["added_name"].replace("|", "/").replace("$", "\\$")
        curva_md.append(
            f"| {s['N']} | `{s['step_id']}` | {nm} (`{s['added_symbol']}`) | `{s['forensic_id']}` "
            f"| `{fmt_price(s['added_price_nov21_0530_usd'])}` | `€{s['invested_eur']:,.2f}` "
            f"| `€{s['portfolio_val_eur_real']:,.2f}` | `{s['portfolio_pct_eur_real']:+.2f}%` "
            f"| `€{s['portfolio_val_nov21_eur_real']:,.2f}` | **`{s['portfolio_pct_nov21_eur_real']:+.2f}%`** "
            f"| `{fmt_pct(s['added_coin_jul_to_nov21_eur_pct'])}` |"
        )
    curva_md_txt = "\n".join(curva_md) + "\n"
    check_katex_safe(curva_md_txt, "report_curva_N1_to_N500.md")
    for p in (os.path.join(PROJ_DIR, "report_curva_N1_to_N500.md"), os.path.join(ARTIFACT_DIR, "report_curva_N1_to_N500.md")):
        with open(p, "w", encoding="utf-8") as f:
            f.write(curva_md_txt)

    print("=== ALL 5 FULL 500-COIN LISTS ENRICHED WITH 2026-11-21 05:30 CET ===")
    print(f"FX EUR/USD: Jul 1 = {fx_jul:.6f} | Oct 1 = {fx_oct:.6f} | Nov 21 05:30 = {fx_nov:.6f}")
    print(f"Original 500 active on Nov 21 05:30: {len(orig_active_nov)}/500 | Total MCap=${orig_mcap_nov:,.0f}")
    print(f"Clean 500 active on Nov 21 05:30:    {len(clean_active_nov)}/500 | Total MCap=${clean_mcap_nov:,.0f} ({cm['cohort_mcap_jul_to_nov21_pct']:+.2f}% vs Jul 1)")
    print(f"Clean 500 €5x500 (€2,500) -> Oct 1: €{clean_tot_5eur_oct:,.2f} ({(clean_tot_5eur_oct/2500-1)*100:+.2f}%) -> Nov 21 05:30: €{clean_tot_5eur_nov:,.2f} ({(clean_tot_5eur_nov/2500-1)*100:+.2f}%)")
    best_nov_step = max(curva_doc["steps"], key=lambda x: x["portfolio_pct_nov21_eur_real"])
    print(f"Best N on Nov 21 05:30 (N=1..500): N={best_nov_step['N']} (+{best_nov_step['added_symbol']}) -> €{best_nov_step['invested_eur']:.0f} -> €{best_nov_step['portfolio_val_nov21_eur_real']:.2f} ({best_nov_step['portfolio_pct_nov21_eur_real']:+.2f}%)")


if __name__ == "__main__":
    main()
