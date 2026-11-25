#!/usr/bin/env python3
"""
STAGE 2: Apply EXACT Pure-Crypto Top 500 Filter independently to EACH of the 12 new dates
(D01 2022-12-30 .. D12 2026-05-12), producing:
  - 12 survivorship-bias-free Clean Pure Top 500 cohorts (6,000 coin-date rows!)
  - Full audit of excluded non-pure assets per date & category
  - Automatic quantitative peg/tracker/stablecoin anomaly scan across all 6,000 selections
  - Sub-cent (< $0.0001) exact precision fix via CMC v3.1/cryptocurrency/historical
  - Union of all unique cmc_ids across all 15 dates (for Stage 3 metadata/unlocks/holders fetch!)
"""
import datetime, json, re, ssl, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
RAW = BASE / "raw"

fx_manifest = json.loads((RAW / "fx_and_snapshots_manifest_12dates.json").read_text(encoding="utf-8"))
old_excluded = json.loads((PROJ / "raw" / "excluded_non_pure_above_top500.json").read_text(encoding="utf-8"))
old_clean500 = json.loads((PROJ / "clean500_crypto_2026-07-01_vs_2026-10-01.json").read_text(encoding="utf-8"))["cryptocurrencies"]
old_clean_ids = {int(r["cmc_id"]) for r in old_clean500}

# Import ALL 229 previously verified non-pure excluded IDs from 2026-07-01 audit!
OLD_EXCL_MAP = {int(e["cmc_id"]): e["reason"] for e in old_excluded}

# Exact tag sets
STABLECOIN_TAGS = {
    "stablecoin", "usd-stablecoin", "eur-stablecoin", "fiat-stablecoin",
    "asset-backed-stablecoin", "algorithmic-stablecoin", "gbp-stablecoin",
    "chf-stablecoin", "jpy-stablecoin", "cny-stablecoin", "sgd-stablecoin",
}
TOKENIZED_TAGS = {
    "tokenized-stock", "xstocks-ecosystem", "tokenized-etfs", "bstocks",
    "tokenized-gold", "tokenized-commodities", "tokenized-assets",
    "tokenized-treasury-bills", "tokenized-real-estate",
}
WRAPPED_LST_TAGS = {
    "wrapped-tokens", "liquid-staking-derivatives", "liquid-restaking-tokens",
    "restaking-tokens", "bridged-tokens",
}

# Explicit native governance/protocol coins that must NEVER be excluded by name heuristics
KEEP_NATIVE_IDS = {
    1, 1027, 1839, 52, 5426, 1958, 74, 2010, 1975, 2, 1831, 512, 328, 4642, 5805, 6535, 6636, 7083,
    7278,   # Aave (AAVE)
    5692,   # Compound (COMP)
    7288,   # Venus (XVS)
    8000,   # Lido DAO (LDO)
    2943,   # Rocket Pool (RPL)
    28541,  # Jito (JTO)
    3783,   # Ankr (ANKR)
    32198,  # Babylon (BABY)
    38569,  # aPriori (APR)
    36296,  # Lorenzo Protocol (BANK)
    2586,   # Synthetix (SNX)
    1518,   # Maker (MKR)
    33038,  # Sky (SKY)
    30171,  # Ethena (ENA)
    6953,   # Frax Share (FXS)
    7429,   # Liquity (LQTY)
    6538,   # Curve DAO (CRV)
    9481,   # Pendle (PENDLE)
    30494,  # EigenLayer (EIGEN)
    29814,  # ether.fi (ETHFI)
    30843,  # Renzo (REZ)
    36341,  # KernelDAO (KERNEL)
    33311,  # Solv Protocol (SOLV)
    31520,  # Lista DAO (LISTA)
    13524,  # Marinade (MNDE) -- NOTE: 11461 is mSOL (Marinade Staked SOL, EXCLUDED!)
    32078,  # Sanctum (CLOUD)
    12623,  # Stader (SD)
    33566,  # Swell Network (SWELL)
    33352,  # Puffer (PUFFER)
    34104,  # Morpho (MORPHO)
    33824,  # Maple Finance (SYRUP)
    21159,  # Ondo (ONDO)
    27075,  # Mantle (MNT)
    13967,  # Goldfinch (GFI)
    12999,  # SSV Network (SSV)
    5882,   # StaFi (FIS)
    9288,   # BENQI (QI)
    7950,   # Flare (FLR)
    11857,  # GMX (GMX)
    29210,  # Jupiter (JUP)
    19091,  # Aavegotchi (GHST)
    3717,   # WAIT: 3717 is WBTC -> NEVER keep!
    36063,  # Bedrock (BR)
    39158,  # Bitway (BTW)
    30746,  # BounceBit (BB)
    1816,   # Civic
    5617,   # UMA
    6892,   # MultiversX
    2280,   # Filecoin
    1042,   # Siacoin
    3890,   # Polygon (MATIC)
    28321,  # POL
    3635,   # Cronos (CRO)
    11419,  # Toncoin
    20947,  # Sui
    21794,  # Aptos
    22974,  # Bittensor (TAO)
    22861,  # Celestia (TIA)
    23149,  # Sei
    11841,  # Arbitrum
    11840,  # Optimism
    32196,  # Hyperliquid (HYPE)
} - {3717}

