#!/usr/bin/env python3
"""
apply_ux_ui_round1_fixes.py
Applies the complete Unified Apple / Craft / Things 3 Design System (Light + True OLED Dark)
and fixes 100% of Round 1 Blind UX/UI Audit findings (P0, P1, P2) across all 7 HTML pages
while preserving 100% of embedded JSON datasets verbatim (zero data loss, 500/500 completeness parity).
"""
import csv
import json
import re
from pathlib import Path

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")

ANTI_FOUC = (
    "<script>(function(){try{var t=localStorage.getItem('crypto_hub_theme');"
    "document.documentElement.setAttribute('data-theme',t==='light'?'light':'dark');"
    "}catch(e){document.documentElement.setAttribute('data-theme','dark');}})();</script>"
)

SEARCH_SVG = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.1" '
    'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">'
    '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
)


def extract_regex(text: str, pattern: str, name: str) -> str:
    m = re.search(pattern, text, re.S)
    if not m:
        raise RuntimeError(f"Could not extract {name} using pattern: {pattern}")
    return m.group(1)


def load_excl_map() -> dict:
    p = PROJ / "excluded_274_assets_clean500.csv"
    reason_short = {
        "STABLECOIN": ("STABLE", "p-blue", "Esclusa da Pure 500: Stablecoin"),
        "WRAPPED_LST_LRT_RECEIPT": ("WRAP/LST", "p-purple", "Esclusa da Pure 500: Wrapped / LST / Receipt"),
        "TOKENIZED_ETF_STOCK_RWA_COMMODITY": ("RWA", "p-amber", "Esclusa da Pure 500: Tokenized Stock / ETF / Gold / RWA"),
        "PUNTO_1_ILLIQUIDI_VOL_LT_100K": ("ILLIQ", "p-red", "Esclusa da Pure 500: Illiquida (Vol 24h < 100k USD)"),
        "PUNTO_2_ZOMBIE_FALLITI_CHIUSI": ("ZOMBIE", "p-red", "Esclusa da Pure 500: Progetto chiuso / zombie"),
        "PUNTO_3_SUBNET_E_GAS_SECONDARI": ("SUBNET", "p-muted", "Esclusa da Pure 500: Subnet / gas secondario"),
    }
    out = {}
    with open(p, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = str(row["cmc_id"]).strip()
            r = row.get("reason", "").strip()
            out[cid] = reason_short.get(r, ("ESCLUSA", "p-muted", r))
    return out


# ==============================================================================
# 1. HOME PORTAL (index.html)
# ==============================================================================
def upgrade_index():
    p = PROJ / "index.html"
    orig = p.read_text(encoding="utf-8")
    census_json = extract_regex(orig, r"const CENSUS = (\[.*?\]);", "index CENSUS")
    # Preserve the 12 cohort links HTML
    cohorts_grid = extract_regex(
        orig,
        r"12 File CSV Individuali delle Nuove Coorti Pure Top 500 \(500 coin ciascuno\)</h3>\s*<div class=\"dl-grid\">(.*?)</div>",
        "index 12 cohorts grid",
    )

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pure Crypto Top 500 — Ricerca Forense Multi-Ciclo (2022–2026)</title>
<meta name="description" content="Analisi forense zero-survivorship-bias e zero-look-ahead sulle Pure Crypto Top 500 attraverso 15 date dal 30 Dicembre 2022 al 21 Novembre 2026: backtest 5 EUR, tranche 50-500, curve vesting CMC e concentrazione on-chain EVM Archive Multicall3.">
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1320px; }}
.hero {{ padding: 14px 0 22px; }}
.eyebrow {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 12.5px;
  font-weight: 600;
  color: var(--accent-text);
  background: var(--accent-soft);
  border: 1px solid var(--accent-soft-border);
  padding: 6px 13px;
  border-radius: 999px;
  margin-bottom: 14px;
  line-height: 1.35;
  max-width: 100%;
}}
.hero h1 {{
  margin: 0 0 12px;
  font-size: clamp(1.58rem, 3.8vw, 2.85rem);
  font-weight: 700;
  letter-spacing: -0.028em;
  line-height: 1.12;
  max-width: 920px;
}}
.lead {{
  color: var(--muted);
  font-size: clamp(14.5px, 1.35vw, 17px);
  max-width: 840px;
  margin: 0 0 20px;
  line-height: 1.54;
}}
.lead strong {{ color: var(--ink); font-weight: 600; }}
.hero-cta {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}}
.hero-cta .btn {{ min-height: 44px; padding: 0 18px; font-size: 13.5px; }}
[data-theme="light"] .hero-cta .btn:not(.btn-primary) {{
  background: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}}
.sec-title {{
  font-size: clamp(1.18rem, 2vw, 1.42rem);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin: 34px 0 6px;
}}
.sec-sub {{ color: var(--muted); font-size: 14px; margin: 0 0 16px; }}
.grid-apps {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 320px), 1fr));
  gap: 14px;
}}
.app-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  text-decoration: none;
  color: inherit;
  box-shadow: var(--shadow-card);
  transition: transform 0.16s var(--ease), border-color 0.16s var(--ease), box-shadow 0.16s var(--ease);
  min-width: 0;
}}
@media (hover: hover) {{
  .app-card:hover {{
    border-color: var(--accent-text);
    transform: translateY(-2px);
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.22);
  }}
}}
.app-card.featured {{
  border-color: var(--accent-soft-border);
  background: linear-gradient(155deg, var(--accent-soft) 0%, var(--surface) 58%);
}}
.tag {{
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 3px 9px;
  border-radius: 999px;
  margin-bottom: 10px;
}}
.tag-blue {{ background: var(--accent-soft); color: var(--accent-text); }}
.tag-green {{ background: var(--green-soft); color: var(--green-text); }}
.tag-purple {{ background: var(--purple-soft); color: var(--purple-text); }}
.tag-amber {{ background: var(--amber-soft); color: var(--amber-text); }}
.app-card h3 {{ margin: 0 0 8px; font-size: 17px; font-weight: 700; letter-spacing: -0.015em; }}
.app-card p {{ margin: 0 0 16px; font-size: 13.5px; color: var(--muted); line-height: 1.48; }}
.app-foot {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--accent-text);
  min-height: 24px;
}}
.findings {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 270px), 1fr));
  gap: 13px;
}}
.f-box {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 18px 20px;
  box-shadow: var(--shadow-card);
  min-width: 0;
}}
.f-box h4 {{ margin: 0 0 8px; font-size: 15.5px; font-weight: 700; line-height: 1.3; }}
.f-box p {{ margin: 0; font-size: 13.5px; color: var(--muted); line-height: 1.5; }}
.f-box strong {{ color: var(--ink-secondary); font-weight: 600; }}
.code-chip {{
  font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  font-size: 0.86em;
  padding: 1px 6px;
  border-radius: 5px;
  background: var(--surface2);
  color: var(--ink);
  border: 1px solid var(--border);
}}
.dl-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(100%, 215px), 1fr));
  gap: 10px;
}}
.dl-chip {{
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 2px;
  min-height: 50px;
  padding: 10px 13px;
  border-radius: var(--r-sm);
  background: var(--surface2);
  border: 1px solid var(--border);
  text-decoration: none;
  color: var(--ink);
  font-size: 13px;
  transition: border-color 0.15s var(--ease), transform 0.15s var(--ease);
  min-width: 0;
}}
@media (hover: hover) {{
  .dl-chip:hover {{ border-color: var(--accent-text); transform: translateY(-1px); }}
}}
.dl-chip span {{ font-size: 11.5px; color: var(--muted); }}
footer {{
  margin-top: 48px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--muted);
  font-size: 12.5px;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}}
footer a {{
  color: var(--accent-text);
  text-decoration: none;
  font-weight: 600;
  display: inline-flex;
  align-items: center;
  min-height: 38px;
}}
/* Tablet 2x2 CTA grid */
@media (max-width: 960px) and (min-width: 541px) {{
  .hero-cta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .hero-cta .btn {{ width: 100%; }}
}}
/* Mobile full-width CTA stack + clean multi-line badge radius */
@media (max-width: 540px) {{
  .eyebrow {{ border-radius: 14px; font-size: 11.5px; padding: 6px 11px; margin-bottom: 10px; }}
  .hero {{ padding: 8px 0 16px; }}
  .hero h1 {{ font-size: clamp(1.38rem, 6.2vw, 1.85rem); margin-bottom: 9px; }}
  .lead {{ font-size: 14px; margin-bottom: 14px; }}
  .hero-cta {{ display: grid; grid-template-columns: 1fr; gap: 8px; }}
  .hero-cta .btn {{ width: 100%; }}
}}
/* Short Mobile Landscape (667x375): fit hero + Primary CTA cleanly above the fold */
@media (max-height: 480px) and (max-width: 900px) {{
  .hero {{ padding: 6px 0 12px; }}
  .eyebrow {{ padding: 4px 10px; font-size: 11px; margin-bottom: 8px; }}
  .hero h1 {{ font-size: 1.38rem; margin-bottom: 6px; }}
  .lead {{ font-size: 13px; margin-bottom: 12px; line-height: 1.4; }}
  .hero-cta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; }}
  .hero-cta .btn {{ min-height: 40px; font-size: 12.5px; padding: 0 10px; width: 100%; }}
}}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("home", "./");</script>

