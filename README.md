# Pure Crypto Top 500 — Analisi Forense Multi-Ciclo su 15 Date (2022–2026)

[![Sito Web Live (GitHub Pages)](https://img.shields.io/badge/Live_Web_App-GitHub_Pages-0a84ff?style=for-the-badge)](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/)
[![Forensic Completeness Gate](https://img.shields.io/badge/Completeness_Gate-100%25_PASS-30d158?style=for-the-badge)](#metodologia-e-integrit%C3%A0-forense)

Ricerca quantitativa e forense **Zero Survivorship Bias** e **Zero Look-Ahead** sulle prime **500 criptovalute pure** per capitalizzazione di mercato attraverso un intero ciclo quadriennale di **15 date storiche** (`30 Dicembre 2022` → `21 Novembre 2026 05:30 CET`).

### Sito Web Pubblicato (6 Dashboard Interattive + Download Center)

> **Apri il portale interattivo live:** **[https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/)**

| Dashboard Web Interattiva | Descrizione | Link Diretto Live |
|---|---|---|
| **Home Portal & Download Center** | Panoramica multi-ciclo, evidenze empiriche e download CSV/JSON | [index.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/) |
| **Dashboard Flagship 15 Date (2022–2026)** | Matrice `14x15` interattiva, Tranche `50..500`, Vista A (`7.500` righe), Vista B (`500/500`), fattori on-chain | [dashboard_15date_ciclo_2022_2026.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/multidate_15_2022_2026/dashboard_15date_ciclo_2022_2026.html) |
| **Storico Point-in-Time 3 Date (Lug–Nov 2026)** | Evoluzione esatta `1 Lug`, `1 Ott`, `21 Nov 2026 05:30 CET` | [dashboard_storico_3date_500.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/dashboard_storico_3date_500.html) |
| **Audit Forense Tokenomics, Unlocks & Whale** | Sblocchi, Holders (`95,2%` copertura nativa) e decomposizione Burn/CEX/Protocol/EOA | [dashboard_tokenomics_holders_500.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/dashboard_tokenomics_holders_500.html) |
| **Curva Cumulativa Passo-Passo `N=1..500`** | Impatto marginale di ogni singola aggiunta da `1` a `500` coin (`5 EUR/coin`) | [curva_rendimento_N1_to_N500.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/curva_rendimento_N1_to_N500.html) |
| **Clean Pure Top 500 Q3 2026** | Coorte pura del 1° Luglio 2026 e confronto tranche | [dashboard_pure500_crypto_2026.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/dashboard_pure500_crypto_2026.html) |
| **Snapshot Raw Top 500 Pre-Filtro** | Baseline CMC originale prima della pulizia forense | [dashboard_top500_crypto_2026.html](https://raffaele-ando.github.io/crypto-top500-multicycle-2022-2026/dashboard_top500_crypto_2026.html) |

---

## Risultati Chiave del Backtest Multi-Ciclo (`5 EUR/coin = 2.500 EUR/coorte`)

- **Finestra Migliore (`Top 500`):** `D01 (30 Dic 2022) → D02 (09 Apr 2024)` = **`6.825,12 EUR` (`+173,00% EUR`)**, contro Bitcoin Buy & Hold `+308,72% EUR`.
- **Finestra Peggiore (`Top 500`):** `D02 (09 Apr 2024) → D13 (01 Lug 2026)` = **`469,90 EUR` (`-81,20% EUR`)** e `D05 (24 Gen 2025) → D15 (21 Nov 2026)` = **`473,19 EUR` (`-81,07% EUR`)**.
- **Hold 4 Anni (`30 Dic 2022 → 21 Nov 2026`):** `Top 500` = **`1.067,15 EUR` (`-57,31%` conservativo con `44` delisting / `-53,20%` solo attive)**; **`Top 50` = `+37,53% EUR`**; **Bitcoin = `+226,09% EUR`**.
- **Vincitore Tranche `Top 50..500`:** Su tutti gli ingressi `D01..D07 (2022–Set 2025)` tenuti al `21 Nov 2026`, le large-cap (`Top 50`, `Top 100`, `Top 150`) battono sistematicamente la `Top 500` di `+17 / +95` punti percentuali. Su `D08..D13` le tranche `250..450` vincono formalmente solo per il singolo micro-cap outlier `DHN` (`+8.207%..+13.148%`); escludendo `DHN`, le `Top 50–100` dominano anche nel 2026.
- **Fattori Empirici `Zero Look-Ahead`:**
  - **Overhang Unlocks (`D01→D08`):** mediana EUR `0–10%` (`-25,6%`) → `10–30%` (`-31,5%`, media `+41,3%`) → `30–60%` (`-46,6%`) → `>60%` (`-66,9%`).
  - **Concentrazione EOA Whale (`D08→D15`):** perdita media EUR `<10% EOA` (`-41,6%`) → `10–35%` (`-75,0%`) → `>35%` (`-77,2%`).

---

## Metodologia e Integrità Forense

1. **Doppia Vista Completa (`15.000` record):**
   - **Vista A (`panel_vistaA_15coorti_7500_righe.csv`):** 15 coorti Pure Top 500 ricostruite indipendentemente su ogni singola data (`15 x 500 = 7.500` righe + 12 CSV individuali `coorte_pure500_D01..D12.csv`), paginando gli snapshot CMC oltre il rank `10.000` (risolvendo lo split Tier-1/Tier-2) e filtrando stablecoin, wrapped/LST/LRT, ricevute DeFi, RWA/ETF/oro tokenizzati, illiquidi (`vol24h < 100.000 USD`), zombie falliti, dual-gas e subnet Alpha.
   - **Vista B (`panel_vistaB_jul1_500_su_15date_7500_righe.csv` & `storico_15date_vistaB_500_crypto.csv`):** le esatte 500 coin pure del `1° Luglio 2026` tracciate su tutte le 15 date (`N/Q` prima del lancio).
2. **Precisione Prezzi & Cambio FX Esatto:** Quote duali CMC/ECB `EUR/USD` per ogni singola data e correzione della troncatura a 8 decimali (`< 0,0001 USD`) tramite serie giornaliere `v3.1/cryptocurrency/historical`.
3. **24 Migrazioni / Rebrand Ufficiali Risolti:** `MATIC→POL (1:1)`, `FTM→S (1:1)`, `MKR→SKY (1:24.000)`, `EOS→A (1:1)`, `KLAY/LN→KAIA`, `OCEAN/AGIX/CUDOS→FET`, `1000SATS→SATS (1:1.000)`, `1MBABYDOGE→BABYDOGE (1:1.000.000)`, `MC→BEAM (1:100)`, `MPL→SYRUP (1:100)`, ecc.
4. **Dati On-Chain & Unlocks Storici (`Zero Look-Ahead`):**
   - **498 curve ufficiali di vesting CMC** campionate alla data esatta `<= T`.
   - **446 asset EVM** ricostruiti blocco-per-blocco tramite **`EVM Archive RPC Multicall3`** (`Ethereum`, `Base`, `Arbitrum`, `Optimism`, più `ETH` nativo con Beacon Contract), integrati con `CoinMetrics v4` (`AdrBalCnt` dal 2022), `CoinCarp` historical richlists e `CMC DAPI` verificato (`supply_ratio >= 0,45`).

---

## Struttura della Repository

```text
.
├── index.html                                         # Portale Web Apple-Craft (GitHub Pages Root)
├── multidate_15_2022_2026/
│   ├── dashboard_15date_ciclo_2022_2026.html          # Dashboard Flagship 15 Date (4 Tab)
│   ├── report_15date_2022_2026_completo.md            # Dossier Forense Integrale 15 Date (500/500)
│   ├── panel_vistaA_15coorti_7500_righe.csv           # Vista A: 15 coorti indipendenti x 500
│   ├── panel_vistaB_jul1_500_su_15date_7500_righe.csv # Vista B: 500 coin Lug1 x 15 date
│   ├── storico_15date_vistaB_500_crypto.{csv,json}    # Vista B tabella larga (128 colonne)
│   ├── backtest_matrice_14x15_5eur.csv                # Matrice completa 105 finestre 5 EUR
│   ├── backtest_tranche_50_to_500_tutte_date.csv      # 960 righe Tranche Cumulative & Marginali
│   ├── backtest_15date_completo.json                  # JSON Master Backtest + Fattori 4 Anni
│   ├── coorte_pure500_D01..D12_*.csv                  # 12 CSV individuali (500 coin/data)
│   └── raw/                                           # 12 Snapshot CMC completi + Archive RPC + Unlocks
├── dashboard_storico_3date_500.html                   # Dashboard 3 Date (Lug–Nov 2026)
├── dashboard_tokenomics_holders_500.html              # Dashboard Tokenomics, Unlocks & Wallet
├── curva_rendimento_N1_to_N500.html                   # Dashboard Curva N=1..500
├── dashboard_pure500_crypto_2026.html                 # Dashboard Clean Pure Top 500 Q3
├── dashboard_top500_crypto_2026.html                  # Dashboard Raw Top 500 Originale
├── report_*.md                                        # Dossier Forensi Completi (100% PASS)
├── *.csv / *.json                                     # Dataset 3 Date, Audit Forense & Tranche
├── raw/                                               # Snapshot 2026 & cache on-chain/explorer
└── scripts/
    ├── *.py                                           # Pipeline Q3 2026 & Curva N=1..500
    └── pipeline_3date_and_15date/                     # Pipeline completa 3 Date & 15 Date (Stage 1–6)
```

---

## Riproducibilità

Tutti gli script Python in `scripts/pipeline_3date_and_15date/` usano esclusivamente la standard library Python (`urllib`, `json`, `csv`, `concurrent.futures`) e API pubbliche senza chiavi a pagamento (CoinMarketCap public data-api/dapi, CoinMetrics Community v4, DefiLlama block API, Free Archive EVM RPCs via `Multicall3`).