# Explicit banned IDs from our Jul 1 audit + well-known historical stablecoins/wrapped/LST/zombies/dual-gas/subnets
ZOMBIE_BANKRUPT_IDS = {
    4195,   # FTX Token (FTT)
    4172,   # Terra Classic (LUNC)
    20314,  # Terra (LUNA2)
    11171,  # Celsius / bankrupt
    21296,  # Zombie
    8049,   # Zombie
    2700,   # Celsius (CEL)
    1817,   # Voyager Token (VGX)
    7129,   # TerraClassicUSD (USTC)
    20056,  # Mirror / dead
}
SUBNET_DUALGAS_IDS = {
    36912, 36902, 36901, 36904,  # Bittensor Alpha subnets
    1785,   # Gas (NEO GAS)
    3822,   # Theta Fuel (TFUEL)
    3012,   # VeThor Token (VTHO)
    3217,   # Ontology Gas (ONG)
}

EXTRA_STABLECOIN_SYMS = {
    "EDGT", "USDT", "USDC", "BUSD", "DAI", "TUSD", "USDP", "USDD", "GUSD", "FRAX", "LUSD", "FDUSD", "PYUSD",
    "USDE", "SUSDE", "USDS", "SUSDS", "SDAI", "EURS", "EURT", "EURC", "EURA", "AGEUR", "MIM", "USDN",
    "USTC", "UST", "HUSD", "FEI", "USDJ", "SUSD", "OUSD", "USDK", "MUSD", "CUSD", "CEUR", "XSGD",
    "VAI", "ALUSD", "DOLA", "CRVUSD", "GHO", "RLUSD", "USD1", "USD0", "BUSD0", "USDY", "USDF", "USDG",
    "USDX", "USDA", "USDR", "USDL", "WUSDL", "ZCHF", "XCHF", "BOLD", "DEUSD", "SDEUSD", "USR", "YUSD",
    "EUSD", "SYRUPUSDT", "SYRUPUSDC", "STUSDT", "USX", "EUSX", "FLEXUSD", "AUSD", "ZUSD", "GYEN",
    "TRYB", "BRZ", "IDRT", "BIDR", "CADC", "GBPT", "USDM", "USDZ", "FXUSD", "MKUSD", "HYUSD", "USDB",
    "VNDC", "IDRX", "CNHT", "MXNT", "ZARP", "NGNC", "ARSX", "KRWT", "EUROC", "EURCV", "AEUR", "EURI",
    "USDD", "USD+", "USDC.E", "USDT.E", "USDBC", "AXLUSDC", "AXLUSDT", "CEUSDC", "CEUSDT", "MULTIUSD",
    "USDON", "OUSG", "BUIDL", "TBILL", "BENJI", "USTB", "USYC", "ONDOUSDY", "USDY",
}
EXTRA_RWA_GOLD_SYMS = {
    "PAXG", "XAUT", "KAG", "KAU", "PMGT", "DGX", "CGO", "GOLDGR", "PDDON", "SOFION", "NVDAX", "AAPLX",
    "TSLAX", "SPYX", "QQQX", "MSTRX", "COINX", "GOOGLX", "AMZNX", "METAX", "MSFTX", "GLDX", "SLVX",
    "XAUM", "VRO", "TGLD", "AUSDT", "XAU", "XAG", "DPI", "MVI", "BED",
}
EXTRA_WRAPPED_LST_SYMS = {
    "WBTC", "BTCB", "BTCT", "HBTC", "RENBTC", "TBTC", "SBTC", "CBBTC", "LBTC", "FBTC", "SOLVBTC",
    "XSOLVBTC", "PUMPBTC", "UNIBTC", "EBTC", "MBTC", "KBTC", "OBTC", "PBTC", "RBTC", "WRBTC", "IBTC",
    "WETH", "STETH", "WSTETH", "RETH", "CBETH", "BETH", "WBETH", "FRXETH", "SFRXETH", "SWETH", "EETH",
    "WEETH", "EZETH", "RSETH", "PUFETH", "METH", "CMETH", "OSETH", "ETHX", "ANKRETH", "LSETH", "OETH",
    "UNIETH", "PXETH", "APXETH", "SETH", "SETH2", "RETH2", "STETH2", "CRETH2", "RSETH", "AGETH", "YNLSDE",
    "WBNB", "SLISBNB", "SLISBNBX", "ASBNB", "STKBNB", "ANKRBNB", "BNBX", "SNBNB", "WBBNB",
    "WSOL", "STSOL", "MSOL", "JITOSOL", "BSOL", "BNSOL", "INF", "JUPSOL", "HSOL", "DSOL", "VSOL",
    "LAINESOL", "CGNTSOL", "COMPASSOL", "EDGESOL", "HUBSOL", "JSOL", "JLP", "GLP", "SAVAX", "GGAVAX",
    "WAVAX", "WMATIC", "WPOL", "STMATIC", "MATICX", "STATOM", "STTIA", "STOSMO", "STINJ", "STSUI",
    "AFSUI", "HASUI", "VSUI", "STAPT", "AMAPT", "THAPT", "STTON", "TSTON", "HTON", "STNEAR", "LINEAR",
    "STDOT", "VDOT", "LDOT", "SFTM", "WFTM", "STS", "WS", "STHYPE", "KHYPE", "WHYPE", "WTRX", "STRX",
    "WTON", "WADA", "WDOGE", "WXRP", "WNEAR", "WFIL", "WFLOW", "WCRO", "WGLMR", "WROSE", "WCELO",
    "CETH", "CUSDC", "CUSDT", "CDAI", "CWBTC", "CUNI", "CCOMP", "CBAT", "CZRX", "CLINK", "CSUSHI",
    "AETH", "AWETH", "AUSDC", "AUSDT", "ADAI", "AWBTC", "ASTETH", "ALINK", "AAAVE",
    "VBNB", "VUSDT", "VUSDC", "VBTC", "VETH", "VXVS", "VBUSD", "VDAI", "VXRP", "VADA", "VDOGE", "VLINK",
    "3CRV", "CRV3CRYPTO", "HBTC", "OBTC", "SBTC", "BBTC", "BBETH", "BBUSD", "BETH", "KETH", "ZETH",
    "YETH", "YCRV", "CVXCRV", "SDCRV", "AURA",  # wait AURA is native gov -> remove AURA below!
    "STFIL", "STZETA", "STROSE", "STCELO", "STFLOW", "STSEI", "ISEI", "STKSM", "VKSM",
    "AUSD", "SUSD", "SEUR", "SGBP", "SAUD", "SJPY", "SCHF", "SXAU", "SXAG",
} - {"AURA"}