<main class="wrap">
  <section class="hero">
    <div class="eyebrow">100% Forensic Completeness Gate PASS &middot; Zero Survivorship Bias &middot; Zero Look-Ahead</div>
    <h1>Analisi Forense Multi-Ciclo sulle Pure Crypto Top 500 <span style="white-space:nowrap">(2022–2026)</span></h1>
    <p class="lead">
      Dataset point-in-time su <strong>15 date storiche</strong> dal minimo del bear market (30 Dicembre 2022) al picco del ciclo (7 Ottobre 2025) fino al 21 Novembre 2026 05:30&nbsp;CET. Include backtest <strong class="nowrap">5&nbsp;EUR/coin</strong> su 105 finestre, tranche Top 50..500, 498 curve ufficiali di vesting CMC, 446 asset EVM ricostruiti crittograficamente via Archive RPC Multicall3 e 24 migrazioni ufficiali risolte al rapporto reale.
    </p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="./multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html">Apri Dashboard Flagship 15 Date &rarr;</a>
      <a class="btn" href="./dashboard_tokenomics_holders_500.html">Apri Audit Tokenomics &amp; Whale</a>
      <a class="btn" href="./dashboard_storico_3date_500.html">Storico 3 Date (Lug–Nov 2026)</a>
      <a class="btn" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/multidate_15_2022_2026/report_15date_2022_2026_completo.md" target="_blank" rel="noopener">Leggi Dossier Forense 15 Date &nearr;</a>
    </div>
  </section>

  <section class="kpis" aria-label="Indicatori chiave della ricerca">
    <div class="kpi"><div class="lbl">Orizzonte Temporale</div><div class="val">15 Date &middot; 4 Anni</div><div class="note">30 Dic 2022 &rarr; 21 Nov 2026<span class="kpi-sep"> &middot; </span><span class="nowrap">05:30&nbsp;CET</span></div></div>
    <div class="kpi"><div class="lbl">Record Point-in-Time</div><div class="val">15.000 Righe</div><div class="note">7.500 Vista A + 7.500 Vista B</div></div>
    <div class="kpi"><div class="lbl">On-Chain Archive RPC</div><div class="val">446 Asset EVM</div><div class="note">Multicall3 su ETH, Base, Arbitrum e&nbsp;OP</div></div>
    <div class="kpi"><div class="lbl">Curve Vesting Ufficiali</div><div class="val">498 Curve CMC</div><div class="note">Unlocks point-in-time dal Dicembre&nbsp;2022</div></div>
    <div class="kpi"><div class="lbl">Holders Nativi</div><div class="val">95,2% (476/500)</div><div class="note">96,0% dei 496 asset non&#8209;privacy</div></div>
    <div class="kpi"><div class="lbl">Migrazioni &amp; Integrit&agrave;</div><div class="val">24 Swap Mappati</div><div class="note">MATIC&rarr;POL, FTM&rarr;S, MKR&rarr;SKY e altri</div></div>
  </section>

  <h2 class="sec-title" id="dashboards">Suite delle 6 Dashboard Web Interattive</h2>
  <p class="sec-sub">Tutte le applicazioni sono zero-dependency, filtrabili, ordinabili, dotate di tema Light/OLED Dark e funzionanti lato client con tutti i record 1:1 incorporati.</p>
  <section class="grid-apps">
    <a class="app-card featured" href="./multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html">
      <div>
        <span class="tag tag-blue">Flagship &middot; 15 Date (2022–2026)</span>
        <h3>Dashboard Multi-Ciclo 15 Date (14&times;15)</h3>
        <p>Heatmap interattiva su tutte le 105 finestre di investimento 5 EUR/coin, confronto Conservative vs Active-Only vs Bitcoin, grafici divergenti Tranche Top 50..500, esploratore completo Vista A (500 coin/data) e Vista B (500/500) + fattori on-chain 4 anni.</p>
      </div>
      <div class="app-foot"><span>Apri Dashboard 15 Date</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_storico_3date_500.html">
      <div>
        <span class="tag tag-green">Point-in-Time 2026</span>
        <h3>Storico 3 Date — 1 Lug, 1 Ott &amp; 21 Nov 2026</h3>
        <p>Confronto ad alta risoluzione dei parametri storici esatti sulle 3 date del 2026 (inclusa rilevazione intraday 05:30&nbsp;CET del 21 Novembre): evoluzione rank, supply inflation, token sbloccati, holders storici (334/500) e delta concentrazione Archive RPC.</p>
      </div>
      <div class="app-foot"><span>Apri Storico 3 Date</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_tokenomics_holders_500.html">
      <div>
        <span class="tag tag-purple">On-Chain Forensics &middot; 95,2%</span>
        <h3>Tokenomics, Unlocks &amp; Decomposizione Wallet</h3>
        <p>Analisi integrale dei 500 asset puri su token sbloccati/da sbloccare, numero holder e decomposizione dei Top-10 wallet on-chain in Burn, CEX, Protocol/Lock/LP ed EOA Whale Residua, con punteggio affidabilit&agrave; A+–C e 58 bug bridge bonificati.</p>
      </div>
      <div class="app-foot"><span>Apri Audit On-Chain</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./curva_rendimento_N1_to_N500.html">
      <div>
        <span class="tag tag-amber">Ottimizzazione N = 1..500</span>
        <h3>Curva Cumulativa Passo-Passo (da 1 a 500 Coin)</h3>
        <p>Valutazione marginale di ogni singola aggiunta di criptovaluta dalla #1 alla #500 con ticket da 5 EUR: identifica il punto di massimo rendimento cumulativo (N=143 +BTW / N=93 ex-BTW), il contributo di ogni ingresso e il profilo rischio/rendimento.</p>
      </div>
      <div class="app-foot"><span>Apri Curva N=1..500</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_pure500_crypto_2026.html">
      <div>
        <span class="tag tag-green">Coorte Pulita Q3 2026</span>
        <h3>Clean Pure Top 500 &amp; Analisi Tranche Q3 2026</h3>
        <p>Esplorazione della coorte filtrata del 1&deg; Luglio 2026 (depurata da 274 asset non puri: stablecoin, wrapped, LST/LRT, RWA, illiquide &lt;100k USD, zombie e subnet) con backtest Q3 al 1&deg; Ottobre e al 21 Novembre 2026.</p>
      </div>
      <div class="app-foot"><span>Apri Pure 500 Q3</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_top500_crypto_2026.html">
      <div>
        <span class="tag tag-blue">Baseline Pre-Filtro</span>
        <h3>Snapshot Raw Top 500 Originale (Pre-Pulizia)</h3>
        <p>Snapshot integrale originale delle prime 500 capitalizzazioni CMC al 1&deg; Luglio 2026 prima delle esclusioni forensi, con badge di classificazione sui 182 asset esclusi per verificare l'impatto quantitativo della pulizia.</p>
      </div>
      <div class="app-foot"><span>Apri Raw Top 500</span><span>&rarr;</span></div>
    </a>
  </section>

  <h2 class="sec-title" id="evidenze">Evidenze Empiriche Principali <span style="white-space:nowrap">(Ciclo 2022–2026)</span></h2>
  <p class="sec-sub">Sintesi quantitativa certificata su 5 EUR per coin (2.500 EUR per coorte Top 500), con delisting valutati a 0 EUR (-100%) e migrazioni ufficiali convertite al tasso reale.</p>
  <section class="findings">
    <div class="f-box">
      <h4>Miglior Finestra (Top 500): <span class="pos">+173,00% EUR</span></h4>
      <p>Entrando al minimo <strong>D01 (30 Dic 2022)</strong> ed uscendo a <strong>D02 (09 Apr 2024)</strong>, 2.500 EUR diventano <strong>6.825,12 EUR</strong> (BTC Buy&amp;Hold: <strong>+308,72% EUR</strong>). Sul ciclo di 4 anni fino al 21 Nov 2026, la Top 500 chiude a <strong>1.067,15 EUR (-57,31%)</strong> con 44 delisting, mentre la Top 50 registra <strong>+37,53% EUR</strong> e BTC <strong>+226,09% EUR</strong>.</p>
    </div>
    <div class="f-box">
      <h4>Dominio Strutturale delle Large-Cap (Top 50–100)</h4>
      <p>Su tutti gli ingressi 2022–Set 2025 (D01–D07) tenuti al 21 Nov 2026, le tranche <strong>Top 50 / Top 100 / Top 150</strong> battono sistematicamente la Top 500 di <strong>+17 / +95 punti %</strong>. Nel 2026 (D08–D13) le tranche 250–450 prevalgono solo per il singolo outlier <strong>DHN</strong> (+8.207%..+13.148%); ex-DHN vincono ancora le Top 50–100.</p>
    </div>
    <div class="f-box">
      <h4>Fattore Unlocks: Degrado Monotonico su 4 Anni</h4>
      <p>Misurando l'overhang <code class="code-chip">to_unlock_pct</code> alla sola data di ingresso (zero look-ahead): su D01&rarr;D08 la mediana EUR crolla da <strong>-25,6%</strong> (0–10% bloccati) a <strong>-31,5%</strong> (10–30%), <strong>-46,6%</strong> (30–60%) fino a <strong>-66,9%</strong> (&gt;60% bloccati). Stesso gradiente nel bear D08&rarr;D15 (-76,9% vs -86,1%).</p>
    </div>
    <div class="f-box">
      <h4>EOA Whale Residua: Amplificatore di Drawdown</h4>
      <p>Grazie alla ricostruzione crittografica <strong>EVM Archive RPC Multicall3</strong>, nel ribasso D08&rarr;D15 la perdita media peggiora monotonicamente con la quota in mano a whale EOA: <strong>-41,6%</strong> (&lt;10% EOA), <strong>-75,0%</strong> (10–35% EOA) e <strong>-77,2%</strong> (&gt;35% EOA).</p>
    </div>
  </section>

  <div class="tbl-head-bar" style="margin-top:34px">
    <div>
      <h2 class="sec-title" id="timeline" style="margin:0 0 4px">Censimento Macro delle 15 Date <span style="white-space:nowrap">(30 Dic 2022 – 21 Nov 2026)</span></h2>
      <p class="sec-sub" style="margin:0">Cambio EUR/USD storico esatto, filtro di purezza identico, correzione sub-cent (&lt;0,0001 USD) e stato point-in-time di unlocks e holders.</p>
    </div>
    <span class="scroll-hint" data-scroll-hint="timelineWrap">&larr; Scorri tabella &rarr;</span>
  </div>
  <div class="card" style="padding:0;overflow:hidden">
    <div class="tbl-wrap no-maxh" id="timelineWrap" style="border:none"><table id="timelineTbl"></table></div>
  </div>

  <h2 class="sec-title" id="downloads">Centro Download Dataset (CSV / JSON) e Dossier Forensi (Markdown)</h2>
  <p class="sec-sub">Tutti i file grezzi, strutturati e i report completi sono scaricabili direttamente dal sito o consultabili nella repository GitHub.</p>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">Master Panel &amp; Backtest (15 Date + 3 Date + Audit Forense)</h3>
    <div class="dl-grid">
      <a class="dl-chip" href="./multidate_15_2022_2026/panel_vistaA_15coorti_7500_righe.csv" download><b>Vista A Master Panel</b><span>15 coorti &times; 500 = 7.500 righe (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/panel_vistaB_jul1_500_su_15date_7500_righe.csv" download><b>Vista B Master Lungo</b><span>500 coin Lug1 &times; 15 date = 7.500 righe</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/storico_15date_vistaB_500_crypto.csv" download><b>Vista B Tabella Larga</b><span>500 coin &times; 128 colonne (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_matrice_14x15_5eur.csv" download><b>Matrice Backtest 14&times;15</b><span>105 finestre 5 EUR + BTC Alpha (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_tranche_50_to_500_tutte_date.csv" download><b>Tranche 50..500 Tutte le Date</b><span>960 righe Cumulative &amp; Marginali</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_15date_completo.json" download><b>JSON Master Backtest 15 Date</b><span>Matrice, Tranche, Fattori &amp; Migrazioni</span></a>
      <a class="dl-chip" href="./storico_3date_completo_500_crypto.csv" download><b>Storico 3 Date (Lug–Nov 2026)</b><span>500 coin point-in-time completo (CSV)</span></a>
      <a class="dl-chip" href="./audit_forense_500_crypto.csv" download><b>Audit Forense Tokenomics/Whale</b><span>500 coin + decomposizione wallet (CSV)</span></a>
      <a class="dl-chip" href="./curva_cumulativa_N1_a_N500.csv" download><b>Curva Cumulativa N=1..500</b><span>Ogni singola aggiunta 5 EUR (CSV)</span></a>
      <a class="dl-chip" href="./classifica_500_per_rendimento_desc.csv" download><b>Classifica 500 per Rendimento</b><span>Ordinata dal miglior al peggior asset</span></a>
    </div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">12 File CSV Individuali delle Nuove Coorti Pure Top 500 (500 coin ciascuno)</h3>
    <div class="dl-grid">{cohorts_grid}</div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">Dossier Forensi Completi in Markdown (su GitHub)</h3>
    <div class="dl-grid">
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/multidate_15_2022_2026/report_15date_2022_2026_completo.md" target="_blank" rel="noopener"><b>Dossier 15 Date (2022–2026)</b><span>Report completo + Vista B 500/500 &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_storico_3date_500_crypto.md" target="_blank" rel="noopener"><b>Dossier Storico 3 Date</b><span>1 Lug, 1 Ott, 21 Nov 2026 05:30 &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_audit_forense_500_crypto.md" target="_blank" rel="noopener"><b>Dossier Audit Forense 500</b><span>Unlocks, Holders 95,2% &amp; EOA Whale &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_tokenomics_unlocks_holders_500.md" target="_blank" rel="noopener"><b>Dossier Tokenomics &amp; Unlocks</b><span>Sblocchi &amp; concentrazione 500/500 &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_curva_N1_to_N500.md" target="_blank" rel="noopener"><b>Report Curva N=1..500</b><span>Analisi passo-passo 5 EUR &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/classifica_500_per_rendimento.md" target="_blank" rel="noopener"><b>Classifica 500 per Rendimento</b><span>Ranking integrale Q3 &amp; Nov 21 &nearr;</span></a>
    </div>
  </div>

  <footer>
    <div>Pure Crypto Top 500 Multi-Cycle Forensic Research (2022–2026) &middot; Open Data &amp; Reproducible Python Pipeline</div>
    <div><a href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026" target="_blank" rel="noopener">Repository GitHub (raffaele-ando/crypto-top500-multicycle-2022-2026) &nearr;</a></div>
  </footer>
</main>

<script>
const CENSUS = {census_json};
let html = "<thead><tr><th class='l sticky-col'>Cod</th><th class='l'>Data / Rif. Temporale</th><th>FX EUR/USD</th><th>BTC USD</th><th>ETH USD</th><th>MCap Pure500 (Mld)</th><th class='l'>Cutoff #500</th><th>Curve CMC</th><th>Holders Hist</th><th>Top10 Archive/CC</th><th>Vista B Quotate</th></tr></thead><tbody>";
for (const c of CENSUS) {{
  html += `<tr><td class='l sticky-col'><b>${{c.code}}</b></td><td class='l'>${{c.it_label}}</td><td>${{FMT.fx(c.fx_eur_usd)}}</td><td>${{FMT.dec1(c.btc_usd)}}</td><td>${{FMT.dec1(c.eth_usd)}}</td><td>${{FMT.dec2(c.cohort_mcap_usd_b)}}</td><td class='l'><b>${{c.cutoff_rank500_sym}}</b> <span class='mut'>(${{FMT.dec1(c.cutoff_rank500_mcap_m)}} M)</span></td><td>${{c.n_unlock_official_curve}}/500</td><td>${{c.n_hist_holders_cnt}}/500</td><td>${{c.n_hist_top10_conc}}/500</td><td>${{c.n_vistaB_already_listed}}/500</td></tr>`;
}}
html += "</tbody>";
document.getElementById("timelineTbl").innerHTML = html;
agyRefreshScrollHints();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded index.html ({len(html):,} bytes)")


# ==============================================================================
# 2. FLAGSHIP 15-DATE DASHBOARD
# ==============================================================================
def upgrade_flagship15():
    p = PROJ / "multidate_15_2022_2026" / "dashboard_15date_ciclo_2022_2026.html"
    orig = p.read_text(encoding="utf-8")
    d_json = extract_regex(orig, r"const D = (\{.*?\});\s*\r?\nconst CODES", "flagship15 D JSON")

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pure Crypto Top 500 — Dashboard Multi-Ciclo 15 Date (2022–2026)</title>
{ANTI_FOUC}
<link rel="stylesheet" href="../assets/apple-craft.css">
<style>
.wrap {{ max-width: 1500px; }}
/* Heatmap specific high-contrast ergonomics */
.hm-wrap {{
  position: relative;
  border: 1px solid var(--border);
  border-radius: var(--r-md);
  background: var(--surface);
  overflow: visible;
}}
.hm-wrap table {{ border-collapse: separate; border-spacing: 2px; font-size: 12px; }}
.hm-wrap thead th {{
  position: sticky;
  top: var(--nav-h);
  z-index: 15;
  text-align: center;
  padding: 8px 4px;
  background: var(--surface2);
  border-bottom: 1px solid var(--border-strong);
}}
.hm-wrap thead th.l {{ text-align: left; padding-left: 8px; }}
.hm-wrap tbody td {{ border-bottom: none; padding: 6px 4px; }}
.hm-wrap td.hm-entry {{
  text-align: left;
  padding: 6px 8px;
  white-space: nowrap;
  background: var(--surface);
}}
.hm-entry .hm-d {{ color: var(--muted); font-size: 11px; margin-left: 4px; }}
.hm-cell {{
  cursor: pointer;
  text-align: center;
  font-weight: 700;
  font-size: 11.5px;
  padding: 7px 4px;
  border-radius: 5px;
  min-width: 58px;
  transition: transform 0.1s var(--ease);
}}
@media (hover: hover) {{
  .hm-cell:hover {{ outline: 2px solid var(--accent-text); transform: scale(1.04); position: relative; z-index: 3; }}
}}
.hm-sel {{
  outline: 2.5px solid var(--ink) !important;
  outline-offset: -2px;
  box-shadow: 0 0 0 1px var(--surface);
  position: relative;
  z-index: 4;
}}
.hm-empty {{ text-align: center; color: var(--muted); opacity: 0.55; }}
.inspector {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 165px), 1fr));
  gap: 10px;
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 13px 14px;
  border-radius: var(--r-md);
  margin-top: 12px;
  font-size: 12.5px;
}}
.insp-lbl {{ font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; font-weight: 600; margin-bottom: 3px; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 6px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 7px 6px; height: 46px; }}
.stato-col {{ padding-left: 18px !important; text-align: center !important; }}
.asset-col-va {{ width: 152px; min-width: 136px; max-width: 156px; overflow: hidden; }}
.asset-col-vb {{ width: 162px; min-width: 152px; max-width: 162px; overflow: hidden; }}
#trSummary {{ white-space: normal; max-width: 100%; border-radius: 10px; line-height: 1.35; padding: 5px 10px; }}
@media (max-width: 1100px) {{
  .hm-wrap {{ overflow: auto; max-height: 62vh; }}
  .hm-wrap thead th {{ top: 0; z-index: 10; }}
  .hm-wrap thead th.sticky-col {{ z-index: 12; }}
  .hm-cell {{ padding: 9px 6px; font-size: 11.5px; }}
}}
@media (max-width: 640px) {{
  .hm-entry .hm-d {{ display: block; margin-left: 0; font-size: 10.5px; }}
  .hm-wrap td.hm-entry {{ max-width: 78px; padding: 6px 6px; }}
  .inspector {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 10px; padding: 11px 12px; }}
  .inspector > div:first-child {{ grid-column: 1 / -1; padding-bottom: 4px; border-bottom: 1px solid var(--border); }}
}}
@media (max-height: 480px) and (max-width: 900px) {{
  .page-head h1 {{ font-size: 1.18rem; margin-bottom: 3px; }}
  .page-head .sub {{ font-size: 12px; margin-bottom: 8px; }}
  .kpis {{ gap: 6px; margin-bottom: 10px; }}
  .kpi {{ padding: 8px 10px; }}
  .tabs {{ margin-bottom: 8px; padding-bottom: 6px; }}
}}
</style>
</head>
<body>
<script src="../assets/hub-shell.js"></script>
<script>agyInitHubNav("flagship15", "../");</script>

