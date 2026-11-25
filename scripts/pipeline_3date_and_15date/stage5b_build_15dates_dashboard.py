#!/usr/bin/env python3
"""
STAGE 5B: Build Standalone Zero-Dependency Interactive Apple-Grade HTML Dashboard
-> multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html
4 Interactive Tabs:
  1. Backtest 5 EUR Multi-Ciclo (14x15 Interactive Heatmap + BTC Alpha Toggle + Dynamic Tranche 50..500 Explorer)
  2. Vista A — Esploratore 15 Date (D01..D15, all 500 coins per date searchable/sortable!)
  3. Vista B — Storico 15 Date Coorte Fissa 500 (2026-07-01, all 500/500 forensic IDs C001..C500!)
  4. Fattori On-Chain & Unlocks (4-Year Zero-Look-Ahead Analytics + 15-Date Coverage Census)
"""
import csv, json
from pathlib import Path

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"

bt = json.loads((BASE / "backtest_15date_completo.json").read_text(encoding="utf-8"))
vb_data = json.loads((BASE / "storico_15date_vistaB_500_crypto.json").read_text(encoding="utf-8"))["cryptocurrencies"]

# Load Vista A 7,500 rows compactly grouped by date_code (compact array format for ultra-fast load!)
va_by_code = {}
with open(BASE / "panel_vistaA_15coorti_7500_righe.csv", encoding="utf-8-sig") as f:
    for r in csv.DictReader(f):
        dc = r["date_code"]
        va_by_code.setdefault(dc, []).append([
            int(r["rank_clean"]),
            int(r["cmc_rank"] or 0),
            r["symbol"],
            r["name"],
            float(r["price_usd"]),
            round(float(r["mcap_usd"]) / 1e6, 2),
            round(float(r["vol24h_usd"]) / 1e6, 2),
            float(r["to_unlock_pct"]) if r["to_unlock_pct"] != "" else None,
            int(float(r["holders_cnt_hist"])) if r["holders_cnt_hist"] != "" else None,
            float(r["top10_hist_pct"]) if r["top10_hist_pct"] != "" else None,
            float(r["eoa_whale_hist_pct"]) if r["eoa_whale_hist_pct"] != "" else None,
            float(r["ret_eur_to_next_pct"]) if r["ret_eur_to_next_pct"] != "" else None,
            float(r["ret_eur_to_d08_pct"]) if r["ret_eur_to_d08_pct"] != "" else None,
            float(r["ret_eur_to_d14_pct"]) if r["ret_eur_to_d14_pct"] != "" else None,
            float(r["ret_eur_to_d15_pct"]) if r["ret_eur_to_d15_pct"] != "" else None,
            r["status_at_d15"] or r["status_at_next"] or "",
        ])

# Compact Vista B 500 rows (preserving exact forensic_id C001..C500!)
vb_compact = []
for r in vb_data:
    vb_compact.append({
        "fid": r["forensic_id"], "rk": r["rank_clean_jul1"], "cm": r["cmc_rank_jul1"],
        "sym": r["symbol"], "nm": r["name"], "fs": r["first_seen_15dates"], "nl": r["n_dates_listed"],
        "p01": r["p_usd_d01"], "p02": r["p_usd_d02"], "p04": r["p_usd_d04"], "p06": r["p_usd_d06"],
        "p08": r["p_usd_d08"], "p10": r["p_usd_d10"], "p12": r["p_usd_d12"], "p13": r["p_usd_d13"],
        "p14": r["p_usd_d14"], "p15": r["p_usd_d15"],
        "rf": r["ret_first_to_nov21_eur_pct"], "rq3": r["ret_jul1_to_oct1_eur_pct"],
        "rn": r["ret_jul1_to_nov21_eur_pct"], "t10": r["top10_ref_nov24_pct"],
    })

payload = {
    "census": bt["census_15dates"],
    "matrix": bt["matrix_14x15"],
    "tranches": bt["tranches_50_to_500"],
    "factors": bt["factor_backtests"],
    "migrations_n": bt["official_migrations_count"],
    "va": va_by_code,
    "vb": vb_compact,
}
payload_json = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).replace("</script>", "<\\/script>")

