#!/usr/bin/env python3
"""
Final Clean Pure Crypto Top 500 Builder & Verifier (1 July 2026 vs 1 October 2026)
Excludes:
  0. Stablecoins, Wrapped/LST/LRT/Receipts/LP Baskets, Tokenized Stocks/ETFs/Pre-IPO/Commodities
  1. Illiquid / Ghost tokens with 24h Volume < $100,000 on 1 July 2026
  2. Bankrupt / Zombie / Closed chains & protocols (FTT, LUNC, LUNA, MNGO, ETHW, TORN)
  3. Bittensor Subnet Alpha tokens (SN*) & Dual-Chain Secondary Gas tokens (GAS, TFUEL, VTHO, ONG)
"""

import csv
import datetime
import json
import os
import re
import statistics
import time
import urllib.request

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


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


STABLECOIN_TAGS = {
    "stablecoin", "usd-stablecoin", "eur-stablecoin", "fiat-stablecoin",
    "asset-backed-stablecoin", "algorithmic-stablecoin",
}
TOKENIZED_TAGS = {
    "tokenized-stock", "xstocks-ecosystem", "tokenized-etfs", "bstocks",
    "tokenized-gold", "tokenized-commodities",
}
WRAPPED_TAGS = {"wrapped-tokens"}

EXTRA_STABLECOIN_IDS = {
    38786, 38779, 33981, 35437, 27793, 22933, 38273, 38948, 38947, 31379, 7129, 38407,
}
EXTRA_TOKENIZED_IDS = {36354, 39247, 39283}
EXTRA_WRAPPED_LST_LP_IDS = {
    4023, 9486, 28853, 26133, 33055, 8353, 32306, 29325, 25147, 23773,
}
KEEP_NATIVE_IDS = {32198, 8000, 28541, 38569, 3783, 2943, 36296}

ZOMBIE_IDS = {
    4195,   # FTX Token (FTT)
    4172,   # Terra Classic (LUNC)
    20314,  # Terra (LUNA)
    11171,  # Mango (MNGO)
    21296,  # EthereumPoW (ETHW)
    8049,   # Tornado Cash (TORN)
}
SUBNET_IDS = {36912, 36902, 36901, 36904}
SECONDARY_GAS_IDS = {
    1785,  # Gas (GAS - Neo)
    3822,  # Theta Fuel (TFUEL - Theta)
    3012,  # VeThor Token (VTHO - VeChain)
    3217,  # Ontology Gas (ONG - Ontology)
}


def classify_exclusion(r):
    cid = r["id"]
    tags = set(r.get("tags") or [])
    nl = r["name"].lower().replace("\n", " ")
    vol = float(r["quotes"][0].get("volume24h") or 0.0)

    if cid not in KEEP_NATIVE_IDS:
        if cid in EXTRA_TOKENIZED_IDS or (tags & TOKENIZED_TAGS) or any(x in nl for x in ["tokenized", "tokenised", "pre-ipo stock"]):
            return "TOKENIZED_ETF_STOCK_RWA_COMMODITY"
        if cid in EXTRA_STABLECOIN_IDS or (tags & STABLECOIN_TAGS):
            return "WRAPPED_LST_LRT_RECEIPT" if cid == 7957 else "STABLECOIN"
        if cid in EXTRA_WRAPPED_LST_LP_IDS or (tags & WRAPPED_TAGS):
            return "WRAPPED_LST_LRT_RECEIPT"
        if any(x in nl for x in [
            "wrapped ", "staked ", "restaked ", "liquid staked", "bridged", "venus ",
            "aave ", "compound ", "lido ", "kelp dao restaked", "ether.fi staked",
            "renzo restaked", "mantle staked", "mantle restaked",
            "coinbase wrapped", "binance-pegged", "huobi btc", "bitcoin on rootstock",
            "universal btc", "solvbtc", "xsolvbtc", "pumpbtc", "lombard",
            "aster asbnb", "lista staked", "jpool", "marinade staked",
            "jito staked", "blazestake", "sanctum infinity", "stader ", "rocket pool eth",
            "frax staked", "stakewise", "treehouse eth", "ankr staked", "swell ethereum",
            "amnis staked",
        ]):
            return "WRAPPED_LST_LRT_RECEIPT"

    # Point 2 checked before Point 1 so MNGO & TORN are explicitly attributed to Zombie/Closed too if desired,
    # or Point 1 first: let's attribute Zombie explicitly first so all 6 Zombie tokens show under Point 2!
    if cid in ZOMBIE_IDS:
        return "PUNTO_2_ZOMBIE_FALLITI_CHIUSI"
    if cid in SUBNET_IDS or "bittensor-subnets" in tags or (r["symbol"].startswith("SN") and r["symbol"][2:].isdigit()):
        return "PUNTO_3_SUBNET_E_GAS_SECONDARI"
    if cid in SECONDARY_GAS_IDS:
        return "PUNTO_3_SUBNET_E_GAS_SECONDARI"
    if vol < 100000.0:
        return "PUNTO_1_ILLIQUIDI_VOL_LT_100K"

    return None


