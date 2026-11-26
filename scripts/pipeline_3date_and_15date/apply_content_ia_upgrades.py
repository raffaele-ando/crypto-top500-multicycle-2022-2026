#!/usr/bin/env python3
"""
apply_content_ia_upgrades.py
Upgrades UX Writing, Content Design, and Information Architecture across all 7 HTML pages
while preserving 100% of embedded JSON data verbatim, 500/500 Forensic Completeness parity,
and 100% of the 3/3 APPROVED Apple-Craft Light & True OLED Dark visual system.
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
        "STABLECOIN": ("Stablecoin", "p-blue", "Esclusa dalla Top 500 Pure: stablecoin ancorata a valuta fiat"),
        "WRAPPED_LST_LRT_RECEIPT": ("Wrapped/LST", "p-purple", "Esclusa dalla Top 500 Pure: token wrapped, liquid staking o ricevuta"),
        "TOKENIZED_ETF_STOCK_RWA_COMMODITY": ("RWA", "p-amber", "Esclusa dalla Top 500 Pure: azione, ETF, oro o asset tokenizzato (RWA)"),
        "PUNTO_1_ILLIQUIDI_VOL_LT_100K": ("Illiquida", "p-red", "Esclusa dalla Top 500 Pure: volume 24h inferiore a 100.000 $"),
        "PUNTO_2_ZOMBIE_FALLITI_CHIUSI": ("Chiusa", "p-red", "Esclusa dalla Top 500 Pure: progetto chiuso o inattivo"),
        "PUNTO_3_SUBNET_E_GAS_SECONDARI": ("Subnet", "p-muted", "Esclusa dalla Top 500 Pure: subnet o token gas secondario"),
    }
    out = {}
    with open(p, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            cid = str(row["cmc_id"]).strip()
            r = row.get("reason", "").strip()
            out[cid] = reason_short.get(r, ("Esclusa", "p-muted", r))
    return out


# ==============================================================================
# 1. PANORAMICA (index.html)
# ==============================================================================
def upgrade_index():
    p = PROJ / "index.html"
    orig = p.read_text(encoding="utf-8")
    census_json = extract_regex(orig, r"const CENSUS = (\[.*?\]);", "index CENSUS")
    cohorts_grid = extract_regex(
        orig,
        r"(?:12 [Ff]ile CSV [Ii]ndividuali[^<]*</h3>)\s*<div class=\"dl-grid\">(.*?)</div>",
        "index 12 cohorts grid",
    )

    html = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pure Crypto Top 500 — Backtest e Analisi On-Chain Multi-Ciclo (2022–2026)</title>
<meta name="description" content="Ricerca empirica indipendente sulle prime 500 criptovalute native liquide (Pure Crypto) attraverso 15 date dal 30 dicembre 2022 al 21 novembre 2026: backtest 5 EUR per coin, fasce Top 50-500, sblocchi di supply e concentrazione on-chain.">
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1320px; }}
.hero {{ padding: 14px 0 20px; }}
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
  font-size: clamp(1.56rem, 3.7vw, 2.75rem);
  font-weight: 700;
  letter-spacing: -0.028em;
  line-height: 1.12;
  max-width: 920px;
}}
.lead {{
  color: var(--muted);
  font-size: clamp(14.5px, 1.32vw, 16.5px);
  max-width: 860px;
  margin: 0 0 18px;
  line-height: 1.54;
}}
.lead strong {{ color: var(--ink); font-weight: 600; }}
.hero-cta {{ display: flex; flex-wrap: wrap; gap: 10px; }}
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
.app-card h3 {{ margin: 0 0 8px; font-size: 16.5px; font-weight: 700; letter-spacing: -0.015em; }}
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
@media (max-width: 960px) and (min-width: 541px) {{
  .hero-cta {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .hero-cta .btn {{ width: 100%; }}
}}
@media (max-width: 540px) {{
  .eyebrow {{ border-radius: 14px; font-size: 11.5px; padding: 6px 11px; margin-bottom: 10px; }}
  .hero {{ padding: 8px 0 16px; }}
  .hero h1 {{ font-size: clamp(1.38rem, 6.2vw, 1.85rem); margin-bottom: 9px; }}
  .lead {{ font-size: 14px; margin-bottom: 14px; }}
  .hero-cta {{ display: grid; grid-template-columns: 1fr; gap: 8px; }}
  .hero-cta .btn {{ width: 100%; }}
}}
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
    <div class="eyebrow">Ricerca indipendente &middot; 500/500 prezzi storici verificati &middot; Zero bias di sopravvivenza</div>
    <h1>Come rendono davvero le prime 500 criptovalute su un intero ciclo <span class="nowrap">(2022–2026)</span></h1>
    <p class="lead">
      Investendo <strong class="nowrap">5&nbsp;&euro;</strong> su ciascuna delle prime <strong>500 criptovalute native</strong> (&laquo;Pure Crypto&raquo;, <span class="nowrap">2.500&nbsp;&euro;</span> totali) dal 30 dicembre 2022 al 21 novembre 2026, il portafoglio perde il <strong>57,3% in EUR</strong> (scendendo a <span class="nowrap">1.067&nbsp;&euro;</span>), mentre le <strong>Top 50</strong> crescono del <strong>37,5%</strong> e Bitcoin del <strong>226,1%</strong>. I calcoli includono i 44 token rimossi dal mercato (valutati a <span class="nowrap">0&nbsp;&euro;</span>) e 24 cambi di ticker o contratto convertiti al rapporto ufficiale.
    </p>
    <p class="lead-note"><strong>Cos'&egrave; il paniere &laquo;Pure Crypto&raquo;:</strong> criptovalute native liquide, escluse stablecoin, token replicati o di staking liquido (wrapped/LST), asset reali tokenizzati (RWA) e token con volume giornaliero inferiore a <span class="nowrap">100.000&nbsp;USD</span>.</p>
    <div class="hero-cta">
      <a class="btn btn-primary" href="./multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html">Esplora il Backtest 2022–2026 &rarr;</a>
      <a class="btn" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/multidate_15_2022_2026/report_15date_2022_2026_completo.md" target="_blank" rel="noopener">Dossier metodologico (GitHub &nearr;)</a>
    </div>
  </section>

  <section class="kpis" aria-label="Risultati principali della ricerca">
    <div class="kpi"><div class="lbl">Miglior finestra (Top 500)</div><div class="val pos">+173,0% EUR</div><div class="note">Dic 2022 &rarr; Apr 2024<span class="kpi-sep"> &middot; </span><span class="nowrap">2.500&nbsp;&euro; &rarr; 6.825&nbsp;&euro;</span></div></div>
    <div class="kpi"><div class="lbl">Intero ciclo (Top 500 &middot; 4 anni)</div><div class="val neg">-57,3% EUR</div><div class="note"><span class="nowrap">2.500&nbsp;&euro; &rarr; 1.067&nbsp;&euro;</span><span class="kpi-sep"> &middot; </span><span class="nowrap">Top 50 +37,5%</span> &middot; <span class="nowrap">BTC +226,1%</span></div></div>
    <div class="kpi"><div class="lbl">Orizzonte e rilevazioni</div><div class="val">15 date &middot; 4 anni</div><div class="note">7.500 classifiche storiche + 7.500 paniere fisso lug 2026 (15.000 totali)</div></div>
    <div class="kpi"><div class="lbl">Copertura on-chain diretta</div><div class="val acc">95,2% (476/500)</div><div class="note">96,0% esclusi i 4 privacy coin &middot; 446 asset su reti EVM</div></div>
    <div class="kpi"><div class="lbl">Calendari ufficiali di sblocco</div><div class="val">498 curve CoinMarketCap</div><div class="note">Asset univoci nel quadriennio (196–261/500 per data)</div></div>
    <div class="kpi"><div class="lbl">Migrazioni di token risolte</div><div class="val">24 conversioni</div><div class="note">MATIC&rarr;POL, FTM&rarr;S, MKR&rarr;SKY al rapporto ufficiale</div></div>
  </section>

  <h2 class="sec-title" id="dashboards">Esplora le dashboard interattive</h2>
  <p class="sec-sub">Scegli la vista adatta alla tua domanda: dal rendimento sull'intero ciclo fino al dettaglio on-chain dei singoli asset.</p>
  <section class="grid-apps">
    <a class="app-card featured" href="./multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html">
      <div>
        <span class="tag tag-blue">Ciclo 2022–2026 &middot; 15 date</span>
        <h3>Backtest 2022–2026</h3>
        <p>Matrice interattiva su tutte le 105 finestre di investimento (5&nbsp;&euro; per asset), confronto tra scenario prudenziale (delisting a 0&nbsp;&euro;), sole sopravvissute e Bitcoin, fasce Top 50–500, classifiche storiche per data e impatto di sblocchi e balene.</p>
      </div>
      <div class="app-foot"><span>Apri Backtest 2022–2026</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_storico_3date_500.html">
      <div>
        <span class="tag tag-green">Confronto 2026 &middot; 3 date</span>
        <h3>Evoluzione 2026 (3 date)</h3>
        <p>Fotografia comparata al 1&deg; luglio (23:59&nbsp;UTC), 1&deg; ottobre (23:59&nbsp;UTC) e 21 novembre 2026 (05:30&nbsp;CET): cambi di classifica, diluizione dell'offerta circolante, sblocchi, serie storica dei detentori (334/500) e concentrazione on-chain (193/500).</p>
      </div>
      <div class="app-foot"><span>Apri Evoluzione 2026</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_tokenomics_holders_500.html">
      <div>
        <span class="tag tag-purple">Registro on-chain &middot; 95,2%</span>
        <h3>Tokenomics e Balene</h3>
        <p>Verifica individuale su 500 asset: offerta sbloccata e residua, numero di detentori e scomposizione dei primi 10 wallet tra burn, exchange centralizzati (CEX), smart contract/staking e balene private (EOA), con grado della fonte dati separato dagli avvisi.</p>
      </div>
      <div class="app-foot"><span>Apri Tokenomics e Balene</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./curva_rendimento_N1_to_N500.html">
      <div>
        <span class="tag tag-amber">Diversificazione Lug–Ott 2026</span>
        <h3>Curva Top 1–500 (Q3 2026)</h3>
        <p>Come varia il rendimento in EUR tra il 1&deg; luglio e il 1&deg; ottobre 2026 aggiungendo una criptovaluta alla volta (da solo Bitcoin fino alle Top 500, 5&nbsp;&euro; ciascuna), isolando l'effetto dell'outlier Bitway (BTW, #143, +2.021,9% EUR).</p>
      </div>
      <div class="app-foot"><span>Apri Curva Top 1–500</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_pure500_crypto_2026.html">
      <div>
        <span class="tag tag-green">Prezzi USD &middot; Post-Filtro</span>
        <h3>Prezzi e Filtro CMC: Top 500 Pure</h3>
        <p>Tabella completa delle 500 criptovalute native liquide del 1&deg; luglio 2026 (ottenute scartando 274 asset tra #1 e #774 CoinMarketCap) con prezzi USD, capitalizzazioni e variazioni al 1&deg; ottobre e al 21 novembre 2026.</p>
      </div>
      <div class="app-foot"><span>Apri Top 500 Pure</span><span>&rarr;</span></div>
    </a>

    <a class="app-card" href="./dashboard_top500_crypto_2026.html">
      <div>
        <span class="tag tag-blue">Prezzi USD &middot; Pre-Filtro</span>
        <h3>Prezzi e Filtro CMC: Top 500 Originali</h3>
        <p>Classifica originale delle prime 500 capitalizzazioni CoinMarketCap al 1&deg; luglio 2026 prima delle esclusioni, con etichette sui 182 asset scartati (stablecoin, wrapped/LST, RWA, illiquide) per misurare l'impatto del filtro Pure Crypto.</p>
      </div>
      <div class="app-foot"><span>Apri Top 500 Originali</span><span>&rarr;</span></div>
    </a>
  </section>

  <h2 class="sec-title" id="evidenze">Evidenze empiriche principali <span class="nowrap">(ciclo 2022–2026)</span></h2>
  <p class="sec-sub">Sintesi su 5&nbsp;&euro; per criptovaluta (2.500&nbsp;&euro; per portafoglio Top 500), con delisting valutati a 0&nbsp;&euro; (-100%) e migrazioni ufficiali convertite al rapporto reale.</p>
  <section class="findings">
    <div class="f-box">
      <h4>Miglior finestra (Top 500): <span class="pos">+173,00% EUR</span></h4>
      <p>Entrando al minimo del <strong>30 dicembre 2022</strong> e uscendo il <strong>9 aprile 2024</strong>, 2.500&nbsp;&euro; diventano <strong>6.825,12&nbsp;&euro;</strong> (Bitcoin buy &amp; hold: <strong>+308,72% EUR</strong>). Sull'intero ciclo di 4 anni fino al 21 novembre 2026, la Top 500 chiude a <strong>1.067,15&nbsp;&euro; (-57,31% EUR)</strong> con 44 delisting, mentre la Top 50 registra <strong>+37,53% EUR</strong> e Bitcoin <strong>+226,09% EUR</strong>.</p>
    </div>
    <div class="f-box">
      <h4>Dominio strutturale delle large-cap (Top 50–100)</h4>
      <p>Su tutti gli ingressi tra dicembre 2022 e settembre 2025 tenuti fino al 21 novembre 2026, le fasce <strong>Top 50, Top 100 e Top 150</strong> battono la Top 500 di <strong>+17 fino a +95 punti %</strong> in EUR. Dal picco di ottobre 2025 a luglio 2026 le fasce <strong>Top 250–450</strong> prevalgono solo grazie al singolo outlier <strong>Dohrnii (DHN, da +8.207% a +13.148% EUR)</strong>; escluso DHN vincono ancora le Top 50–100.</p>
    </div>
    <div class="f-box">
      <h4>Sblocchi di offerta: rendimenti sempre pi&ugrave; bassi su 4 anni</h4>
      <p>Misurando la quota di token ancora da emettere o sbloccare alla sola data di ingresso (senza dati futuri): tra dicembre 2022 e ottobre 2025 la mediana dei rendimenti EUR scende da <strong>-25,6%</strong> (0–10% residui) a <strong>-31,5%</strong> (10–30%), <strong>-46,6%</strong> (30–60%) fino a <strong>-66,9%</strong> (&gt;60% residui). Lo stesso schema ricompare nel ribasso ottobre 2025 – novembre 2026: mediana EUR di <strong>-76,9%</strong> (0–10%) contro <strong>-86,1%</strong> (&gt;60%).</p>
    </div>
    <div class="f-box">
      <h4>Balene private (wallet EOA): perdite amplificate nei ribassi</h4>
      <p>Dalla ricostruzione storica diretta su reti compatibili con Ethereum (EVM), durante la fase ribassista tra ottobre 2025 e novembre 2026 la perdita media in <strong>EUR</strong> peggiora al crescere della quota detenuta da grandi wallet privati (EOA, esclusi exchange, smart contract e burn): <strong>-41,6%</strong> (&lt;10% in wallet privati), <strong>-75,0%</strong> (10–35%) e <strong>-77,2%</strong> (&gt;35%).</p>
    </div>
  </section>

  <div class="tbl-head-bar" style="margin-top:34px">
    <div>
      <h2 class="sec-title" id="timeline" style="margin:0 0 4px">Censimento macro delle 15 date <span class="nowrap">(30 dic 2022 – 21 nov 2026)</span></h2>
      <p class="sec-sub" style="margin:0">Cambio EUR/USD storico esatto, filtro Pure Crypto identico su ogni data, correzione micro-prezzi (&lt;0,0001&nbsp;USD) e copertura storica di sblocchi e detentori.</p>
    </div>
    <span class="scroll-hint" data-scroll-hint="timelineWrap">&larr; Scorri tabella &rarr;</span>
  </div>
  <div class="card" style="padding:0;overflow:hidden">
    <div class="tbl-wrap no-maxh" id="timelineWrap" style="border:none"><table id="timelineTbl"></table></div>
  </div>
  <div class="tbl-note" style="margin:-8px 0 20px">
    <strong>Legenda colonne:</strong> &laquo;Curve sblocchi CMC&raquo; = asset della data con calendario ufficiale CoinMarketCap (per i restanti si usa l'offerta storica circolante/massima). &laquo;N. detentori (storico)&raquo; cresce da dic 2025 grazie agli archivi giornalieri CoinCarp avviati a nov 2025. &laquo;Paniere Lug 26 gi&agrave; attivo&raquo; = quante delle 500 criptovalute di luglio 2026 esistevano gi&agrave; a quella data (dato diverso dai 44 delisting del portafoglio dic 2022). Orari rilevazione: dic 2022–mag 2026 alle 01:00/02:00 ora italiana; 1&deg; lug e 1&deg; ott 2026 alle 23:59 UTC; 21 nov 2026 alle 05:30 CET.
  </div>

  <h2 class="sec-title" id="downloads">Download dataset (CSV / JSON) e dossier metodologici</h2>
  <p class="sec-sub">Tutti i dataset strutturati e i dossier completi in Markdown sono liberamente scaricabili o consultabili su GitHub.</p>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">Dataset principali e backtest (15 date + 3 date + tokenomics)</h3>
    <div class="dl-grid">
      <a class="dl-chip" href="./multidate_15_2022_2026/panel_vistaA_15coorti_7500_righe.csv" download><b>Classifiche storiche (15 date)</b><span>15 date &times; 500 = 7.500 osservazioni (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/panel_vistaB_jul1_500_su_15date_7500_righe.csv" download><b>Paniere luglio 2026 (formato lungo)</b><span>500 asset &times; 15 date = 7.500 osservazioni (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/storico_15date_vistaB_500_crypto.csv" download><b>Paniere luglio 2026 (tabella)</b><span>500 asset &times; 128 colonne (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_matrice_14x15_5eur.csv" download><b>Matrice backtest 105 finestre</b><span>Simulazioni 5&nbsp;&euro; + scarto BTC (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_tranche_50_to_500_tutte_date.csv" download><b>Fasce Top 50–500 (tutte le date)</b><span>960 righe cumulative e scaglioni da 50 (CSV)</span></a>
      <a class="dl-chip" href="./multidate_15_2022_2026/backtest_15date_completo.json" download><b>JSON master backtest 15 date</b><span>Matrice, fasce, fattori e migrazioni</span></a>
      <a class="dl-chip" href="./storico_3date_completo_500_crypto.csv" download><b>Evoluzione 2026 (3 date: lug–nov)</b><span>500 asset point-in-time completo (CSV)</span></a>
      <a class="dl-chip" href="./audit_forense_500_crypto.csv" download><b>Tokenomics e composizione wallet</b><span>500 asset + scomposizione Top 10 (CSV)</span></a>
      <a class="dl-chip" href="./curva_cumulativa_N1_a_N500.csv" download><b>Curva Top 1–500 (lug–ott 2026)</b><span>Ogni singola aggiunta da 5&nbsp;&euro; (CSV)</span></a>
      <a class="dl-chip" href="./classifica_500_per_rendimento_desc.csv" download><b>Classifica 500 per rendimento</b><span>Ordinata dal miglior al peggior asset</span></a>
    </div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">12 file CSV individuali delle classifiche storiche Pure Top 500 (500 asset ciascuno)</h3>
    <div class="dl-grid">{cohorts_grid}</div>
  </div>

  <div class="card">
    <h3 style="margin:0 0 12px;font-size:15px">Dossier completi in Markdown (su GitHub)</h3>
    <div class="dl-grid">
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/multidate_15_2022_2026/report_15date_2022_2026_completo.md" target="_blank" rel="noopener"><b>Dossier 15 date (2022–2026)</b><span>Report completo + storico 500/500 &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_storico_3date_500_crypto.md" target="_blank" rel="noopener"><b>Dossier Evoluzione 2026 (3 date)</b><span>1&deg; lug, 1&deg; ott e 21 nov 2026 &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_audit_forense_500_crypto.md" target="_blank" rel="noopener"><b>Dossier Tokenomics e Balene</b><span>Sblocchi, detentori 95,2% e wallet &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_tokenomics_unlocks_holders_500.md" target="_blank" rel="noopener"><b>Report Sblocchi e Concentrazione</b><span>Dettaglio 500/500 asset Pure &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/report_curva_N1_to_N500.md" target="_blank" rel="noopener"><b>Report Curva Top 1–500 (Q3 2026)</b><span>Analisi progressiva 5&nbsp;&euro; per asset &nearr;</span></a>
      <a class="dl-chip" href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026/blob/main/classifica_500_per_rendimento.md" target="_blank" rel="noopener"><b>Classifica 500 per rendimento</b><span>Graduatoria integrale lug–nov 2026 &nearr;</span></a>
    </div>
  </div>

  <footer>
    <div>Pure Crypto Top 500 — Ricerca empirica sull'intero ciclo (2022–2026) &middot; Dati aperti e pipeline Python riproducibile</div>
    <div><a href="https://github.com/raffaele-ando/crypto-top500-multicycle-2022-2026" target="_blank" rel="noopener">Codice sorgente e dataset su GitHub &nearr;</a></div>
  </footer>
</main>

<script>
const CENSUS = {census_json};
let html = "<thead><tr><th class='l sticky-col'>Data</th><th>EUR/USD</th><th>BTC (USD)</th><th>ETH (USD)</th><th>Cap. Pure 500 (mld USD)</th><th class='l'>Soglia #500 (mln USD)</th><th>Curve sblocchi CMC</th><th>N. detentori (storico)</th><th>Top 10 wallet (storico)</th><th>Paniere Lug 26 gi&agrave; attivo</th></tr></thead><tbody>";
for (const c of CENSUS) {{
  html += `<tr><td class='l sticky-col'><b>${{FMT.dateIt(c.date)}}</b></td><td>${{FMT.fx(c.fx_eur_usd)}}</td><td>${{FMT.dec1(c.btc_usd)}}</td><td>${{FMT.dec1(c.eth_usd)}}</td><td>${{FMT.dec2(c.cohort_mcap_usd_b)}}</td><td class='l'><b>${{c.cutoff_rank500_sym}}</b> <span class='mut'>(${{FMT.dec1(c.cutoff_rank500_mcap_m)}} mln)</span></td><td>${{c.n_unlock_official_curve}}/500</td><td>${{c.n_hist_holders_cnt}}/500</td><td>${{c.n_hist_top10_conc}}/500</td><td>${{c.n_vistaB_already_listed}}/500</td></tr>`;
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
# 2. BACKTEST 2022-2026 (multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html)
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
<title>Backtest 2022–2026 — Pure Crypto Top 500 (15 Date)</title>
{ANTI_FOUC}
<link rel="stylesheet" href="../assets/apple-craft.css">
<style>
.wrap {{ max-width: 1500px; }}
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
  padding: 6px 4px;
  background: var(--surface2);
  border-bottom: 1px solid var(--border-strong);
  line-height: 1.18;
}}
.hm-th-d {{ display: block; font-size: 10px; font-weight: 500; color: var(--muted); margin-top: 1px; }}
.hm-wrap thead th.l {{ text-align: left; padding-left: 8px; }}
.hm-wrap tbody td {{ border-bottom: none; padding: 6px 4px; }}
.hm-wrap td.hm-entry {{
  text-align: left;
  padding: 5px 8px;
  white-space: nowrap;
  background: var(--surface);
}}
.hm-entry .hm-d {{ color: var(--muted); font-size: 10.5px; margin-left: 5px; font-weight: 500; }}
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
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px 12px;
  background: var(--surface2);
  border: 1px solid var(--border);
  padding: 13px 14px;
  border-radius: var(--r-md);
  margin-top: 12px;
  font-size: 12.5px;
}}
.insp-lbl {{ font-size: 10.5px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.04em; font-weight: 700; margin-bottom: 3px; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 5px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 7px 5px; height: 46px; }}
.stato-col {{ padding-left: 16px !important; text-align: center !important; }}
.asset-col-va {{ width: 152px; min-width: 136px; max-width: 156px; overflow: hidden; }}
.asset-col-vb {{ width: 148px; min-width: 138px; max-width: 150px; overflow: hidden; }}
@media (min-width: 1360px) {{
  #vbTable thead th, #vbTable tbody td {{ padding: 6px 4.5px; font-size: 11.5px; }}
}}
#trSummary {{ white-space: normal; max-width: 100%; border-radius: 10px; line-height: 1.35; padding: 5px 10px; }}
@media (max-width: 1100px) {{
  .hm-wrap {{ overflow: auto; max-height: 62vh; }}
  .hm-wrap thead th {{ top: 0; z-index: 10; }}
  .hm-wrap thead th.sticky-col {{ z-index: 12; }}
  .hm-cell {{ padding: 9px 6px; font-size: 11.5px; }}
  .inspector {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 640px) {{
  .hm-entry .hm-d {{ display: block; margin-left: 0; font-size: 10px; }}
  .hm-wrap td.hm-entry {{ max-width: 84px; padding: 6px 6px; }}
  .inspector {{ grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px 10px; padding: 11px 12px; }}
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
    <h1>Backtest sull'Intero Ciclo — Pure Crypto Top 500 <span class="nowrap">(2022–2026)</span></h1>
    <div class="sub">Confronto su 15 date (dic 2022 – nov 2026) tra le Top 500 reali di ogni data (senza bias di sopravvivenza) e il paniere fisso del 1&deg; luglio 2026 (base del focus Q3), integrato con sblocchi di offerta e dati on-chain.</div>
  </div>

  <!-- 4 100% Italian task-oriented tabs immediately below header (ZERO orphan letter wrap at 320px!) -->
  <div class="tabs" role="tablist">
    <button class="btn active" role="tab" onclick="showTab('tab-bt', this)">Matrice e Fasce</button>
    <button class="btn" role="tab" onclick="showTab('tab-va', this)">Classifiche Storiche (Senza Bias)</button>
    <button class="btn" role="tab" onclick="showTab('tab-vb', this)">Paniere Fisso (Lug 2026)</button>
    <button class="btn" role="tab" onclick="showTab('tab-fac', this)">Correlazione Sblocchi e Balene</button>
  </div>

  <!-- TAB 1: BACKTEST & FASCE -->
  <section id="tab-bt">
    <div class="kpis kpis-6" id="kpiStrip"></div>

    <div class="card">
      <h2>Matrice dei rendimenti — 105 finestre ingresso/uscita (15 date)</h2>
      <p class="tbl-note" style="margin:-4px 0 10px">Simulazione di <strong>5&nbsp;&euro; per criptovaluta</strong> (2.500&nbsp;&euro; per portafoglio Top 500). Seleziona una cella per il dettaglio e il confronto con Bitcoin.</p>
      <div class="controls">
        <label>Metrica:
          <select id="hmMode" onchange="renderHeatmap()">
            <option value="ret_eur_cons_pct">Rendimento EUR % (delisting = 0 &euro;)</option>
            <option value="ret_eur_active_pct">Rendimento EUR % (solo sopravvissute)</option>
            <option value="alpha_vs_btc_pp">Scarto EUR vs Bitcoin (punti %)</option>
            <option value="ret_usd_cons_pct">Rendimento USD % (delisting = 0 $)</option>
          </select>
        </label>
      </div>
      <div class="tbl-sub-bar">
        <span class="tbl-note">Righe = data di ingresso &middot; Colonne = data di uscita</span>
        <span class="scroll-hint" data-scroll-hint="hmWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="hm-wrap" id="hmWrap"><table id="hmTable"></table></div>
      <div id="hmInspector" class="inspector"></div>
    </div>

    <div class="card">
      <h2>Confronto per fascia di classifica (Top 50 – Top 500)</h2>
      <p class="tbl-note" style="margin:-4px 0 10px">Selettore indipendente dalla matrice sopra: confronta i portafogli cumulativi (Top 50, Top 100&hellip; Top 500) con i singoli scaglioni separati da 50 asset (es. #51–100). <strong>&#9733;</strong> indica la fascia migliore.</p>
      <div class="controls">
        <label>Data di ingresso: <select id="trEntry" onchange="syncHorizons(); renderTranches()"></select></label>
        <label>Data di uscita: <select id="trHoriz" onchange="renderTranches()"></select></label>
        <span id="trSummary" class="pill p-blue"></span>
      </div>
      <div class="bars-grid">
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--ink-secondary)">Portafogli cumulativi (dalla #1 alla #N)</h3>
          <div id="barsCum"></div>
        </div>
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--ink-secondary)">Singoli scaglioni da 50 asset (#1–50 &rarr; #451–500)</h3>
          <div id="barsMarg"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 2: CLASSIFICHE PER DATA (EX VISTA A) -->
  <section id="tab-va" class="hidden">
    <div class="card">
      <h2>Classifica Top 500 Pure alla data selezionata (senza bias di sopravvivenza)</h2>
      <div class="controls controls-grid">
        <label>Data: <select id="vaDate" onchange="renderVistaA()"></select></label>
        <label>Ordina per: <select id="vaSort" onchange="renderVistaA()">
          <option value="0-asc">Posizione Pure (1 &rarr; 500)</option>
          <option value="14-desc">Rendimento EUR al 21 nov 2026 &darr;</option>
          <option value="14-asc">Rendimento EUR al 21 nov 2026 &uarr;</option>
          <option value="11-desc">Rendimento EUR data successiva &darr;</option>
          <option value="7-desc">Offerta da emettere (%) &darr;</option>
          <option value="9-desc">Top 10 wallet storico (%) &darr;</option>
          <option value="8-desc">Numero detentori storici &darr;</option>
        </select></label>
        <div class="search-box ctrl-full">
          <span class="s-ico">{SEARCH_SVG}</span>
          <input type="search" id="vaSearch" placeholder="Cerca nome o ticker (es. BTC, ETH)" oninput="renderVistaA()">
          <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
        </div>
        <span id="vaMeta" class="mut ctrl-full" style="font-size:12px"></span>
      </div>
      <div class="tbl-sub-bar">
        <span class="tbl-note">Prezzi, capitalizzazione e volumi in <strong>USD</strong> (mln = milioni, mld = miliardi); rendimenti futuri in <strong>EUR</strong> al cambio storico. &laquo;CMC #&raquo; = posizione CoinMarketCap prima dei filtri Pure. &laquo;Da emettere %&raquo; = offerta residua non ancora circolante alla data. &laquo;Balene EOA %&raquo; = quota nei primi 10 wallet privati (esclusi exchange, smart contract e burn). N/D = metrica non disponibile per questa rete o data.</span>
        <span class="scroll-hint" data-scroll-hint="vaWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="tbl-wrap tbl-compact" id="vaWrap"><table id="vaTable"></table></div>
    </div>
  </section>

  <!-- TAB 3: STORICO PER TOKEN (EX VISTA B) -->
  <section id="tab-vb" class="hidden">
    <div class="card">
      <h2>Paniere fisso 1&deg; luglio 2026 — prezzi USD e rendimenti EUR (10 tappe su 15)</h2>
      <div class="controls controls-grid">
        <div class="search-box">
          <span class="s-ico">{SEARCH_SVG}</span>
          <input type="search" id="vbSearch" placeholder="Cerca nome o ticker (es. BTC, SOL)" oninput="renderVistaB()">
          <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
        </div>
        <label>Ordina per: <select id="vbSort" onchange="renderVistaB()">
          <option value="rk-asc">Posizione Pure 1&deg; lug 2026 (1 &rarr; 500)</option>
          <option value="rf-desc">Rendimento EUR 1&ordf; data &rarr; nov 2026 &darr;</option>
          <option value="rn-desc">Rendimento EUR lug &rarr; nov 2026 &darr;</option>
          <option value="nl-desc">Anzianit&agrave; (date quotate su 15) &darr;</option>
          <option value="t10-desc">Top 10 lordo nov 2026 (%) &darr;</option>
        </select></label>
        <span id="vbCount" class="mut ctrl-full" style="font-size:12px"></span>
      </div>
      <div class="tbl-sub-bar">
        <span class="tbl-note">Prezzi nelle 10 colonne centrali in <strong>USD</strong>; variazioni a destra in <strong>EUR</strong> al cambio storico. &laquo;1&ordf; Data&rarr;Nov (EUR)&raquo; = rendimento dalla prima rilevazione storica del singolo asset fino al 21 nov 2026 (anche se precedente alle 10 tappe mostrate). &laquo;Top 10 Lordo (%)&raquo; (nov 2026) = quota nei primi 10 indirizzi inclusi exchange, staking e burn. N/Q = non ancora quotato.</span>
        <span class="scroll-hint" data-scroll-hint="vbWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="tbl-wrap tbl-compact" id="vbWrap"><table id="vbTable"></table></div>
    </div>
  </section>

  <!-- TAB 4: CORRELAZIONE SBLOCCHI E BALENE (Fattori PRIMA del Censimento!) -->
  <section id="tab-fac" class="hidden">
    <div class="card">
      <h2>Impatto di sblocchi e concentrazione on-chain sui rendimenti EUR (senza dati futuri)</h2>
      <p class="tbl-note" style="margin:-4px 0 10px">I gruppi sono classificati esclusivamente sui valori noti alla <strong>data di ingresso</strong>, verificando i rendimenti EUR realizzati fino alla data di uscita. Per gli sblocchi il campione copre 500/500 asset (196–261 da calendari ufficiali CoinMarketCap + resto da offerta storica).</p>
      <div class="controls">
        <label>Finestra analizzata: <select id="facWin" onchange="renderFactors()"></select></label>
      </div>
      <div class="tbl-sub-bar">
        <span class="tbl-note">Rendimenti espressi in EUR al cambio storico esatto.</span>
        <span class="scroll-hint" data-scroll-hint="facWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="tbl-wrap no-maxh" id="facWrap"><table id="facTable"></table></div>
    </div>

    <div class="card">
      <div class="tbl-head-bar">
        <h2 style="margin:0">Censimento macro e copertura dati sulle 15 date (2022–2026)</h2>
        <span class="scroll-hint" data-scroll-hint="censusWrap">&larr; Scorri tabella &rarr;</span>
      </div>
      <div class="tbl-wrap no-maxh" id="censusWrap"><table id="censusTable"></table></div>
      <div class="tbl-note" style="margin-top:8px">&laquo;Curve sblocchi CMC&raquo; = asset della data con calendario ufficiale CoinMarketCap; &laquo;Paniere Lug 26 gi&agrave; attivo&raquo; = quante delle 500 cripto di luglio 2026 esistevano gi&agrave; alla data.</div>
    </div>
  </section>
</div>

<script>
const D = {d_json};
const CODES = D.census.map(c => c.code);
const CENSUS_BY_CODE = Object.fromEntries(D.census.map(c => [c.code, c]));
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
  if (st === "ACTIVE") return '<span class="pill p-green" title="Attiva al 21 novembre 2026">Attiva</span>';
  if (st.startsWith("MIGRATED")) {{
    const tgt = st.replace("MIGRATED->", "").replace("MIGRATED:", "");
    return `<span class="pill p-purple" title="Migrata ufficialmente in ${{tgt}}">Migrata &rarr; ${{tgt}}</span>`;
  }}
  if (st.includes("DELIST")) return `<span class="pill p-red" title="Delistata / valutata a 0 €">${{st.includes("ZERO") ? "Delistata" : "Delistata"}}</span>`;
  return `<span class="pill p-muted" title="${{st}}">${{st.slice(0, 12)}}</span>`;
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
  const bEn = FMT.dateShort(bestM.entry_date), bEx = FMT.dateShort(bestM.exit_date);
  const wEn = FMT.dateShort(worstM.entry_date), wEx = FMT.dateShort(worstM.exit_date);
  // Insight-first order: financial outcomes in Row 1 (immediately visible above the fold on Mobile Landscape!)
  const kpis = [
    ["Intero ciclo (Top 500 · 4 anni)", FMT.pct(d01_15.ret_eur_cons_pct, true, 1) + " EUR", d01_15.ret_eur_cons_pct >= 0 ? "pos" : "neg", `Dic 22 &rarr; Nov 26 (${{FMT.eurInt(d01_15.final_eur_cons)}} su 2.500&nbsp;&euro; &middot; <span class="nowrap">BTC ${{FMT.pct(d01_15.btc_bench_ret_eur_pct, true, 1)}}</span>)`],
    ["Miglior finestra (Top 500)", FMT.pct(bestM.ret_eur_cons_pct, true, 1) + " EUR", "pos", `${{bEn}} &rarr; ${{bEx}} (${{FMT.eurInt(bestM.final_eur_cons)}} su 2.500&nbsp;&euro;)`],
    ["Peggior finestra (Top 500)", FMT.pct(worstM.ret_eur_cons_pct, true, 1) + " EUR", "neg", `${{wEn}} &rarr; ${{wEx}} (${{FMT.eurInt(worstM.final_eur_cons)}} su 2.500&nbsp;&euro;)`],
    ["Orizzonte analisi", "15 date (4 anni)", "", "Dic 2022 &rarr; Nov 2026 &middot; 105 finestre"],
    ["Osservazioni totali", "15.000 osservazioni", "", "7.500 classifiche storiche + 7.500 paniere Lug 26"],
    ["Migrazioni risolte", `${{D.migrations_n}} conversioni`, "acc", "Cambi ticker/contratto al rapporto ufficiale (es. MATIC&rarr;POL)"],
  ];
  document.getElementById("kpiStrip").innerHTML = kpis.map(k =>
    `<div class="kpi"><div class="lbl">${{k[0]}}</div><div class="val ${{k[2]}}">${{k[1]}}</div><div class="note">${{k[3]}}</div></div>`
  ).join("");
}}

function renderHeatmap() {{
  const mode = document.getElementById("hmMode").value;
  const colHeaders = CODES.slice(1).map(c => {{
    const ds = FMT.dateShort(CENSUS_BY_CODE[c].date);
    const [mon, yr] = ds.split(" ");
    return `<th class='c' title='${{FMT.dateIt(CENSUS_BY_CODE[c].date)}}'>${{mon}}<span class='hm-th-d'>20${{yr}}</span></th>`;
  }}).join("");
  let html = `<thead><tr><th class='l sticky-col'>Ingresso &darr; / Uscita &rarr;</th>${{colHeaders}}</tr></thead><tbody>`;
  for (let i = 0; i < 14; i++) {{
    const ec = CODES[i], ed = D.census[i].date;
    html += `<tr><td class='hm-entry sticky-col'><b>${{FMT.dateIt(ed)}}</b></td>`;
    for (let j = 1; j < 15; j++) {{
      const xc = CODES[j];
      const r = MAT_MAP[ec + "_" + xc];
      if (!r) {{ html += `<td class='hm-empty'>&middot;</td>`; continue; }}
      const v = r[mode];
      const key = ec + "_" + xc;
      const sel = key === selPair ? " hm-sel" : "";
      html += `<td class="hm-cell${{sel}}" style="${{heatStyle(v)}}" onclick="selectPair('${{key}}')" title="${{FMT.dateIt(ed)}} &rarr; ${{FMT.dateIt(r.exit_date)}}: ${{FMT.pct(v, true, 2)}}">${{FMT.pct(v, true, 1)}}</td>`;
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
  const survN = (r.n_active || 0) + (r.n_migrated || 0);
  const dur = FMT.durationIt(r.entry_date, r.exit_date);
  const bestClean = String(r.best_coin || "").replace(/\\(#(\\d+)\\)/, "(pos. #$1 all'ingresso)");
  document.getElementById("hmInspector").innerHTML = [
    ["Finestra selezionata", `<b>${{FMT.dateIt(r.entry_date)}} &rarr; ${{FMT.dateIt(r.exit_date)}}</b><br><span class='mut'>Durata: ${{dur}}</span>`],
    ["Prudenziale (delisting = 0 €)", `<b>${{FMT.eur(r.final_eur_cons)}}</b><br>${{fmtPct(r.ret_eur_cons_pct)}} EUR su 2.500&nbsp;&euro;`],
    ["Solo sopravvissute (escl. delisting)", `<b>${{FMT.eur(r.final_eur_active_norm)}}</b><br>${{fmtPct(r.ret_eur_active_pct)}} EUR (${{survN}} sopravvissute su 2.500&nbsp;&euro;)`],
    ["Se investiti in Bitcoin", `<b>${{FMT.eur(r.btc_bench_final_eur)}}</b><br>${{fmtPct(r.btc_bench_ret_eur_pct)}} EUR`],
    ["Scarto vs Bitcoin", `<b class="${{FMT.pctClass(r.alpha_vs_btc_pp)}}">${{r.alpha_vs_btc_pp >= 0 ? "+" : ""}}${{FMT.dec2(r.alpha_vs_btc_pp)}} punti %</b><br><span class='mut'>Differenziale Top 500 vs BTC</span>`],
    ["Distribuzione dei 500 asset", `Mediana: ${{fmtPct(r.median_ret_eur_pct)}} EUR<br>In profitto: <b>${{FMT.dec1(r.win_rate_pct)}}%</b>`],
    ["Stato dei 500 asset", `Attive: <b>${{r.n_active}}</b> &middot; Migrate: <b>${{r.n_migrated}}</b> (=${{survN}})<br>Delistate (0&nbsp;&euro;): <b class='neg'>${{r.n_delisted_0eur}}</b>`],
    ["Miglior singolo asset", `<b>${{bestClean}}</b><br>${{fmtPct(r.best_ret_pct)}} EUR nella finestra`],
  ].map(x => `<div><div class='insp-lbl'>${{x[0]}}</div><div>${{x[1]}}</div></div>`).join("");
}}

function syncHorizons() {{
  const ec = document.getElementById("trEntry").value;
  const avail = [...new Set(D.tranches.filter(x => x.entry_code === ec).map(x => x.horizon))];
  const idx = CODES.indexOf(ec);
  const nextC = idx >= 0 && idx + 1 < CODES.length ? CENSUS_BY_CODE[CODES[idx + 1]] : null;
  const labels = {{
    NEXT_LEG: nextC ? `${{FMT.dateIt(nextC.date)}} (data successiva)` : "Data successiva",
    TO_D08_PEAK: "7 ott 2025 (picco ciclo)",
    TO_D14_OCT1: "1° ott 2026",
    TO_D15_NOV21: "21 nov 2026 (fine ciclo)"
  }};
  const sel = document.getElementById("trHoriz");
  const prev = sel.value;
  sel.innerHTML = avail.map(h => `<option value="${{h}}">${{labels[h] || h}}</option>`).join("");
  if (avail.includes(prev)) sel.value = prev;
  else if (avail.includes("TO_D15_NOV21")) sel.value = "TO_D15_NOV21";
}}

function renderBars(elId, rows, labelKey, colTitle) {{
  const maxAbs = Math.max(15, ...rows.map(r => Math.abs(r.ret_eur_cons_pct)));
  const bestV = Math.max(...rows.map(r => r.ret_eur_cons_pct));
  const scaleHtml = `<div class="div-scale"><span>${{colTitle}}</span><div class="div-scale-mid"><span>-${{FMT.dec1(maxAbs)}}%</span><span>0%</span><span>+${{FMT.dec1(maxAbs)}}%</span></div><span style="text-align:right">EUR %</span></div>`;
  const rowsHtml = rows.map(r => {{
    const v = r.ret_eur_cons_pct;
    const w = Math.min(100, Math.abs(v) / maxAbs * 100).toFixed(1);
    const star = v === bestV ? ' <span class="warn" title="Fascia migliore">&#9733;</span>' : "";
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
  document.getElementById("trSummary").innerHTML = `Miglior fascia: Top ${{best.tranche_k}} (${{FMT.pct(best.ret_eur_cons_pct, true, 2)}} EUR) &middot; Bitcoin: ${{FMT.pct(best.btc_bench_ret_eur_pct, true, 2)}} EUR`;
  renderBars("barsCum", cums, "lbl", "Portafoglio");
  renderBars("barsMarg", margs, "lbl", "Scaglione");
}}

function renderVistaA() {{
  const dc = document.getElementById("vaDate").value;
  const q = document.getElementById("vaSearch").value.trim().toLowerCase();
  const [colIdx, dir] = document.getElementById("vaSort").value.split("-");
  const ci = Number(colIdx);
  const cMeta = CENSUS_BY_CODE[dc];
  const dIdx = CODES.indexOf(dc);
  const nextC = dIdx >= 0 && dIdx + 1 < CODES.length ? CENSUS_BY_CODE[CODES[dIdx + 1]] : null;
  const nextLbl = nextC ? `&rarr; ${{FMT.dateShort(nextC.date)}} (EUR)` : "Succ. (EUR)";
  let rows = D.va[dc] || [];
  if (q) rows = rows.filter(r => r[2].toLowerCase().includes(q) || r[3].toLowerCase().includes(q));
  rows = [...rows].sort((a,b) => {{
    const va = a[ci], vb = b[ci];
    if (va === null && vb === null) return 0;
    if (va === null) return 1; if (vb === null) return -1;
    return dir === "asc" ? va - vb : vb - va;
  }});
  document.getElementById("vaMeta").textContent = `Mostrati ${{rows.length}} di 500 asset · BTC ${{FMT.dec2(cMeta.btc_usd)}} USD · Cambio EUR/USD ${{FMT.fx(cMeta.fx_eur_usd)}} · Cap. totale ${{FMT.dec2(cMeta.cohort_mcap_usd_b)}} mld USD`;
  let html = `<thead><tr><th class='l sticky-col asset-col-va'># / Asset</th><th>Prezzo (USD)</th><th>Cap. (USD)</th><th>Vol. 24h (USD)</th><th>Da emettere %</th><th>Detentori</th><th>Top 10 wallet %</th><th>Balene EOA %</th><th>${{nextLbl}}</th><th>Ott 25 (EUR)</th><th>Ott 26 (EUR)</th><th>Nov 26 (EUR)</th><th class='stato-col'>Stato Nov 26</th></tr></thead><tbody>`;
  for (const r of rows) {{
    html += `<tr><td class='l sticky-col asset-col-va'><b>#${{r[0]}} ${{r[2]}}</b><span class='small cell-clip' title='${{r[3]}} (Pos. CoinMarketCap #${{r[1]}})'>${{r[3]}} &middot; CMC #${{r[1]}}</span></td><td>${{fmtP(r[4])}}</td><td title="${{FMT.dec1(r[5])}} mln USD">${{FMT.compact(r[5]*1e6)}}</td><td title="${{FMT.dec1(r[6])}} mln USD">${{FMT.compact(r[6]*1e6)}}</td><td>${{r[7]!==null ? FMT.dec1(r[7])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[8]!==null ? FMT.int(r[8]) : "<span class='mut'>N/D</span>"}}</td><td>${{r[9]!==null ? FMT.dec1(r[9])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[10]!==null ? FMT.dec1(r[10])+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{fmtPct(r[11])}}</td><td>${{fmtPct(r[12])}}</td><td>${{fmtPct(r[13])}}</td><td>${{fmtPct(r[14])}}</td><td class='stato-col'>${{statusBadge(r[15])}}</td></tr>`;
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
  document.getElementById("vbCount").textContent = `Mostrati ${{rows.length}} di 500 asset del paniere 1° luglio 2026`;
  let html = "<thead><tr><th class='l sticky-col asset-col-vb'># / Asset</th><th class='l'>1&ordf; Data</th><th>Date quot.</th><th>Dic 22 (USD)</th><th>Apr 24 (USD)</th><th>Nov 24 (USD)</th><th>Apr 25 (USD)</th><th>Ott 25 (USD)</th><th>Gen 26 (USD)</th><th>Mag 26 (USD)</th><th>Lug 26 (USD)</th><th>Ott 26 (USD)</th><th>Nov 26 (USD)</th><th>1&ordf; Data&rarr;Nov (EUR)</th><th>Lug&rarr;Nov (EUR)</th><th>Top 10 Lordo (%)</th></tr></thead><tbody>";
  for (const r of rows) {{
    const fsIso = r.fs && r.fs.includes("(") ? r.fs.split("(")[1].replace(")", "") : "";
    const fsLbl = fsIso ? FMT.dateShort(fsIso) : (r.fs || "—");
    html += `<tr><td class='l sticky-col asset-col-vb'><b>#${{r.rk}} ${{r.sym}}</b><span class='small cell-clip' title="${{r.nm}}">${{r.nm}}</span></td><td class='l mut' title="${{r.fs}}">${{fsLbl}}</td><td>${{r.nl}}/15</td><td>${{fmtP(r.p01)}}</td><td>${{fmtP(r.p02)}}</td><td>${{fmtP(r.p04)}}</td><td>${{fmtP(r.p06)}}</td><td>${{fmtP(r.p08)}}</td><td>${{fmtP(r.p10)}}</td><td>${{fmtP(r.p12)}}</td><td>${{fmtP(r.p13)}}</td><td>${{fmtP(r.p14)}}</td><td>${{fmtP(r.p15)}}</td><td>${{fmtPct(r.rf)}}</td><td>${{fmtPct(r.rn)}}</td><td>${{r.t10!==null ? FMT.dec1(r.t10)+"%" : "<span class='mut'>N/D</span>"}}</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("vbTable").innerHTML = html;
  agyRefreshScrollHints();
}}

function renderCensus() {{
  let html = "<thead><tr><th class='l sticky-col'>Data</th><th>EUR/USD</th><th>BTC (USD)</th><th>ETH (USD)</th><th>Cap. Pure 500 (mld USD)</th><th class='l'>Soglia #500 (mln USD)</th><th>Curve sblocchi CMC</th><th>N. detentori (storico)</th><th>Top 10 wallet (storico)</th><th>Balene EOA (storico)</th><th>Paniere Lug 26 gi&agrave; attivo</th></tr></thead><tbody>";
  for (const c of D.census) {{
    html += `<tr><td class='l sticky-col'><b>${{FMT.dateIt(c.date)}}</b></td><td>${{FMT.fx(c.fx_eur_usd)}}</td><td>${{FMT.dec1(c.btc_usd)}}</td><td>${{FMT.dec1(c.eth_usd)}}</td><td>${{FMT.dec2(c.cohort_mcap_usd_b)}}</td><td class='l'><b>${{c.cutoff_rank500_sym}}</b> <span class='mut'>(${{FMT.dec1(c.cutoff_rank500_mcap_m)}} mln)</span></td><td>${{c.n_unlock_official_curve}}/500</td><td>${{c.n_hist_holders_cnt}}/500</td><td>${{c.n_hist_top10_conc}}/500</td><td>${{c.n_hist_eoa_whale}}/500</td><td>${{c.n_vistaB_already_listed}}/500</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("censusTable").innerHTML = html;
}}

function formatWinLabel(k) {{
  const map = {{
    D01_to_D08_BearToPeak: "Minimo → Picco: 30 dic 2022 → 7 ott 2025",
    D01_to_D15_Full4YrHold: "Intero ciclo (4 anni): 30 dic 2022 → 21 nov 2026",
    D02_to_D08_HalvingToPeak: "Pre-Halving → Picco: 9 apr 2024 → 7 ott 2025",
    D06_to_D08_Apr25DipToPeak: "Minimo primaverile → Picco: 8 apr 2025 → 7 ott 2025",
    D08_to_D15_PeakToBearNov26: "Picco → Ribasso: 7 ott 2025 → 21 nov 2026",
    D12_to_D15_May26ToNov26: "Semestre ribassista: 12 mag 2026 → 21 nov 2026"
  }};
  return map[k] || k.replaceAll("_to_", " → ").replaceAll("_", " ");
}}

function cleanBucketLabel(bk) {{
  const map = {{
    "0-10% (Matura)": "0–10% (Basso)",
    "10-30% (Moderato)": "10–30% (Moderato)",
    "30-60% (Alto)": "30–60% (Alto)",
    ">60% (Overhang Estremo)": ">60% (Estremo)",
    "<35% (Distribuita)": "<35% (Distribuita)",
    "35-65% (Media)": "35–65% (Media)",
    "65-85% (Alta)": "65–85% (Alta)",
    ">85% (Estrema)": ">85% (Estrema)",
    "<10% EOA Whale": "<10% (Bassa)",
    "10-35% EOA Whale": "10–35% (Media)",
    ">35% EOA Whale": ">35% (Alta)"
  }};
  return map[bk] || bk;
}}

function renderFactors() {{
  const w = document.getElementById("facWin").value;
  const fb = D.factors[w];
  const groups = [
    ["unlock_overhang", "1. Offerta ancora da emettere / sbloccare alla data di ingresso (%)"],
    ["hist_top10", "2. Concentrazione storica nei primi 10 wallet alla data di ingresso (%)"],
    ["hist_eoa_whale", "3. Quota storica in balene private (wallet EOA) alla data di ingresso (%)"]
  ];
  let html = "<thead><tr><th class='l'>Fascia del fattore (all'ingresso)</th><th>N. asset</th><th>Media EUR %</th><th>Mediana EUR %</th><th>In profitto (%)</th></tr></thead><tbody>";
  for (const [gk, gt] of groups) {{
    html += `<tr class='sec-row'><td class='l' colspan='5'>${{gt}}</td></tr>`;
    for (const [bk, bv] of Object.entries(fb[gk])) {{
      if (!bv.n) continue;
      html += `<tr><td class='l'><b>${{cleanBucketLabel(bk)}}</b></td><td>${{FMT.int(bv.n)}}</td><td>${{fmtPct(bv.mean_eur_pct)}}</td><td>${{fmtPct(bv.median_eur_pct)}}</td><td>${{FMT.dec1(bv.win_rate_pct)}}%</td></tr>`;
    }}
  }}
  html += "</tbody>";
  document.getElementById("facTable").innerHTML = html;
}}

initKPIs();
document.getElementById("trEntry").innerHTML = D.census.slice(0,14).map(c => `<option value="${{c.code}}">${{FMT.dateIt(c.date)}}</option>`).join("");
document.getElementById("vaDate").innerHTML = D.census.map(c => `<option value="${{c.code}}">${{FMT.dateIt(c.date)}}</option>`).join("");
document.getElementById("facWin").innerHTML = Object.keys(D.factors).map(k => `<option value="${{k}}">${{formatWinLabel(k)}}</option>`).join("");
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
# 3. FOCUS 2026 (3 DATE) — dashboard_storico_3date_500.html
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
<title>Focus 2026 (3 Date: Luglio – Novembre) — Top 500 Pure Crypto</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1520px; }}
.tbl-wrap {{ max-height: 68vh; }}
.asset-col {{ max-width: 144px; min-width: 108px; }}
.asset-col .cell-clip {{ max-width: 132px; }}
@media (min-width: 960px) {{
  .controls.controls-grid {{ flex-wrap: nowrap; }}
  .controls.controls-grid > select {{ flex: 0 1 245px; }}
}}
@media (min-width: 1280px) {{
  #stWrap table {{ font-size: 11.5px; }}
  #stWrap thead th, #stWrap tbody td {{ padding: 7px 6px; }}
  #stWrap thead th:last-child, #stWrap tbody td:last-child {{ padding-right: 10px; }}
}}
</style>
</head>
<body>
<script src="./assets/hub-shell.js"></script>
<script>agyInitHubNav("storico3", "./");</script>

<div class="wrap">
  <div class="page-head">
    <h1>Evoluzione 2026 su 3 Date (Luglio – Novembre) — Top 500 Pure Crypto</h1>
    <div class="sub">Parametri storici esatti al <b>1&deg; luglio (23:59&nbsp;UTC)</b>, <b>1&deg; ottobre (23:59&nbsp;UTC)</b> e <b>21 novembre 2026 (05:30&nbsp;CET)</b>. Copertura offerta/sblocchi: <b>500/500</b> (258 da calendari ufficiali CoinMarketCap + 242 da offerta storica) &middot; Serie storica detentori: <b>334/500</b> &middot; Concentrazione Top 10 storica su 3 date: <b>193/500</b>. Per gli altri asset &egrave; indicato lo stato corrente del 24 nov 2026 (escluso dai backtest).</div>
  </div>

  <div class="tabs" role="tablist">
    <button class="tab active" data-mode="compare">Confronto (Lug &rarr; Nov 2026)</button>
    <button class="tab" data-mode="jul1">1&deg; lug 2026</button>
    <button class="tab" data-mode="oct1">1&deg; ott 2026</button>
    <button class="tab" data-mode="nov21">21 nov 2026</button>
  </div>

  <div class="controls controls-grid">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome o ticker (es. BTC, ETH)">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <select id="hFilter" aria-label="Filtro copertura dati">
      <option value="">Tutti i 500 asset Pure Crypto</option>
      <option value="hist_t10">Con concentrazione storica 3 date (193)</option>
      <option value="official_ul">Con calendario ufficiale CMC (258)</option>
      <option value="diluted">Diluizione offerta &gt;5% (lug &rarr; nov)</option>
    </select>
    <select id="sortBy" aria-label="Ordinamento tabella">
      <option value="rank_clean_jul1:asc">Ordina: Pos. Pure (1&deg; lug)</option>
      <option value="rank_clean_oct1:asc">Ordina: Pos. Pure (1&deg; ott)</option>
      <option value="rank_clean_nov21:asc">Ordina: Pos. Pure (21 nov)</option>
      <option value="delta_rank_clean_jul_to_nov21:desc">Ordina: Maggior scalata Pure &darr;</option>
      <option value="supply_inflation_jul_to_nov21_pct:desc">Ordina: Maggior diluizione &darr;</option>
      <option value="to_unlock_pct_jul1:desc">Ordina: Pi&ugrave; da emettere (1&deg; lug) &darr;</option>
      <option value="eoa_whale_hist_jul1_pct:asc">Ordina: Meno balene EOA (1&deg; lug) &uarr;</option>
      <option value="ticket_5eur_nov21_eur:desc">Ordina: Valore 5 &euro; al 21 nov &darr;</option>
    </select>
    <span id="shown" class="pill p-muted" style="justify-self:start">Mostrati 500 di 500</span>
  </div>

  <div class="info-banner">
    <div><strong>Note metodologiche:</strong> &laquo;CMC #&raquo; = posizione su CoinMarketCap prima dei filtri Pure. Capitalizzazioni in <strong>USD</strong> (mln = milioni, mld = miliardi); rendimenti del ticket da 5&nbsp;&euro; in <strong>EUR</strong> al cambio storico. &laquo;Offerta circ. %&raquo; = offerta circolante sul tetto massimo/totale (100% per asset senza tetto massimo come ETH/DOGE, dove <em>Var. offerta</em> riflette inflazione o burn). Su Ethereum il Top 10 storico on-chain (8,4% &rarr; 8,2%) esclude il contratto ufficiale di deposito staking (Beacon Chain); per il Top 10 lordo scomposto consulta la sezione <strong>Tokenomics e Balene</strong>.</div>
  </div>

  <div class="tbl-sub-bar">
    <span class="tbl-note">Confronto puntuale tra 1&deg; luglio, 1&deg; ottobre e 21 novembre 2026.</span>
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
  if (tier && tier.startsWith("ARCHIVE")) return '<span class="pill p-arch">On-chain EVM</span>';
  if (tier && tier.startsWith("COINCARD")) return '<span class="pill p-cc">CoinCarp</span>';
  if (tier && (tier.includes("CNT_ONLY"))) return '<span class="pill p-blue">Detentori 3 date</span>';
  return '<span class="pill p-ref" title="Archivio storico non disponibile: mostrato stato corrente 24 nov 2026">Solo stato 24 nov</span>';
}}

function cleanSource(s) {{
  if (!s) return "";
  let t = s
    .replace(/\\(blk[^)]*\\)/gi, "")
    .replace(/Archive RPC Ethereum Multicall3/gi, "Storico Ethereum on-chain")
    .replace(/Archive RPC Base Multicall3/gi, "Storico Base on-chain")
    .replace(/Archive RPC/gi, "Storico on-chain")
    .replace(/ex-Beacon/gi, "escl. staking Beacon")
    .replace(/CoinMetrics AdrBalCnt/gi, "detentori CoinMetrics")
    .replace(/CMC DAPI Holders Count 3-date \\([^)]*\\)/gi, "Detentori CMC 3 date (Top 10 solo 24 nov)")
    .replace(/CoinMetrics Holders Count 3-date \\([^)]*\\)/gi, "Detentori CoinMetrics 3 date (Top 10 solo 24 nov)")
    .replace(/CoinCarp Daily[^\\(]*\\((\\d{{4}}-\\d{{2}}-\\d{{2}})[^)]*\\)/gi, (_, iso) => "Archivio CoinCarp (dal " + FMT.dateIt(iso) + ")")
    .replace(/CoinCarp Daily/gi, "Archivio CoinCarp")
    .replace(/Solo Ref\\. 24 Nov \\([^)]*\\)/gi, "Nessun archivio pubblico (stato 24 nov)")
    .replace(/Nessuna richlist API pubblica/gi, "Nessun archivio pubblico")
    .replace(/(\\d{{4}}-\\d{{2}}-\\d{{2}})/g, (_, iso) => FMT.dateIt(iso))
    .replace(/\\s+/g, " ")
    .trim();
  return t;
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
  document.getElementById("shown").textContent = `Mostrati ${{arr.length}} di ${{DATA.length}}`;

  if (mode === "compare") {{
    document.getElementById("th").innerHTML = `<tr>
      <th class="l sticky-col">Asset (Pos. Pure)</th>
      <th class="num">Pos. Pure<br><span class="mut" style="font-weight:500">Lug&rarr;Ott&rarr;Nov</span></th>
      <th class="num">Cap. (USD)<br><span class="mut" style="font-weight:500">Lug&rarr;Ott&rarr;Nov</span></th>
      <th class="num">Offerta circ. %<br><span class="mut" style="font-weight:500">Lug&rarr;Ott&rarr;Nov</span></th>
      <th class="num">Var. offerta<br><span class="mut" style="font-weight:500">Lug&rarr;Nov</span></th>
      <th class="num">Top 10 storico<br><span class="mut" style="font-weight:500">Lug&rarr;Nov</span></th>
      <th class="num">Balene EOA<br><span class="mut" style="font-weight:500">Lug&rarr;Nov</span></th>
      <th class="num">5 &euro; dal 1&deg; lug<br><span class="mut" style="font-weight:500">Ott / Nov (EUR)</span></th>
      <th class="l">Fonte dati</th>
    </tr>`;
    document.getElementById("tb").innerHTML = arr.map(x => {{
      const dcl = x.delta_rank_clean_jul_to_nov21;
      const dclS = dcl === null ? "" : (dcl === 0 ? '<span class="mut">invariato</span>' : `<span class="${{dcl > 0 ? "pos" : "neg"}}">${{dcl > 0 ? "+" : ""}}${{dcl}} pos</span>`);
      const inf = x.supply_inflation_jul_to_nov21_pct;
      const t10 = (x.top10_hist_jul1_pct !== null || x.top10_hist_nov21_pct !== null)
        ? `${{FMT.pct(x.top10_hist_jul1_pct, false, 1)}} &rarr; <b>${{FMT.pct(x.top10_hist_nov21_pct, false, 1)}}</b>`
        : `<span class="small">Storico N/D<br>(24 nov: <b style="color:var(--ink-secondary)">${{FMT.pct(x.top10_ref_nov24_pct, false, 1)}}</b>)</span>`;
      const eoa = (x.eoa_whale_hist_jul1_pct !== null || x.eoa_whale_hist_nov21_pct !== null)
        ? `${{FMT.pct(x.eoa_whale_hist_jul1_pct, false, 1)}} &rarr; <b>${{FMT.pct(x.eoa_whale_hist_nov21_pct, false, 1)}}</b>`
        : '<span class="mut">N/D</span>';
      const retOctEur = x.ticket_5eur_oct1_eur ? ((x.ticket_5eur_oct1_eur / 5 - 1) * 100) : null;
      const retNovEur = x.ticket_5eur_nov21_eur ? ((x.ticket_5eur_nov21_eur / 5 - 1) * 100) : null;
      const srcRaw = x.hist_holders_source || "";
      const srcClean = cleanSource(srcRaw);
      return `<tr>
        <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}} (Pos. CoinMarketCap 1 lug: #${{x.cmc_rank_jul1}})">#${{x.rank_clean_jul1}} ${{x.name}}</b><span class="small">${{x.symbol}} &middot; CMC #${{x.cmc_rank_jul1}}</span></td>
        <td class="num">#${{x.rank_clean_jul1}} &rarr; #${{x.rank_clean_oct1 || "—"}} &rarr; <b>#${{x.rank_clean_nov21 || "—"}}</b><span class="small">${{dclS}}</span></td>
        <td class="num">${{FMT.compact(x.mcap_usd_jul1)}} &rarr; ${{FMT.compact(x.mcap_usd_oct1)}}<br><span class="small">&rarr; <b style="color:var(--ink)">${{FMT.compact(x.mcap_usd_nov21)}}</b></span></td>
        <td class="num">${{FMT.pct(x.unlocked_pct_jul1, false, 1)}} &rarr; ${{FMT.pct(x.unlocked_pct_oct1, false, 1)}}<br><span class="small">&rarr; <b style="color:var(--ink)">${{FMT.pct(x.unlocked_pct_nov21, false, 1)}}</b></span></td>
        <td class="num"><span class="${{(inf || 0) > 5 ? "neg" : ""}}">${{FMT.pct(inf, true, 2)}}</span></td>
        <td class="num">${{t10}}</td>
        <td class="num">${{eoa}}</td>
        <td class="num"><b>${{x.ticket_5eur_oct1_eur ? FMT.eur(x.ticket_5eur_oct1_eur) : "N/D"}}</b> / <b>${{x.ticket_5eur_nov21_eur ? FMT.eur(x.ticket_5eur_nov21_eur) : "N/D"}}</b><span class="small">${{FMT.pct(retOctEur, true, 1)}} / ${{FMT.pct(retNovEur, true, 1)}} EUR</span></td>
        <td class="l src-cell">${{badge(x.hist_holders_tier)}}<span class="small" style="margin-top:2px" title="${{srcRaw}}">${{srcClean}}</span></td>
      </tr>`;
    }}).join("");
  }} else {{
    const d = mode;
    const dlbl = d === "jul1" ? "1° lug" : (d === "oct1" ? "1° ott" : "21 nov");
    document.getElementById("th").innerHTML = `<tr>
      <th class="l sticky-col">Asset (Pos. Pure ${{dlbl}})</th>
      <th class="num">Pos. CMC</th>
      <th class="num">Prezzo USD / EUR</th>
      <th class="num">Cap. (USD) / FDV</th>
      <th class="num">Vol. 24h (USD)</th>
      <th class="num">Offerta circ. (%)</th>
      <th class="num">Da emettere</th>
      <th class="num">Top 10 / Altri</th>
      <th class="num">EOA / Detentori</th>
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
        <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}}">${{rkc ? "#" + rkc : "N/D"}} ${{x.name}}</b><span class="small">${{x.symbol}}</span></td>
        <td class="num">${{rkm ? "#" + rkm : "N/D"}}</td>
        <td class="num">${{FMT.price(pu, true)}}<span class="small">${{FMT.price(pe)}} &euro;</span></td>
        <td class="num">${{FMT.compact(mc)}}<span class="small">${{fr ? "FDV/Cap " + FMT.dec2(fr) + "×" : "Offerta max illimitata"}}</span></td>
        <td class="num">${{FMT.compact(v24)}}<span class="small">${{prs ? FMT.int(prs) + " mercati" : ""}}</span></td>
        <td class="num"><b>${{FMT.pct(ulp, false, 2)}}</b><span class="small">${{FMT.compact(ult)}}</span></td>
        <td class="num"><b>${{tulp !== null ? FMT.pct(tulp, false, 2) : "Illimitata"}}</b><span class="small">${{tult !== null ? FMT.compact(tult) : "Emissione continua"}}</span></td>
        <td class="num">${{t10 !== null ? `<b>${{FMT.pct(t10, false, 2)}}</b> / ${{FMT.pct(d10, false, 1)}}` : '<span class="mut">Storico N/D</span>'}}</td>
        <td class="num">${{eoa !== null ? `<b>${{FMT.pct(eoa, false, 2)}}</b>` : '<span class="mut">N/D</span>'}}<span class="small">Detentori: ${{hc ? FMT.int(hc) : "N/D"}}</span></td>
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
# 4. TOKENOMICS & BALENE (dashboard_tokenomics_holders_500.html)
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
<title>Tokenomics, Sblocchi e Composizione Top 10 Wallet — Top 500 Pure (2026)</title>
{ANTI_FOUC}
<link rel="stylesheet" href="./assets/apple-craft.css">
<style>
.wrap {{ max-width: 1520px; }}
.legend-row {{
  display: flex;
  gap: 6px 14px;
  font-size: 12px;
  color: var(--ink-secondary);
  margin-top: 6px;
  padding-top: 6px;
  border-top: 1px solid var(--border);
  flex-wrap: wrap;
  align-items: center;
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
.tbl-wrap {{ max-height: 60vh; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 6px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 6px 6px; }}
.asset-col {{ max-width: 138px; min-width: 108px; }}
.asset-col .cell-clip {{ max-width: 126px; }}
.sort-ind {{ opacity: 0.9; margin-left: 3px; color: var(--accent-text); }}
#tokWrap thead th:nth-child(5), #tokWrap tbody td:nth-child(5) {{ padding-left: 20px; }}
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
    <h1>Tokenomics, Sblocchi e Composizione dei Top 10 Wallet — Top 500 Pure (2026)</h1>
    <div class="sub" id="tokSub">Verifica individuale su 500/500 crypto...</div>
  </div>

  <div class="kpis kpis-5" id="tokKpis"></div>

  <div class="controls controls-grid">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome, ticker, wallet o avviso...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <select id="grade" aria-label="Filtro qualità fonte on-chain">
      <option value="">Tutti i gradi fonte (A+, A, B, C, N/D)</option>
      <option value="A+">Grado A+ (explorer nativo verificato)</option>
      <option value="A">Grado A (API on-chain live nov 2026)</option>
      <option value="A+A">Alta affidabilit&agrave; fonte (A+ e A)</option>
      <option value="B">Grado B (snapshot recente)</option>
      <option value="C">Grado C (copertura parziale / staking)</option>
      <option value="N/D">Grado N/D (privacy o rete senza API)</option>
    </select>
    <select id="verdict" aria-label="Filtro avvisi tokenomics">
      <option value="">Tutti gli esiti (nessun avviso / con note / attenzione)</option>
      <option value="PASS_VERIFIED">Nessun avviso strutturale</option>
      <option value="PASS_WITH_CAVEATS">Con note (staking, CEX o vesting)</option>
      <option value="WARNING_CHECK_NOTE">Attenzione (rischio elevato)</option>
      <option value="STRUCTURAL_ND">N/D strutturale (privacy coin)</option>
      <option value="DATA_GAP_ND">Dato on-chain non disponibile</option>
    </select>
    <select id="sortBy" aria-label="Ordinamento tabella">
      <option value="rank_clean_jul1:asc">Ordina: Pos. Pure (1 &rarr; 500)</option>
      <option value="top10_eoa_whale_residual_pct:asc">Ordina: Meno balene EOA &uarr;</option>
      <option value="top10_eoa_whale_residual_pct:desc">Ordina: Pi&ugrave; balene EOA &darr;</option>
      <option value="top10_holders_pct:desc">Ordina: Top 10 lordo &darr;</option>
      <option value="fdv_to_mcap_ratio:desc">Ordina: Multiplo FDV / Cap &darr;</option>
      <option value="to_unlock_pct:desc">Ordina: % Da emettere &darr;</option>
      <option value="ret_q3_pct:desc">Ordina: Var. USD lug&rarr;ott &darr;</option>
    </select>
    <span id="shown" class="pill p-muted" style="justify-self:start">Mostrati 500 di 500</span>
  </div>

  <!-- Explicit Data-Quality, Tokenomics-Alerts & Non-Colliding Wallet-Composition Legend -->
  <div class="info-banner">
    <div><strong>Grado fonte dati (A+–C, NON &egrave; un rating dell'investimento):</strong> <strong>A+</strong> = explorer nativo verificato &middot; <strong>A</strong> = API on-chain live &middot; <strong>B</strong> = snapshot recente &middot; <strong>C</strong> = copertura parziale (es. staking complesso) &middot; <strong>N/D</strong> = privacy o rete senza API.</div>
    <div style="margin-top:4px"><strong>Esito tokenomics (indipendente dal grado fonte):</strong> <em>Nessun avviso</em> = nessuna anomalia &middot; <em>Con note</em> = presenza di staking, custodia CEX o vesting nei primi 10 wallet (pu&ograve; coesistere con fonte A+) &middot; <em>Attenzione</em> = rischio concentrazione/sblocchi elevato. <strong>FDV/Cap</strong> = valutazione a offerta massima (Fully Diluted Valuation) divisa per capitalizzazione circolante.</div>
    <div class="legend-row">
      <strong>Scomposizione Top 10 (somma = Top 10 Lordo):</strong>
      <span><span class="dot" style="background:#ff5a52"></span><strong>EOA</strong> = balene private</span>
      <span><span class="dot" style="background:#38bdf8"></span><strong>CEX</strong> = exchange centralizzati</span>
      <span><span class="dot" style="background:#a855f7"></span><strong>Contr.</strong> = smart contract, staking e vesting</span>
      <span><span class="dot" style="background:#94a3b8"></span><strong>Burn</strong> = indirizzi di distruzione definitiva</span>
    </div>
  </div>

  <div class="tbl-sub-bar">
    <span class="tbl-note">Variazioni dal 1&deg; luglio al 1&deg; ottobre (Q3) e al 21 novembre 2026 espresse in <strong>USD</strong> (a differenza dei backtest in EUR).</span>
    <span class="scroll-hint" data-scroll-hint="tokWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap tbl-compact" id="tokWrap">
    <table>
      <thead>
        <tr>
          <th class="l sticky-col" data-k="rank_clean_jul1"># / Asset</th>
          <th class="l" data-k="reliability_grade">Fonte e Esito</th>
          <th class="num" data-k="unlocked_pct">Offerta circ. / FDV</th>
          <th class="num" data-k="top10_holders_pct">Top 10 Lordo</th>
          <th class="l">Scomposizione Top 10</th>
          <th class="num" data-k="top10_eoa_whale_residual_pct">Balene (EOA)</th>
          <th class="l">Wallet #1 e Vesting</th>
          <th class="num" data-k="ret_q3_pct">Var. USD (Lug&rarr;Ott / Nov)</th>
          <th class="l">Note di verifica</th>
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
  PASS_VERIFIED: "Nessun avviso",
  PASS_WITH_CAVEATS: "Con note",
  WARNING_CHECK_NOTE: "Attenzione",
  STRUCTURAL_ND: "Privacy (N/D)",
  DATA_GAP_ND: "Dato assente"
}};

function cleanNote(s) {{
  if (!s) return "—";
  let t = s
    .replace(/CMC DAPI Live \\(fgp esatto ex-Others; etichette ufficiali CMC incluse\\)/gi, "API on-chain CoinMarketCap live (etichette ufficiali incluse)")
    .replace(/CMC DAPI Live \\([^)]*\\)/gi, "API on-chain CoinMarketCap live")
    .replace(/Verificata 8\\/8 \\(CoinMarketCap On-Chain\\)/gi, "8/8 controlli superati (CoinMarketCap on-chain)")
    .replace(/Verificata 8\\/8/gi, "8/8 controlli superati")
    .replace(/Bug bridge CMC risolto via/gi, "Fonte bridge CMC corretta via")
    .replace(/CMC_BRIDGED_CLEANED/gi, "Fonte bridge corretta su rete nativa")
    .replace(/ETH2 Beacon Deposit/gi, "deposito staking Ethereum (Beacon)")
    .replace(/ex-Beacon live Blockscout/gi, "escluso staking su Blockscout")
    .replace(/\\(non whale libere\\)/gi, "(non balene private)")
    .replace(/Emissione continua senza Max Cap fisso/gi, "Emissione continua senza tetto massimo")
    .replace(/#1 e System Bridge/gi, "#1 è System Bridge")
    .replace(/\\[PROTOCOL\\]/gi, "Protocollo:")
    .replace(/\\[CEX\\]/gi, "CEX:")
    .replace(/(\\d+)\\.(\\d+)%/g, "$1,$2%")
    .replace(/(\\d+)\\.(\\d+)x/gi, "$1,$2×");
  return t;
}}

function cleanWalletLabel(w) {{
  if (!w) return "—";
  return w
    .replace(/\\[PROTOCOL\\]\\s*/gi, "Protocollo: ")
    .replace(/\\[CEX\\]\\s*/gi, "CEX: ")
    .replace(/\\[BURN\\]\\s*/gi, "Burn: ")
    .replace(/\\[EOA\\]\\s*/gi, "Privato: ")
    .replace(/ETH2 Beacon Deposit/gi, "Ethereum Beacon Staking");
}}

function median(vals) {{
  if (!vals.length) return null;
  const s = [...vals].sort((a, b) => a - b);
  const m = Math.floor(s.length / 2);
  return s.length % 2 ? s[m] : (s[m - 1] + s[m]) / 2;
}}

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
    `Verifica individuale su <b>${{tot}}/${{tot}}</b> asset Pure: dati on-chain diretti su <b>${{nTop10}}/${{tot}} (${{FMT.dec1(nTop10/tot*100)}}%)</b>, scomposizione Top 10 su <b>${{nDecomp}}/${{tot}} (${{FMT.dec1(nDecomp/tot*100)}}%)</b> e <b>${{nBridge}}</b> fonti bridge CoinMarketCap sostituite con la blockchain nativa.`;

  document.getElementById("tokKpis").innerHTML = [
    ["Qualit&agrave; fonte dati (A+/A)", `${{nAp + nA}} / ${{tot}}`, "pos", `A+: ${{nAp}} · A: ${{nA}}<br>B: ${{nB}} · C: ${{nC}} · N/D: ${{nND}}`],
    ["Top 10 lordo &rarr; Balene private", `${{FMT.dec1(medTop10)}}% &rarr; ${{FMT.dec1(medEoa)}}%`, "acc", `Mediana dal ${{FMT.dec1(medTop10)}}% lordo al ${{FMT.dec1(medEoa)}}% nei soli wallet privati (EOA)`],
    ["Fonti bridge CMC corrette", `${{nBridge}} asset`, "acc", "Dati su reti secondarie sostituiti con la blockchain originale"],
    ["Vesting nei primi 10 wallet", `${{nDC}} asset`, "warn", "Token bloccati in vesting gi&agrave; nel Top 10 (evitato doppio conteggio)"],
    ["Pochi detentori (&lt;500 wallet)", `${{nMicro}} asset`, "neg", "Asset segnalati per rischio di elevata concentrazione"],
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
  document.getElementById("shown").textContent = `Mostrati ${{arr.length}} di ${{DATA.length}}`;
  document.getElementById("tb").innerHTML = arr.map(x => {{
    const isInf = x.is_infinite_max_supply || (x.fdv_to_mcap_ratio === null && x.to_unlock_pct === null);
    const circMain = isInf && x.unlocked_pct !== null ? `${{FMT.pct(x.unlocked_pct, false, 2)}} <span class="mut" style="font-weight:500;font-size:10.5px">del tot.</span>` : FMT.pct(x.unlocked_pct, false, 2);
    const fdv = x.fdv_to_mcap_ratio ? "FDV/Cap " + FMT.dec2(x.fdv_to_mcap_ratio) + "×" : null;
    const subUnl = isInf
      ? "Offerta max illimitata"
      : `${{fdv || "Offerta max illimitata"}} &middot; ${{x.to_unlock_pct !== null ? "Residua " + FMT.dec1(x.to_unlock_pct) + "%" : "Nessun tetto"}}`;
    // Show ALL 4 components (EOA + CEX + Contr. + Burn) so they visibly sum to Top 10 Lordo with ZERO B/C grade collision!
    const seg = x.top10_burn_pct !== null
      ? `<div class="segbar" title="Balene EOA ${{FMT.dec1(x.top10_eoa_whale_residual_pct)}}% | Exchange CEX ${{FMT.dec1(x.top10_cex_pct)}}% | Contratti/Staking ${{FMT.dec1(x.top10_contract_lock_lp_pct)}}% | Burn ${{FMT.dec1(x.top10_burn_pct)}}%">
           <div class="seg-eoa" style="width:${{x.top10_eoa_whale_residual_pct}}%"></div>
           <div class="seg-cex" style="width:${{x.top10_cex_pct}}%"></div>
           <div class="seg-proto" style="width:${{x.top10_contract_lock_lp_pct}}%"></div>
           <div class="seg-burn" style="width:${{x.top10_burn_pct}}%"></div>
         </div>
         <span class="small">EOA ${{FMT.dec1(x.top10_eoa_whale_residual_pct)}}% &middot; CEX ${{FMT.dec1(x.top10_cex_pct)}}%<br>Contr. ${{FMT.dec1(x.top10_contract_lock_lp_pct)}}% &middot; Burn ${{FMT.dec1(x.top10_burn_pct)}}%</span>`
      : `<span class="small">${{x.wallet_decomposition_status || "N/D"}}</span>`;
    const w1 = x.top1_wallet_label ? `${{cleanWalletLabel(x.top1_wallet_label)}} (${{FMT.dec1(x.top1_wallet_pct)}}%)` : "—";
    const dc = (x.vesting_whale_overlap_flag || "").startsWith("SI") ? '<span class="pill g-c" style="margin-top:2px" title="Token in vesting già compresi nei primi 10 wallet">Vesting in Top 10</span>' : "";
    const q3c = FMT.pctClass(x.ret_q3_pct);
    const n21c = FMT.pctClass(x.ret_nov21_pct);
    const vLbl = VERDICT_LABELS[x.coin_audit_verdict] || x.coin_audit_verdict;
    const rawNote = x.coin_audit_note || "—";
    const noteClean = cleanNote(rawNote);
    const exBurnNote = (x.top10_ex_burn_pct !== null && x.top10_burn_pct > 0) ? ` &middot; Netto burn: ${{FMT.dec1(x.top10_ex_burn_pct)}}%` : "";
    return `<tr>
      <td class="l sticky-col asset-col"><b class="cell-clip" title="${{x.name}} (Pos. CoinMarketCap #${{x.cmc_rank_jul1}})">#${{x.rank_clean_jul1}} ${{x.name}}</b><span class="small">${{x.symbol}} &middot; CMC #${{x.cmc_rank_jul1}}</span></td>
      <td class="l"><span class="pill ${{gCls(x.reliability_grade)}}">Fonte ${{x.reliability_grade}}</span><span class="small" title="Esito tokenomics (indipendente dal grado fonte)">${{vLbl}}</span></td>
      <td class="num"><b>${{circMain}}</b><span class="small">${{subUnl}}</span></td>
      <td class="num"><b>${{FMT.pct(x.top10_holders_pct, false, 2)}}</b><span class="small">Altri: ${{FMT.pct(x.distributed_outside_top10_pct, false, 1)}}${{exBurnNote}}</span></td>
      <td class="l">${{seg}}</td>
      <td class="num"><b>${{FMT.pct(x.top10_eoa_whale_residual_pct, false, 2)}}</b><span class="small">Wallet privati</span></td>
      <td class="l"><div class="small wallet-clamp" style="color:var(--ink)" title="${{w1}}">${{w1}}</div>${{dc}}</td>
      <td class="num"><span class="${{q3c}}">${{FMT.pct(x.ret_q3_pct, true, 2)}}</span><span class="small ${{n21c}}">${{FMT.pct(x.ret_nov21_pct, true, 2)}}</span></td>
      <td class="l"><div class="small note-clamp" title="${{noteClean}}">${{noteClean}}</div></td>
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
# 5. CURVA TOP N (Q3 2026) — curva_rendimento_N1_to_N500.html
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
<title>Curva Top N (Q3 2026): Rendimento da 1 a 500 Crypto</title>
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
    <h1>Curva di Rendimento Progressivo (Lug–Ott 2026): da 1 a 500 Criptovalute</h1>
    <div class="sub">Finestra 1&deg; luglio &ndash; 1&deg; ottobre 2026 (5&nbsp;&euro; per criptovaluta, in EUR al cambio storico EUR/USD 1,1413 &rarr; 1,1327). Mostra come varia il rendimento aggiungendo un asset alla volta per capitalizzazione, da solo Bitcoin (Top 1) fino alle Top 500.</div>
  </div>

  <div class="kpis kpis-4">
    <div class="kpi"><div class="lbl">Picco con outlier BTW (#143)</div><div class="val pos">Top 143 (+56,65% EUR)</div><div class="det">715&nbsp;&euro; &rarr; 1.120,08&nbsp;&euro;<span class="kpi-sep"> &middot; </span><span class="nowrap">portafogli &ge;&nbsp;10 asset</span></div></div>
    <div class="kpi"><div class="lbl">Solo Bitcoin (Top 1)</div><div class="val acc">+42,49% EUR</div><div class="det">5&nbsp;&euro; &rarr; 7,12&nbsp;&euro;<span class="kpi-sep"> &middot; </span><span class="nowrap">riferimento 100% BTC</span></div></div>
    <div class="kpi"><div class="lbl">Picco senza BTW (&ge; 10 asset)</div><div class="val pos">Top 93 (+49,77% EUR)</div><div class="det">465&nbsp;&euro; &rarr; 696,43&nbsp;&euro;<span class="kpi-sep"> &middot; </span><span class="nowrap">In profitto (&gt;0%): 83,9%</span></div></div>
    <div class="kpi"><div class="lbl">Intero portafoglio (Top 500)</div><div class="val pos">+32,21% EUR</div><div class="det">2.500&nbsp;&euro; &rarr; 3.305,21&nbsp;&euro; (+805,21&nbsp;&euro;)<span class="kpi-sep"> &middot; </span><span class="nowrap">Mediana EUR: +24,36%</span></div></div>
  </div>

  <div class="info-banner">
    <strong>Nota sull'outlier Bitway (BTW, #143):</strong> lo scalino verticale a N&nbsp;=&nbsp;143 &egrave; causato dal singolo asset anomalo <strong>Bitway (BTW, +2.021,9% EUR nel trimestre: 5&nbsp;&euro; &rarr; 106,09&nbsp;&euro;)</strong>. La curva verde lo esclude per mostrare il rendimento del resto del mercato. I picchi nei KPI considerano portafogli diversificati (<strong>&ge;&nbsp;10 asset</strong>), escludendo i picchi concentrati su 1–3 asset all'estrema sinistra del grafico. Tocca o scorri sul grafico per ispezionare ogni dimensione di portafoglio (da N&nbsp;=&nbsp;1 a N&nbsp;=&nbsp;500).
  </div>

  <div class="chart-card">
    <div class="legend">
      <div class="leg-item"><span class="swatch" style="background:var(--chart-port)"></span>Portafoglio EUR % (con outlier BTW)</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-struct)"></span>Portafoglio EUR % (senza BTW)</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-median)"></span>Mediana singole criptovalute (EUR %)</div>
      <div class="leg-item"><span class="swatch" style="background:var(--chart-btc)"></span>Solo Bitcoin (+42,49% EUR)</div>
    </div>
    <canvas id="cv" role="img" aria-label="Grafico della curva di rendimento progressiva da Top 1 a Top 500 nel trimestre luglio-ottobre 2026"></canvas>
    <div class="tbl-note" style="text-align:center;margin-top:4px">Asse orizzontale: dimensione del portafoglio (numero di criptovalute Top N, da N = 1 a N = 500)</div>
    <div id="tooltip"></div>
  </div>

  <div class="controls">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input type="search" id="q" placeholder="Cerca posizione (1–500), nome o ticker...">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    <span id="shown" class="pill p-muted">Mostrate 500 di 500 posizioni</span>
    <span class="scroll-hint" data-scroll-hint="curvaWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap" id="curvaWrap">
    <table>
      <thead>
        <tr>
          <th class="l sticky-col" data-k="N">N / Criptovaluta aggiunta</th>
          <th data-k="added_coin_pct_eur">Rend. asset (EUR)</th>
          <th data-k="invested_eur">Investito (&euro;)</th>
          <th data-k="portfolio_val_eur_real">Valore finale (&euro;)</th>
          <th data-k="portfolio_pnl_eur_real">Guadagno (&euro;)</th>
          <th data-k="portfolio_pct_eur_real">Cum. EUR %</th>
          <th data-k="portfolio_pct_eur_ex_btw">Cum. senza BTW %</th>
          <th data-k="marginal_impact_pp">Impatto (punti %)</th>
          <th data-k="median_return_pct">Mediana EUR %</th>
          <th data-k="win_rate_pct">In profitto (%)</th>
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
    axis: "#c0c0ca",
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

  if (W >= 420) {{
    const s93 = STEPS[92], s143 = STEPS[142];
    if (s93) drawCallout(xOf(93), yOf(s93.portfolio_pct_eur_ex_btw), "Picco (N ≥ 10): Top 93 (+49,77% senza BTW)", pal.green, pal.greenText, pal.pillBgGreen, true, 36);
    if (s143) drawCallout(xOf(143), yOf(s143.portfolio_pct_eur_real), "Picco (N ≥ 10): Top 143 (+56,65% con BTW)", pal.blue, pal.blueText, pal.pillBgBlue, false, 11);
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
  tip.innerHTML = `<strong>Top ${{s.N}} &middot; ${{s.added_name}} (${{s.added_symbol}})</strong><br>` +
    `Singolo asset: <span class="${{FMT.pctClass(s.added_coin_pct_eur)}}">${{FMT.pct(s.added_coin_pct_eur, true, 2)}} EUR</span> (${{FMT.eur(s.added_coin_val_oct1_eur)}})<br>` +
    `Portafoglio: ${{FMT.eurInt(s.invested_eur)}} &rarr; <strong>${{FMT.eur(s.portfolio_val_eur_real)}}</strong> (${{FMT.eurSigned(s.portfolio_pnl_eur_real)}})<br>` +
    `Cumulativo EUR: <strong class="pos">${{FMT.pct(s.portfolio_pct_eur_real, true, 2)}}</strong> (senza BTW: ${{FMT.pct(s.portfolio_pct_eur_ex_btw, true, 2)}})<br>` +
    `Mediana EUR: ${{FMT.pct(s.median_return_pct, true, 2)}} &middot; In profitto (&gt;0%): ${{FMT.dec1(s.win_rate_pct)}}%`;
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
  document.getElementById("shown").textContent = `Mostrate ${{rows.length}} di ${{STEPS.length}} posizioni`;
  document.getElementById("tb").innerHTML = rows.map(s => `
    <tr>
      <td class="l sticky-col"><strong>#${{s.N}} ${{s.added_name}}</strong> <span class="mut">(${{s.added_symbol}})</span></td>
      <td class="${{FMT.pctClass(s.added_coin_pct_eur)}}">${{FMT.pct(s.added_coin_pct_eur, true, 2)}}</td>
      <td>${{FMT.eur(s.invested_eur)}}</td>
      <td>${{FMT.eur(s.portfolio_val_eur_real)}}</td>
      <td class="${{FMT.pctClass(s.portfolio_pnl_eur_real)}}">${{FMT.eurSigned(s.portfolio_pnl_eur_real)}}</td>
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
# 6 & 7. DATASET 2026: PURE 500 vs RAW TOP 500 (Unified Switcher!)
# ==============================================================================
def upgrade_pure_or_raw(is_raw: bool, excl_map: dict):
    fname = "dashboard_top500_crypto_2026.html" if is_raw else "dashboard_pure500_crypto_2026.html"
    p = PROJ / fname
    orig = p.read_text(encoding="utf-8")
    d_full_json = extract_regex(orig, r"const (?:D|RAW)\s*=\s*(\{.*?\})(?:\.rows)?;", f"{fname} D JSON")

    active_id = "raw500" if is_raw else "pure500"
    rank_key = "rank_mcap_jul1" if is_raw else "rank_clean_jul1"
    title = (
        "Prezzi e Filtro CMC 2026: Top 500 Originali (Pre-Filtro) — Lug–Nov 2026"
        if is_raw
        else "Prezzi e Filtro CMC 2026: Top 500 Pure Crypto (Post-Filtro) — Lug–Nov 2026"
    )
    h1 = (
        "Prezzi e Filtro CMC 2026: Top 500 Originali (Pre-Filtro)"
        if is_raw
        else "Prezzi e Filtro CMC 2026: Top 500 Pure Crypto (1&deg; Lug – 21 Nov)"
    )
    sub = (
        "Classifica originale delle prime 500 capitalizzazioni CoinMarketCap al 1&deg; luglio 2026 (23:59&nbsp;UTC) prima delle esclusioni: 318 criptovalute Pure e 182 escluse (stablecoin, wrapped/liquid staking, asset reali tokenizzati RWA e token illiquidi)."
        if is_raw
        else "Le 500 criptovalute native liquide al 1&deg; luglio 2026 (23:59&nbsp;UTC), selezionate scartando 274 asset lungo la classifica CoinMarketCap (182 nella Top 500 iniziale e 92 tra #501 e #774 per completare 500 asset Pure: stablecoin, wrapped/LST, RWA e token con volume giornaliero &lt;100.000&nbsp;USD). Portafoglio 5&nbsp;&euro;/asset: 2.500&nbsp;&euro; &rarr; 3.305,21&nbsp;&euro; (1&deg; ott) &rarr; 2.728,87&nbsp;&euro; (21 nov 05:30&nbsp;CET)."
    )

    page_switch_html = (
        '<div class="page-switch" role="navigation" aria-label="Seleziona vista Top 500 2026">'
        '<a class="btn" href="./dashboard_pure500_crypto_2026.html">Top 500 Pure (Post-Filtro &middot; 500 asset)</a>'
        '<a class="btn active" href="./dashboard_top500_crypto_2026.html" aria-current="page">Top 500 Originali CMC (Pre-Filtro &middot; 182 escluse)</a>'
        '</div>'
        if is_raw
        else
        '<div class="page-switch" role="navigation" aria-label="Seleziona vista Top 500 2026">'
        '<a class="btn active" href="./dashboard_pure500_crypto_2026.html" aria-current="page">Top 500 Pure (Post-Filtro &middot; 500 asset)</a>'
        '<a class="btn" href="./dashboard_top500_crypto_2026.html">Top 500 Originali CMC (Pre-Filtro &middot; 182 escluse)</a>'
        '</div>'
    )

    excl_script = f"const EXCL = {json.dumps(excl_map, ensure_ascii=False)};" if is_raw else "const EXCL = {};"
    raw_filter_html = (
        """<div class="seg-group" role="group" aria-label="Filtro purezza">
      <button type="button" class="btn active" data-ef="all">Tutte (500)</button>
      <button type="button" class="btn" data-ef="pure">Solo Pure (318)</button>
      <button type="button" class="btn" data-ef="excl">Escluse (182)</button>
    </div>"""
        if is_raw
        else ""
    )

    # Pure 500 computes EUR Q3 median across ALL 500 assets (including the 1 delisted asset as -100% -> +24,36%, IDENTICAL to Curva Top 1-500!)
    kpi_js = (
        """const S = RAW.summary;