NAME_WRAPPED_PATTERNS = [
    "wrapped ", "staked ", "restaked ", "liquid staked", "liquid staking", "bridged ", "bridged-",
    "binance-pegged", "coinbase wrapped", "huobi btc", "bitcoin on rootstock", "bitcoin bep2",
    "bitcoin trc20", "universal btc", "universal eth", "solvbtc", "pumpbtc", "lombard staked",
    "lista staked", "marinade staked", "jito staked", "blazestake", "sanctum infinity", "stader ",
    "rocket pool eth", "frax staked", "stakewise", "treehouse eth", "ankr staked", "ether.fi staked",
    "renzo restaked", "kelp dao restaked", "mantle staked", "mantle restaked", "lido staked",
    "lido dao staked", "compound ether", "compound usd", "compound dai", "compound usdt",
    "compound wrapped", "aave eth", "aave usdc", "aave usdt", "aave dai", "aave wbtc", "aave interest",
    "venus bnb", "venus usdt", "venus usdc", "venus btc", "venus eth", "venus busd", "venus dai",
    "venus xrp", "venus ada", "venus doge", "venus link", "jupiter perps lp", "gmx glp",
    "savings dai", "savings usds", "staked usde", "staked usdt", "staked usdc", "syrup usdc",
    "syrup usdt", "beacon eth", "wrapped beacon", "ether.fi liquid", "puffer eth", "swell eth",
    "origin ether", "origin dollar", "benqi liquid", "stride staked", "pstake staked",
]
NAME_TOKENIZED_PATTERNS = [
    "tokenized", "tokenised", "pre-ipo stock", "ondo us dollar yield", "ondo short-term",
    "blackrock usd institutional", "franklin onchain", "pax gold", "tether gold", "kinesis gold",
    "kinesis silver", "perth mint gold", "digix gold", "cache gold", "matrixdock", "backed ",
    "xstock", "t-bill", "treasury bill", "u.s. dollar tokenized",
]