def main():
    with open(os.path.join(RAW_DIR, "cmc_full_2026-07-01.json"), encoding="utf-8") as f:
        jul_all = json.load(f)["data"]
    with open(os.path.join(RAW_DIR, "cmc_full_2026-10-01.json"), encoding="utf-8") as f:
        oct_all = json.load(f)["data"]
    with open(os.path.join(RAW_DIR, "cmc_subcent_exact_v31.json"), encoding="utf-8") as f:
        subcent = json.load(f)

    oct_by_id = {r["id"]: r for r in oct_all}
    ranked = [r for r in jul_all if r["quotes"][0].get("marketCap", 0) > 0]
    ranked.sort(key=lambda r: r["quotes"][0]["marketCap"], reverse=True)

    clean500 = []
    excluded_log = []
    for r in ranked:
        reason = classify_exclusion(r)
        if reason:
            if len(clean500) < 500:
                excluded_log.append({
                    "cmc_id": r["id"],
                    "cmc_rank_jul1": r["cmcRank"],
                    "name": r["name"].replace("\n", " "),
                    "symbol": r["symbol"],
                    "mcap_jul1_usd": r["quotes"][0]["marketCap"],
                    "volume24h_jul1_usd": r["quotes"][0]["volume24h"],
                    "price_jul1_usd": r["quotes"][0]["price"],
                    "reason": reason,
                })
        else:
            clean500.append(r)
            if len(clean500) == 500:
                break

    assert len(clean500) == 500

    # Fetch exact v3.1 quotes for any newly entering sub-$0.01 coin
    ts_jul_s = int(datetime.datetime(2026, 6, 30, tzinfo=datetime.timezone.utc).timestamp())
    ts_jul_e = int(datetime.datetime(2026, 7, 3, tzinfo=datetime.timezone.utc).timestamp())
    ts_oct_s = int(datetime.datetime(2026, 9, 30, tzinfo=datetime.timezone.utc).timestamp())
    ts_oct_e = int(datetime.datetime(2026, 10, 3, tzinfo=datetime.timezone.utc).timestamp())

    new_fetched = 0
    for r in clean500:
        cid = r["id"]
        scid = str(cid)
        pj = r["quotes"][0]["price"]
        ro = oct_by_id.get(cid)
        po = ro["quotes"][0]["price"] if ro else 1.0
        if (pj < 0.01 or po < 0.01) and scid not in subcent:
            new_fetched += 1
            subcent[scid] = {"symbol": r["symbol"], "name": r["name"]}
            for lbl, s, e, m_str in [("2026-07-01", ts_jul_s, ts_jul_e, "2026-07-01"), ("2026-10-01", ts_oct_s, ts_oct_e, "2026-10-01")]:
                d = fetch_json(f"https://api.coinmarketcap.com/data-api/v3/cryptocurrency/historical?id={cid}&convertId=2781&timeStart={s}&timeEnd={e}&interval=1d")
                for q in d.get("data", {}).get("quotes", []):
                    if m_str in q.get("timeClose", ""):
                        subcent[scid][lbl] = q["quote"]
            time.sleep(0.12)

    if new_fetched > 0:
        with open(os.path.join(RAW_DIR, "cmc_subcent_exact_v31.json"), "w", encoding="utf-8") as f:
            json.dump(subcent, f, indent=2)

    CEX_IDS = {1839, 3957, 3635, 3897, 29160, 11092, 2087, 4269, 2694, 4041, 2933, 33849, 7501}

    records = []
    for idx, rj in enumerate(clean500, 1):
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
            v31_j = subcent.get(scid, {}).get("2026-07-01", {})
            if "close" in v31_j and v31_j["close"] > 0:
                price_jul = float(v31_j["close"])
                price_source_jul = "CMC v3.1 Exact Unrounded"
            elif cs_jul > 0 and mcap_jul > 0:
                price_jul = mcap_jul / cs_jul
                price_source_jul = "CMC Implied Exact"

        ro = oct_by_id.get(cid)
        status_oct = "ACTIVE"
        source_oct = "CMC Snapshot"
        cmc_rank_oct = None
        price_oct = None
        mcap_oct = None
        cs_oct = None
        vol_oct = None
        note = ""

        if ro is not None:
            qo = ro["quotes"][0]
            cmc_rank_oct = ro.get("cmcRank")
            price_oct = float(qo["price"])
            mcap_oct = float(qo["marketCap"])
            cs_oct = float(ro.get("circulatingSupply") or 0.0)
            vol_oct = float(qo["volume24h"] or 0.0)

            if price_oct < 0.01:
                v31_o = subcent.get(scid, {}).get("2026-10-01", {})
                if "close" in v31_o and v31_o["close"] > 0:
                    price_oct = float(v31_o["close"])
                    source_oct = "CMC v3.1 Exact Unrounded"
                elif cs_oct > 0 and mcap_oct > 0:
                    price_oct = mcap_oct / cs_oct
                    source_oct = "CMC Implied Exact"

            if mcap_oct == 0.0:
                status_oct = "ACTIVE_UNVERIFIED_SUPPLY"
                imp_mcap = cs_jul * price_oct
                note = f"Supply circolante non verificata su CMC al 2026-10-01 (mcap implicita a supply costante: `${imp_mcap:,.2f}`)."
        else:
            status_oct = "UNTRACKED"
            source_oct = "Untracked pre-2026-10-01"
            if cid == 5468:
                note = "Scambi sospesi su CMC/CG dopo il `2026-09-28` (ultimo dato: P=`$0.230941`, MCap=`$23,094,144`)."

        price_change_pct = ((price_oct - price_jul) / price_jul * 100.0) if (price_oct is not None and price_jul > 0) else None
        mcap_change_pct = ((mcap_oct - mcap_jul) / mcap_jul * 100.0) if (mcap_oct is not None and mcap_jul > 0) else None

        cat_tags = []
        if "memes" in tags:
            cat_tags.append("MEMECOIN")
        if cid in CEX_IDS:
            cat_tags.append("CEX_TOKEN")
        if cid == 38186:
            cat_tags.append("API_COMPUTE_TOKEN")

        records.append({
            "forensic_id": forensic_id,
            "rank_clean_jul1": idx,
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
            "category_note": ",".join(cat_tags),
            "notes": note,
        })

    # Verify strict monotonic decreasing Market Cap on July 1 AND Volume >= $100k on all 500!
    for i in range(500):
        assert records[i]["volume24h_jul1_usd"] >= 100000.0, f"Vol < 100k leaked: {records[i]}"
        if i < 499:
            assert records[i]["mcap_jul1_usd"] >= records[i + 1]["mcap_jul1_usd"]

    excl_counts = {}
    for e in excluded_log:
        excl_counts[e["reason"]] = excl_counts.get(e["reason"], 0) + 1

    total_mcap_jul1 = sum(r["mcap_jul1_usd"] for r in records)
    active_oct = [r for r in records if r["mcap_oct1_usd"] is not None]
    priced_oct = [r for r in records if r["price_oct1_usd"] is not None]
    zero_mcap_oct = [r for r in records if r["mcap_oct1_usd"] == 0.0]
    total_mcap_oct1 = sum(r["mcap_oct1_usd"] for r in active_oct)
    total_mcap_jul1_active = sum(r["mcap_jul1_usd"] for r in active_oct)

    price_pcts = [r["price_change_pct"] for r in priced_oct if r["price_change_pct"] is not None]
    mcap_pcts = [r["mcap_change_pct"] for r in active_oct if r["mcap_change_pct"] is not None]
    pos_p = sum(1 for x in price_pcts if x > 0)
    neg_p = sum(1 for x in price_pcts if x < 0)

    summary = {
        "universe_type": "CLEAN_PURE_CRYPTO_TOP_500 (Excluded: Stablecoins, Wrapped/LST/Receipts, Tokenized Stocks/ETFs/Gold + Point 1 Illiquid <$100k Vol + Point 2 Zombie/Bankrupt + Point 3 Subnet/Secondary Gas)",
        "snapshot_date_start_utc": "2026-07-01T23:59:59.999Z",
        "snapshot_date_end_utc": "2026-10-01T23:59:59.999Z",
        "universe_size": 500,
        "excluded_above_cutoff_total": len(excluded_log),
        "excluded_breakdown": excl_counts,
        "active_priced_on_oct1": len(priced_oct),
        "untracked_delisted_by_oct1": 500 - len(priced_oct),
        "zero_mcap_on_oct1": len(zero_mcap_oct),
        "min_volume24h_jul1_usd": min(r["volume24h_jul1_usd"] for r in records),
        "rank1_jul1_mcap_usd": records[0]["mcap_jul1_usd"],
        "rank500_jul1_mcap_usd": records[499]["mcap_jul1_usd"],
        "rank500_coin": f"{records[499]['name']} ({records[499]['symbol']}, CMC #{records[499]['cmc_rank_jul1']})",
        "total_cohort_mcap_jul1_usd": total_mcap_jul1,
        "total_cohort_mcap_oct1_active_usd": total_mcap_oct1,
        "cohort_mcap_growth_pct": round((total_mcap_oct1 - total_mcap_jul1_active) / total_mcap_jul1_active * 100.0, 4),
        "median_price_return_pct": round(statistics.median(price_pcts), 4),
        "mean_price_return_pct": round(statistics.mean(price_pcts), 4),
        "median_mcap_return_pct": round(statistics.median(mcap_pcts), 4),
        "winners_price_count": pos_p,
        "losers_price_count": neg_p,
    }

    # Save Clean 500 CSV, JSON, and Excluded 274 CSV
    excl_csv = os.path.join(PROJ_DIR, f"excluded_{len(excluded_log)}_assets_clean500.csv")
    with open(excl_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(excluded_log[0].keys()))
        w.writeheader()
        w.writerows(excluded_log)

    for prefix in ("clean500", "pure500"):
        jp = os.path.join(PROJ_DIR, f"{prefix}_crypto_2026-07-01_vs_2026-10-01.json")
        cp = os.path.join(PROJ_DIR, f"{prefix}_crypto_2026-07-01_vs_2026-10-01.csv")
        with open(jp, "w", encoding="utf-8") as f:
            json.dump({"metadata": summary, "excluded_above_cutoff": excluded_log, "cryptocurrencies": records}, f, indent=2, ensure_ascii=False)
        with open(cp, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
            w.writeheader()
            w.writerows(records)

    json_path = os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json")
    csv_path = os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.csv")

    top_gainers = sorted(priced_oct, key=lambda x: x["price_change_pct"], reverse=True)[:15]
    top_losers = sorted(priced_oct, key=lambda x: x["price_change_pct"])[:15]

    md = []
    md.append("# Dossier Definitivo Clean Pure Crypto Top 500 (1° Luglio 2026 vs 1° Ottobre 2026)")
    md.append("")
    md.append("> [!IMPORTANT]")
    md.append(f"> **Universo Clean Pure Crypto Point-in-Time (`500/500` Criptovalute Liquide & Attive — Soglia `CMC #774 Metis`)**")
    md.append(f"> Dalla graduatoria globale per capitalizzazione del **1° luglio 2026 (`2026-07-01 23:59:59 UTC`)** sono stati esclusi in modo deterministico **{len(excluded_log)} asset**:")
    md.append(f"> - **Filtro Base Non-Puri:** `{excl_counts.get('STABLECOIN',0)}` Stablecoin + `{excl_counts.get('WRAPPED_LST_LRT_RECEIPT',0)}` Wrapped / Liquid Staking / Receipt / LP Basket + `{excl_counts.get('TOKENIZED_ETF_STOCK_RWA_COMMODITY',0)}` Azioni, ETF, Pre-IPO e Materie Prime Tokenizzate;")
    md.append(f"> - **Punto 1 (Illiquidi / Fantasma):** `{excl_counts.get('PUNTO_1_ILLIQUIDI_VOL_LT_100K',0)}` token con Volume 24h `< $100,000` al 1° luglio 2026;")
    md.append(f"> - **Punto 2 (Zombie / Falliti / Chiusi):** `{excl_counts.get('PUNTO_2_ZOMBIE_FALLITI_CHIUSI',0)}` token (`FTT`, `LUNC`, `LUNA`, `MNGO`, `ETHW`, `TORN`);")
    md.append(f"> - **Punto 3 (Subnet & Gas Secondari):** `{excl_counts.get('PUNTO_3_SUBNET_E_GAS_SECONDARI',0)}` token (`SN4`, `SN51`, `SN44`, `SN9`, `GAS`, `TFUEL`, `VTHO`, `ONG`).")
    md.append("")
    md.append("**File Dataset & Strumenti Generati (Versione Definitiva Clean Pure 500):**")
    md.append("- Tabella CSV Clean Pure 500 (Excel/Pandas): [clean500_crypto_2026-07-01_vs_2026-10-01.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/clean500_crypto_2026-07-01_vs_2026-10-01.csv)")
    md.append("- Dataset JSON Clean Pure 500 + Metadati: [clean500_crypto_2026-07-01_vs_2026-10-01.json](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/clean500_crypto_2026-07-01_vs_2026-10-01.json)")
    md.append(f"- Registro completo dei {len(excluded_log)} asset esclusi con causale: [excluded_{len(excluded_log)}_assets_clean500.csv](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/excluded_{len(excluded_log)}_assets_clean500.csv)")
    md.append("- Dashboard Interattiva HTML aggiornata: [dashboard_pure500_crypto_2026.html](file:///C:/Users/Administrator/.gemini/antigravity/scratch/crypto_top500_jul_oct_2026/dashboard_pure500_crypto_2026.html)")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 1. Sintesi Macroeconomica Clean Pure Crypto Top 500 (1° Luglio → 1° Ottobre 2026)")
    md.append("")
    md.append("| Metrica Aggregata Coorte Clean Pure Crypto (500 Asset Liquidi del 1° Luglio 2026) | Valore Certificato |")
    md.append("| :--- | ---: |")
    md.append(f"| **Criptovalute Censite (1:1)** | **500 / 500** (`100.00%`) |")
    md.append(f"| **Asset Attivi e Quotati al 1° Ottobre 2026** | **{len(priced_oct)} / 500** (`{len(priced_oct)/5:.2f}%` di sopravvivenza attiva!) |")
    md.append(f"| **Volume 24h Minimo Garantito al 1° Luglio 2026** | **`${summary['min_volume24h_jul1_usd']:,.2f}`** (`>= $100,000`) |")
    md.append(f"| **Capitalizzazione #1 al 1° Luglio 2026 (`Bitcoin`)** | **`${records[0]['mcap_jul1_usd']:,.2f}`** (Prezzo: `${records[0]['price_jul1_usd']:,.2f}`) |")
    md.append(f"| **Capitalizzazione Soglia #500 (`Metis [METIS]`, `CMC #774`)** | **`${records[499]['mcap_jul1_usd']:,.2f}`** (Prezzo: `${records[499]['price_jul1_usd']:.4f}`) |")
    md.append(f"| **Capitalizzazione Aggregata Coorte al 1° Luglio 2026** | **`${total_mcap_jul1:,.2f}`** (`${total_mcap_jul1/1e12:.3f} Trilioni`) |")
    md.append(f"| **Capitalizzazione Aggregata Coorte al 1° Ottobre 2026** | **`${total_mcap_oct1:,.2f}`** (`${total_mcap_oct1/1e12:.3f} Trilioni`) |")
    md.append(f"| **Variazione Capitalizzazione Coorte (1° Lug → 1° Ott 2026)** | **{summary['cohort_mcap_growth_pct']:+.2f}%** (`+${total_mcap_oct1 - total_mcap_jul1_active:,.0f}`) |")
    md.append(f"| **Rendimento Mediano di Prezzo** | **{summary['median_price_return_pct']:+.2f}%** |")
    md.append(f"| **Rendimento Medio Equipesato di Prezzo** | **{summary['mean_price_return_pct']:+.2f}%** |")
    md.append(f"| **Variazione Mediana di Market Cap** | **{summary['median_mcap_return_pct']:+.2f}%** |")
    md.append(f"| **Bilancio Performance Prezzo (Rialzo / Ribasso)** | **{pos_p} positivi** (`{pos_p/len(priced_oct)*100:.1f}%`) / **{neg_p} negativi** (`{neg_p/len(priced_oct)*100:.1f}%`) |")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 2. Top 15 Maggiori Rialzi e Top 15 Maggiori Ribassi — Clean Pure Crypto Top 500")
    md.append("")
    md.append("### Top 15 Performance Positive (Prezzo USD)")
    md.append("")
    md.append("| Rank # | ID | Criptovaluta (Ticker) | Prezzo 1 Lug 2026 | Prezzo 1 Ott 2026 | Δ% Prezzo | Market Cap 1 Lug 2026 | Market Cap 1 Ott 2026 | Δ% MCap |")
    md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in top_gainers:
        md.append(
            f"| #{r['rank_clean_jul1']:03d} | `{r['forensic_id']}` | **{r['name']}** (`{r['symbol']}`) | `{fmt_price(r['price_jul1_usd'])}` | `{fmt_price(r['price_oct1_usd'])}` | **{fmt_pct(r['price_change_pct'])}** | `{fmt_mcap(r['mcap_jul1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` | {fmt_pct(r['mcap_change_pct'])} |"
        )
    md.append("")
    md.append("### Top 15 Performance Negative (Prezzo USD)")
    md.append("")
    md.append("| Rank # | ID | Criptovaluta (Ticker) | Prezzo 1 Lug 2026 | Prezzo 1 Ott 2026 | Δ% Prezzo | Market Cap 1 Lug 2026 | Market Cap 1 Ott 2026 | Δ% MCap |")
    md.append("| ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |")
    for r in top_losers:
        md.append(
            f"| #{r['rank_clean_jul1']:03d} | `{r['forensic_id']}` | **{r['name']}** (`{r['symbol']}`) | `{fmt_price(r['price_jul1_usd'])}` | `{fmt_price(r['price_oct1_usd'])}` | **{fmt_pct(r['price_change_pct'])}** | `{fmt_mcap(r['mcap_jul1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` | {fmt_pct(r['mcap_change_pct'])} |"
        )
    md.append("")
    md.append("---")
    md.append("")
    md.append("## 3. Tabella Integrale 1:1 — Tutte le 500 Clean Pure Crypto per Capitalizzazione (1° Luglio 2026 vs 1° Ottobre 2026)")
    md.append("")
    md.append("| # Clean | CMC # | ID | Nome | Ticker | Prezzo 1 Lug 2026 | Market Cap 1 Lug 2026 | Prezzo 1 Ott 2026 | Market Cap 1 Ott 2026 | Δ% Prezzo | Δ% MCap | Categoria / Stato |")
    md.append("| ---: | ---: | :--- | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: | :--- |")
    for r in records:
        safe_name = r["name"].replace("|", "/").replace("$", "\\$")
        safe_sym = r["symbol"].replace("|", "/")
        cat_str = r["category_note"] if r["category_note"] else "CORE_CRYPTO"
        if r["status_oct1"] != "ACTIVE":
            cat_str = f"{r['status_oct1']} | {cat_str}"
        md.append(
            f"| {r['rank_clean_jul1']:03d} | {r['cmc_rank_jul1']} | `{r['forensic_id']}` | {safe_name} | `{safe_sym}` "
            f"| `{fmt_price(r['price_jul1_usd'])}` | `{fmt_mcap(r['mcap_jul1_usd'])}` "
            f"| `{fmt_price(r['price_oct1_usd'])}` | `{fmt_mcap(r['mcap_oct1_usd'])}` "
            f"| {fmt_pct(r['price_change_pct'])} | {fmt_pct(r['mcap_change_pct'])} | {cat_str} |"
        )
    md.append("")

    md_text = "\n".join(md)
    proj_md = os.path.join(PROJ_DIR, "report_pure500_crypto_2026.md")
    clean_md = os.path.join(PROJ_DIR, "report_clean500_crypto_2026.md")
    for mp in (proj_md, clean_md):
        with open(mp, "w", encoding="utf-8") as f:
            f.write(md_text)

    # Update Interactive HTML Dashboard
    html_path = os.path.join(PROJ_DIR, "dashboard_pure500_crypto_2026.html")
    html_payload = json.dumps({"summary": summary, "rows": records}, ensure_ascii=False)
    html_doc = f"""<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Clean Pure Crypto Top 500 — 1 Luglio 2026 vs 1 Ottobre 2026</title>
<style>
  :root {{
    --bg: #0b0f17; --panel: #131a26; --border: #232f42; --text: #e6edf3;
    --muted: #8b9bb4; --accent: #3b82f6; --pos: #10b981; --neg: #ef4444;
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
  input[type="text"] {{ min-width: 280px; }}
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
</style>
</head>
<body>
<header>
  <h1>Clean Pure Crypto Top 500: 1° Luglio 2026 vs 1° Ottobre 2026</h1>
  <div class="sub">Esclusi {len(excluded_log)} asset (Stablecoin • Wrapped/LST • ETF/Azioni/Oro Tokenizzati • Illiquidi &lt;$100k • Zombie/Falliti • Subnet &amp; Gas Secondari)</div>
</header>
<div class="kpis" id="kpis"></div>
<div class="controls">
  <input type="text" id="q" placeholder="Cerca nome, ticker o ID (es. BTC, SOL, METIS, cmc-1)...">
  <select id="filter">
    <option value="ALL">Tutte le 500 Clean Crypto</option>
    <option value="GAINERS">Solo in rialzo (Δ% > 0)</option>
    <option value="LOSERS">Solo in ribasso (Δ% < 0)</option>
  </select>
  <label class="chk"><input type="checkbox" id="exMeme"> Nascondi Memecoin</label>
  <label class="chk"><input type="checkbox" id="exCex"> Nascondi Token CEX</label>
  <span class="count-badge" id="countBadge"></span>
</div>
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th data-k="rank_clean_jul1"># Clean</th>
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
        <th data-k="category_note">Categoria</th>
      </tr>
    </thead>
    <tbody id="tb"></tbody>
  </table>
</div>
<script>
const DATA = {html_payload};
let sortKey = 'rank_clean_jul1', sortDir = 1;
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
  const exM = document.getElementById('exMeme').checked;
  const exC = document.getElementById('exCex').checked;
  let rows = DATA.rows.filter(r => {{
    if (q && !(r.name.toLowerCase().includes(q) || r.symbol.toLowerCase().includes(q) || r.forensic_id.toLowerCase().includes(q))) return false;
    if (exM && r.category_note.includes('MEMECOIN')) return false;
    if (exC && r.category_note.includes('CEX_TOKEN')) return false;
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
      <td>${{r.rank_clean_jul1}}</td>
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
      <td><span class="tag">${{r.category_note || 'CORE_CRYPTO'}}</span></td>
    </tr>
  `).join('');
}}
['q','filter','exMeme','exCex'].forEach(id => document.getElementById(id).addEventListener('input', render));
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

    manifest_clean = {
        "target": "Clean Pure Crypto Top 500 (Points 1-3 Removed)",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "expected_counts": {"clean500_cryptos": 500},
        "sources": [
            f"clean500_json={json_path}:cryptocurrencies:forensic_id",
            f"clean500_csv={csv_path}::forensic_id",
        ],
        "required_files": [json_path, csv_path, excl_csv, html_path],
    }
    with open(os.path.join(PROJ_DIR, "manifest_clean500.json"), "w", encoding="utf-8") as f:
        json.dump(manifest_clean, f, indent=2)

    for i, ln in enumerate(md_text.splitlines(), 1):
        rem = re.sub(r"`[^`]*`", "", ln).replace("\\$", "")
        assert "$" not in rem, f"Unescaped '$' at line {i}: {rem}"

    print("=== CLEAN PURE 500 BUILD COMPLETE ===")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
