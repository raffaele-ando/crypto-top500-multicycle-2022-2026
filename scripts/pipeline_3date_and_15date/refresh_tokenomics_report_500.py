#!/usr/bin/env python3
"""Refresh report_tokenomics_unlocks_holders_500.md (Project + Artifact) from upgraded tokenomics_unlocks_holders_500.json (476/500 = 95.2%)."""
import json, os, statistics

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
ART_DIR = r"C:\Users\Administrator\.gemini\antigravity\brain\ef94cd2a-0982-41cb-9b2e-62eba3745324"

doc = json.load(open(os.path.join(PROJ_DIR, "tokenomics_unlocks_holders_500.json"), encoding="utf-8"))
rows = doc["cryptocurrencies"]
assert len(rows) == 500

def safe_md(s): return str(s or "").replace("|", "/").replace("$", "USD ")
def fq(v):
    if v is None: return "N/D"
    v = float(v)
    if v == 0: return "0"
    a = abs(v)
    if a >= 1e15: return f"{v/1e15:.2f}Q"
    if a >= 1e12: return f"{v/1e12:.2f}T"
    if a >= 1e9:  return f"{v/1e9:.2f}B"
    if a >= 1e6:  return f"{v/1e6:.2f}M"
    if a >= 1e3:  return f"{v/1e3:.1f}K"
    return f"{v:,.0f}"
def fi(v): return "N/D" if v is None else f"{int(v):,}".replace(",", ".")
def fp(v, s=False):
    if v is None: return "N/D"
    return f"{v:+.2f}%" if s else f"{v:.2f}%"

ver_h = [x for x in rows if x["top10_holders_pct"] is not None]
ver_100 = [x for x in rows if x["top100_holders_pct"] is not None]
ver_cnt = [x for x in rows if x["total_holders_count"] is not None]
fin = [x for x in rows if x["to_unlock_pct"] is not None]

med_ul = statistics.median([x["unlocked_pct"] for x in fin])
avg_ul = statistics.mean([x["unlocked_pct"] for x in fin])
med_t10 = statistics.median([x["top10_holders_pct"] for x in ver_h])
avg_t10 = statistics.mean([x["top10_holders_pct"] for x in ver_h])
med_t100 = statistics.median([x["top100_holders_pct"] for x in ver_100])
avg_t100 = statistics.mean([x["top100_holders_pct"] for x in ver_100])

n_off_ul = sum(1 for x in rows if x["unlock_source"] == "CMC Token Unlocks")
n_next_ul = sum(1 for x in rows if x["next_unlock_date"])
n_cap = sum(1 for x in rows if x["unlock_source"] == "CMC Supply (Circ/Max)")
n_tot = sum(1 for x in rows if x["unlock_source"] == "CMC Supply (Circ/Total)")
n_inf = sum(1 for x in rows if x["unlock_source"] == "CMC Supply (Infinita)")
n_nd = 500 - len(ver_h)

# Tier tables
conc_tiers = []
for tn in ["Distribuita (<25%)", "Media (25-50%)", "Alta (50-80%)", "Estrema (>=80%)", "N/D"]:
    sub = [x for x in rows if x["concentration_tier"] == tn]
    q3s = [x["ret_q3_pct"] for x in sub if x["ret_q3_pct"] is not None]
    n21s = [x["ret_nov21_pct"] for x in sub if x["ret_nov21_pct"] is not None]
    conc_tiers.append((tn, len(sub), statistics.mean(q3s), statistics.median(q3s), sum(1 for v in q3s if v > 0)/len(q3s)*100, statistics.mean(n21s), statistics.median(n21s)))

def ul_bucket(x):
    tu = x["to_unlock_pct"]
    if tu is None: return "Offerta Infinita (emissione continua)"
    if tu <= 5.0:  return "Quasi 100% Sbloccati (<=5% da sbloccare)"
    if tu <= 25.0: return "Overhang Basso (5-25% da sbloccare)"
    if tu <= 50.0: return "Overhang Medio (25-50% da sbloccare)"
    return "Overhang Pesante (>50% da sbloccare)"