<div class="wrap">
  <div class="page-head">
    <h1>Pure Crypto Top 500 — Analisi Multi-Ciclo 15 Date <span style="white-space:nowrap">(2022–2026)</span></h1>
    <div class="sub">Zero Survivorship Bias (Vista A: 15&times;500 = 7.500 righe) &middot; Coorte Fissa 1&deg; Luglio 2026 (Vista B: 500&times;15 = 7.500 righe) &middot; EVM Archive Multicall3 &amp; Curve Vesting CMC</div>
  </div>

  <div class="kpis kpis-6" id="kpiStrip"></div>

  <div class="tabs" role="tablist">
    <button class="btn active" role="tab" onclick="showTab('tab-bt', this)">1. Backtest &amp; Tranche</button>
    <button class="btn" role="tab" onclick="showTab('tab-va', this)">2. Vista A (15 Date)</button>
    <button class="btn" role="tab" onclick="showTab('tab-vb', this)">3. Vista B (500 Coin)</button>
    <button class="btn" role="tab" onclick="showTab('tab-fac', this)">4. Fattori &amp; Censimento</button>
  </div>

  <!-- TAB 1: BACKTEST -->
  <section id="tab-bt">
    <div class="card">
      <h2>Matrice Completa 14&times;15 — Investimento 5 EUR/coin (2.500 EUR/coorte)</h2>
      <div class="controls">
        <label>Metrica heatmap:
          <select id="hmMode" onchange="renderHeatmap()">
            <option value="ret_eur_cons_pct">EUR % (Conservativo, Delist = 0)</option>
            <option value="ret_eur_active_pct">EUR % (Solo Attive / Migrate)</option>
            <option value="alpha_vs_btc_pp">Alpha vs BTC EUR (punti %)</option>
            <option value="ret_usd_cons_pct">USD % (Conservativo)</option>
          </select>
        </label>
        <span class="mut" style="font-size:12px">Tocca o clicca una cella per dettagli e confronto BTC</span>
      </div>
      <div class="tbl-sub-bar"><span class="scroll-hint" data-scroll-hint="hmWrap">&larr; Scorri D02..D15 &rarr;</span></div>
      <div class="hm-wrap" id="hmWrap"><table id="hmTable"></table></div>
      <div id="hmInspector" class="inspector"></div>
    </div>

    <div class="card">
      <h2>Analisi Tranche 50..500 (Divergente rispetto allo 0%: Cumulative &amp; Marginali)</h2>
      <div class="controls">
        <label>Ingresso: <select id="trEntry" onchange="syncHorizons(); renderTranches()"></select></label>
        <label>Orizzonte Exit: <select id="trHoriz" onchange="renderTranches()"></select></label>
        <span id="trSummary" class="pill p-blue"></span>
      </div>
      <div class="bars-grid">
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--ink-secondary)">Tranche Cumulative (Top 50 &rarr; Top 500)</h3>
          <div id="barsCum"></div>
        </div>
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--ink-secondary)">Fasce Marginali da 50 Coin (1–50 &rarr; 451–500)</h3>
          <div id="barsMarg"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 2: VISTA A -->
  <section id="tab-va" class="hidden">
    <div class="card">
      <h2>Vista A — Coorte Indipendente Pure Top 500 alla Data Selezionata</h2>
      <div class="controls controls-grid">
        <label>Data: <select id="vaDate" onchange="renderVistaA()"></select></label>
        <label>Ordina: <select id="vaSort" onchange="renderVistaA()">
          <option value="0-asc">Rank Pure (1 &rarr; 500)</option>
          <option value="14-desc">Rend. EUR a D15 (Nov26) &darr;</option>
          <option value="14-asc">Rend. EUR a D15 (Nov26) &uarr;</option>
          <option value="11-desc">Rend. EUR Tappa Succ. &darr;</option>
          <option value="7-desc">Da Sbloccare % &darr;</option>
          <option value="9-desc">Top-10 On-Chain Storica % &darr;</option>
          <option value="8-desc">Holders Storici &darr;</option>
        </select></label>
        <div class="search-box ctrl-full">
          <span class="s-ico">{SEARCH_SVG}</span>
          <input type="search" id="vaSearch" placeholder="Filtra ticker o nome..." oninput="renderVistaA()">
          <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
        </div>
        <span id="vaMeta" class="mut ctrl-full" style="font-size:12px"></span>
      </div>
      <div class="tbl-sub-bar"><span class="scroll-hint" data-scroll-hint="vaWrap">&larr; Scorri tabella &rarr;</span></div>
      <div class="tbl-wrap tbl-compact" id="vaWrap"><table id="vaTable"></table></div>
    </div>
  </section>

  <!-- TAB 3: VISTA B -->
  <section id="tab-vb" class="hidden">
    <div class="card">
      <h2>Vista B — Storico Completo 15 Date delle 500 Crypto (Coorte 1&deg; Luglio 2026)</h2>
      <div class="controls controls-grid">
        <div class="search-box">
          <span class="s-ico">{SEARCH_SVG}</span>
          <input type="search" id="vbSearch" placeholder="Cerca cmc-ID, ticker o nome..." oninput="renderVistaB()">
          <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
        </div>
        <label>Ordina: <select id="vbSort" onchange="renderVistaB()">
          <option value="rk-asc">Rank Pure 1 Lug 2026 (1 &rarr; 500)</option>
          <option value="rf-desc">Rend. EUR 1a Data &rarr; Nov26 &darr;</option>
          <option value="rn-desc">Rend. EUR Lug26 &rarr; Nov26 &darr;</option>
          <option value="nl-desc">Anzianit&agrave; (Date Quotate /15) &darr;</option>
          <option value="t10-desc">Top-10 Ref Nov26 % &darr;</option>
        </select></label>
        <span id="vbCount" class="mut ctrl-full" style="font-size:12px"></span>
      </div>
      <div class="tbl-sub-bar"><span class="scroll-hint" data-scroll-hint="vbWrap">&larr; Scorri tabella &rarr;</span></div>
      <div class="tbl-wrap tbl-compact" id="vbWrap"><table id="vbTable"></table></div>
    </div>
  </section>

  <!-- TAB 4: FACTORS & CENSUS -->
  <section id="tab-fac" class="hidden">
    <div class="card">
      <div class="tbl-head-bar">
        <h2 style="margin:0">Censimento Macro e Copertura Point-in-Time sulle 15 Date (2022–2026)</h2>
        <span class="scroll-hint" data-scroll-hint="censusWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="tbl-wrap no-maxh" id="censusWrap"><table id="censusTable"></table></div>
    </div>
    <div class="card">
      <div class="tbl-head-bar">
        <h2 style="margin:0">Verifica Empirica Zero-Look-Ahead — Unlocks &amp; Concentrazione On-Chain Storica</h2>
        <span class="scroll-hint" data-scroll-hint="facWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="controls">
        <label>Finestra Temporale: <select id="facWin" onchange="renderFactors()"></select></label>
      </div>
      <div class="tbl-wrap no-maxh" id="facWrap"><table id="facTable"></table></div>
    </div>
  </section>
</div>

<script>
const D = {d_json};
const CODES = D.census.map(c => c.code);
const MAT_MAP = Object.fromEntries(D.matrix.map(r => [r.entry_code + "_" + r.exit_code, r]));
let selPair = "D01_D08";