HTML = f"""<!DOCTYPE html>
<html lang="it" data-theme="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pure Crypto Top 500 — Dashboard Multi-Ciclo 15 Date (2022-2026)</title>
<style>
:root {{
  --bg: #000000; --surface: #111215; --surface2: #191b20; --border: rgba(255,255,255,0.09);
  --text: #f5f5f7; --muted: #98989f; --accent: #0a84ff; --green: #30d158; --red: #ff453a;
  --amber: #ff9f0a; --purple: #bf5af2; --radius: 14px;
}}
[data-theme="light"] {{
  --bg: #f5f5f7; --surface: #ffffff; --surface2: #f0f1f4; --border: rgba(0,0,0,0.09);
  --text: #1d1d1f; --muted: #6e6e73; --accent: #0071e3; --green: #248a3d; --red: #d70015;
  --amber: #c96a00; --purple: #8944ab;
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Segoe UI", Roboto, sans-serif;
  background: var(--bg); color: var(--text); -webkit-font-smoothing: antialiased; line-height: 1.45;
}}
.wrap {{ max-width: 1520px; margin: 0 auto; padding: 20px 22px 48px; }}
header {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 14px; margin-bottom: 18px; }}
h1 {{ margin: 0; font-size: 23px; font-weight: 700; letter-spacing: -0.02em; }}
.sub {{ color: var(--muted); font-size: 13px; margin-top: 3px; }}
.btn {{
  background: var(--surface2); color: var(--text); border: 1px solid var(--border);
  border-radius: 10px; padding: 8px 13px; font-size: 13px; font-weight: 500; cursor: pointer;
}}
.btn:hover {{ border-color: var(--accent); }}
.btn.active {{ background: var(--accent); color: #fff; border-color: var(--accent); }}
.kpis {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 10px; margin-bottom: 18px; }}
.kpi {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 13px 15px; }}
.kpi .lbl {{ font-size: 11px; text-transform: uppercase; letter-spacing: 0.04em; color: var(--muted); }}
.kpi .val {{ font-size: 20px; font-weight: 700; font-variant-numeric: tabular-nums; margin-top: 3px; }}
.kpi .note {{ font-size: 11.5px; color: var(--muted); margin-top: 2px; }}
.tabs {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid var(--border); padding-bottom: 12px; }}
.card {{ background: var(--surface); border: 1px solid var(--border); border-radius: var(--radius); padding: 16px 18px; margin-bottom: 16px; }}
.card h2 {{ margin: 0 0 10px; font-size: 16px; font-weight: 600; }}
.controls {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; margin-bottom: 12px; }}
select, input[type="search"] {{
  background: var(--surface2); color: var(--text); border: 1px solid var(--border);
  border-radius: 9px; padding: 7px 11px; font-size: 13px; outline: none;
}}
select:focus, input[type="search"]:focus {{ border-color: var(--accent); }}
.tbl-wrap {{ overflow-x: auto; max-height: 68vh; border: 1px solid var(--border); border-radius: 10px; }}
table {{ width: 100%; border-collapse: collapse; font-size: 12.5px; font-variant-numeric: tabular-nums; }}
th, td {{ padding: 7px 9px; border-bottom: 1px solid var(--border); text-align: right; white-space: nowrap; }}
th {{ position: sticky; top: 0; background: var(--surface2); font-weight: 600; color: var(--muted); z-index: 2; cursor: pointer; }}
td.l, th.l {{ text-align: left; }}
tr:hover td {{ background: rgba(10,132,255,0.06); }}
.pos {{ color: var(--green); font-weight: 600; }}
.neg {{ color: var(--red); font-weight: 600; }}
.mut {{ color: var(--muted); }}
.hm-cell {{ cursor: pointer; text-align: center; font-weight: 600; font-size: 11.5px; padding: 7px 5px; border-radius: 4px; transition: transform .1s; }}
.hm-cell:hover {{ outline: 2px solid var(--accent); transform: scale(1.04); position: relative; z-index: 3; }}
.hm-sel {{ outline: 2px solid #fff !important; }}
.bars {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(420px, 1fr)); gap: 16px; }}
.bar-row {{ display: grid; grid-template-columns: 74px 1fr 78px; align-items: center; gap: 8px; margin-bottom: 6px; font-size: 12.5px; }}
.bar-track {{ background: var(--surface2); height: 18px; border-radius: 5px; overflow: hidden; position: relative; }}
.bar-fill {{ height: 100%; border-radius: 5px; }}
.pill {{ display: inline-block; padding: 2px 7px; border-radius: 6px; font-size: 11px; font-weight: 600; background: var(--surface2); }}
.hidden {{ display: none !important; }}
.inspector {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 8px; background: var(--surface2); padding: 12px; border-radius: 10px; margin-top: 12px; font-size: 12.5px; }}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <div>
      <h1>Pure Crypto Top 500 — Analisi Multi-Ciclo 15 Date (2022–2026)</h1>
      <div class="sub">Zero Survivorship Bias (Vista A: 15x500 = 7.500 righe) &middot; Coorte Fissa 1° Luglio 2026 (Vista B: 500x15 = 7.500 righe) &middot; EVM Archive Multicall3 &amp; Curve Vesting CMC</div>
    </div>
    <button class="btn" id="themeBtn" onclick="toggleTheme()">Tema Chiaro / Scuro</button>
  </header>

  <div class="kpis" id="kpiStrip"></div>

  <div class="tabs">
    <button class="btn active" onclick="showTab('tab-bt', this)">1. Backtest 5 EUR &amp; Tranche 50–500</button>
    <button class="btn" onclick="showTab('tab-va', this)">2. Vista A — Esploratore 15 Date (500/data)</button>
    <button class="btn" onclick="showTab('tab-vb', this)">3. Vista B — Coorte Fissa 500 su 15 Date</button>
    <button class="btn" onclick="showTab('tab-fac', this)">4. Fattori On-Chain, Unlocks &amp; Copertura</button>
  </div>

  <!-- TAB 1: BACKTEST -->
  <section id="tab-bt">
    <div class="card">
      <h2>Matrice Completa 14 x 15 — Investimento 5 EUR/coin (2.500 EUR per coorte, Zero Survivorship Bias)</h2>
      <div class="controls">
        <span class="mut" style="font-size:12.5px">Metrica heatmap:</span>
        <select id="hmMode" onchange="renderHeatmap()">
          <option value="ret_eur_cons_pct">Rendimento EUR % (Conservativo: Delist = 0 EUR)</option>
          <option value="ret_eur_active_pct">Rendimento EUR % (Solo Sopravvissute/Migrate)</option>
          <option value="alpha_vs_btc_pp">Alpha vs Bitcoin Buy&amp;Hold EUR (punti %)</option>
          <option value="ret_usd_cons_pct">Rendimento USD % (Conservativo)</option>
        </select>
        <span class="mut" style="font-size:12px">Clicca qualsiasi cella per ispezionare dettagli e confronto BTC</span>
      </div>
      <div class="tbl-wrap" style="max-height:none"><table id="hmTable"></table></div>
      <div id="hmInspector" class="inspector"></div>
    </div>

    <div class="card">
      <h2>Analisi Tranche 50..500 (Cumulative 1..K e Fasce Marginali 50 Coin)</h2>
      <div class="controls">
        <label>Ingresso: <select id="trEntry" onchange="syncHorizons(); renderTranches()"></select></label>
        <label>Orizzonte Exit: <select id="trHoriz" onchange="renderTranches()"></select></label>
        <span id="trSummary" class="pill"></span>
      </div>
      <div class="bars">
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--muted)">Tranche Cumulative (Top 50 &rarr; Top 500)</h3>
          <div id="barsCum"></div>
        </div>
        <div>
          <h3 style="margin:0 0 8px;font-size:13.5px;color:var(--muted)">Fasce Marginali da 50 Coin (1-50 &rarr; 451-500)</h3>
          <div id="barsMarg"></div>
        </div>
      </div>
    </div>
  </section>

  <!-- TAB 2: VISTA A -->
  <section id="tab-va" class="hidden">
    <div class="card">
      <h2>Vista A — Coorte Indipendente Pure Top 500 alla Data Selezionata</h2>
      <div class="controls">
        <label>Data: <select id="vaDate" onchange="renderVistaA()"></select></label>
        <input type="search" id="vaSearch" placeholder="Filtra ticker o nome..." oninput="renderVistaA()">
        <label>Ordina: <select id="vaSort" onchange="renderVistaA()">
          <option value="0-asc">Rank Pure (1 &rarr; 500)</option>
          <option value="14-desc">Rend. EUR a D15 (Nov26) &darr;</option>
          <option value="14-asc">Rend. EUR a D15 (Nov26) &uarr;</option>
          <option value="11-desc">Rend. EUR Tappa Succ. &darr;</option>
          <option value="7-desc">Da Sbloccare % &darr;</option>
          <option value="9-desc">Top-10 On-Chain Storica % &darr;</option>
          <option value="8-desc">Holders Storici &darr;</option>
        </select></label>
        <span id="vaMeta" class="mut" style="font-size:12.5px"></span>
      </div>
      <div class="tbl-wrap"><table id="vaTable"></table></div>
    </div>
  </section>

  <!-- TAB 3: VISTA B -->
  <section id="tab-vb" class="hidden">
    <div class="card">
      <h2>Vista B — Storico Completo 15 Date delle 500 Crypto della Coorte 1° Luglio 2026</h2>
      <div class="controls">
        <input type="search" id="vbSearch" placeholder="Cerca C001..C500, ticker o nome..." oninput="renderVistaB()">
        <label>Ordina: <select id="vbSort" onchange="renderVistaB()">
          <option value="rk-asc">Rank Pure 1 Lug 2026 (1 &rarr; 500)</option>
          <option value="rf-desc">Rend. EUR 1a Data &rarr; Nov26 &darr;</option>
          <option value="rn-desc">Rend. EUR Lug26 &rarr; Nov26 &darr;</option>
          <option value="nl-desc">Anzianità (Date Quotate /15) &darr;</option>
          <option value="t10-desc">Top-10 Ref Nov26 % &darr;</option>
        </select></label>
        <span id="vbCount" class="mut" style="font-size:12.5px"></span>
      </div>
      <div class="tbl-wrap"><table id="vbTable"></table></div>
    </div>
  </section>

  <!-- TAB 4: FACTORS & CENSUS -->
  <section id="tab-fac" class="hidden">
    <div class="card">
      <h2>Censimento Macro e Copertura Point-in-Time sulle 15 Date (2022–2026)</h2>
      <div class="tbl-wrap" style="max-height:none"><table id="censusTable"></table></div>
    </div>
    <div class="card">
      <h2>Verifica Empirica Zero-Look-Ahead — Unlocks &amp; Concentrazione On-Chain Storica</h2>
      <div class="controls">
        <label>Finestra Temporale: <select id="facWin" onchange="renderFactors()"></select></label>
      </div>
      <div class="tbl-wrap" style="max-height:none"><table id="facTable"></table></div>
    </div>
  </section>
</div>

<script>
const D = {payload_json};
const CODES = D.census.map(c => c.code);
const MAT_MAP = Object.fromEntries(D.matrix.map(r => [r.entry_code + "_" + r.exit_code, r]));
let selPair = "D01_D08";

function toggleTheme() {{
  const h = document.documentElement;
  h.dataset.theme = h.dataset.theme === "dark" ? "light" : "dark";
}}
function showTab(id, btn) {{
  document.querySelectorAll("section").forEach(s => s.classList.add("hidden"));
  document.getElementById(id).classList.remove("hidden");
  document.querySelectorAll(".tabs .btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");
}}
function fmtP(v) {{
  if (v === "" || v === null || v === undefined) return '<span class="mut">N/Q</span>';
  v = Number(v);
  if (v >= 1000) return v.toLocaleString("it-IT", {{maximumFractionDigits: 0}});
  if (v >= 10) return v.toLocaleString("it-IT", {{minimumFractionDigits: 2, maximumFractionDigits: 2}});
  if (v >= 0.01) return v.toFixed(4);
  if (v >= 0.0001) return v.toFixed(6);
  return v.toExponential(2);
}}
function fmtPct(v) {{
  if (v === null || v === undefined || v === "") return '<span class="mut">N/D</span>';
  const n = Number(v);
  const cls = n >= 0 ? "pos" : "neg";
  return `<span class="${{cls}}">${{n >= 0 ? "+" : ""}}${{n.toFixed(2)}}%</span>`;
}}
function heatColor(v) {{
  if (v >= 150) return "rgba(48,209,88,0.55)";
  if (v >= 50) return "rgba(48,209,88,0.36)";
  if (v >= 10) return "rgba(48,209,88,0.20)";
  if (v >= 0) return "rgba(48,209,88,0.10)";
  if (v > -20) return "rgba(255,69,58,0.14)";
  if (v > -45) return "rgba(255,69,58,0.28)";
  return "rgba(255,69,58,0.48)";
}}

function initKPIs() {{
  const bestM = D.matrix.reduce((a,b) => b.ret_eur_cons_pct > a.ret_eur_cons_pct ? b : a);
  const worstM = D.matrix.reduce((a,b) => b.ret_eur_cons_pct < a.ret_eur_cons_pct ? b : a);
  const d01_15 = MAT_MAP["D01_D15"];
  const kpis = [
    ["Orizzonte Multi-Ciclo", "15 Date (4 Anni)", "30 Dic 2022 &rarr; 21 Nov 2026"],
    ["Righe Totali (Vista A+B)", "15.000 Record", "7.500 Vista A + 7.500 Vista B"],
    ["Miglior Finestra 500 Coin", `+${{bestM.ret_eur_cons_pct.toFixed(1)}}%`, `${{bestM.entry_code}} &rarr; ${{bestM.exit_code}} (${{bestM.final_eur_cons.toLocaleString("it-IT")}} EUR)`],
    ["Peggior Finestra 500 Coin", `${{worstM.ret_eur_cons_pct.toFixed(1)}}%`, `${{worstM.entry_code}} &rarr; ${{worstM.exit_code}} (${{worstM.final_eur_cons.toLocaleString("it-IT")}} EUR)`],
    ["Hold 4 Anni (D01&rarr;D15)", `${{d01_15.ret_eur_cons_pct >= 0 ? "+" : ""}}${{d01_15.ret_eur_cons_pct.toFixed(1)}}%`, `${{d01_15.final_eur_cons.toLocaleString("it-IT")}} EUR (BTC: +${{d01_15.btc_bench_ret_eur_pct.toFixed(1)}}%)`],
    ["Integrità On-Chain &amp; Mig.", `${{D.migrations_n}} Migrazioni`, "446 EVM Archive + 498 Curve CMC"],
  ];
  document.getElementById("kpiStrip").innerHTML = kpis.map(k =>
    `<div class="kpi"><div class="lbl">${{k[0]}}</div><div class="val">${{k[1]}}</div><div class="note">${{k[2]}}</div></div>`
  ).join("");
}}

function renderHeatmap() {{
  const mode = document.getElementById("hmMode").value;
  let html = "<thead><tr><th class='l'>Entry \\ Exit</th>" + CODES.slice(1).map(c => `<th>${{c}}</th>`).join("") + "</tr></thead><tbody>";
  for (let i = 0; i < 14; i++) {{
    const ec = CODES[i], ed = D.census[i].date;
    html += `<tr><td class='l'><b>${{ec}}</b> <span class='mut'>${{ed}}</span></td>`;
    for (let j = 1; j < 15; j++) {{
      const xc = CODES[j];
      const r = MAT_MAP[ec + "_" + xc];
      if (!r) {{ html += `<td class='mut' style='text-align:center'>&middot;</td>`; continue; }}
      const v = r[mode];
      const key = ec + "_" + xc;
      const sel = key === selPair ? " hm-sel" : "";
      html += `<td class="hm-cell${{sel}}" style="background:${{heatColor(v)}}" onclick="selectPair('${{key}}')">${{v >= 0 ? "+" : ""}}${{v.toFixed(1)}}%</td>`;
    }}
    html += "</tr>";
  }}
  html += "</tbody>";
  document.getElementById("hmTable").innerHTML = html;
  renderInspector();
}}

function selectPair(k) {{ selPair = k; renderHeatmap(); }}
function renderInspector() {{
  const r = MAT_MAP[selPair];
  if (!r) return;
  document.getElementById("hmInspector").innerHTML = [
    ["Finestra Selezionata", `<b>${{r.entry_code}} &rarr; ${{r.exit_code}}</b><br><span class='mut'>${{r.entry_date}} &rarr; ${{r.exit_date}}</span>`],
    ["Finale Cons. (2.500 EUR)", `<b>${{r.final_eur_cons.toLocaleString("it-IT",{{minimumFractionDigits:2}})}} EUR</b><br>${{fmtPct(r.ret_eur_cons_pct)}} EUR`],
    ["Solo Attive/Migrate", `<b>${{r.final_eur_active_norm.toLocaleString("it-IT",{{minimumFractionDigits:2}})}} EUR</b><br>${{fmtPct(r.ret_eur_active_pct)}} EUR`],
    ["Benchmark BTC (EUR)", `<b>${{r.btc_bench_final_eur.toLocaleString("it-IT",{{minimumFractionDigits:2}})}} EUR</b><br>${{fmtPct(r.btc_bench_ret_eur_pct)}}`],
    ["Alpha vs Bitcoin", `<b>${{r.alpha_vs_btc_pp >= 0 ? "+" : ""}}${{r.alpha_vs_btc_pp.toFixed(2)}} pp</b><br>Mediana: ${{fmtPct(r.median_ret_eur_pct)}}`],
    ["Sopravvivenza Coorte", `Attive: <b>${{r.n_active}}</b> &middot; Mig: <b>${{r.n_migrated}}</b><br>Delist (0 EUR): <b class='neg'>${{r.n_delisted_0eur}}</b>`],
    ["Miglior Asset", `<b>${{r.best_coin}}</b><br>${{fmtPct(r.best_ret_pct)}} | Win: ${{r.win_rate_pct}}%`],
  ].map(x => `<div><div class='mut' style='font-size:11px'>${{x[0]}}</div><div>${{x[1]}}</div></div>`).join("");
}}

function syncHorizons() {{
  const ec = document.getElementById("trEntry").value;
  const avail = [...new Set(D.tranches.filter(x => x.entry_code === ec).map(x => x.horizon))];
  const labels = {{ NEXT_LEG: "Tappa Successiva (Di+1)", TO_D08_PEAK: "Picco Ciclo D08 (07 Ott 2025)", TO_D14_OCT1: "1° Ottobre 2026 (D14)", TO_D15_NOV21: "21 Novembre 2026 05:30 CET (D15)" }};
  const sel = document.getElementById("trHoriz");
  const prev = sel.value;
  sel.innerHTML = avail.map(h => `<option value="${{h}}">${{labels[h] || h}}</option>`).join("");
  if (avail.includes(prev)) sel.value = prev;
  else if (avail.includes("TO_D15_NOV21")) sel.value = "TO_D15_NOV21";
}}

function renderBars(elId, rows, labelKey) {{
  const maxAbs = Math.max(10, ...rows.map(r => Math.abs(r.ret_eur_cons_pct)));
  const bestV = Math.max(...rows.map(r => r.ret_eur_cons_pct));
  document.getElementById(elId).innerHTML = rows.map(r => {{
    const v = r.ret_eur_cons_pct;
    const w = Math.min(100, Math.abs(v) / maxAbs * 100);
    const col = v >= 0 ? "var(--green)" : "var(--red)";
    const star = v === bestV ? " &#9733;" : "";
    return `<div class="bar-row"><div><b>${{r[labelKey]}}</b>${{star}}</div><div class="bar-track"><div class="bar-fill" style="width:${{w.toFixed(1)}}%;background:${{col}}"></div></div><div style="text-align:right">${{fmtPct(v)}}</div></div>`;
  }}).join("");
}}

function renderTranches() {{
  const ec = document.getElementById("trEntry").value;
  const hz = document.getElementById("trHoriz").value;
  const cums = D.tranches.filter(x => x.entry_code === ec && x.horizon === hz && x.tranche_type === "CUMULATIVE").map(x => ({{...x, lbl: "Top " + x.tranche_k}}));
  const margs = D.tranches.filter(x => x.entry_code === ec && x.horizon === hz && x.tranche_type === "MARGINAL_50").map(x => ({{...x, lbl: x.slice}}));
  if (!cums.length) return;
  const best = cums.reduce((a,b) => b.ret_eur_cons_pct > a.ret_eur_cons_pct ? b : a);
  document.getElementById("trSummary").innerHTML = `Exit: ${{best.exit_code}} (${{best.exit_date}}) &middot; Vincitore: <b>Top ${{best.tranche_k}} (${{best.ret_eur_cons_pct >= 0 ? "+" : ""}}${{best.ret_eur_cons_pct.toFixed(2)}}%)</b> &middot; BTC EUR: ${{best.btc_bench_ret_eur_pct >= 0 ? "+" : ""}}${{best.btc_bench_ret_eur_pct.toFixed(2)}}%`;
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
  document.getElementById("vaMeta").textContent = `${{rows.length}}/500 coin · BTC ${{cMeta.btc_usd.toLocaleString("it-IT")}} USD · FX ${{cMeta.fx_eur_usd.toFixed(4)}} · MCap Pure500 ${{cMeta.cohort_mcap_usd_b}} Mld USD`;
  let html = "<thead><tr><th>Pure#</th><th>CMC#</th><th class='l'>Ticker</th><th class='l'>Nome</th><th>Prezzo USD</th><th>MCap M</th><th>Vol24h M</th><th>Da Sbl.%</th><th>Holders Hist</th><th>Top10 Hist%</th><th>EOA Hist%</th><th>Tappa Succ.</th><th>A Picco D08</th><th>A Ott26 D14</th><th>A Nov26 D15</th><th class='l'>Stato D15</th></tr></thead><tbody>";
  for (const r of rows) {{
    html += `<tr><td><b>${{r[0]}}</b></td><td class='mut'>${{r[1]}}</td><td class='l'><b>${{r[2]}}</b></td><td class='l'>${{r[3]}}</td><td>${{fmtP(r[4])}}</td><td>${{r[5].toLocaleString("it-IT",{{maximumFractionDigits:1}})}}</td><td>${{r[6].toLocaleString("it-IT",{{maximumFractionDigits:1}})}}</td><td>${{r[7]!==null ? r[7].toFixed(1)+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[8]!==null ? r[8].toLocaleString("it-IT") : "<span class='mut'>N/D</span>"}}</td><td>${{r[9]!==null ? r[9].toFixed(1)+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{r[10]!==null ? r[10].toFixed(1)+"%" : "<span class='mut'>N/D</span>"}}</td><td>${{fmtPct(r[11])}}</td><td>${{fmtPct(r[12])}}</td><td>${{fmtPct(r[13])}}</td><td>${{fmtPct(r[14])}}</td><td class='l mut'>${{r[15]}}</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("vaTable").innerHTML = html;
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
  document.getElementById("vbCount").textContent = `${{rows.length}} / 500 criptovalute della coorte 1° Luglio 2026`;
  let html = "<thead><tr><th class='l'>ID</th><th>Rk Lug1</th><th class='l'>Ticker</th><th class='l'>Nome</th><th class='l'>1a Data</th><th>Date</th><th>D01 Dic22</th><th>D02 Apr24</th><th>D04 Nov24</th><th>D06 Apr25</th><th>D08 Ott25</th><th>D10 Gen26</th><th>D12 Mag26</th><th>D13 Lug26</th><th>D14 Ott26</th><th>D15 Nov26</th><th>1a&rarr;D15</th><th>Lug&rarr;Nov21</th><th>Top10 Ref</th></tr></thead><tbody>";
  for (const r of rows) {{
    html += `<tr><td class='l mut'>${{r.fid}}</td><td><b>${{r.rk}}</b></td><td class='l'><b>${{r.sym}}</b></td><td class='l'>${{r.nm}}</td><td class='l mut'>${{r.fs}}</td><td>${{r.nl}}/15</td><td>${{fmtP(r.p01)}}</td><td>${{fmtP(r.p02)}}</td><td>${{fmtP(r.p04)}}</td><td>${{fmtP(r.p06)}}</td><td>${{fmtP(r.p08)}}</td><td>${{fmtP(r.p10)}}</td><td>${{fmtP(r.p12)}}</td><td>${{fmtP(r.p13)}}</td><td>${{fmtP(r.p14)}}</td><td>${{fmtP(r.p15)}}</td><td>${{fmtPct(r.rf)}}</td><td>${{fmtPct(r.rn)}}</td><td>${{r.t10!==null ? r.t10+"%" : "<span class='mut'>N/D</span>"}}</td></tr>`;
  }}
  html += "</tbody>";
  document.getElementById("vbTable").innerHTML = html;
}}

function renderCensus() {{
  let html = "<thead><tr><th class='l'>Cod</th><th class='l'>Data (IT)</th><th>FX EUR/USD</th><th>BTC USD</th><th>ETH USD</th><th>MCap Pure500 (Mld)</th><th>Cutoff #500</th><th>Curve CMC Unlocks</th><th>Holders Hist</th><th>Top10 Hist (Archive/CC)</th><th>EOA Whale Hist</th><th>Vista B Quotate</th></tr></thead><tbody>";
  for (const c of D.census) {{
    html += `<tr><td class='l'><b>${{c.code}}</b></td><td class='l'>${{c.it_label}}</td><td>${{c.fx_eur_usd.toFixed(4)}}</td><td>${{c.btc_usd.toLocaleString("it-IT",{{maximumFractionDigits:1}})}}</td><td>${{c.eth_usd.toLocaleString("it-IT",{{maximumFractionDigits:1}})}}</td><td>${{c.cohort_mcap_usd_b.toFixed(2)}}</td><td><b>${{c.cutoff_rank500_sym}}</b> (${{c.cutoff_rank500_mcap_m.toFixed(1)}}M)</td><td>${{c.n_unlock_official_curve}}/500</td><td>${{c.n_hist_holders_cnt}}/500</td><td>${{c.n_hist_top10_conc}}/500</td><td>${{c.n_hist_eoa_whale}}/500</td><td>${{c.n_vistaB_already_listed}}/500</td></tr>`;
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
      html += `<tr><td class='l'><b>${{gt}}</b></td><td class='l'>${{bk}}</td><td>${{bv.n}}</td><td>${{fmtPct(bv.mean_eur_pct)}}</td><td>${{fmtPct(bv.median_eur_pct)}}</td><td>${{bv.win_rate_pct.toFixed(1)}}%</td></tr>`;
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
syncHorizons(); renderHeatmap(); renderTranches(); renderVistaA(); renderVistaB(); renderCensus(); renderFactors();
</script>
</body>
</html>"""

out_html = BASE / "dashboard_15date_ciclo_2022_2026.html"
out_html.write_text(HTML, encoding="utf-8")
print(f"Saved Interactive 4-Tab HTML Dashboard ({len(HTML)/1024/1024:.2f} MB) -> {out_html}")