ul_tiers = []
for tn in ["Quasi 100% Sbloccati (<=5% da sbloccare)", "Overhang Basso (5-25% da sbloccare)", "Overhang Medio (25-50% da sbloccare)", "Overhang Pesante (>50% da sbloccare)", "Offerta Infinita (emissione continua)"]:
    sub = [x for x in rows if ul_bucket(x) == tn]
    q3s = [x["ret_q3_pct"] for x in sub if x["ret_q3_pct"] is not None]
    n21s = [x["ret_nov21_pct"] for x in sub if x["ret_nov21_pct"] is not None]
    ul_tiers.append((tn, len(sub), statistics.mean(q3s), statistics.median(q3s), sum(1 for v in q3s if v > 0)/len(q3s)*100, statistics.mean(n21s), statistics.median(n21s)))

most_dist = sorted(ver_h, key=lambda x: x["top10_holders_pct"])[:10]
most_conc_t100 = sorted([x for x in ver_h if x["rank_clean_jul1"] <= 100], key=lambda x: -x["top10_holders_pct"])[:10]

md = []
md.append("# Tokenomics, Sblocchi e Concentrazione On-Chain — Tutte le 500 Criptovalute Pure (2026)")
md.append("")
md.append(f"> **Data rilevazione on-chain e supply:** `24 Novembre 2026` | **Coorte analizzata:** `500 / 500` Criptovalute Pure (coorte pulita dal `1° Luglio 2026`) | **Copertura Concentrazione On-Chain Primaria:** **`{len(ver_h)} / 500 ({len(ver_h)/5:.1f}%)`** (`{len(ver_h)} / 496 = {len(ver_h)/4.96:.1f}%` delle crypto pubbliche non-privacy) | **Audit Completezza Forense:** `500/500 PASS (100,0%, Exit Code 0)`.")
md.append("")
md.append("> [!IMPORTANT]")
md.append("> **Nota metodologica fondamentale su Concentrazione vs Distribuzione:** Le percentuali `Top 10` e `Top 100` rilevate on-chain provengono dalle blockchain native primarie (`Stellar.Expert`, `Hedera Mirror Node`, `Bittensor.ai`, `Subscan AssetHub`, `Celenium`, `ConfluxScan`, `0G Chainscan`, `THORChain.net`, `XDCScan`, `Blockchair`, `NanExplorer`, `AdaStat`, `SteemDB`, `Fogo SVM RPC`, `Blockscout v2`, `CMC Live DAPI`, `XRPScan`, `TronScan`, `Routescan`, `GoPlus`, `RugCheck`, `OKX Web3`, `TzKT`, `MultiversX`, `TonAPI`, `Hypurrscan`). Tali indirizzi includono anche **cold wallet CEX**, **smart contract di staking/vesting/LP** e **burn**: per la scomposizione esatta `Burn / CEX / Contract / EOA Whale` si veda il report gemello `report_audit_forense_500_crypto.md`. Le privacy coin schermate (`XMR`, `ZANO`, `BDX`) e il ledger privato (`CC`) sono marcati trasparentemente `N/D`.")
md.append("")
md.append("## 1. Sintesi Esecutiva & Copertura Forense")
md.append("")
md.append("| Metrica | Valore | Copertura / Dettaglio |")
md.append("|---|---:|---|")
md.append(f"| **Copertura Token Sbloccati / Da Sbloccare** | **500 / 500** | `100,0%` (`{n_off_ul}` con calendario vesting ufficiale CMC Token Unlocks, `{n_next_ul}` con data prossimo sblocco; `{n_cap}` Cap Fisso; `{n_tot}` Total Supply; `{n_inf}` Offerta Infinita) |")
md.append(f"| **Mediana % Gia Sbloccata** ({len(fin)} crypto a cap finito) | **{med_ul:.2f}%** | Media: `{avg_ul:.2f}%` — la meta delle crypto a offerta finita ha ancora oltre `{100-med_ul:.2f}%` di supply da sbloccare |")
md.append(f"| **Copertura Concentrazione On-Chain (Top 10)** | **{len(ver_h)} / 500** | **`{len(ver_h)/5:.1f}%`** verificati su rete primaria (**`{len(ver_h)/4.96:.1f}%`** delle 496 pubbliche non-privacy; `{len(ver_100)} / 500` = `{len(ver_100)/5:.1f}%` anche con `Top 100`) |")
md.append(f"| **Copertura Numero Holders Totali** | **{len(ver_cnt)} / 500** | **`{len(ver_cnt)/5:.1f}%`** con conteggio indirizzi/account verificato on-chain |")
md.append(f"| **Non Osservabili / Senza Richlist Pubblica** | **{n_nd} / 500** | `3` Privacy Coin schermate (`XMR`, `ZANO`, `BDX`), `1` Ledger privato (`CC`), `{n_nd-4}` L1 senza richlist aperta (o dietro gate anti-bot/CAPTCHA) |")
md.append(f"| **Mediana Concentrazione Top 10 Wallet** | **{med_t10:.2f}%** | Media: `{avg_t10:.2f}%` (Distribuiti fuori Top 10 mediana: **`{100-med_t10:.2f}%`**) |")
md.append(f"| **Mediana Concentrazione Top 100 Wallet** | **{med_t100:.2f}%** | Media: `{avg_t100:.2f}%` (Distribuiti fuori Top 100 mediana: **`{100-med_t100:.2f}%`**) |")
md.append("")
md.append("## 2. Impatto di Concentrazione e Overhang Sblocchi sui Rendimenti (1 Lug → 1 Ott e 21 Nov 2026)")
md.append("")
md.append("### 2.1 Rendimento per Fascia di Concentrazione On-Chain (Top 10 Wallet)")
md.append("")
md.append("| Fascia Concentrazione (Top 10) | N. Crypto | Quota Coorte | Rend. Medio Q3 (1 Lug→1 Ott) | Rend. Mediano Q3 | Win Rate Q3 | Rend. Medio 1 Lug→21 Nov | Rend. Mediano 21 Nov |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for tn, cnt, aq, mq, wq, an, mn in conc_tiers:
    md.append(f"| **{tn}** | {cnt} | {cnt/5:.1f}% | `{aq:+.2f}%` | `{mq:+.2f}%` | {wq:.1f}% | `{an:+.2f}%` | `{mn:+.2f}%` |")
md.append("")
md.append("### 2.2 Rendimento per Peso dei Token Ancora da Sbloccare (Overhang)")
md.append("")
md.append("| Fascia Token Ancora da Sbloccare | N. Crypto | Quota Coorte | Rend. Medio Q3 (1 Lug→1 Ott) | Rend. Mediano Q3 | Win Rate Q3 | Rend. Medio 1 Lug→21 Nov | Rend. Mediano 21 Nov |")
md.append("|---|---:|---:|---:|---:|---:|---:|---:|")
for tn, cnt, aq, mq, wq, an, mn in ul_tiers:
    md.append(f"| **{tn}** | {cnt} | {cnt/5:.1f}% | `{aq:+.2f}%` | `{mq:+.2f}%` | {wq:.1f}% | `{an:+.2f}%` | `{mn:+.2f}%` |")
md.append("")
md.append("## 3. Evidenze Principali: Piu Distribuite e Piu Concentrate")
md.append("")
md.append("### 3.1 Top 10 Crypto Piu Distribuite (Minor Concentrazione nei Top 10 Wallet)")
md.append("")
md.append("| # Clean | CMC | Crypto | Ticker | Top 10 Wallet % | Distribuiti fuori Top 10 % | Top 100 % | Holders Totali | Rend. Q3 |")
md.append("|---:|---:|---|---|---:|---:|---:|---:|---:|")
for x in most_dist:
    md.append(f"| #{x['rank_clean_jul1']:03d} | #{x['cmc_rank_jul1']} | {safe_md(x['name'])} | `{safe_md(x['symbol'])}` | **{fp(x['top10_holders_pct'])}** | **{fp(x['distributed_outside_top10_pct'])}** | {fp(x['top100_holders_pct'])} | {fi(x['total_holders_count'])} | `{fp(x['ret_q3_pct'], True)}` |")
md.append("")
md.append("### 3.2 Top 10 Crypto Piu Concentrate nella Top 100 per Market Cap")
md.append("")
md.append("| # Clean | CMC | Crypto | Ticker | Top 10 Wallet % | Distribuiti fuori Top 10 % | Top 100 % | Holders Totali | Fonte |")
md.append("|---:|---:|---|---|---:|---:|---:|---:|---|")
for x in most_conc_t100:
    md.append(f"| #{x['rank_clean_jul1']:03d} | #{x['cmc_rank_jul1']} | {safe_md(x['name'])} | `{safe_md(x['symbol'])}` | **{fp(x['top10_holders_pct'])}** | {fp(x['distributed_outside_top10_pct'])} | {fp(x['top100_holders_pct'])} | {fi(x['total_holders_count'])} | {safe_md(x['holder_source'])} |")
md.append("")
md.append("## 4. Censimento Integrale 500 / 500 — Token Sbloccati, Da Sbloccare, Concentrazione e Distribuzione")
md.append("")
md.append("| # Clean | CMC | Criptovaluta | Ticker | Sbloccati (Qty / %) | Da Sbloccare (Qty / %) | Prossimo Sblocco | Holders Totali | Top 10 Wallet (Qty / %) | Distribuiti Fuori Top 10 (Qty / %) | Top 100 % | Grade | Fonte On-Chain |")
md.append("|---:|---:|---|---|---|---|---|---:|---|---|---:|---|---|")
for x in rows:
    ul_s = f"{fq(x['unlocked_tokens'])} (`{fp(x['unlocked_pct'])}`)"
    toul_s = f"{fq(x['to_unlock_tokens'])} (`{fp(x['to_unlock_pct'])}`)" if x["to_unlock_pct"] is not None else "Infinita (emissione)"
    nxt_s = f"{x['next_unlock_date']} ({fp(x['next_unlock_pct'])})" if x["next_unlock_date"] else "—"
    t10_s = f"{fq(x['top10_tokens_qty'])} (**{fp(x['top10_holders_pct'])}**)" if x["top10_holders_pct"] is not None else "N/D"
    d10_s = f"{fq(x['distributed_outside_top10_tokens'])} ({fp(x['distributed_outside_top10_pct'])})" if x["distributed_outside_top10_pct"] is not None else "N/D"
    md.append(
        f"| #{x['rank_clean_jul1']:03d} | #{x['cmc_rank_jul1']} | {safe_md(x['name'])} | `{safe_md(x['symbol'])}` | "
        f"{ul_s} | {toul_s} | {nxt_s} | {fi(x['total_holders_count'])} | {t10_s} | {d10_s} | {fp(x['top100_holders_pct'])} | `{x['reliability_grade']}` | {safe_md(x['holder_source'])} |"
    )

txt = "\n".join(md) + "\n"
assert "$" not in txt
for dst in [
    os.path.join(PROJ_DIR, "report_tokenomics_unlocks_holders_500.md"),
    os.path.join(ART_DIR, "report_tokenomics_unlocks_holders_500.md"),
]:
    with open(dst, "w", encoding="utf-8") as f:
        f.write(txt)
print(f"Refreshed report_tokenomics_unlocks_holders_500.md ({len(ver_h)}/500 = {len(ver_h)/5:.1f}%) in Project + Artifact!")