function showTab(id, btn) {{
  document.querySelectorAll("section").forEach(s => s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
  document.querySelectorAll(".tabs .btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  setTimeout(agyRefreshScrollHints, 30);
}}

function fmtP(v) {{
  if (v === "" || v === null || v === undefined) return '<span class="mut">N/Q</span>';
  return FMT.price(v);
}}
function fmtPct(v) {{
  if (v === null || v === undefined || v === "") return '<span class="mut">N/D</span>';
  return `<span class="${{FMT.pctClass(v)}}">${{FMT.pct(v, true, 2)}}</span>`;
}}
function statusBadge(st) {{
  if (!st) return '<span class="pill p-muted">N/D</span>';
  if (st === "ACTIVE") return '<span class="pill p-green" title="ACTIVE al 21 Nov 2026">Attiva</span>';
  if (st.startsWith("MIGRATED")) {{
    const tgt = st.replace("MIGRATED->", "").replace("MIGRATED:", "");
    return `<span class="pill p-purple" title="${{st}}">MIG&rarr;${{tgt}}</span>`;
  }}
  if (st.includes("DELIST")) return `<span class="pill p-red" title="${{st}}">Delist</span>`;
  return `<span class="pill p-muted" title="${{st}}">${{st.slice(0, 10)}}</span>`;
}}

function heatStyle(v) {{
  const light = document.documentElement.getAttribute("data-theme") === "light";
  if (light) {{
    if (v >= 150) return "background:#86efac;color:#052e16";
    if (v >= 50) return "background:#bbf7d0;color:#052e16";
    if (v >= 10) return "background:#dcfce7;color:#14532d";
    if (v >= 0) return "background:#f0fdf4;color:#166534";
    if (v > -20) return "background:#fef2f2;color:#991b1b";
    if (v > -45) return "background:#fee2e2;color:#7f1d1d";
    return "background:#fecaca;color:#7f1d1d";
  }}
  if (v >= 150) return "background:#14532d;color:#ffffff";
  if (v >= 50) return "background:#166534;color:#ffffff";
  if (v >= 10) return "background:#1a4731;color:#ffffff";
  if (v >= 0) return "background:#163024;color:#d1fae5";
  if (v > -20) return "background:#3b1c1c;color:#fecaca";
  if (v > -45) return "background:#5c1d1d;color:#ffffff";
  return "background:#7f1d1d;color:#ffffff";
}}

function initKPIs() {{
  const bestM = D.matrix.reduce((a,b) => b.ret_eur_cons_pct > a.ret_eur_cons_pct ? b : a);
  const worstM = D.matrix.reduce((a,b) => b.ret_eur_cons_pct < a.ret_eur_cons_pct ? b : a);
  const d01_15 = MAT_MAP["D01_D15"];
  const kpis = [
    ["Orizzonte Multi-Ciclo", "15 Date (4 Anni)", "", "30 Dic 2022 &rarr; 21 Nov 2026"],
    ["Righe Totali (A+B)", "15.000 Record", "", "7.500 Vista A + 7.500 Vista B"],
    ["Miglior Finestra", FMT.pct(bestM.ret_eur_cons_pct, true, 1), "pos", `${{bestM.entry_code}} &rarr; ${{bestM.exit_code}} (${{FMT.eur(bestM.final_eur_cons)}})`],
    ["Peggior Finestra", FMT.pct(worstM.ret_eur_cons_pct, true, 1), "neg", `${{worstM.entry_code}} &rarr; ${{worstM.exit_code}} (${{FMT.eur(worstM.final_eur_cons)}})`],
    ["Hold 4 Anni (D01&rarr;D15)", FMT.pct(d01_15.ret_eur_cons_pct, true, 1), d01_15.ret_eur_cons_pct >= 0 ? "pos" : "neg", `${{FMT.eur(d01_15.final_eur_cons)}} <span class="nowrap">(BTC: ${{FMT.pct(d01_15.btc_bench_ret_eur_pct, true, 1)}})</span>`],
    ["Integrit&agrave; On-Chain", `${{D.migrations_n}} Migrazioni`, "acc", "446 EVM Archive + 498 Curve CMC"],
  ];
  document.getElementById("kpiStrip").innerHTML = kpis.map(k =>
    `<div class="kpi"><div class="lbl">${{k[0]}}</div><div class="val ${{k[2]}}">${{k[1]}}</div><div class="note">${{k[3]}}</div></div>`
  ).join("");
}}

function renderHeatmap() {{
  const mode = document.getElementById("hmMode").value;
  let html = "<thead><tr><th class='l sticky-col'>Entry &#8600; Exit</th>" + CODES.slice(1).map(c => `<th class='c'>${{c}}</th>`).join("") + "</tr></thead><tbody>";
  for (let i = 0; i < 14; i++) {{
    const ec = CODES[i], ed = D.census[i].date;
    html += `<tr><td class='hm-entry sticky-col'><b>${{ec}}</b><span class='hm-d'>${{ed}}</span></td>`;
    for (let j = 1; j < 15; j++) {{
      const xc = CODES[j];
      const r = MAT_MAP[ec + "_" + xc];
      if (!r) {{ html += `<td class='hm-empty'>&middot;</td>`; continue; }}
      const v = r[mode];
      const key = ec + "_" + xc;
      const sel = key === selPair ? " hm-sel" : "";
      html += `<td class="hm-cell${{sel}}" style="${{heatStyle(v)}}" onclick="selectPair('${{key}}')" title="${{ec}} (${{ed}}) &rarr; ${{xc}} (${{r.exit_date}}): ${{FMT.pct(v, true, 2)}}">${{FMT.pct(v, true, 1)}}</td>`;
    }}
    html += "</tr>";
  }}
  html += "</tbody>";
  document.getElementById("hmTable").innerHTML = html;
  renderInspector();
  agyRefreshScrollHints();
}}

function selectPair(k) {{ selPair = k; renderHeatmap(); }}
function renderInspector() {{
  const r = MAT_MAP[selPair];
  if (!r) return;
  document.getElementById("hmInspector").innerHTML = [
    ["Finestra Selezionata", `<b>${{r.entry_code}} &rarr; ${{r.exit_code}}</b><br><span class='mut'>${{r.entry_date}} &rarr; ${{r.exit_date}}</span>`],
    ["Finale Cons. (2.500 EUR)", `<b>${{FMT.eur(r.final_eur_cons)}}</b><br>${{fmtPct(r.ret_eur_cons_pct)}} EUR`],
    ["Solo Attive/Migrate", `<b>${{FMT.eur(r.final_eur_active_norm)}}</b><br>${{fmtPct(r.ret_eur_active_pct)}} EUR`],
    ["Benchmark BTC (EUR)", `<b>${{FMT.eur(r.btc_bench_final_eur)}}</b><br>${{fmtPct(r.btc_bench_ret_eur_pct)}}`],
    ["Alpha vs Bitcoin", `<b class="${{r.alpha_vs_btc_pp >= 0 ? 'pos' : 'neg'}}">${{r.alpha_vs_btc_pp >= 0 ? "+" : ""}}${{FMT.dec2(r.alpha_vs_btc_pp)}} pp</b><br>Mediana: ${{fmtPct(r.median_ret_eur_pct)}}`],
    ["Sopravvivenza Coorte", `Attive: <b>${{r.n_active}}</b> &middot; Mig: <b>${{r.n_migrated}}</b><br>Delist (0 EUR): <b class='neg'>${{r.n_delisted_0eur}}</b>`],
    ["Miglior Asset", `<b>${{r.best_coin}}</b><br>${{fmtPct(r.best_ret_pct)}} &middot; Win: ${{FMT.dec1(r.win_rate_pct)}}%`],
  ].map(x => `<div><div class='insp-lbl'>${{x[0]}}</div><div>${{x[1]}}</div></div>`).join("");
}}

function syncHorizons() {{
  const ec = document.getElementById("trEntry").value;
  const avail = [...new Set(D.tranches.filter(x => x.entry_code === ec).map(x => x.horizon))];
  const labels = {{ NEXT_LEG: "Tappa Succ. (Di+1)", TO_D08_PEAK: "D08 — 07 Ott 2025 (Picco)", TO_D14_OCT1: "D14 — 01 Ott 2026", TO_D15_NOV21: "D15 — 21 Nov 2026 05:30 CET" }};
  const sel = document.getElementById("trHoriz");
  const prev = sel.value;
  sel.innerHTML = avail.map(h => `<option value="${{h}}">${{labels[h] || h}}</option>`).join("");
  if (avail.includes(prev)) sel.value = prev;
  else if (avail.includes("TO_D15_NOV21")) sel.value = "TO_D15_NOV21";
}}

function renderBars(elId, rows, labelKey) {{
  const maxAbs = Math.max(15, ...rows.map(r => Math.abs(r.ret_eur_cons_pct)));
  const bestV = Math.max(...rows.map(r => r.ret_eur_cons_pct));
  const scaleHtml = `<div class="div-scale"><span>Tranche</span><div class="div-scale-mid"><span>-${{FMT.dec1(maxAbs)}}%</span><span>0%</span><span>+${{FMT.dec1(maxAbs)}}%</span></div><span style="text-align:right">EUR %</span></div>`;
  const rowsHtml = rows.map(r => {{
    const v = r.ret_eur_cons_pct;
    const w = Math.min(100, Math.abs(v) / maxAbs * 100).toFixed(1);
    const star = v === bestV ? ' <span class="warn" title="Migliore tranche">&#9733;</span>' : "";
    const negBar = v < 0 ? `<div class="div-neg-fill" style="width:${{w}}%"></div>` : "";
    const posBar = v >= 0 ? `<div class="div-pos-fill" style="width:${{w}}%"></div>` : "";
    return `<div class="bar-row"><div><b>${{r[labelKey]}}</b>${{star}}</div><div class="div-track" aria-label="${{r[labelKey]}}: ${{FMT.pct(v, true, 2)}}"><div class="div-neg-wrap">${{negBar}}</div><div class="div-zero"></div><div class="div-pos-wrap">${{posBar}}</div></div><div style="text-align:right">${{fmtPct(v)}}</div></div>`;
  }}).join("");
  document.getElementById(elId).innerHTML = scaleHtml + rowsHtml;
}}

function renderTranches() {{
  const ec = document.getElementById("trEntry").value;
  const hz = document.getElementById("trHoriz").value;
  const cums = D.tranches.filter(x => x.entry_code === ec && x.horizon === hz && x.tranche_type === "CUMULATIVE").map(x => ({{...x, lbl: "Top " + x.tranche_k}}));
  const margs = D.tranches.filter(x => x.entry_code === ec && x.horizon === hz && x.tranche_type === "MARGINAL_50").map(x => ({{...x, lbl: x.slice}}));
  if (!cums.length) return;
  const best = cums.reduce((a,b) => b.ret_eur_cons_pct > a.ret_eur_cons_pct ? b : a);
  document.getElementById("trSummary").innerHTML = `Exit ${{best.exit_code}} (${{best.exit_date}}) &middot; Best: Top ${{best.tranche_k}} (${{FMT.pct(best.ret_eur_cons_pct, true, 2)}}) &middot; BTC: ${{FMT.pct(best.btc_bench_ret_eur_pct, true, 2)}}`;
  renderBars("barsCum", cums, "lbl");
  renderBars("barsMarg", margs, "lbl");
}}

function renderVistaA() {{
  const dc = document.getElementById("vaDate").value;
  const q = document.getElementById("vaSearch").value.trim().toLowerCase();
  const [colIdx, dir] = document.getElementById("vaSort").value.split("-");
  const ci = Number(colIdx);
  const cMeta = D.census.find(c => c.code === dc);
  let rows = D.va[dc] || [];
  if (q) rows = rows.filter(r => r[2].toLowerCase().includes(q) || r[3].toLowerCase().includes(q));
  rows = [...rows].sort((a,b) => {{
    const va = a[ci], vb = b[ci];
    if (va === null && vb === null) return 0;
    if (va === null) return 1; if (vb === null) return -1;
    return dir === "asc" ? va - vb : vb - va;
  }});
  document.getElementById("vaMeta").textContent = `${{rows.length}}/500 coin · BTC ${{FMT.dec2(cMeta.btc_usd)}} USD · FX ${{FMT.fx(cMeta.fx_eur_usd)}} · MCap ${{FMT.dec2(cMeta.cohort_mcap_usd_b)}} Mld USD`;
  let html = "<thead><tr><th class='l sticky-col asset-col-va'># / Asset</th><th>Prezzo USD</th><th>MCap</th><th>Vol 24h</th><th>Da Sbl.</th><th>Holders</th><th>Top10%</th><th>EOA%</th><th>Tappa +1</th><th>A D08</th><th>A D14</th><th>A D15</th><th class='stato-col'>Stato D15</th></tr></thead><tbody>";
  for (const r of rows) {{
    html += `<tr><td class='l sticky-col asset-col-va'><b>#${{r[0]}} ${{r[2]}}</b><span class='small cell-clip' title='${{r[3]}} (CMC #${{r[1]}})'>${{r[3]}} &middot; CMC ${{r[1]}}</span></td><td>${{fmtP(r[4])}}</td><td title="${{FMT.dec1(r[5])}} M USD">${{FMT.compact(r[5]*1e6, "$")}}</td><td title="${{FMT.dec1(r[6])}} M USD">${{FMT.compact(r[6]*1e6, "$")}}</td><td>${{r[7]!==null ? FMT.dec1(r[7])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[8]!==null ? FMT.int(r[8]) : "<span class='mut'>N/D</span>"}}</td><td>${{r[9]!==null ? FMT.dec1(r[9])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[10]!==null ? FMT.dec1(r[10])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{fmtPct(r[11])}}</td><td>${{fmtPct(r[12])}}</td><td>${{fmtPct(r[13])}}</td><td>${{fmtPct(r[14])}}</td><td class='stato-col'>${{statusBadge(r[15])}}</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("vaTable").innerHTML = html;
  agyRefreshScrollHints();
}}

function renderVistaB() {{
  const q = document.getElementById("vbSearch").value.trim().toLowerCase();
  const [key, dir] = document.getElementById("vbSort").value.split("-");
  let rows = D.vb;
  if (q) rows = rows.filter(r => r.fid.toLowerCase().includes(q) || r.sym.toLowerCase().includes(q) || r.nm.toLowerCase().includes(q));
  rows = [...rows].sort((a,b) => {{
    const va = a[key], vb = b[key];
    if (va === null || va === "") return 1; if (vb === null || vb === "") return -1;
    return dir === "asc" ? va - vb : vb - va;
  }});
  document.getElementById("vbCount").textContent = `${{rows.length}} / 500 criptovalute coorte 1° Luglio 2026`;
  let html = "<thead><tr><th class='l sticky-col asset-col-vb'># / Asset</th><th class='l'>1a Data</th><th>Date</th><th>D01 Dic22</th><th>D02 Apr24</th><th>D04 Nov24</th><th>D06 Apr25</th><th>D08 Ott25</th><th>D10 Gen26</th><th>D12 Mag26</th><th>D13 Lug26</th><th>D14 Ott26</th><th>D15 Nov26</th><th>1a&rarr;D15</th><th>Lug&rarr;21N</th><th>Top10</th></tr></thead><tbody>";
  for (const r of rows) {{
    const fsShort = r.fs ? r.fs.replace(" (20", " '").replace(")", "") : "—";
    html += `<tr><td class='l sticky-col asset-col-vb'><b>#${{r.rk}} ${{r.sym}}</b><span class='small cell-clip' title="${{r.nm}} (${{r.fid}})">${{r.nm}} &middot; ${{r.fid}}</span></td><td class='l mut' style='min-width:96px' title="${{r.fs}}">${{fsShort}}</td><td>${{r.nl}}/15</td><td>${{fmtP(r.p01)}}</td><td>${{fmtP(r.p02)}}</td><td>${{fmtP(r.p04)}}</td><td>${{fmtP(r.p06)}}</td><td>${{fmtP(r.p08)}}</td><td>${{fmtP(r.p10)}}</td><td>${{fmtP(r.p12)}}</td><td>${{fmtP(r.p13)}}</td><td>${{fmtP(r.p14)}}</td><td>${{fmtP(r.p15)}}</td><td>${{fmtPct(r.rf)}}</td><td>${{fmtPct(r.rn)}}</td><td>${{r.t10!==null ? FMT.dec1(r.t10)+"%" : "<span class='mut'>N/D</span>"}}</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("vbTable").innerHTML = html;
  agyRefreshScrollHints();
}}

function renderCensus() {{
  let html = "<thead><tr><th class='l sticky-col'>Cod</th><th class='l'>Data / Rif. Temporale</th><th>FX EUR/USD</th><th>BTC USD</th><th>ETH USD</th><th>MCap Pure500 (Mld)</th><th class='l'>Cutoff #500</th><th>Curve CMC</th><th>Holders Hist</th><th>Top10 Hist</th><th>EOA Whale</th><th>Vista B</th></tr></thead><tbody>";
  for (const c of D.census) {{
    html += `<tr><td class='l sticky-col'><b>${{c.code}}</b></td><td class='l'>${{c.it_label}}</td><td>${{FMT.fx(c.fx_eur_usd)}}</td><td>${{FMT.dec1(c.btc_usd)}}</td><td>${{FMT.dec1(c.eth_usd)}}</td><td>${{FMT.dec2(c.cohort_mcap_usd_b)}}</td><td class='l'><b>${{c.cutoff_rank500_sym}}</b> <span class='mut'>(${{FMT.dec1(c.cutoff_rank500_mcap_m)}} M)</span></td><td>${{c.n_unlock_official_curve}}/500</td><td>${{c.n_hist_holders_cnt}}/500</td><td>${{c.n_hist_top10_conc}}/500</td><td>${{c.n_hist_eoa_whale}}/500</td><td>${{c.n_vistaB_already_listed}}/500</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("censusTable").innerHTML = html;
}}

function renderFactors() {{
  const w = document.getElementById("facWin").value;
  const fb = D.factors[w];
  const groups = [["unlock_overhang", "Token da Sbloccare (%)"], ["hist_top10", "Top-10 On-Chain Storica (%)"], ["hist_eoa_whale", "EOA Whale Residua Storica (%)"]];
  let html = "<thead><tr><th class='l'>Fattore Point-in-Time all'Ingresso</th><th class='l'>Fascia</th><th>N Coin</th><th>Media EUR %</th><th>Mediana EUR %</th><th>Win Rate</th></tr></thead><tbody>";
  for (const [gk, gt] of groups) {{
    for (const [bk, bv] of Object.entries(fb[gk])) {{
      if (!bv.n) continue;
      html += `<tr><td class='l'><b>${{gt}}</b></td><td class='l'>${{bk}}</td><td>${{FMT.int(bv.n)}}</td><td>${{fmtPct(bv.mean_eur_pct)}}</td><td>${{fmtPct(bv.median_eur_pct)}}</td><td>${{FMT.dec1(bv.win_rate_pct)}}%</td></tr>`;
    }}
  }}
  html += "</tbody>";
  document.getElementById("facTable").innerHTML = html;
}}

// Init dropdowns & views
initKPIs();
document.getElementById("trEntry").innerHTML = D.census.slice(0,14).map(c => `<option value="${{c.code}}">${{c.code}} — ${{c.it_label}}</option>`).join("");
document.getElementById("vaDate").innerHTML = D.census.map(c => `<option value="${{c.code}}">${{c.code}} — ${{c.it_label}}</option>`).join("");
document.getElementById("facWin").innerHTML = Object.keys(D.factors).map(k => `<option value="${{k}}">${{k.replaceAll("_"," ")}}</option>`).join("");
agyBindSearchClear("vaSearch", renderVistaA);
agyBindSearchClear("vbSearch", renderVistaB);
window.addEventListener("agy-theme-change", renderHeatmap);
syncHorizons(); renderHeatmap(); renderTranches(); renderVistaA(); renderVistaB(); renderCensus(); renderFactors();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded dashboard_15date_ciclo_2022_2026.html ({len(html):,} bytes)")


# ==============================================================================
# 3. STORICO 3 DATE DASHBOARD
# ==============================================================================
def upgrade_storico3():
    p = PROJ / "dashboard_storico_3date_500.html"
    orig = p.read_text(encoding="utf-8")
    data_json = extract_regex(orig, r"const DATA = (\[.*?\]);\s*\r?\nlet mode", "storico3 DATA JSON")

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Serie Storica Point-in-Time sulle 3 Date — Top 500 Pure Crypto (2026)</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1520px; }}
.tbl-wrap {{ max-height: 70vh; }}
.asset-col {{ max-width: 146px; min-width: 110px; }}
.asset-col .cell-clip {{ max-width: 130px; }}
#stWrap .note-clamp {{ max-width: 185px; min-width: 135px; }}
@media (min-width: 960px) {{
  .controls.controls-grid {{ flex-wrap: nowrap; }}
  .controls.controls-grid > select {{ flex: 0 1 255px; }}
}}
@media (min-width: 1280px) {{
  #stWrap thead th, #stWrap tbody td {{ padding: 8px 8px; }}
  #stWrap thead th:nth-child(4), #stWrap tbody td:nth-child(4) {{ padding-left: 14px; }}
  #stWrap thead th:last-child, #stWrap tbody td:last-child {{ padding-right: 12px; }}
}}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("storico3", "./");</script>

<div class="wrap">
  <div class="page-head">
    <h1>Serie Storica Point-in-Time sulle 3 Date — Top 500 Pure Crypto <span style="white-space:nowrap">(Zero Look-Ahead)</span></h1>
    <div class="sub">T1: <b>1&deg; Luglio 2026 23:59 UTC</b> &middot; T2: <b>1&deg; Ottobre 2026 23:59 UTC</b> &middot; T3: <b>21 Novembre 2026 05:30&nbsp;CET</b> &middot; Unlocks storici: <b>500/500 (100%)</b> &middot; Concentrazione on-chain storica (Archive RPC + CoinCarp): <b>193/500</b></div>
  </div>

  <div class="tabs" role="tablist">
    <button class="tab active" data-mode="compare">Confronto 3 Date (T1&rarr;T3)</button>
    <button class="tab" data-mode="jul1">1&deg; Luglio 2026 (T1)</button>
    <button class="tab" data-mode="oct1">1&deg; Ottobre 2026 (T2)</button>
    <button class="tab" data-mode="nov21">21 Nov 05:30 CET (T3)</button>
  </div>

  <div class="controls controls-grid">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome o ticker...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <select id="hFilter" aria-label="Filtro copertura dati">
      <option value="">Tutte le 500 crypto</option>
      <option value="hist_t10">Con Concentrazione Storica 3-Date (193)</option>
      <option value="official_ul">Con Vesting Ufficiale CMC (258)</option>
      <option value="diluted">Diluizione Supply &gt;5% (1 Lug&rarr;21 Nov)</option>
    </select>
    <select id="sortBy" aria-label="Ordinamento tabella">
      <option value="rank_clean_jul1:asc">Ordina: # Clean 1 Lug</option>
      <option value="rank_clean_oct1:asc">Ordina: # Clean 1 Ott</option>
      <option value="rank_clean_nov21:asc">Ordina: # Clean 21 Nov</option>
      <option value="delta_rank_clean_jul_to_nov21:desc">Ordina: Maggior Scalata Clean &darr;</option>
      <option value="supply_inflation_jul_to_nov21_pct:desc">Ordina: Maggior Diluizione Supply &darr;</option>
      <option value="to_unlock_pct_jul1:desc">Ordina: Pi&ugrave; Da Sbloccare (1 Lug) &darr;</option>
      <option value="eoa_whale_hist_jul1_pct:asc">Ordina: Meno Whale EOA (1 Lug) &uarr;</option>
      <option value="ret_jul_to_nov21_usd_pct:desc">Ordina: Rend. 1 Lug&rarr;21 Nov &darr;</option>
    </select>
    <span id="shown" class="pill p-muted" style="justify-self:start">500 / 500</span>
  </div>

  <div class="tbl-sub-bar">
    <span class="scroll-hint" data-scroll-hint="stWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap" id="stWrap">
    <table>
      <thead id="th"></thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>

<script>
const DATA = {data_json};
let mode = "compare";
let curSort = ["rank_clean_jul1", "asc"];

function badge(tier) {{
  if (tier && tier.startsWith("ARCHIVE")) return '<span class="pill p-arch">Archive RPC</span>';
  if (tier && tier.startsWith("COINCARD")) return '<span class="pill p-cc">CoinCarp Hist.</span>';
  return '<span class="pill p-ref">Ref. 24 Nov</span>';
}}

function render() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  const hf = document.getElementById("hFilter").value;
  let arr = DATA.filter(x => {{
    if (q && !(x.name.toLowerCase().includes(q) || x.symbol.toLowerCase().includes(q) || (x.hist_holders_source || "").toLowerCase().includes(q))) return false;
    if (hf === "hist_t10" && x.top10_hist_jul1_pct === null && x.top10_hist_nov21_pct === null) return false;
    if (hf === "official_ul" && !(x.unlock_hist_method || "").includes("Ufficiale")) return false;
    if (hf === "diluted" && !(x.supply_inflation_jul_to_nov21_pct !== null && x.supply_inflation_jul_to_nov21_pct > 5)) return false;
    return true;
  }});
  const [k, dir] = curSort;
  arr.sort((a, b) => {{
    let va = a[k], vb = b[k];
    const na = (va === null || va === undefined), nb = (vb === null || vb === undefined);
    if (na && nb) return a.rank_clean_jul1 - b.rank_clean_jul1;
    if (na) return 1; if (nb) return -1;
    if (typeof va === "string") return dir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
    return dir === "asc" ? va - vb : vb - va;
  }});
  document.getElementById("shown").textContent = `${{arr.length}} / ${{DATA.length}}`;

  if (mode === "compare") {{
    document.getElementById("th").innerHTML = `<tr>
      <th class="l sticky-col">Asset (#1L)</th>
      <th class="num">Clean / CMC (1L&rarr;1O&rarr;21N)</th>
      <th class="num">MCap USD (1L&rarr;1O&rarr;21N)</th>
      <th class="num">Sbloccati % (1L&rarr;1O&rarr;21N)</th>
      <th class="num">&Delta; Supply</th>
      <th class="num">Top 10 Storico (1L&rarr;21N)</th>
      <th class="num">Whale EOA (1L&rarr;21N)</th>
      <th class="num">5 EUR (1O / 21N)</th>
      <th class="l">Fonte Storica</th>
    </tr>`;
    document.getElementById("tb").innerHTML = arr.map(x => {{
      const dcl = x.delta_rank_clean_jul_to_nov21;
      const dclS = dcl !== null ? `<span class="${{dcl >= 0 ? "pos" : "neg"}}">${{dcl > 0 ? "+" : ""}}${{dcl}} pos</span>` : "";
      const inf = x.supply_inflation_jul_to_nov21_pct;
      const t10 = (x.top10_hist_jul1_pct !== null || x.top10_hist_nov21_pct !== null)
        ? `${{FMT.pct(x.top10_hist_jul1_pct, false, 1)}} &rarr; <b>${{FMT.pct(x.top10_hist_nov21_pct, false, 1)}}</b>`
        : `<span class="small">N/D stor. (24N: ${{FMT.pct(x.top10_ref_nov24_pct, false, 1)}})</span>`;
      const eoa = (x.eoa_whale_hist_jul1_pct !== null || x.eoa_whale_hist_nov21_pct !== null)
        ? `${{FMT.pct(x.eoa_whale_hist_jul1_pct, false, 1)}} &rarr; <b>${{FMT.pct(x.eoa_whale_hist_nov21_pct, false, 1)}}</b>`
        : '<span class="mut">N/D</span>';
      const src = x.hist_holders_source || "";
      return `<tr>
        <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}}">#${{String(x.rank_clean_jul1).padStart(3,"0")}} ${{x.name}}</b><span class="small">${{x.symbol}}</span></td>
        <td class="num">#${{x.rank_clean_jul1}}/#${{x.cmc_rank_jul1}} &rarr; #${{x.rank_clean_oct1 || "—"}} &rarr; <b>#${{x.rank_clean_nov21 || "—"}}</b><span class="small">${{dclS}}</span></td>
        <td class="num">${{FMT.compact(x.mcap_usd_jul1)}} &rarr; ${{FMT.compact(x.mcap_usd_oct1)}} &rarr; <b>${{FMT.compact(x.mcap_usd_nov21)}}</b></td>
        <td class="num">${{FMT.pct(x.unlocked_pct_jul1, false, 1)}} &rarr; ${{FMT.pct(x.unlocked_pct_oct1, false, 1)}} &rarr; <b>${{FMT.pct(x.unlocked_pct_nov21, false, 1)}}</b></td>
        <td class="num"><span class="${{(inf || 0) > 5 ? "neg" : ""}}">${{FMT.pct(inf, true, 2)}}</span></td>
        <td class="num">${{t10}}</td>
        <td class="num">${{eoa}}</td>
        <td class="num"><b>${{x.ticket_5eur_oct1_eur ? FMT.dec2(x.ticket_5eur_oct1_eur) + " &euro;" : "N/D"}}</b> / <b>${{x.ticket_5eur_nov21_eur ? FMT.dec2(x.ticket_5eur_nov21_eur) + " &euro;" : "N/D"}}</b><span class="small">${{FMT.pct(x.ret_q3_usd_pct, true, 1)}} / ${{FMT.pct(x.ret_jul_to_nov21_usd_pct, true, 1)}}</span></td>
        <td class="l">${{badge(x.hist_holders_tier)}}<span class="small note-clamp" title="${{src}}">${{src}}</span></td>
      </tr>`;
    }}).join("");
  }} else {{
    const d = mode;
    const dlbl = d === "jul1" ? "1° Lug" : (d === "oct1" ? "1° Ott" : "21 Nov");
    document.getElementById("th").innerHTML = `<tr>
      <th class="l sticky-col">Asset (${{dlbl}})</th>
      <th class="num"># CMC</th>
      <th class="num">Prezzo USD / EUR</th>
      <th class="num">MCap / FDV</th>
      <th class="num">Vol 24h / Pairs</th>
      <th class="num">Sbloccati</th>
      <th class="num">Da Sbloccare</th>
      <th class="num">Top 10 / Distr.</th>
      <th class="num">EOA / Holders</th>
    </tr>`;
    document.getElementById("tb").innerHTML = arr.map(x => {{
      const rkc = x["rank_clean_" + d], rkm = x["cmc_rank_" + d];
      const pu = x["price_usd_" + d], pe = x["price_eur_" + d];
      const mc = x["mcap_usd_" + d], fr = x["fdv_to_mcap_" + d];
      const v24 = x["vol24h_usd_" + d], prs = x["num_pairs_" + d];
      const ult = x["unlocked_tokens_" + d], ulp = x["unlocked_pct_" + d];
      const tult = x["to_unlock_tokens_" + d], tulp = x["to_unlock_pct_" + d];
      const t10 = x["top10_hist_" + d + "_pct"], d10 = x["dist_out_top10_hist_" + d + "_pct"];
      const eoa = x["eoa_whale_hist_" + d + "_pct"], hc = x["holders_cnt_hist_" + d];
      return `<tr>
        <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}}">${{rkc ? "#" + String(rkc).padStart(3,"0") : "N/D"}} ${{x.name}}</b><span class="small">${{x.symbol}}</span></td>
        <td class="num">${{rkm ? "#" + rkm : "N/D"}}</td>
        <td class="num">${{FMT.price(pu, "$")}}<span class="small">${{FMT.price(pe)}} EUR</span></td>
        <td class="num">${{FMT.compact(mc, "$")}}<span class="small">FDV: ${{fr ? FMT.dec2(fr) + "x" : "No Cap"}}</span></td>
        <td class="num">${{FMT.compact(v24, "$")}}<span class="small">${{prs ? FMT.int(prs) + " mercati" : ""}}</span></td>
        <td class="num"><b>${{FMT.pct(ulp, false, 2)}}</b><span class="small">${{FMT.compact(ult)}}</span></td>
        <td class="num"><b>${{tulp !== null ? FMT.pct(tulp, false, 2) : "No Cap"}}</b><span class="small">${{tult !== null ? FMT.compact(tult) : "Supply illimitata"}}</span></td>
        <td class="num">${{t10 !== null ? `<b>${{FMT.pct(t10, false, 2)}}</b> / ${{FMT.pct(d10, false, 1)}}` : '<span class="mut">N/D stor.</span>'}}</td>
        <td class="num">${{eoa !== null ? `<b>${{FMT.pct(eoa, false, 2)}}</b>` : '<span class="mut">N/D</span>'}}<span class="small">Holders: ${{hc ? FMT.int(hc) : "N/D"}}</span></td>
      </tr>`;
    }}).join("");
  }}
  agyRefreshScrollHints();
}}

document.querySelectorAll(".tab").forEach(btn => btn.addEventListener("click", () => {{
  document.querySelectorAll(".tab").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
  mode = btn.dataset.mode;
  if (mode !== "compare") curSort = ["rank_clean_" + mode, "asc"];
  render();
}}));
document.getElementById("q").addEventListener("input", render);
document.getElementById("hFilter").addEventListener("change", render);
document.getElementById("sortBy").addEventListener("change", e => {{ curSort = e.target.value.split(":"); render(); }});
agyBindSearchClear("q", render);
render();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded dashboard_storico_3date_500.html ({len(html):,} bytes)")


# ==============================================================================
# 4. TOKENOMICS & WHALE DECOMPOSITION DASHBOARD
# ==============================================================================
def upgrade_tokenomics():
    p = PROJ / "dashboard_tokenomics_holders_500.html"
    orig = p.read_text(encoding="utf-8")
    data_json = extract_regex(orig, r"const DATA = (\[.*?\]);\s*\r?\nfunction (?:fp|gCls)", "tokenomics DATA JSON")

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audit Forense, Tokenomics &amp; Decomposizione Wallet — Top 500 Pure Crypto 2026</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1520px; }}
.legend {{
  display: flex;
  gap: 8px 16px;
  font-size: 12px;
  color: var(--ink-secondary);
  margin-bottom: 10px;
  flex-wrap: wrap;
}}
.dot {{ width: 9px; height: 9px; border-radius: 50%; display: inline-block; margin-right: 5px; vertical-align: middle; }}
.segbar {{
  display: flex;
  width: 112px;
  height: 8px;
  background: var(--surface2);
  border: 1px solid var(--border);
  border-radius: 99px;
  overflow: hidden;
  margin-top: 2px;
}}
.seg-burn {{ background: #94a3b8; }}
.seg-cex {{ background: #38bdf8; }}
.seg-proto {{ background: #a855f7; }}
.seg-eoa {{ background: #ff5a52; }}
.tbl-wrap {{ max-height: 64vh; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 6px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 6px 6px; }}
.asset-col {{ max-width: 138px; min-width: 108px; }}
.asset-col .cell-clip {{ max-width: 126px; }}
.sort-ind {{ opacity: 0.9; margin-left: 3px; color: var(--accent-text); }}
@media (min-width: 1100px) {{
  .controls.controls-grid {{ flex-wrap: nowrap; }}
  .controls.controls-grid > select {{ flex: 0 1 auto; }}
}}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("tokenomics", "./");</script>

<div class="wrap">
  <div class="page-head">
    <h1>Audit Forense 1-a-1, Sblocchi &amp; Decomposizione Wallet — Top 500 Pure Crypto (2026)</h1>
    <div class="sub" id="tokSub">Verifica individuale su 500/500 crypto...</div>
  </div>

  <div class="kpis kpis-5" id="tokKpis"></div>

  <div class="legend">
    <span><span class="dot" style="background:#94a3b8"></span>Burn / Dead</span>
    <span><span class="dot" style="background:#38bdf8"></span>Custodia CEX (Binance, Coinbase, Upbit...)</span>
    <span><span class="dot" style="background:#a855f7"></span>Smart Contract / Staking / Vesting / LP</span>
    <span><span class="dot" style="background:#ff5a52"></span>Whale / EOA Residui</span>
  </div>

  <div class="controls controls-grid">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome, ticker, wallet o flag...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <select id="grade" aria-label="Filtro Grade affidabilità">
      <option value="">Tutti i Grade (A+/A/B/C/N/D)</option>
      <option value="A+">Solo Grade A+ (Live Top 100 + Decomp)</option>
      <option value="A">Solo Grade A (Live Nov 2026)</option>
      <option value="A+A">Alta Affidabilit&agrave; (A+ e A)</option>
      <option value="B">Grade B (Snapshot 2025–2026)</option>
      <option value="C">Grade C (Datato / Parziale)</option>
      <option value="N/D">Grade N/D (Privacy / L1 senza API)</option>
    </select>
    <select id="verdict" aria-label="Filtro Verdetto Audit">
      <option value="">Tutti i Verdetti Audit</option>
      <option value="PASS_VERIFIED">Verificato (PASS_VERIFIED)</option>
      <option value="PASS_WITH_CAVEATS">Con Riserve (PASS_WITH_CAVEATS)</option>
      <option value="WARNING_CHECK_NOTE">Verifica Nota (WARNING)</option>
      <option value="STRUCTURAL_ND">N/D Strutturale (Privacy)</option>
      <option value="DATA_GAP_ND">Gap Dati (DATA_GAP_ND)</option>
    </select>
    <select id="sortBy" aria-label="Ordinamento tabella">
      <option value="rank_clean_jul1:asc">Ordina: # Clean (1 &rarr; 500)</option>
      <option value="top10_eoa_whale_residual_pct:asc">Ordina: Meno Whale EOA &uarr;</option>
      <option value="top10_eoa_whale_residual_pct:desc">Ordina: Pi&ugrave; Whale EOA &darr;</option>
      <option value="top10_holders_pct:desc">Ordina: Top 10 Lordo &darr;</option>
      <option value="fdv_to_mcap_ratio:desc">Ordina: FDV / Market Cap &darr;</option>
      <option value="to_unlock_pct:desc">Ordina: % Da Sbloccare &darr;</option>
      <option value="ret_q3_pct:desc">Ordina: Rendimento Q3 &darr;</option>
    </select>
    <span id="shown" class="pill p-muted" style="justify-self:start">500 / 500</span>
  </div>

  <div class="tbl-sub-bar">
    <span class="scroll-hint" data-scroll-hint="tokWrap">&larr; Scorri Decomp. &amp; Audit &rarr;</span>
  </div>

  <div class="tbl-wrap tbl-compact" id="tokWrap">
    <table>
      <thead>
        <tr>
          <th class="l sticky-col" data-k="rank_clean_jul1"># / Asset</th>
          <th class="l" data-k="reliability_grade">Grade</th>
          <th class="num" data-k="unlocked_pct">Sbloccati / FDV</th>
          <th class="num" data-k="top10_holders_pct">Top 10</th>
          <th class="l">Decomp. Top 10</th>
          <th class="num" data-k="top10_eoa_whale_residual_pct">Whale EOA</th>
          <th class="l">#1 Wallet &amp; DC</th>
          <th class="num" data-k="ret_q3_pct">Q3 / 21 Nov</th>
          <th class="l">Nota Audit</th>
        </tr>
      </thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>

<script>
const DATA = {data_json};
function gCls(g) {{ return g === "A+" ? "g-ap" : g === "A" ? "g-a" : g === "B" ? "g-b" : g === "C" ? "g-c" : "g-nd"; }}
const VERDICT_LABELS = {{
  PASS_VERIFIED: "Verificato",
  PASS_WITH_CAVEATS: "Con riserve",
  WARNING_CHECK_NOTE: "Verifica nota",
  STRUCTURAL_ND: "N/D strutt.",
  DATA_GAP_ND: "Gap dati"
}};

function median(vals) {{
  if (!vals.length) return null;
  const s = [...vals].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}}

// Dynamic single-source-of-truth KPIs & Subtitle (Zero hardcoded 54 vs 58 contradiction!)
(function initHeaderStats() {{
  const tot = DATA.length;
  const nTop10 = DATA.filter(x => x.top10_holders_pct !== null).length;
  const nDecomp = DATA.filter(x => x.top10_burn_pct !== null).length;
  const nBridge = DATA.filter(x => (x.risk_flags || "").includes("CMC_BRIDGED_CLEANED")).length;
  const nDC = DATA.filter(x => (x.vesting_whale_overlap_flag || "").startsWith("SI")).length;
  const nMicro = DATA.filter(x => (x.risk_flags || "").includes("MICRO_HOLDER_BASE_LT500")).length;
  const nAp = DATA.filter(x => x.reliability_grade === "A+").length;
  const nA = DATA.filter(x => x.reliability_grade === "A").length;
  const nB = DATA.filter(x => x.reliability_grade === "B").length;
  const nC = DATA.filter(x => x.reliability_grade === "C").length;
  const nND = DATA.filter(x => x.reliability_grade === "N/D").length;
  const medTop10 = median(DATA.map(x => x.top10_holders_pct).filter(v => v !== null));
  const medEoa = median(DATA.map(x => x.top10_eoa_whale_residual_pct).filter(v => v !== null));

  document.getElementById("tokSub").innerHTML =
    `Verifica individuale su <b>${{tot}}/${{tot}}</b> crypto &middot; Concentrazione On-Chain Primaria: <b>${{nTop10}}/${{tot}} (${{FMT.dec1(nTop10/tot*100)}}%)</b> &middot; Decomposizione Burn/CEX/SC/EOA: <b>${{nDecomp}}/${{tot}} (${{FMT.dec1(nDecomp/tot*100)}}%)</b> &middot; <b>${{nBridge}}</b> bug bridge CMC bonificati`;

  document.getElementById("tokKpis").innerHTML = [
    ["Grade A+ / A (Live)", `${{nAp + nA}} / ${{tot}}`, "pos", `A+: ${{nAp}} · A: ${{nA}}<br>B: ${{nB}} · C: ${{nC}} · N/D: ${{nND}}`],
    ["Top 10 Lordo &rarr; Whale EOA", `${{FMT.dec1(medTop10)}}% &rarr; ${{FMT.dec1(medEoa)}}%`, "acc", "Mediana reale EOA al netto di Burn, CEX e Smart Contract"],
    ["Bug Bridge CMC Bonificati", `${{nBridge}}`, "acc", "Sostituiti con explorer nativi primari o marcati N/D"],
    ["Rischio Doppio Conteggio", `${{nDC}}`, "warn", "Asset dove il vesting bloccato rientra nei Top 10 wallet"],
    ["Micro-Base (&lt;500 Holder)", `${{nMicro}}`, "neg", "Segnalate con flag di rischio concentrazione elevata"],
  ].map(k => `<div class="kpi"><div class="lbl">${{k[0]}}</div><div class="val ${{k[2]}}">${{k[1]}}</div><div class="det">${{k[3]}}</div></div>`).join("");
}})();

let curSort = ["rank_clean_jul1", "asc"];

function updateSortIndicators() {{
  document.querySelectorAll("thead th[data-k]").forEach(th => {{
    const base = th.dataset.label || th.textContent.replace(/[↑↓]/g, "").trim();
    th.dataset.label = base;
    if (th.dataset.k === curSort[0]) {{
      th.innerHTML = `${{base}}<span class="sort-ind">${{curSort[1] === "asc" ? "&#8593;" : "&#8595;"}}</span>`;
    }} else {{
      th.textContent = base;
    }}
  }});
}}

function render() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  const g = document.getElementById("grade").value;
  const v = document.getElementById("verdict").value;
  let arr = DATA.filter(x => {{
    if (q && !(x.name.toLowerCase().includes(q) || x.symbol.toLowerCase().includes(q) || (x.coin_audit_note || "").toLowerCase().includes(q) || (x.top1_wallet_label || "").toLowerCase().includes(q) || (x.risk_flags || "").toLowerCase().includes(q) || (x.coin_audit_verdict || "").toLowerCase().includes(q))) return false;
    if (g === "A+A" && !(x.reliability_grade === "A+" || x.reliability_grade === "A")) return false;
    else if (g && g !== "A+A" && x.reliability_grade !== g) return false;
    if (v && x.coin_audit_verdict !== v) return false;
    return true;
  }});
  const [k, dir] = curSort;
  arr.sort((a, b) => {{
    let va = a[k], vb = b[k];
    const na = (va === null || va === undefined), nb = (vb === null || vb === undefined);
    if (na && nb) return a.rank_clean_jul1 - b.rank_clean_jul1;
    if (na) return 1; if (nb) return -1;
    if (typeof va === "string") return dir === "asc" ? va.localeCompare(vb) : vb.localeCompare(va);
    return dir === "asc" ? va - vb : vb - va;
  }});
  updateSortIndicators();
  document.getElementById("shown").textContent = `${{arr.length}} / ${{DATA.length}}`;
  document.getElementById("tb").innerHTML = arr.map(x => {{
    const fdv = x.fdv_to_mcap_ratio ? FMT.dec2(x.fdv_to_mcap_ratio) + "x" : null;
    const subUnl = (fdv === null && x.to_unlock_pct === null)
      ? "Supply &infin; (No Cap)"
      : `${{fdv || "No Cap"}} &middot; ${{x.to_unlock_pct !== null ? "Da sbl: " + FMT.dec1(x.to_unlock_pct) + "%" : "Supply &infin;"}}`;
    const seg = x.top10_burn_pct !== null
      ? `<div class="segbar" title="Burn ${{FMT.dec1(x.top10_burn_pct)}}% | CEX ${{FMT.dec1(x.top10_cex_pct)}}% | SC ${{FMT.dec1(x.top10_contract_lock_lp_pct)}}% | EOA ${{FMT.dec1(x.top10_eoa_whale_residual_pct)}}%">
           <div class="seg-burn" style="width:${{x.top10_burn_pct}}%"></div>
           <div class="seg-cex" style="width:${{x.top10_cex_pct}}%"></div>
           <div class="seg-proto" style="width:${{x.top10_contract_lock_lp_pct}}%"></div>
           <div class="seg-eoa" style="width:${{x.top10_eoa_whale_residual_pct}}%"></div>
         </div>
         <span class="small">B:${{FMT.dec1(x.top10_burn_pct)}} · C:${{FMT.dec1(x.top10_cex_pct)}} · S:${{FMT.dec1(x.top10_contract_lock_lp_pct)}}%</span>`
      : `<span class="small">${{x.wallet_decomposition_status || "N/D"}}</span>`;
    const w1 = x.top1_wallet_label ? `${{x.top1_wallet_label}} (${{FMT.dec1(x.top1_wallet_pct)}}%)` : "—";
    const dc = (x.vesting_whale_overlap_flag || "").startsWith("SI") ? '<span class="pill g-c" style="margin-top:2px" title="Doppio conteggio vesting/whale">DC: S&igrave;</span>' : "";
    const q3c = FMT.pctClass(x.ret_q3_pct);
    const n21c = FMT.pctClass(x.ret_nov21_pct);
    const vLbl = VERDICT_LABELS[x.coin_audit_verdict] || x.coin_audit_verdict;
    const note = x.coin_audit_note || "—";
    return `<tr>
      <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}} (CMC #${{x.cmc_rank_jul1}})">#${{String(x.rank_clean_jul1).padStart(3,"0")}} ${{x.name}}</b><span class="small">${{x.symbol}} &middot; CMC #${{x.cmc_rank_jul1}}</span></td>
      <td class="l"><span class="pill ${{gCls(x.reliability_grade)}}">${{x.reliability_grade}}</span><span class="small" title="${{x.coin_audit_verdict}}">${{vLbl}}</span></td>
      <td class="num"><b>${{FMT.pct(x.unlocked_pct, false, 2)}}</b><span class="small">${{subUnl}}</span></td>
      <td class="num"><b>${{FMT.pct(x.top10_holders_pct, false, 2)}}</b><span class="small">Distr: ${{FMT.pct(x.distributed_outside_top10_pct, false, 1)}}</span></td>
      <td class="l">${{seg}}</td>
      <td class="num"><b>${{FMT.pct(x.top10_eoa_whale_residual_pct, false, 2)}}</b><span class="small">ex-B: ${{FMT.pct(x.top10_ex_burn_pct, false, 1)}}</span></td>
      <td class="l"><div class="small wallet-clamp" style="color:var(--ink)" title="${{w1}}">${{w1}}</div>${{dc}}</td>
      <td class="num"><span class="${{q3c}}">${{FMT.pct(x.ret_q3_pct, true, 2)}}</span><span class="small ${{n21c}}">${{FMT.pct(x.ret_nov21_pct, true, 2)}}</span></td>
      <td class="l"><div class="small note-clamp" title="${{note}}">${{note}}</div></td>
    </tr>`;
  }}).join("");
  agyRefreshScrollHints();
}}

document.getElementById("q").addEventListener("input", render);
document.getElementById("grade").addEventListener("change", render);
document.getElementById("verdict").addEventListener("change", render);
document.getElementById("sortBy").addEventListener("change", e => {{ curSort = e.target.value.split(":"); render(); }});
document.querySelectorAll("thead th[data-k]").forEach(th => th.addEventListener("click", () => {{
  const k = th.dataset.k;
  curSort = curSort[0] === k ? [k, curSort[1] === "asc" ? "desc" : "asc"] : [k, "desc"];
  render();
}}));
agyBindSearchClear("q", render);
render();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded dashboard_tokenomics_holders_500.html ({len(html):,} bytes)")


# ==============================================================================
# 5. CURVA N=1..500 DASHBOARD
# ==============================================================================
def upgrade_curva():
    p = PROJ / "curva_rendimento_N1_to_N500.html"
    orig = p.read_text(encoding="utf-8")
    steps_json = extract_regex(orig, r"const STEPS = (\[.*?\]);\s*\r?\nconst cv", "curva STEPS JSON")

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Curva di Rendimento Cumulativa Step-by-Step (N = 1 &rarr; 500)</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
:root, [data-theme="dark"] {{
  --chart-port: #60a5fa;
  --chart-struct: #30d158;
  --chart-median: #fbbf24;
  --chart-btc: #d8b4fe;
}}
[data-theme="light"] {{
  --chart-port: #005ec4;
  --chart-struct: #137333;
  --chart-median: #b45309;
  --chart-btc: #7e22ce;
}}
.wrap {{ max-width: 1480px; }}
.chart-card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--r-lg);
  padding: 14px 16px;
  margin-bottom: 16px;
  position: relative;
  box-shadow: var(--shadow-card);
}}
.legend {{
  display: flex;
  flex-wrap: wrap;
  gap: 6px 16px;
  margin-bottom: 10px;
  font-size: 12px;
  color: var(--ink-secondary);
}}
.leg-item {{ display: inline-flex; align-items: center; gap: 6px; white-space: nowrap; }}
.swatch {{ width: 14px; height: 4px; border-radius: 2px; flex-shrink: 0; }}
canvas#cv {{
  width: 100%;
  height: clamp(235px, 38vh, 360px);
  display: block;
  cursor: crosshair;
  touch-action: pan-y;
}}
#tooltip {{
  position: absolute;
  pointer-events: none;
  background: var(--surface);
  color: var(--ink);
  border: 1px solid var(--border-strong);
  border-radius: 10px;
  padding: 9px 12px;
  font-size: 12px;
  line-height: 1.45;
  display: none;
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35);
  z-index: 20;
  min-width: 225px;
  max-width: calc(100% - 20px);
}}
.sort-ind {{ opacity: 0.9; margin-left: 3px; color: var(--accent-text); }}
@media (max-width: 768px) {{
  .kpis.kpis-4 {{ gap: 7px; margin-bottom: 12px; }}
  .kpi {{ padding: 9px 10px; }}
  .kpi .val {{ font-size: 0.98rem; }}
  .kpi .det {{ font-size: 11px; }}
  .legend {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 5px 8px; font-size: 11px; }}
  .leg-item {{ white-space: normal; line-height: 1.25; }}
  canvas#cv {{ height: 235px; }}
}}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("curva", "./");</script>

<div class="wrap">
  <div class="page-head">
    <h1>Curva di Rendimento Step-by-Step: da N = 1 fino a N = 500 (5 EUR per Crypto)</h1>
    <div class="sub">1&deg; Luglio 2026 &rarr; 1&deg; Ottobre 2026 (Euro Reali, FX 1,1413 &rarr; 1,1327) &middot; Tocca o scorri sul grafico per ispezionare ogni singolo passo N</div>
  </div>

  <div class="kpis kpis-4">
    <div class="kpi"><div class="lbl">Picco Globale (con BTW)</div><div class="val pos">N = 143 (+56,65%)</div><div class="det">715 EUR &rarr; 1.120,08&nbsp;EUR<span class="kpi-sep"> &middot; </span><span class="nowrap">N&nbsp;&ge;&nbsp;10</span></div></div>
    <div class="kpi"><div class="lbl">Benchmark 100% Bitcoin</div><div class="val acc">N = 1 (+42,49%)</div><div class="det">5,00 EUR &rarr; 7,12&nbsp;EUR<span class="kpi-sep"> &middot; </span><span class="nowrap">Riferimento BTC</span></div></div>
    <div class="kpi"><div class="lbl">Picco Strutturale <span class="nowrap">(ex-BTW)</span></div><div class="val pos">N = 93 (+49,77%)</div><div class="det">465 EUR &rarr; 696,43&nbsp;EUR<span class="kpi-sep"> &middot; </span><span class="nowrap">Win&nbsp;83,9%</span></div></div>
    <div class="kpi"><div class="lbl">Portafoglio N = 500</div><div class="val pos">+32,21% (<span class="nowrap">3.305,21&nbsp;EUR</span>)</div><div class="det">2.500 EUR &rarr; +805,21&nbsp;EUR<span class="kpi-sep"> &middot; </span><span class="nowrap">Med.&nbsp;+24,36%</span></div></div>
  </div>

  <div class="chart-card">
    <div class="legend">
      <div class="leg-item"><span class="swatch" style="background:var(--chart-port)"></span>Portafoglio % EUR (con BTW)</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-struct)"></span>Strutturale % EUR (ex-BTW)</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-median)"></span>Mediana % quote portafoglio</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-btc)"></span>Benchmark 100% BTC (+42,49%)</div>
    </div>
    <canvas id="cv" role="img" aria-label="Grafico della curva di rendimento cumulativa da N=1 a N=500"></canvas>
    <div id="tooltip"></div>
  </div>

  <div class="controls">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input type="search" id="q" placeholder="Filtra per N, nome o ticker...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <span id="shown" class="pill p-muted">500 / 500</span>
    <span class="scroll-hint" data-scroll-hint="curvaWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap" id="curvaWrap">
    <table>
      <thead>
        <tr>
          <th class="l sticky-col" data-k="N">N / Crypto Aggiunta</th>
          <th data-k="added_coin_pct_eur">Rend. Singola</th>
          <th data-k="invested_eur">Investito</th>
          <th data-k="portfolio_val_eur_real">Valore Finale</th>
          <th data-k="portfolio_pnl_eur_real">Guadagno</th>
          <th data-k="portfolio_pct_eur_real">Cum. % EUR</th>
          <th data-k="portfolio_pct_eur_ex_btw">Cum. ex-BTW</th>
          <th data-k="marginal_impact_pp">Impatto &Delta;pp</th>
          <th data-k="median_return_pct">Mediana %</th>
          <th data-k="win_rate_pct">Vincenti %</th>
        </tr>
      </thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>

<script>
const STEPS = {steps_json};
const cv = document.getElementById("cv");
const ctx = cv.getContext("2d");
const tip = document.getElementById("tooltip");
let lastHoverIdx = -1;

function chartPalette() {{
  const light = document.documentElement.getAttribute("data-theme") === "light";
  const cs = getComputedStyle(document.documentElement);
  const cPort = cs.getPropertyValue("--chart-port").trim() || (light ? "#005ec4" : "#60a5fa");
  const cStruct = cs.getPropertyValue("--chart-struct").trim() || (light ? "#137333" : "#30d158");
  const cMed = cs.getPropertyValue("--chart-median").trim() || (light ? "#b45309" : "#fbbf24");
  const cBtc = cs.getPropertyValue("--chart-btc").trim() || (light ? "#7e22ce" : "#d8b4fe");
  return light ? {{
    grid: "#e2e2e8",
    axis: "#55555c",
    cross: "#636366",
    pillBgBlue: "#eff6ff",
    pillBgGreen: "#ecfdf5",
    blue: cPort,
    blueText: "#004999",
    green: cStruct,
    greenText: "#137333",
    amber: cMed,
    purple: cBtc
  }} : {{
    grid: "#2c2c2e",
    axis: "#b5b5be",
    cross: "#8e8e93",
    pillBgBlue: "#0d1f38",
    pillBgGreen: "#0b2416",
    blue: cPort,
    blueText: "#93c5fd",
    green: cStruct,
    greenText: "#4ade80",
    amber: cMed,
    purple: cBtc
  }};
}}

function drawCallout(px, py, text, strokeCol, textCol, bgCol, alignRight, yLift = 11) {{
  ctx.save();
  ctx.setLineDash([3, 3]);
  ctx.strokeStyle = strokeCol;
  ctx.lineWidth = 1.1;
  ctx.beginPath(); ctx.moveTo(px, py); ctx.lineTo(px, cv.clientHeight - 30); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = strokeCol;
  ctx.beginPath(); ctx.arc(px, py, 4, 0, Math.PI * 2); ctx.fill();
  ctx.font = "600 10.5px -apple-system, BlinkMacSystemFont, sans-serif";
  const tw = ctx.measureText(text).width + 12;
  const bx = alignRight ? px - tw - 6 : px + 6;
  const by = Math.max(6, py - yLift);
  if (yLift > 14) {{
    ctx.strokeStyle = strokeCol;
    ctx.lineWidth = 1.1;
    ctx.beginPath();
    ctx.moveTo(px, py - 4);
    ctx.lineTo(alignRight ? bx + tw : bx, by + 10);
    ctx.stroke();
  }}
  ctx.fillStyle = bgCol;
  ctx.strokeStyle = strokeCol;
  ctx.lineWidth = 1.1;
  ctx.beginPath();
  ctx.roundRect(bx, by, tw, 20, 6);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = textCol;
  ctx.fillText(text, bx + 6, by + 13.5);
  ctx.restore();
}}

function drawChart(hoverIdx = -1) {{
  lastHoverIdx = hoverIdx;
  const pal = chartPalette();
  const dpr = window.devicePixelRatio || 1;
  const W = cv.clientWidth, H = cv.clientHeight;
  if (!W || !H) return;
  cv.width = W * dpr; cv.height = H * dpr;
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.clearRect(0, 0, W, H);
  const pad = {{ l: 50, r: 16, t: 18, b: 30 }};
  const pw = W - pad.l - pad.r, ph = H - pad.t - pad.b;
  const minY = 15, maxY = 65;
  const xOf = n => pad.l + ((n - 1) / 499) * pw;
  const yOf = v => pad.t + ph - ((v - minY) / (maxY - minY)) * ph;

  ctx.strokeStyle = pal.grid; ctx.lineWidth = 1; ctx.fillStyle = pal.axis;
  ctx.font = "11px -apple-system, BlinkMacSystemFont, sans-serif";
  for (let y = 20; y <= 65; y += 5) {{
    const py = yOf(y);
    ctx.beginPath(); ctx.moveTo(pad.l, py); ctx.lineTo(W - pad.r, py); ctx.stroke();
    ctx.fillText("+" + y + "%", 6, py + 4);
  }}
  const xTicks = W < 540 ? [1, 100, 200, 300, 400, 500] : [1, 50, 100, 150, 200, 250, 300, 350, 400, 450, 500];
  for (const n of xTicks) {{
    const px = xOf(n);
    ctx.beginPath(); ctx.moveTo(px, pad.t); ctx.lineTo(px, H - pad.b); ctx.stroke();
    ctx.fillText("N=" + n, Math.min(W - 38, Math.max(pad.l, px - 14)), H - 10);
  }}

  // BTC benchmark line
  ctx.save(); ctx.setLineDash([5, 5]); ctx.strokeStyle = pal.purple; ctx.lineWidth = 1.4;
  ctx.beginPath(); ctx.moveTo(pad.l, yOf(42.49)); ctx.lineTo(W - pad.r, yOf(42.49)); ctx.stroke();
  ctx.restore();

  const plotLine = (key, color, width) => {{
    ctx.beginPath(); ctx.strokeStyle = color; ctx.lineWidth = width;
    STEPS.forEach((s, i) => {{
      const px = xOf(s.N), py = yOf(s[key]);
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
    }});
    ctx.stroke();
  }};
  plotLine("median_return_pct", pal.amber, 1.6);
  plotLine("portfolio_pct_eur_ex_btw", pal.green, 2.0);
  plotLine("portfolio_pct_eur_real", pal.blue, 2.4);

  // Dedicated Peak Callouts (N=93 ex-BTW lifted cleanly above early peak & N=143 +BTW) with WCAG AAA contrast
  if (W >= 420) {{
    const s93 = STEPS[92], s143 = STEPS[142];
    if (s93) drawCallout(xOf(93), yOf(s93.portfolio_pct_eur_ex_btw), "N=93 (+49,77% ex-BTW)", pal.green, pal.greenText, pal.pillBgGreen, true, 36);
    if (s143) drawCallout(xOf(143), yOf(s143.portfolio_pct_eur_real), "N=143 (+56,65% +BTW)", pal.blue, pal.blueText, pal.pillBgBlue, false, 11);
  }}

  if (hoverIdx >= 0 && hoverIdx < STEPS.length) {{
    const s = STEPS[hoverIdx];
    const px = xOf(s.N), py = yOf(s.portfolio_pct_eur_real);
    ctx.strokeStyle = pal.cross; ctx.lineWidth = 1;
    ctx.beginPath(); ctx.moveTo(px, pad.t); ctx.lineTo(px, H - pad.b); ctx.stroke();
    ctx.fillStyle = pal.blue; ctx.beginPath(); ctx.arc(px, py, 5, 0, Math.PI * 2); ctx.fill();
  }}
}}

function inspectAtClientX(clientX) {{
  const rect = cv.getBoundingClientRect();
  const mx = clientX - rect.left;
  const pw = rect.width - 50 - 16;
  let idx = Math.round(((mx - 50) / pw) * 499);
  idx = Math.max(0, Math.min(499, idx));
  drawChart(idx);
  const s = STEPS[idx];
  tip.style.display = "block";
  const left = Math.min(rect.width - 240, Math.max(10, mx + 14));
  tip.style.left = left + "px";
  tip.style.top = "44px";
  tip.innerHTML = `<strong>N = ${{s.N}} &middot; ${{s.added_name}} [${{s.added_symbol}}]</strong><br>` +
    `Singola: <span class="${{s.added_coin_pct_eur >= 0 ? "pos" : "neg"}}">${{FMT.pct(s.added_coin_pct_eur, true, 2)}}</span> (${{FMT.eur(s.added_coin_val_oct1_eur)}})<br>` +
    `Portafoglio: ${{FMT.int(s.invested_eur)}} EUR &rarr; <strong>${{FMT.eur(s.portfolio_val_eur_real)}}</strong> (${{FMT.eurSigned(s.portfolio_pnl_eur_real)}})<br>` +
    `Cumulativo: <strong class="pos">${{FMT.pct(s.portfolio_pct_eur_real, true, 2)}}</strong> (ex-BTW: ${{FMT.pct(s.portfolio_pct_eur_ex_btw, true, 2)}})<br>` +
    `Mediana: ${{FMT.pct(s.median_return_pct, true, 2)}} &middot; Vincenti: ${{FMT.dec1(s.win_rate_pct)}}%`;
}}

cv.addEventListener("pointermove", e => inspectAtClientX(e.clientX));
cv.addEventListener("pointerdown", e => inspectAtClientX(e.clientX));
cv.addEventListener("touchstart", e => {{ if (e.touches[0]) inspectAtClientX(e.touches[0].clientX); }}, {{ passive: true }});
cv.addEventListener("touchmove", e => {{ if (e.touches[0]) inspectAtClientX(e.touches[0].clientX); }}, {{ passive: true }});
cv.addEventListener("pointerleave", e => {{ if (e.pointerType === "mouse") {{ tip.style.display = "none"; drawChart(-1); }} }});
window.addEventListener("resize", () => drawChart(lastHoverIdx));
window.addEventListener("agy-theme-change", () => drawChart(lastHoverIdx));
drawChart(-1);

let sortKey = "N", sortDir = 1;
function updateSortIndicators() {{
  document.querySelectorAll("thead th[data-k]").forEach(th => {{
    const base = th.dataset.label || th.textContent.replace(/[↑↓]/g, "").trim();
    th.dataset.label = base;
    if (th.dataset.k === sortKey) {{
      th.innerHTML = `${{base}}<span class="sort-ind">${{sortDir === 1 ? "&#8593;" : "&#8595;"}}</span>`;
    }} else {{
      th.textContent = base;
    }}
  }});
}}
function renderTable() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  let rows = STEPS.filter(s => !q || String(s.N) === q || s.added_name.toLowerCase().includes(q) || s.added_symbol.toLowerCase().includes(q));
  rows.sort((a, b) => typeof a[sortKey] === "string" ? a[sortKey].localeCompare(b[sortKey]) * sortDir : (a[sortKey] - b[sortKey]) * sortDir);
  updateSortIndicators();
  document.getElementById("shown").textContent = `${{rows.length}} / ${{STEPS.length}}`;
  document.getElementById("tb").innerHTML = rows.map(s => `
    <tr>
      <td class="l sticky-col"><strong>#${{s.N}} ${{s.added_name}}</strong> <span class="mut">(${{s.added_symbol}})</span></td>
      <td class="${{s.added_coin_pct_eur >= 0 ? "pos" : "neg"}}">${{FMT.pct(s.added_coin_pct_eur, true, 2)}}</td>
      <td>${{FMT.eur(s.invested_eur)}}</td>
      <td>${{FMT.eur(s.portfolio_val_eur_real)}}</td>
      <td class="${{s.portfolio_pnl_eur_real >= 0 ? "pos" : "neg"}}">${{FMT.eurSigned(s.portfolio_pnl_eur_real)}}</td>
      <td class="pos">${{FMT.pct(s.portfolio_pct_eur_real, true, 2)}}</td>
      <td>${{FMT.pct(s.portfolio_pct_eur_ex_btw, true, 2)}}</td>
      <td class="${{s.marginal_impact_pp >= 0 ? "pos" : "neg"}}">${{s.marginal_impact_pp >= 0 ? "+" : ""}}${{s.marginal_impact_pp.toFixed(3).replace(".", ",")}}</td>
      <td>${{FMT.pct(s.median_return_pct, true, 2)}}</td>
      <td>${{FMT.dec1(s.win_rate_pct)}}%</td>
    </tr>`).join("");
  agyRefreshScrollHints();
}}
document.getElementById("q").addEventListener("input", renderTable);
document.querySelectorAll("th[data-k]").forEach(th => th.addEventListener("click", () => {{
  if (sortKey === th.dataset.k) sortDir *= -1; else {{ sortKey = th.dataset.k; sortDir = th.dataset.k === "N" ? 1 : -1; }}
  renderTable();
}}));
agyBindSearchClear("q", renderTable);
renderTable();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded curva_rendimento_N1_to_N500.html ({len(html):,} bytes)")


# ==============================================================================
# 6 & 7. PURE 500 Q3 & RAW TOP 500 BASELINE
# ==============================================================================
def upgrade_pure_or_raw(is_raw: bool, excl_map: dict):
    fname = "dashboard_top500_crypto_2026.html" if is_raw else "dashboard_pure500_crypto_2026.html"
    p = PROJ / fname
    orig = p.read_text(encoding="utf-8")
    d_full_json = extract_regex(orig, r"const (?:D|RAW)\s*=\s*(\{.*?\})(?:\.rows)?;", f"{fname} D JSON")

    active_id = "raw500" if is_raw else "pure500"
    rank_key = "rank_mcap_jul1" if is_raw else "rank_clean_jul1"
    title = (
        "Snapshot Raw Top 500 Originale (Pre-Pulizia) — 1 Lug · 1 Ott · 21 Nov 2026"
        if is_raw
        else "Clean Pure Crypto Top 500 — 1 Lug · 1 Ott · 21 Nov 2026 (05:30 CET)"
    )
    h1 = (
        "Top 500 Criptovalute Originali (Baseline Pre-Filtro) — 2026"
        if is_raw
        else "Clean Pure Crypto Top 500 — 1&deg; Luglio &middot; 1&deg; Ottobre &middot; 21 Novembre 2026"
    )
    sub = (
        "500/500 asset originali al 1&deg; Luglio 2026 (318 pure + 182 escluse da Pure 500: stablecoin, wrapped/LST, RWA, illiquide) &middot; Clicca le intestazioni per ordinare"
        if is_raw
        else "500/500 criptovalute pure e liquide &middot; Portafoglio 5 EUR/coin: 2.500 EUR &rarr; 3.305,21 EUR (1 Ott) &rarr; 2.728,87 EUR (21 Nov 05:30&nbsp;CET)"
    )

    excl_script = f"const EXCL = {json.dumps(excl_map, ensure_ascii=False)};" if is_raw else "const EXCL = {};"
    raw_filter_html = (
        """<div class="seg-group" role="group" aria-label="Filtro purezza">
      <button type="button" class="btn active" data-ef="all">Tutti (500)</button>
      <button type="button" class="btn" data-ef="pure">Solo Pure (318)</button>
      <button type="button" class="btn" data-ef="excl">Esclusi (182)</button>
    </div>"""
        if is_raw
        else ""
    )

    kpi_js = (
        """const S = RAW.summary;
const nExcl = D.filter(r => EXCL[String(r.cmc_id)]).length;
document.getElementById("kpiStrip").innerHTML = [
  ["Universo Raw 1 Lug", `500 Asset`, "", `${D.length - nExcl} Pure · ${nExcl} Escluse`],
  ["MCap Coorte 1 Lug", FMT.compact(S.total_cohort_mcap_jul1_usd, "$"), "", "Cutoff #500: " + FMT.compact(S.rank500_jul1_mcap_usd, "$")],
  ["MCap Coorte 1 Ott", FMT.compact(S.total_cohort_mcap_oct1_active_usd, "$"), "pos", FMT.pct(S.cohort_mcap_growth_active_pct, true, 2) + " · Med. " + FMT.pct(S.median_price_return_pct, true, 2)],
  ["MCap 21 Nov 05:30", FMT.compact(S.total_cohort_mcap_nov21_0530_usd, "$"), S.total_cohort_mcap_nov21_0530_usd >= S.total_cohort_mcap_jul1_usd ? "pos" : "neg", `Attive: ${S.active_priced_on_nov21_0530}/500`],
].map(k => `<div class="kpi"><div class="lbl">${k[0]}</div><div class="val ${k[2]}">${k[1]}</div><div class="det">${k[3]}</div></div>`).join("");"""
        if is_raw
        else """const S = RAW.summary;
document.getElementById("kpiStrip").innerHTML = [
  ["Portafoglio 1 Ott (Q3)", FMT.eur(S.portfolio_2500eur_oct1_eur), "pos", "+32,21% EUR · Med. " + FMT.pct(S.median_price_return_pct, true, 2)],
  ["Portafoglio 21 Nov 05:30", FMT.eur(S.portfolio_2500eur_nov21_0530_eur), S.portfolio_2500eur_jul_to_nov21_pct >= 0 ? "pos" : "neg", FMT.pct(S.portfolio_2500eur_jul_to_nov21_pct, true, 2) + " EUR · Med. " + FMT.pct(S.median_jul_to_nov21_eur_pct, true, 2)],
  ["MCap Coorte 1 Lug &rarr; 1 Ott", FMT.compact(S.total_cohort_mcap_oct1_active_usd, "$"), "pos", FMT.pct(S.cohort_mcap_growth_pct, true, 2) + " da " + FMT.compact(S.total_cohort_mcap_jul1_usd, "$")],
  ["MCap 21 Nov 05:30", FMT.compact(S.total_cohort_mcap_nov21_0530_usd, "$"), S.cohort_mcap_jul_to_nov21_pct >= 0 ? "pos" : "neg", FMT.pct(S.cohort_mcap_jul_to_nov21_pct, true, 2) + " vs 1 Lug · 274 escluse"],
].map(k => `<div class="kpi"><div class="lbl">${k[0]}</div><div class="val ${k[2]}">${k[1]}</div><div class="det">${k[3]}</div></div>`).join("");"""
    )

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1500px; }}
.tbl-wrap {{ max-height: 66vh; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 6px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 6px 6px; }}
.asset-col {{ max-width: 210px; min-width: 145px; }}
.asset-title-row {{ display: flex; align-items: center; gap: 5px; min-width: 0; }}
.asset-title-row strong.cell-clip {{ display: inline-block; flex: 0 1 auto; min-width: 0; max-width: 142px; }}
.seg-group {{ display: inline-flex; gap: 6px; flex-wrap: wrap; }}
.sort-ind {{ opacity: 0.9; margin-left: 3px; color: var(--accent-text); }}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("{active_id}", "./");</script>

<div class="wrap">
  <div class="page-head">
    <h1>{h1}</h1>
    <div class="sub">{sub}</div>
  </div>

  <div class="kpis kpis-4" id="kpiStrip"></div>

  <div class="controls">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome, ticker o cmc-ID...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    {raw_filter_html}
    <span id="shown" class="pill p-muted">500 / 500</span>
    <span class="scroll-hint" data-scroll-hint="tblWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap tbl-compact" id="tblWrap">
    <table>
      <thead>
        <tr>
          <th class="l sticky-col" data-k="{rank_key}">#</th>
          <th data-k="cmc_rank_jul1">CMC#</th>
          <th class="l" data-k="name">Criptovaluta</th>
          <th data-k="price_jul1_usd">Prezzo 1 Lug</th>
          <th data-k="mcap_jul1_usd">MCap 1 Lug</th>
          <th data-k="price_oct1_usd">Prezzo 1 Ott</th>
          <th data-k="mcap_oct1_usd">MCap 1 Ott</th>
          <th data-k="price_nov21_0530_usd">Prezzo 21 Nov</th>
          <th data-k="mcap_nov21_0530_usd">MCap 21 Nov</th>
          <th data-k="price_change_pct">&Delta;% Lug&rarr;Ott</th>
          <th data-k="price_change_jul_to_nov21_pct">&Delta;% Lug&rarr;21N</th>
          <th data-k="price_change_oct_to_nov21_pct">&Delta;% Ott&rarr;21N</th>
        </tr>
      </thead>
      <tbody id="tb"></tbody>
    </table>
  </div>
</div>

<script>
const RAW = {d_full_json};
const D = RAW.rows;
{excl_script}
{kpi_js}

let sk = "{rank_key}", sd = 1, ef = "all";

function updateSortIndicators() {{
  document.querySelectorAll("thead th[data-k]").forEach(th => {{
    const base = th.dataset.label || th.textContent.replace(/[↑↓]/g, "").trim();
    th.dataset.label = base;
    if (th.dataset.k === sk) {{
      th.innerHTML = `${{base}}<span class="sort-ind">${{sd === 1 ? "&#8593;" : "&#8595;"}}</span>`;
    }} else {{
      th.textContent = base;
    }}
  }});
}}

function rawUsdTitle(v) {{
  return v == null ? "N/D" : "$" + FMT.int(v) + " USD";
}}

function ren() {{
  const q = document.getElementById("q").value.trim().toLowerCase();
  let rs = D.filter(r => {{
    const ex = EXCL[String(r.cmc_id)];
    if (ef === "pure" && ex) return false;
    if (ef === "excl" && !ex) return false;
    if (!q) return true;
    return r.name.toLowerCase().includes(q) || r.symbol.toLowerCase().includes(q) || r.forensic_id.toLowerCase().includes(q) || (ex && ex[0].toLowerCase().includes(q));
  }});
  rs.sort((a, b) => {{
    let va = a[sk], vb = b[sk];
    if (va == null && vb == null) return 0;
    if (va == null) return 1;
    if (vb == null) return -1;
    return typeof va === "string" ? va.localeCompare(vb) * sd : (va - vb) * sd;
  }});
  updateSortIndicators();
  document.getElementById("shown").textContent = `${{rs.length}} / ${{D.length}}`;
  document.getElementById("tb").innerHTML = rs.map(r => {{
    const ex = EXCL[String(r.cmc_id)];
    const exBadge = ex ? ` <span class="pill ${{ex[1]}}" title="${{ex[2]}}">${{ex[0]}}</span>` : "";
    return `<tr>
      <td class="l sticky-col"><b>${{r["{rank_key}"]}}</b></td>
      <td class="mut">${{r.cmc_rank_jul1}}</td>
      <td class="l asset-col"><div class="asset-title-row"><strong class="cell-clip" title="${{r.name}}">${{r.name}}</strong>${{exBadge}}</div><span class="small">${{r.symbol}} &middot; ${{r.forensic_id}}</span></td>
      <td>${{FMT.price(r.price_jul1_usd, "$")}}</td>
      <td title="${{rawUsdTitle(r.mcap_jul1_usd)}}">${{FMT.compact(r.mcap_jul1_usd, "$")}}</td>
      <td>${{FMT.price(r.price_oct1_usd, "$")}}</td>
      <td title="${{rawUsdTitle(r.mcap_oct1_usd)}}">${{FMT.compact(r.mcap_oct1_usd, "$")}}</td>
      <td>${{FMT.price(r.price_nov21_0530_usd, "$")}}</td>
      <td title="${{rawUsdTitle(r.mcap_nov21_0530_usd)}}">${{FMT.compact(r.mcap_nov21_0530_usd, "$")}}</td>
      <td class="${{FMT.pctClass(r.price_change_pct)}}">${{FMT.pct(r.price_change_pct, true, 2)}}</td>
      <td class="${{FMT.pctClass(r.price_change_jul_to_nov21_pct)}}">${{FMT.pct(r.price_change_jul_to_nov21_pct, true, 2)}}</td>
      <td class="${{FMT.pctClass(r.price_change_oct_to_nov21_pct)}}">${{FMT.pct(r.price_change_oct_to_nov21_pct, true, 2)}}</td>
    </tr>`;
  }}).join("");
  agyRefreshScrollHints();
}}

document.getElementById("q").addEventListener("input", ren);
document.querySelectorAll("th[data-k]").forEach(t => t.addEventListener("click", () => {{
  sk === t.dataset.k ? (sd *= -1) : (sk = t.dataset.k, sd = (t.dataset.k === "{rank_key}" || t.dataset.k === "cmc_rank_jul1" || t.dataset.k === "name") ? 1 : -1);
  ren();
}}));
document.querySelectorAll("[data-ef]").forEach(b => b.addEventListener("click", () => {{
  document.querySelectorAll("[data-ef]").forEach(x => x.classList.remove("active"));
  b.classList.add("active");
  ef = b.dataset.ef;
  ren();
}}));
agyBindSearchClear("q", ren);
ren();
</script>
</body>
</html>
"""
    p.write_text(html, encoding="utf-8")
    print(f"[OK] Upgraded {fname} ({len(html):,} bytes)")


def main():
    excl_map = load_excl_map()
    print(f"Loaded {len(excl_map)} forensic exclusion categories from excluded_274_assets_clean500.csv")
    upgrade_index()
    upgrade_flagship15()
    upgrade_storico3()
    upgrade_tokenomics()
    upgrade_curva()
    upgrade_pure_or_raw(is_raw=False, excl_map=excl_map)
    upgrade_pure_or_raw(is_raw=True, excl_map=excl_map)
    print("\n=== ALL 7 HTML PAGES UPGRADED TO UNIFIED APPLE-CRAFT DESIGN SYSTEM ===")


if __name__ == "__main__":
    main()