def classify_exclusion(c):
    cid = int(c["id"])
    vol = float(c.get("volume24h") or 0.0)
    mcap = float(c.get("marketCap") or 0.0)
    price = float(c.get("price") or 0.0)
    if mcap <= 0 or price <= 0:
        return "ZERO_MCAP_OR_PRICE"
    if cid in ZOMBIE_BANKRUPT_IDS:
        return "PUNTO_2_ZOMBIE_FALLITI_CHIUSI"
    if cid in SUBNET_DUALGAS_IDS:
        return "PUNTO_3_SUBNET_E_GAS_SECONDARI"
    if cid in KEEP_NATIVE_IDS:
        if vol < 100_000.0:
            return "PUNTO_1_ILLIQUIDI_VOL_LT_100K"
        return None
    if cid in OLD_EXCL_MAP:
        return OLD_EXCL_MAP[cid]

    tags = {t.lower() for t in (c.get("tags") or [])}
    sym_u = str(c.get("symbol") or "").upper().strip()
    nl = str(c.get("name") or "").lower().replace("\n", " ").strip()

    if (tags & TOKENIZED_TAGS) or sym_u in EXTRA_RWA_GOLD_SYMS or any(p in nl for p in NAME_TOKENIZED_PATTERNS):
        return "TOKENIZED_ETF_STOCK_RWA_COMMODITY"
    if (tags & STABLECOIN_TAGS) or sym_u in EXTRA_STABLECOIN_SYMS or ("stablecoin" in nl) or ("synthetic dollar" in nl) or re.match(r'^(usd|eur)[a-z0-9]{1,4}$', sym_u.lower()) and 0.92 <= price <= 1.15:
        return "STABLECOIN"
    if (tags & WRAPPED_LST_TAGS) or sym_u in EXTRA_WRAPPED_LST_SYMS or any(p in nl for p in NAME_WRAPPED_PATTERNS):
        return "WRAPPED_LST_LRT_RECEIPT"
    # Catch Bittensor Alpha subnets (e.g. "Subnet 1", "SN1", tag "bittensor-subnets" / "bittensor-ecosystem" with "alpha")
    if "bittensor-subnets" in tags or ("subnet" in nl and "bittensor" in nl):
        return "PUNTO_3_SUBNET_E_GAS_SECONDARI"
    # Liquidity gate: $100,000 minimum 24h volume (identical to Jul 1 Clean 500 rule!)
    if vol < 100_000.0:
        return "PUNTO_1_ILLIQUIDI_VOL_LT_100K"
    return None

# Run across all 12 dates!
cohorts_12 = {}
excl_summary_12 = {}
union_cids = set(old_clean_ids)
suspect_pegs = []