const nExcl = D.filter(r => EXCL[String(r.cmc_id)]).length;
const capNovPct = ((S.total_cohort_mcap_nov21_0530_usd / S.total_cohort_mcap_jul1_usd) - 1) * 100;
document.getElementById("kpiStrip").innerHTML = [
  ["Universo originale (1° lug)", "500 asset", "", `${D.length - nExcl} Pure · ${nExcl} Escluse`],
  ["Cap. coorte 1° luglio", FMT.compact(S.total_cohort_mcap_jul1_usd, "\u00A0USD"), "", "Soglia #500: " + FMT.compact(S.rank500_jul1_mcap_usd, "\u00A0USD")],
  ["Cap. coorte 1° ottobre", FMT.compact(S.total_cohort_mcap_oct1_active_usd, "\u00A0USD"), "pos", FMT.pct(S.cohort_mcap_growth_active_pct, true, 2) + " vs 1° lug · Mediana var. USD: " + FMT.pct(S.median_price_return_pct, true, 2)],
  ["Cap. coorte 21 novembre", FMT.compact(S.total_cohort_mcap_nov21_0530_usd, "\u00A0USD"), capNovPct >= 0 ? "pos" : "neg", FMT.pct(capNovPct, true, 2) + " vs 1° lug · Quotate: " + S.active_priced_on_nov21_0530 + "/500"],
].map(k => `<div class="kpi"><div class="lbl">${k[0]}</div><div class="val ${k[2]}">${k[1]}</div><div class="det">${k[3]}</div></div>`).join("");"""
        if is_raw
        else """const S = RAW.summary;