print("=== STAGE 2: BUILDING 12 INDEPENDENT CLEAN PURE TOP 500 COHORTS ===")
for dt, meta in fx_manifest.items():
    code = meta["code"]
    snap = json.loads((RAW / f"cmc_snap_{dt}.json").read_text(encoding="utf-8"))
    coins = snap["data"]
    # Rank strictly by Market Cap descending (resolves CMC Tier-1/Tier-2 split!)
    ranked = [c for c in coins if (c.get("marketCap") or 0) > 0 and (c.get("price") or 0) > 0]
    ranked.sort(key=lambda x: float(x["marketCap"]), reverse=True)

    pure = []
    excl_counts = {}
    for c in ranked:
        reason = classify_exclusion(c)
        if reason:
            if len(pure) < 500:
                excl_counts[reason] = excl_counts.get(reason, 0) + 1
        else:
            pure.append(c)
            if len(pure) == 500:
                break

    assert len(pure) == 500, f"Only found {len(pure)} pure coins on {dt}!"
    cohorts_12[dt] = pure
    excl_summary_12[dt] = {
        "code": code, "date": dt, "excluded_above_cutoff": sum(excl_counts.values()),
        "breakdown": excl_counts,
        "cutoff_rank500": f"CMC#{pure[-1]['cmcRank']} {pure[-1]['name']} ({pure[-1]['symbol']})",
        "cutoff_mcap_usd": round(float(pure[-1]["marketCap"]), 2),
        "total_cohort_mcap_usd": round(sum(float(x["marketCap"]) for x in pure), 2),
    }
    btc_p = float(meta["btc_usd"] or 0)
    eth_p = next((float(x["price"]) for x in pure if int(x["id"]) == 1027), 0)
    for rk, c in enumerate(pure, 1):
        cid = int(c["id"])
        union_cids.add(cid)
        p = float(c["price"])
        # Flag any untagged near-$1 or near-BTC or near-ETH coin for forensic verification!
        if cid not in old_clean_ids and cid not in KEEP_NATIVE_IDS:
            if 0.97 <= p <= 1.03 and abs(float(c.get("percentChange24h") or 0)) < 1.2:
                suspect_pegs.append((code, dt, rk, cid, c["symbol"], c["name"], round(p, 5), "NEAR_1USD"))
            elif btc_p > 0 and cid != 1 and 0.90 * btc_p <= p <= 1.10 * btc_p:
                suspect_pegs.append((code, dt, rk, cid, c["symbol"], c["name"], round(p, 2), "NEAR_BTC"))
            elif eth_p > 0 and cid != 1027 and 0.92 * eth_p <= p <= 1.08 * eth_p:
                suspect_pegs.append((code, dt, rk, cid, c["symbol"], c["name"], round(p, 2), "NEAR_ETH"))

    print(f"  [{code}] {dt} | Pure 500 | excl={sum(excl_counts.values()):3d} ({excl_counts.get('STABLECOIN',0)} stab, {excl_counts.get('WRAPPED_LST_LRT_RECEIPT',0)} wrap/LST, {excl_counts.get('TOKENIZED_ETF_STOCK_RWA_COMMODITY',0)} RWA, {excl_counts.get('PUNTO_1_ILLIQUIDI_VOL_LT_100K',0)} <100k) | #500={pure[-1]['symbol']:7s} (${pure[-1]['marketCap']/1e6:5.2f}M)")

print(f"\nUNION OF UNIQUE PURE COINS ACROSS ALL 15 DATES: {len(union_cids)} (New vs Jul 1 500: +{len(union_cids - old_clean_ids)})")
print(f"SUSPECT PEG/TRACKER HITS TO AUDIT ({len(suspect_pegs)}):")
seen_sp = set()
for sp in suspect_pegs:
    if sp[3] not in seen_sp:
        seen_sp.add(sp[3])
        print(f"  [{sp[7]:8s}] ID={sp[3]:5d} {sp[4]:10s} | {sp[5][:30]:30s} | P=${sp[6]} (first seen {sp[0]} #{sp[2]})")

# Save intermediate Stage 2 output for inspection & sub-cent fixing
(RAW / "stage2_cohorts_12dates_pre_audit.json").write_text(json.dumps({
    "union_cids": sorted(union_cids),
    "new_cids_vs_jul1": sorted(union_cids - old_clean_ids),
    "excl_summary": excl_summary_12,
    "suspect_pegs": suspect_pegs,
    "cohort_ids_by_date": {dt: [int(c["id"]) for c in lst] for dt, lst in cohorts_12.items()},
}, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Saved Stage 2 pre-audit manifest -> {RAW / 'stage2_cohorts_12dates_pre_audit.json'}")