const fxRatioQ3 = 1.141311 / 1.132735;
const q3EurRets = D.map(r => r.price_change_pct != null ? (((1 + r.price_change_pct / 100) * fxRatioQ3 - 1) * 100) : -100).sort((a,b) => a - b);
const midQ3 = Math.floor(q3EurRets.length / 2);
const medQ3Eur = q3EurRets.length % 2 ? q3EurRets[midQ3] : (q3EurRets[midQ3 - 1] + q3EurRets[midQ3]) / 2;
document.getElementById("kpiStrip").innerHTML = [
  ["Portafoglio 1° ott (Q3)", FMT.eur(S.portfolio_2500eur_oct1_eur), "pos", "+32,21% EUR · Mediana EUR: " + FMT.pct(medQ3Eur, true, 2)],
  ["Portafoglio 21 novembre", FMT.eur(S.portfolio_2500eur_nov21_0530_eur), S.portfolio_2500eur_jul_to_nov21_pct >= 0 ? "pos" : "neg", FMT.pct(S.portfolio_2500eur_jul_to_nov21_pct, true, 2) + " EUR · Mediana EUR: " + FMT.pct(S.median_jul_to_nov21_eur_pct, true, 2)],
  ["Cap. coorte 1° ottobre", FMT.compact(S.total_cohort_mcap_oct1_active_usd, "\u00A0USD"), "pos", FMT.pct(S.cohort_mcap_growth_pct, true, 2) + " da " + FMT.compact(S.total_cohort_mcap_jul1_usd, "\u00A0USD") + " (1° lug)"],
  ["Cap. coorte 21 novembre", FMT.compact(S.total_cohort_mcap_nov21_0530_usd, "\u00A0USD"), S.cohort_mcap_jul_to_nov21_pct >= 0 ? "pos" : "neg", FMT.pct(S.cohort_mcap_jul_to_nov21_pct, true, 2) + " vs 1° lug · Attive: " + S.active_priced_on_nov21_0530 + "/500"],
].map(k => `<div class="kpi"><div class="lbl">${k[0]}</div><div class="val ${k[2]}">${k[1]}</div><div class="det">${k[3]}</div></div>`).join("");"""
    )

    rank_thead = (
        '<th class="l sticky-col" data-k="cmc_rank_jul1">Pos. CMC</th>'
        if is_raw
        else '<th class="l sticky-col" data-k="rank_clean_jul1">Pos. Pure</th><th data-k="cmc_rank_jul1">Pos. CMC</th>'
    )
    rank_td_js = (
        '<td class="l sticky-col"><b>#${r.cmc_rank_jul1}</b></td>'
        if is_raw
        else '<td class="l sticky-col"><b>#${r.rank_clean_jul1}</b></td><td class="mut">#${r.cmc_rank_jul1}</td>'
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
.tbl-wrap {{ max-height: 62vh; }}
.tbl-compact table {{ font-size: 12px; }}
.tbl-compact thead th {{ padding: 8px 6px; font-size: 11px; }}
.tbl-compact tbody td {{ padding: 6px 6px; }}
.asset-col {{ max-width: 215px; min-width: 145px; }}
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

  {page_switch_html}

  <div class="kpis kpis-4" id="kpiStrip"></div>

  <div class="controls">
    <div class="search-box">
      <span class="s-ico">{SEARCH_SVG}</span>
      <input id="q" type="search" placeholder="Cerca nome o ticker (es. BTC, ETH)">
      <button type="button" class="s-clr" aria-label="Pulisci ricerca">&times;</button>
    </div>
    {raw_filter_html}
    <span id="shown" class="pill p-muted">Mostrati 500 di 500</span>
  </div>

  <div class="tbl-sub-bar">
    <span class="tbl-note">Prezzi, capitalizzazioni (mln = milioni, mld = miliardi) e variazioni in tabella sono espressi in <strong>USD</strong> (i KPI di portafoglio sopra sono in <strong>EUR</strong>). Clicca le intestazioni per ordinare.</span>
    <span class="scroll-hint" data-scroll-hint="tblWrap">&larr; Scorri tabella &rarr;</span>
  </div>

  <div class="tbl-wrap tbl-compact" id="tblWrap">
    <table>
      <thead>
        <tr>
          {rank_thead}
          <th class="l" data-k="name">Criptovaluta</th>
          <th data-k="price_jul1_usd">Prezzo 1&deg; lug (USD)</th>
          <th data-k="mcap_jul1_usd">Cap. 1&deg; lug (USD)</th>
          <th data-k="price_oct1_usd">Prezzo 1&deg; ott (USD)</th>
          <th data-k="mcap_oct1_usd">Cap. 1&deg; ott (USD)</th>
          <th data-k="price_nov21_0530_usd">Prezzo 21 nov (USD)</th>
          <th data-k="mcap_nov21_0530_usd">Cap. 21 nov (USD)</th>
          <th data-k="price_change_pct">Var. USD (Lug&rarr;Ott)</th>
          <th data-k="price_change_jul_to_nov21_pct">Var. USD (Lug&rarr;Nov)</th>
          <th data-k="price_change_oct_to_nov21_pct">Var. USD (Ott&rarr;Nov)</th>
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
  return v == null ? "N/D" : FMT.int(v) + " USD";
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
  document.getElementById("shown").textContent = `Mostrati ${{rs.length}} di ${{D.length}}`;
  document.getElementById("tb").innerHTML = rs.map(r => {{
    const ex = EXCL[String(r.cmc_id)];
    const exBadge = ex ? ` <span class="pill ${{ex[1]}}" title="${{ex[2]}}">${{ex[0]}}</span>` : "";
    return `<tr>
      {rank_td_js}
      <td class="l asset-col"><div class="asset-title-row"><strong class="cell-clip" title="${{r.name}}">${{r.name}}</strong>${{exBadge}}</div><span class="small">${{r.symbol}}</span></td>
      <td>${{FMT.price(r.price_jul1_usd)}}</td>
      <td title="${{rawUsdTitle(r.mcap_jul1_usd)}}">${{FMT.compact(r.mcap_jul1_usd)}}</td>
      <td>${{FMT.price(r.price_oct1_usd)}}</td>
      <td title="${{rawUsdTitle(r.mcap_oct1_usd)}}">${{FMT.compact(r.mcap_oct1_usd)}}</td>
      <td>${{FMT.price(r.price_nov21_0530_usd)}}</td>
      <td title="${{rawUsdTitle(r.mcap_nov21_0530_usd)}}">${{FMT.compact(r.mcap_nov21_0530_usd)}}</td>
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
    print("\n=== ALL 7 HTML PAGES UPGRADED FOR UX WRITING, CONTENT DESIGN & IA ===")


if __name__ == "__main__":
    main()
