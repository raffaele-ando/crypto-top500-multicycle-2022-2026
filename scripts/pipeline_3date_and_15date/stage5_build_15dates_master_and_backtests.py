#!/usr/bin/env python3
"""
STAGE 5: Master 15-Date Multi-Cycle Builder, Zero-Survivorship-Bias Backtests (5 EUR + Tranches 50..500),
Vista A (15x500 = 7,500 rows + 12 per-date 500-coin CSVs), Vista B (500x15 = 7,500 rows + Wide 500-row Master),
4-Year Zero-Look-Ahead Factor Analytics, and Complete Forensic Markdown Report!
"""
import csv, datetime, json, math, re, statistics
from pathlib import Path

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
RAW = BASE / "raw"
ART_DIR = Path(r"C:\Users\Administrator\.gemini\antigravity\brain\ef94cd2a-0982-41cb-9b2e-62eba3745324")

ALL_15_DATES = [
    ("D01", "2022-12-30", "30 Dic 2022 01:00 CET", "2022-12-30 00:00 UTC"),
    ("D02", "2024-04-09", "09 Apr 2024 02:00 CEST", "2024-04-09 00:00 UTC"),
    ("D03", "2024-09-10", "10 Set 2024 02:00 CEST", "2024-09-10 00:00 UTC"),
    ("D04", "2024-11-22", "22 Nov 2024 01:00 CET", "2024-11-22 00:00 UTC"),
    ("D05", "2025-01-24", "24 Gen 2025 01:00 CET", "2025-01-24 00:00 UTC"),
    ("D06", "2025-04-08", "08 Apr 2025 02:00 CEST", "2025-04-08 00:00 UTC"),
    ("D07", "2025-09-19", "19 Set 2025 02:00 CEST", "2025-09-19 00:00 UTC"),
    ("D08", "2025-10-07", "07 Ott 2025 02:00 CEST", "2025-10-07 00:00 UTC"),
    ("D09", "2025-12-26", "26 Dic 2025 01:00 CET", "2025-12-26 00:00 UTC"),
    ("D10", "2026-01-15", "15 Gen 2026 01:00 CET", "2026-01-15 00:00 UTC"),
    ("D11", "2026-02-13", "13 Feb 2026 01:00 CET", "2026-02-13 00:00 UTC"),
    ("D12", "2026-05-12", "12 Mag 2026 02:00 CEST", "2026-05-12 00:00 UTC"),
    ("D13", "2026-07-01", "01 Lug 2026 23:59 UTC", "2026-07-01 23:59 UTC"),
    ("D14", "2026-10-01", "01 Ott 2026 23:59 UTC", "2026-10-01 23:59 UTC"),
    ("D15", "2026-11-21", "21 Nov 2026 05:30 CET", "2026-11-21 04:30 UTC"),
]
DATE_CODES = [x[0] for x in ALL_15_DATES]
DATE_ISOS = [x[1] for x in ALL_15_DATES]
CODE_BY_ISO = {x[1]: x[0] for x in ALL_15_DATES}
META_BY_ISO = {x[1]: {"code": x[0], "iso": x[1], "it_label": x[2], "utc_label": x[3]} for x in ALL_15_DATES}

# Verified Official Token Rebrands / Migrations / Mergers (old_cmc_id -> (new_cmc_id, new_sym, swap_ratio, note))
# swap_ratio = number of NEW tokens received per 1 OLD token!
OFFICIAL_MIGRATIONS = {
    3890:  (28321, "POL",      1.0,        "MATIC->POL 1:1"),
    3513:  (32684, "S",        1.0,        "FTM->Sonic(S) 1:1"),
    1518:  (33038, "SKY",      24000.0,    "MKR->SKY 1:24000"),
    1765:  (36462, "A",        1.0,        "EOS->Vaulta(A) 1:1"),
    4256:  (32880, "KAIA",     1.0,        "KLAY->KAIA 1:1"),
    4512:  (32880, "KAIA",     148.079656, "LN/FNSA->KAIA 1:148.08"),
    3911:  (3773,  "FET",      0.433226,   "OCEAN->FET ASI 1:0.4332"),
    2424:  (3773,  "FET",      0.433350,   "AGIX->FET ASI 1:0.4334"),
    8258:  (3773,  "FET",      0.008450,   "CUDOS->FET ASI 118.34:1"),
    28683: (28194, "SATS",     1000.0,     "1000SATS->SATS 1:1000"),
    33031: (10407, "BABYDOGE", 1000000.0,  "1MBABYDOGE->BABYDOGE 1:1M"),
    5625:  (27622, "LYX",      1.0,        "LYXe->LYX 1:1"),
    13523: (28298, "BEAM",     100.0,      "MC->BEAM 1:100"),
    23757: (32037, "ANYONE",   1.0,        "ATOR->ANYONE 1:1"),
    3884:  (35943, "PUNDIAI",  0.01,       "FX->PUNDIAI 100:1"),
    18860: (30636, "ZBCN",     10.0,       "ZBC->ZBCN 1:10"),
    15585: (30963, "ZENT",     10.0,       "GF->ZENT 1:10"),
    7411:  (32526, "CXT",      1.0,        "CQT->CXT 1:1"),
    9417:  (33824, "SYRUP",    100.0,      "MPL->SYRUP 1:100"),
    8985:  (2130,  "ENJ",      0.25,       "EFI->ENJ 4:1"),
    11877: (32120, "G",        60.0,       "GAL->G(Gravity) 1:60"),
    5631:  (33439, "LUMIA",    1.0,        "ORN->LUMIA 1:1"),
    6833:  (35724, "HEI",      1.0,        "LIT->HEI 1:1"),
    7535:  (8037,  "VANRY",    1.0,        "TVK->VANRY 1:1"),
}

# --- 1. LOAD ALL RAW SOURCES ---
print("=== [1/6] LOADING ALL 15 SNAPSHOTS, FX, METADATA, UNLOCKS, HOLDERS & ARCHIVE EVM DATA ===")
fx_12 = json.loads((RAW / "fx_and_snapshots_manifest_12dates.json").read_text(encoding="utf-8"))
st2 = json.loads((RAW / "stage2_cohorts_12dates_pre_audit.json").read_text(encoding="utf-8"))
subcent_12 = json.loads((RAW / "subcent_exact_12dates.json").read_text(encoding="utf-8"))
unlocks_15 = json.loads((RAW / "unlock_historical_15dates_all.json").read_text(encoding="utf-8"))
cm_15 = json.loads((RAW / "coinmetrics_15dates_all.json").read_text(encoding="utf-8"))
cc_15 = json.loads((RAW / "coincarp_his_15dates.json").read_text(encoding="utf-8"))
dapi_15 = json.loads((RAW / "dapi_holders_15dates_union.json").read_text(encoding="utf-8"))
evm_12 = json.loads((RAW / "evm_archive_12dates_holders.json").read_text(encoding="utf-8"))
new_details = json.loads((RAW / "new679_cmc_details.json").read_text(encoding="utf-8"))

# Existing verified 3-date sources (D13..D15)
old_clean500 = json.loads((PROJ / "clean500_crypto_2026-07-01_vs_2026-10-01.json").read_text(encoding="utf-8"))["cryptocurrencies"]
old_stor3 = {int(r["cmc_id"]): r for r in json.loads((PROJ / "storico_3date_completo_500_crypto.json").read_text(encoding="utf-8"))["cryptocurrencies"]}
old_audit = {int(r["cmc_id"]): r for r in json.loads((PROJ / "audit_forense_500_crypto.json").read_text(encoding="utf-8"))["cryptocurrencies"]}
old_details = json.loads((PROJ / "raw" / "cmc_tokenomics_holders_clean500.json").read_text(encoding="utf-8"))
old_evm3 = json.loads((PROJ / "raw" / "evm_archive_holders_3dates.json").read_text(encoding="utf-8"))
old_cc3 = json.loads((PROJ / "raw" / "coincarp_his_l1.json").read_text(encoding="utf-8"))

all_details = {}
all_details.update(old_details)
all_details.update(new_details)

# FX EUR/USD across all 15 dates (1 EUR = FX USD)
FX = {dt: float(fx_12[dt]["fx_eur_usd"]) for dt in fx_12}
FX["2026-07-01"] = 1.141311
FX["2026-10-01"] = 1.132697
FX["2026-11-21"] = 1.096000

# Normalize all 15 raw full snapshots into dict[dt][cid] = unified_coin_dict
def parse_full_snap_list(path):
    raw = json.loads(path.read_text(encoding="utf-8"))
    arr = raw["data"] if isinstance(raw, dict) and "data" in raw else raw
    out = {}
    for c in arr:
        cid = int(c["id"])
        if c.get("price") is not None:
            p = float(c.get("price") or 0)
            mc = float(c.get("marketCap") or 0)
            v24 = float(c.get("volume24h") or 0)
            p24 = float(c.get("percentChange24h") or 0)
        else:
            qs = c.get("quotes") or []
            q0 = qs[0] if isinstance(qs, list) and qs else (qs.get("USD") or qs.get("2781") or {} if isinstance(qs, dict) else {})
            p = float(q0.get("price") or 0)
            mc = float(q0.get("marketCap") or 0)
            v24 = float(q0.get("volume24h") or 0)
            p24 = float(q0.get("percentChange24h") or 0)
        circ = float(c.get("circulatingSupply") or 0)
        tot = float(c.get("totalSupply") or 0)
        mx = float(c.get("maxSupply") or 0) if c.get("maxSupply") else None
        # Sub-cent precision recovery when snapshot price rounded to 0 or < 1e-6 while mcap & circ > 0
        if (p <= 0 or p < 1e-6) and mc > 0 and circ > 0:
            p_imp = mc / circ
            if p <= 0 or abs(p_imp - p) / max(p_imp, 1e-18) > 0.005:
                p = p_imp
        out[cid] = {
            "id": cid, "name": c.get("name") or "", "symbol": c.get("symbol") or "",
            "slug": c.get("slug") or "", "cmcRank": int(c.get("cmcRank") or 0),
            "numMarketPairs": int(c.get("numMarketPairs") or 0),
            "circulatingSupply": circ, "totalSupply": tot, "maxSupply": mx,
            "price": p, "marketCap": mc, "volume24h": v24, "percentChange24h": p24,
            "tags": [t.get("slug") if isinstance(t, dict) else t for t in (c.get("tags") or [])],
            "dateAdded": c.get("dateAdded") or "",
        }
    return out

SNAPS = {}
for dt in DATE_ISOS[:12]:
    s = parse_full_snap_list(RAW / f"cmc_snap_{dt}.json")
    # Apply exact v3.1 sub-cent overrides!
    for scid, dmap in subcent_12.items():
        cid = int(scid)
        if dt in dmap and cid in s and dmap[dt] > 0:
            s[cid]["price"] = float(dmap[dt])
            if s[cid]["circulatingSupply"] > 0:
                s[cid]["marketCap"] = s[cid]["price"] * s[cid]["circulatingSupply"]
    SNAPS[dt] = s

SNAPS["2026-07-01"] = parse_full_snap_list(PROJ / "raw" / "cmc_full_2026-07-01.json")
SNAPS["2026-10-01"] = parse_full_snap_list(PROJ / "raw" / "cmc_full_2026-10-01.json")
SNAPS["2026-11-21"] = parse_full_snap_list(PROJ / "raw" / "cmc_full_2026-11-21.json")

# Override D13/D14/D15 snapshot entries for the 500 verified Jul 1 coins with exact verified prices (including nov21 05:30 CET intraday!)
for cid, s3 in old_stor3.items():
    for dt, suf in [("2026-07-01", "jul1"), ("2026-10-01", "oct1"), ("2026-11-21", "nov21")]:
        p = s3.get(f"price_usd_{suf}")
        if p is not None and float(p) > 0:
            rec = SNAPS[dt].get(cid)
            if rec:
                rec["price"] = float(p)
                if s3.get(f"mcap_usd_{suf}"):
                    rec["marketCap"] = float(s3[f"mcap_usd_{suf}"])
                if s3.get(f"vol24h_usd_{suf}") is not None:
                    rec["volume24h"] = float(s3[f"vol24h_usd_{suf}"])
                if s3.get(f"circ_supply_{suf}") is not None:
                    rec["circulatingSupply"] = float(s3[f"circ_supply_{suf}"])
                if s3.get(f"cmc_rank_{suf}") is not None:
                    rec["cmcRank"] = int(s3[f"cmc_rank_{suf}"])
            else:
                SNAPS[dt][cid] = {
                    "id": cid, "name": s3["name"], "symbol": s3["symbol"], "slug": "",
                    "cmcRank": int(s3.get(f"cmc_rank_{suf}") or 0),
                    "numMarketPairs": int(s3.get(f"num_pairs_{suf}") or 0),
                    "circulatingSupply": float(s3.get(f"circ_supply_{suf}") or 0),
                    "totalSupply": float(s3.get(f"total_supply_{suf}") or 0),
                    "maxSupply": float(s3[f"max_supply_{suf}"]) if s3.get(f"max_supply_{suf}") else None,
                    "price": float(p), "marketCap": float(s3.get(f"mcap_usd_{suf}") or 0),
                    "volume24h": float(s3.get(f"vol24h_usd_{suf}") or 0), "percentChange24h": 0.0, "tags": [], "dateAdded": "",
                }

# --- 2. BUILD EXACT VISTA A 15 COHORTS (D01..D12 from Stage 2, D13 from verified Jul 1 Clean 500, D14 & D15 via exact Stage 2 filter!) ---
import importlib.util
spec_s2 = importlib.util.spec_from_file_location("stage2_mod", str(ART_DIR / "scratch" / "stage2_filter_12_pure500_cohorts.py"))
# Reuse exact filter logic cleanly without re-executing Stage 2's main loop -> copy classify_exclusion constants cleanly!
old_excluded = json.loads((PROJ / "raw" / "excluded_non_pure_above_top500.json").read_text(encoding="utf-8"))
OLD_EXCL_MAP = {int(e["cmc_id"]): e["reason"] for e in old_excluded}

# Load Stage 2's exact filter sets by reading stage2_filter_12_pure500_cohorts.py AST-free? Better: replicate exact rules cleanly.
STABLECOIN_TAGS = {"stablecoin", "usd-stablecoin", "eur-stablecoin", "fiat-stablecoin", "asset-backed-stablecoin", "algorithmic-stablecoin", "gbp-stablecoin", "chf-stablecoin", "jpy-stablecoin", "cny-stablecoin", "sgd-stablecoin"}
TOKENIZED_TAGS = {"tokenized-stock", "xstocks-ecosystem", "tokenized-etfs", "bstocks", "tokenized-gold", "tokenized-commodities", "tokenized-assets", "tokenized-treasury-bills", "tokenized-real-estate"}
WRAPPED_LST_TAGS = {"wrapped-tokens", "liquid-staking-derivatives", "liquid-restaking-tokens", "restaking-tokens", "bridged-tokens"}
ZOMBIE_IDS = {4195, 4172, 20314, 11171, 21296, 8049, 2700, 1817, 7129, 20056}
SUBNET_DUALGAS_IDS = {36912, 36902, 36901, 36904, 1785, 3822, 3012, 3217}
KEEP_NATIVE_IDS = {1, 1027, 1839, 52, 5426, 1958, 74, 2010, 1975, 2, 1831, 512, 328, 4642, 5805, 6535, 6636, 7083, 7278, 5692, 7288, 8000, 2943, 28541, 3783, 32198, 38569, 36296, 2586, 1518, 33038, 30171, 6953, 7429, 6538, 9481, 30494, 29814, 30843, 36341, 33311, 31520, 13524, 32078, 12623, 33566, 33352, 34104, 33824, 21159, 27075, 13967, 12999, 5882, 9288, 7950, 11857, 29210, 19091, 36063, 39158, 30746, 1816, 5617, 6892, 2280, 1042, 3890, 28321, 3635, 11419, 20947, 21794, 22974, 22861, 23149, 11841, 11840, 32196}
EXTRA_STAB = {"EDGT", "VNDC", "USDT", "USDC", "BUSD", "DAI", "TUSD", "USDP", "USDD", "GUSD", "FRAX", "LUSD", "FDUSD", "PYUSD", "USDE", "SUSDE", "USDS", "SUSDS", "SDAI", "EURS", "EURT", "EURC", "EURA", "AGEUR", "MIM", "USDN", "USTC", "UST", "HUSD", "FEI", "USDJ", "SUSD", "OUSD", "USDK", "MUSD", "CUSD", "CEUR", "XSGD", "VAI", "ALUSD", "DOLA", "CRVUSD", "GHO", "RLUSD", "USD1", "USD0", "BUSD0", "USDY", "USDF", "USDG", "USDX", "USDA", "USDR", "USDL", "WUSDL", "ZCHF", "XCHF", "BOLD", "DEUSD", "SDEUSD", "USR", "YUSD", "EUSD", "SYRUPUSDT", "SYRUPUSDC", "STUSDT", "USX", "EUSX", "FLEXUSD", "AUSD", "ZUSD", "GYEN", "TRYB", "BRZ", "IDRT", "BIDR", "CADC", "GBPT", "USDM", "USDZ", "FXUSD", "MKUSD", "HYUSD", "USDB", "USD+", "USDC.E", "USDT.E", "USDBC", "AXLUSDC", "AXLUSDT", "CEUSDC", "CEUSDT", "MULTIUSD", "USDON", "OUSG", "BUIDL", "TBILL", "BENJI", "USTB", "USYC", "ONDOUSDY", "IDRX", "CNHT", "MXNT", "ZARP", "NGNC", "ARSX", "KRWT", "EUROC", "EURCV", "AEUR", "EURI", "USAT", "USDH", "U", "USDU", "EURAU"}
EXTRA_RWA = {"PAXG", "XAUT", "KAG", "KAU", "PMGT", "DGX", "CGO", "GOLDGR", "PDDON", "SOFION", "NVDAX", "AAPLX", "TSLAX", "SPYX", "QQQX", "MSTRX", "COINX", "GOOGLX", "AMZNX", "METAX", "MSFTX", "GLDX", "SLVX", "XAUM", "VRO", "TGLD", "AUSDT", "XAU", "XAG", "DPI", "MVI", "BED"}
EXTRA_WRAP = {"WBTC", "BTCB", "BTCT", "HBTC", "RENBTC", "TBTC", "SBTC", "CBBTC", "LBTC", "FBTC", "SOLVBTC", "XSOLVBTC", "PUMPBTC", "UNIBTC", "EBTC", "MBTC", "KBTC", "OBTC", "PBTC", "RBTC", "WRBTC", "IBTC", "WETH", "STETH", "WSTETH", "RETH", "CBETH", "BETH", "WBETH", "FRXETH", "SFRXETH", "SWETH", "EETH", "WEETH", "EZETH", "RSETH", "PUFETH", "METH", "CMETH", "OSETH", "ETHX", "ANKRETH", "LSETH", "OETH", "UNIETH", "PXETH", "APXETH", "SETH", "SETH2", "RETH2", "STETH2", "CRETH2", "AGETH", "YNLSDE", "WBNB", "SLISBNB", "SLISBNBX", "ASBNB", "STKBNB", "ANKRBNB", "BNBX", "SNBNB", "WBBNB", "WSOL", "STSOL", "MSOL", "JITOSOL", "BSOL", "BNSOL", "INF", "JUPSOL", "HSOL", "DSOL", "VSOL", "LAINESOL", "CGNTSOL", "COMPASSOL", "EDGESOL", "HUBSOL", "JSOL", "JLP", "GLP", "SAVAX", "GGAVAX", "WAVAX", "WMATIC", "WPOL", "STMATIC", "MATICX", "STATOM", "STTIA", "STOSMO", "STINJ", "STSUI", "AFSUI", "HASUI", "VSUI", "STAPT", "AMAPT", "THAPT", "STTON", "TSTON", "HTON", "STNEAR", "LINEAR", "STDOT", "VDOT", "LDOT", "SFTM", "WFTM", "STS", "WS", "STHYPE", "KHYPE", "WHYPE", "WTRX", "STRX", "WTON", "WADA", "WDOGE", "WXRP", "WNEAR", "WFIL", "WFLOW", "WCRO", "WGLMR", "WROSE", "WCELO", "CETH", "CUSDC", "CUSDT", "CDAI", "CWBTC", "CUNI", "CCOMP", "CBAT", "CZRX", "CLINK", "CSUSHI", "AETH", "AWETH", "AUSDC", "AUSDT", "ADAI", "AWBTC", "ASTETH", "ALINK", "AAAVE", "VBNB", "VUSDT", "VUSDC", "VBTC", "VETH", "VXVS", "VBUSD", "VDAI", "VXRP", "VADA", "VDOGE", "VLINK", "3CRV", "CRV3CRYPTO", "BBTC", "BBETH", "BBUSD", "KETH", "ZETH", "YETH", "YCRV", "CVXCRV", "SDCRV", "STFIL", "STZETA", "STROSE", "STCELO", "STFLOW", "STSEI", "ISEI", "STKSM", "VKSM", "SEUR", "SGBP", "SAUD", "SJPY", "SCHF", "SXAU", "SXAG"}
NAME_WRAP_PATS = ["wrapped ", "staked ", "restaked ", "liquid staked", "liquid staking", "bridged ", "bridged-", "binance-pegged", "coinbase wrapped", "huobi btc", "universal btc", "universal eth", "solvbtc", "pumpbtc", "lombard staked", "lista staked", "marinade staked", "jito staked", "blazestake", "sanctum infinity", "stader ", "rocket pool eth", "frax staked", "stakewise", "treehouse eth", "ankr staked", "ether.fi staked", "renzo restaked", "kelp dao restaked", "mantle staked", "mantle restaked", "lido staked", "lido dao staked", "compound ether", "compound usd", "compound dai", "compound usdt", "compound wrapped", "aave eth", "aave usdc", "aave usdt", "aave dai", "aave wbtc", "aave interest", "venus bnb", "venus usdt", "venus usdc", "venus btc", "venus eth", "jupiter perps lp", "gmx glp", "savings dai", "savings usds", "staked usde", "staked usdt", "staked usdc", "syrup usdc", "syrup usdt", "beacon eth", "wrapped beacon", "ether.fi liquid", "puffer eth", "swell eth", "origin ether", "origin dollar", "benqi liquid", "stride staked", "pstake staked"]
NAME_RWA_PATS = ["tokenized", "tokenised", "pre-ipo stock", "ondo us dollar yield", "ondo short-term", "blackrock usd institutional", "franklin onchain", "pax gold", "tether gold", "kinesis gold", "kinesis silver", "perth mint gold", "digix gold", "cache gold", "matrixdock", "backed ", "xstock", "t-bill", "treasury bill", "u.s. dollar tokenized"]

def is_excluded_pure(c):
    cid = int(c["id"])
    if c["marketCap"] <= 0 or c["price"] <= 0: return "ZERO"
    if cid in ZOMBIE_IDS: return "ZOMBIE"
    if cid in SUBNET_DUALGAS_IDS: return "SUBNET_GAS"
    if cid in KEEP_NATIVE_IDS: return "ILLIQ" if c["volume24h"] < 100_000 else None
    if cid in OLD_EXCL_MAP: return OLD_EXCL_MAP[cid]
    tags = {t.lower() for t in (c.get("tags") or [])}
    su = str(c["symbol"]).upper().strip()
    nl = str(c["name"]).lower().strip()
    if (tags & TOKENIZED_TAGS) or su in EXTRA_RWA or any(p in nl for p in NAME_RWA_PATS): return "RWA"
    if (tags & STABLECOIN_TAGS) or su in EXTRA_STAB or "stablecoin" in nl or "synthetic dollar" in nl or (re.match(r"^(usd|eur)[a-z0-9]{1,4}$", su.lower()) and 0.92 <= c["price"] <= 1.15): return "STABLE"
    if (tags & WRAPPED_LST_TAGS) or su in EXTRA_WRAP or any(p in nl for p in NAME_WRAP_PATS): return "WRAP_LST"
    if "bittensor-subnets" in tags or ("subnet" in nl and "bittensor" in nl): return "SUBNET_GAS"
    if c["volume24h"] < 100_000: return "ILLIQ"
    return None

COHORTS_15 = {}
for dt in DATE_ISOS[:12]:
    COHORTS_15[dt] = [int(x) for x in st2["cohort_ids_by_date"][dt]]
COHORTS_15["2026-07-01"] = [int(r["cmc_id"]) for r in old_clean500]
for dt in ("2026-10-01", "2026-11-21"):
    ranked = sorted([c for c in SNAPS[dt].values() if c["marketCap"] > 0 and c["price"] > 0], key=lambda x: x["marketCap"], reverse=True)
    pure = []
    for c in ranked:
        if not is_excluded_pure(c):
            pure.append(c["id"])
            if len(pure) == 500:
                break
    assert len(pure) == 500, f"Only {len(pure)} pure on {dt}"
    COHORTS_15[dt] = pure

# Clean-rank lookup per date for ALL 15 dates
CLEAN_RANK = {dt: {cid: i + 1 for i, cid in enumerate(cids)} for dt, cids in COHORTS_15.items()}

# --- 3. HELPER FUNCTIONS: WALLET DECOMP, POINT-IN-TIME UNLOCKS, HOLDERS, CONCENTRATION & PRICING ---
BURN_ADDRS = {"0x0000000000000000000000000000000000000000", "0x000000000000000000000000000000000000dead", "0x0000000000000000000000000000000000000001"}
CEX_KWS = ("binance", "coinbase", "okx", "upbit", "bybit", "kraken", "kucoin", "robinhood", "bitfinex", "gate", "htx", "huobi", "crypto.com", "bithumb", "bitget", "mexc", "gemini", "bitstamp", "poloniex", "korbit", "coinone", "deribit", "bingx", "whitebit", "hot wallet", "cold wallet", "exchange", "wintermute", "jump", "cumberland")
PROTO_KWS = ("staking", "stake", "vault", "treasury", "vesting", "timelock", "bridge", "pool", "uniswap", "pancake", "curve", "aave", "compound", "lido", "beacon", "escrow", "foundation", "dao", "multisig", "safe", "gnosis", "lock", "distributor", "router", "proxy", "contract", "genesis", "reserve", "ecosystem", "migrator", "wormhole", "layerzero", "portal", "arbitrum", "optimism", "polygon", "base")

# Build global address -> label lookup from DAPI wallets (554 new + Jul 1!) so Archive EVM wallets get rich labels!
DAPI_ADDR_LABELS = {}
for scid, dv in dapi_15.items():
    for w in (dv.get("wallets") or []):
        a = (w.get("address") or "").lower().strip()
        lb = (w.get("label") or "").strip()
        if a and lb:
            DAPI_ADDR_LABELS[(scid, a)] = lb

def classify_wallets_decomp(scid, wallets, has_contract_meta=False):
    burn = cex = proto = eoa = 0.0
    any_labeled = has_contract_meta
    for w in wallets[:10]:
        pct = float(w.get("pct") or 0)
        addr = (w.get("address") or "").lower().strip()
        lbl = (w.get("label") or DAPI_ADDR_LABELS.get((scid, addr)) or "").lower()
        if lbl or w.get("is_contract") or w.get("is_locked"):
            any_labeled = True
        if addr in BURN_ADDRS or any(k in lbl for k in ("burn", "dead", "null", "black hole")):
            burn += pct
        elif any(k in lbl for k in CEX_KWS):
            cex += pct
        elif w.get("is_contract") or w.get("is_locked") or any(k in lbl for k in PROTO_KWS):
            proto += pct
        else:
            eoa += pct
    if not any_labeled:
        return round(burn, 2) if burn > 0 else None, None, None, None
    return round(burn, 2), round(cex, 2), round(proto, 2), round(eoa, 2)

# Build CoinMetrics symbol->record map (preventing symbol collisions: prefer highest Jul1/D01/D08 ranked native coin)
CM_BY_SYM = {}
for a_sym, rec in cm_15.items():
    CM_BY_SYM[a_sym.lower()] = rec

# Identify primary cmc_id per symbol across our union (highest peak mcap!) so CoinMetrics never attaches to a namesake scam token!
PEAK_MCAP_BY_CID = {}
SYM_BY_CID = {}
for dt in DATE_ISOS:
    for cid, c in SNAPS[dt].items():
        if cid in old_stor3 or any(cid in COHORTS_15[d] for d in DATE_ISOS):
            SYM_BY_CID[cid] = str(c["symbol"]).upper()
            if c["marketCap"] > PEAK_MCAP_BY_CID.get(cid, 0):
                PEAK_MCAP_BY_CID[cid] = c["marketCap"]

PRIMARY_CID_FOR_SYM = {}
for cid, sym in SYM_BY_CID.items():
    sl = sym.lower()
    if sl not in PRIMARY_CID_FOR_SYM or PEAK_MCAP_BY_CID.get(cid, 0) > PEAK_MCAP_BY_CID.get(PRIMARY_CID_FOR_SYM[sl], 0):
        PRIMARY_CID_FOR_SYM[sl] = cid
# Explicit canonical overrides for POL/MATIC and ETH/BTC/etc.
PRIMARY_CID_FOR_SYM["matic"] = 3890
PRIMARY_CID_FOR_SYM["pol"] = 28321
PRIMARY_CID_FOR_SYM["uni"] = 7083
PRIMARY_CID_FOR_SYM["link"] = 1975

CC_BY_SYM = {}
for code_cc, rec in cc_15.items():
    sym_cc = str(rec.get("symbol") or "").upper()
    if sym_cc:
        CC_BY_SYM[sym_cc] = rec

def get_point_in_time_unlock(cid, dt, snap_row):
    scid = str(cid)
    circ = float(snap_row.get("circulatingSupply") or 0)
    tot = float(snap_row.get("totalSupply") or 0)
    mx = snap_row.get("maxSupply")
    det = all_details.get(scid) or {}
    is_inf = bool(det.get("isInfiniteMaxSupply"))
    base_sup = float(mx) if (mx and float(mx) > 0 and not is_inf) else (tot if tot > 0 else circ)

    # Priority 1: Official CMC Historical Vesting Curve
    ul = unlocks_15.get(scid)
    if ul and dt in (ul.get("dates") or {}):
        u_val = float(ul["dates"][dt]["unlocked"] or 0)
        if u_val > 0 and base_sup > 0:
            denom = max(base_sup, u_val, circ)
            u_pct = round(min(100.0, u_val / denom * 100.0), 2)
            rem = max(0.0, denom - u_val)
            rem_pct = round(max(0.0, 100.0 - u_pct), 2)
            return round(u_val, 2), u_pct, round(rem, 2), rem_pct, "CMC_Official_Vesting_Curve"

    # Priority 2: Point-in-time Capped vs Uncapped supply ratio (ZERO look-ahead!)
    if mx and float(mx) > 0 and not is_inf:
        denom = max(float(mx), circ)
        u_val = min(circ, denom) if circ > 0 else tot
        u_pct = round(min(100.0, u_val / denom * 100.0), 2) if denom > 0 else None
        rem = max(0.0, denom - u_val)
        rem_pct = round(max(0.0, 100.0 - u_pct), 2) if u_pct is not None else None
        return round(u_val, 2), u_pct, round(rem, 2), rem_pct, "Fixed_Cap_Supply_Ratio"
    elif tot > 0 and circ > 0:
        denom = max(tot, circ)
        u_pct = round(min(100.0, circ / denom * 100.0), 2)
        rem = max(0.0, denom - circ)
        rem_pct = round(max(0.0, 100.0 - u_pct), 2)
        return round(circ, 2), u_pct, round(rem, 2), rem_pct, "Uncapped_Circ_vs_Total"
    return None, None, None, None, "Supply_ND"

def get_point_in_time_holders_and_conc(cid, dt, snap_row):
    scid = str(cid)
    sym = str(snap_row.get("symbol") or "").upper()
    sym_l = sym.lower()

    # For D13..D15 on verified Jul 1 500 coins, start with exact already-audited 3-date fields!
    if cid in old_stor3 and dt in ("2026-07-01", "2026-10-01", "2026-11-21"):
        s3 = old_stor3[cid]
        suf = {"2026-07-01": "jul1", "2026-10-01": "oct1", "2026-11-21": "nov21"}[dt]
        return (
            s3.get(f"holders_cnt_hist_{suf}"),
            s3.get(f"top10_hist_{suf}_pct"),
            s3.get(f"dist_out_top10_hist_{suf}_pct"),
            s3.get(f"eoa_whale_hist_{suf}_pct"),
            s3.get(f"proto_contract_hist_{suf}_pct"),
            s3.get(f"cex_hist_{suf}_pct"),
            s3.get(f"burn_hist_{suf}_pct"),
            s3.get("hist_holders_source") or "N/D",
            s3.get("top10_ref_nov24_pct"),
        )

    # --- Historical Holder Count (Point-in-Time) ---
    h_cnt = None
    h_cnt_src = None
    # 1. CoinMetrics (ALL 15 dates back to 2022-12-30!)
    cm_key = "matic" if cid == 28321 else sym_l
    if cm_key in CM_BY_SYM and (PRIMARY_CID_FOR_SYM.get(sym_l) == cid or cid in (3890, 28321)):
        c_pt = CM_BY_SYM[cm_key].get(dt)
        if isinstance(c_pt, dict) and c_pt.get("holders_cnt"):
            h_cnt = int(c_pt["holders_cnt"])
            h_cnt_src = "CoinMetrics_v4"
    # 2. CoinCarp Daily History (D09..D15)
    if h_cnt is None and sym in CC_BY_SYM and PRIMARY_CID_FOR_SYM.get(sym_l) == cid:
        cc_pt = (CC_BY_SYM[sym].get("dates") or {}).get(dt)
        if cc_pt and (cc_pt.get("holders") or cc_pt.get("holders_cnt")):
            h_cnt = int(cc_pt.get("holders") or cc_pt.get("holders_cnt"))
            h_cnt_src = "CoinCarp_His"
    # 3. CMC DAPI Historical Holder Counts (D09..D15, verified primary supply_ratio >= 0.45!)
    dv = dapi_15.get(scid) or {}
    sr = dv.get("supply_ratio")
    dapi_primary_ok = (sr is None or float(sr) >= 0.45)
    if h_cnt is None and dapi_primary_ok:
        dp = (dv.get("hist_counts") or {}).get(dt)
        if dp and dp.get("holders_cnt"):
            h_cnt = int(dp["holders_cnt"])
            h_cnt_src = "CMC_DAPI_1y"

    # --- Historical Concentration (Point-in-Time: ZERO Look-Ahead!) ---
    t10 = dist = eoa = proto = cex = burn = None
    conc_src = None

    # 1. Cryptographic EVM Archive RPC Multicall3 (ALL 15 dates!)
    if dt in ("2026-07-01", "2026-10-01", "2026-11-21"):
        ev_tok = (old_evm3.get("tokens") or {}).get(scid)
        dkey = {"2026-07-01": "jul1", "2026-10-01": "oct1", "2026-11-21": "nov21"}[dt]
        ev_rec = (ev_tok or {}).get(dkey)
    else:
        ev_tok = (evm_12.get("tokens") or {}).get(scid)
        ev_rec = (ev_tok or {}).get("dates", {}).get(dt)

    if ev_tok and ev_rec and ev_rec.get("status") == "OK":
        if scid == "1027":  # Native ETH via Multicall3.getEthBalance / circulatingSupply!
            circ = float(snap_row.get("circulatingSupply") or 120_000_000)
            ws = []
            for w in (ev_rec.get("wallets") or []):
                pct = round(min(100.0, float(w["balance_eth"]) / circ * 100.0), 4)
                ws.append({"address": w["address"], "pct": pct, "label": w.get("label"), "is_contract": w.get("is_contract"), "is_locked": w.get("is_locked")})
            ws.sort(key=lambda x: x["pct"], reverse=True)
            t10 = round(min(100.0, sum(x["pct"] for x in ws[:10])), 2)
            dist = round(max(0.0, 100.0 - t10), 2)
            burn, cex, proto, eoa = classify_wallets_decomp(scid, ws[:10], has_contract_meta=True)
            conc_src = f"ArchiveRPC_ETH_blk{ev_rec['block']}"
        else:
            t10 = round(float(ev_rec["top10_pct"]), 2)
            dist = round(max(0.0, 100.0 - t10), 2)
            ws = ev_rec.get("top10_wallets") or []
            has_meta = (cid in old_stor3)
            burn, cex, proto, eoa = classify_wallets_decomp(scid, ws, has_contract_meta=has_meta)
            conc_src = f"ArchiveRPC_{ev_tok['chain']}"

    # 2. CoinCarp Daily Historical Richlists (D09..D15 for BTC, XRP, DOGE, TRX, LTC, DOT, ETC, XTZ)
    if t10 is None and sym in CC_BY_SYM and PRIMARY_CID_FOR_SYM.get(sym_l) == cid:
        cc_pt = (CC_BY_SYM[sym].get("dates") or {}).get(dt)
        cc_t10 = cc_pt.get("top10") if cc_pt and cc_pt.get("top10") is not None else (cc_pt.get("top10_pct") if cc_pt else None)
        if cc_t10 is not None:
            t10 = round(float(cc_t10), 2)
            dist = round(max(0.0, 100.0 - t10), 2)
            conc_src = "CoinCarp_His_Richlist"

    # Reference Current Top 10 % (Nov 2026) — kept strictly separate from historical columns!
    ref_t10 = None
    if cid in old_audit and old_audit[cid].get("top10_holders_pct") is not None:
        ref_t10 = round(float(old_audit[cid]["top10_holders_pct"]), 2)
    elif dapi_primary_ok and dv.get("top10_pct") is not None:
        ref_t10 = round(float(dv["top10_pct"]), 2)
    else:
        dh = (all_details.get(scid) or {}).get("holders") or {}
        if dh.get("topTenHolderRatio") is not None:
            ref_t10 = round(float(dh["topTenHolderRatio"]), 2)

    srcs = [s for s in (conc_src, h_cnt_src) if s]
    src_str = " + ".join(srcs) if srcs else "Non disponibile storicamente (API/RPC)"
    return h_cnt, t10, dist, eoa, proto, cex, burn, src_str, ref_t10

def resolve_exit_price_usd(cid, target_dt):
    """Returns (price_usd, status_tag) at target_dt, seamlessly resolving verified official token migrations!"""
    s_t = SNAPS[target_dt]
    if cid in s_t and s_t[cid]["price"] > 0:
        return s_t[cid]["price"], "ACTIVE"
    if cid in OFFICIAL_MIGRATIONS:
        new_cid, new_sym, ratio, note = OFFICIAL_MIGRATIONS[cid]
        if new_cid in s_t and s_t[new_cid]["price"] > 0:
            return s_t[new_cid]["price"] * ratio, f"MIGRATED->{new_sym}"
    return 0.0, "DELISTED_0EUR"

# --- 4. BUILD ALL 15 VISTA A COHORTS (7,500 ROWS) + 12 INDIVIDUAL COHORT CSVs ---
print("=== [2/6] BUILDING VISTA A (15x500 = 7,500 ROWS) + 12 PER-DATE 500-COIN COHORT CSVs ===")
vistaA_rows = []
vistaA_by_date = {}

for di, (code, dt, it_lbl, utc_lbl) in enumerate(ALL_15_DATES):
    fx_d = FX[dt]
    next_dt = DATE_ISOS[di + 1] if di + 1 < len(ALL_15_DATES) else None
    cids = COHORTS_15[dt]
    rows_d = []
    for rk, cid in enumerate(cids, 1):
        c = SNAPS[dt][cid]
        p_usd = float(c["price"])
        p_eur = p_usd / fx_d
        mcap = float(c["marketCap"])
        vol = float(c["volume24h"])
        circ = float(c["circulatingSupply"])
        tot = float(c["totalSupply"])
        mx = c["maxSupply"]
        det = all_details.get(str(cid)) or {}
        fdv_sup = float(mx) if (mx and float(mx) > 0 and not det.get("isInfiniteMaxSupply")) else (tot if tot > 0 else circ)
        fdv = p_usd * fdv_sup if fdv_sup > 0 else mcap
        fdv_mcap = round(fdv / mcap, 3) if mcap > 0 else None
        vol_mcap = round(vol / mcap * 100.0, 2) if mcap > 0 else None

        u_tok, u_pct, rem_tok, rem_pct, u_meth = get_point_in_time_unlock(cid, dt, c)
        h_cnt, t10, dist, eoa, proto, cex, burn, h_src, ref_t10 = get_point_in_time_holders_and_conc(cid, dt, c)

        # Forward returns (Next Checkpoint, Cycle Peak D08 if di<7, D14 Oct 1, D15 Nov 21)
        def fwd_metrics(exit_dt):
            if not exit_dt or exit_dt <= dt:
                return None, None, None, None
            pe_usd, st_tag = resolve_exit_price_usd(cid, exit_dt)
            if pe_usd <= 0:
                return 0.0, -100.0, -100.0, st_tag
            pe_eur = pe_usd / FX[exit_dt]
            val5 = round(5.0 * (pe_eur / p_eur), 4)
            ret_eur = round((pe_eur / p_eur - 1.0) * 100.0, 2)
            ret_usd = round((pe_usd / p_usd - 1.0) * 100.0, 2)
            return val5, ret_eur, ret_usd, st_tag

        v5_nxt, r_nxt_eur, r_nxt_usd, st_nxt = fwd_metrics(next_dt)
        v5_d08, r_d08_eur, _, _ = fwd_metrics("2025-10-07") if dt < "2025-10-07" else (None, None, None, None)
        v5_d14, r_d14_eur, _, st_d14 = fwd_metrics("2026-10-01") if dt < "2026-10-01" else (None, None, None, None)
        v5_d15, r_d15_eur, _, st_d15 = fwd_metrics("2026-11-21") if dt < "2026-11-21" else (None, None, None, None)

        row = {
            "date_code": code, "date_iso": dt, "date_it": it_lbl, "fx_eur_usd": round(fx_d, 6),
            "rank_clean": rk, "cmc_rank": c["cmcRank"], "cmc_id": cid,
            "name": c["name"], "symbol": c["symbol"], "category": det.get("category") or "",
            "price_usd": p_usd, "price_eur": round(p_eur, 10) if p_eur < 0.01 else round(p_eur, 6),
            "mcap_usd": round(mcap, 2), "fdv_usd": round(fdv, 2), "fdv_to_mcap": fdv_mcap,
            "vol24h_usd": round(vol, 2), "vol_to_mcap_pct": vol_mcap, "num_pairs": c["numMarketPairs"],
            "circ_supply": round(circ, 4), "total_supply": round(tot, 4), "max_supply": round(float(mx), 4) if mx else "",
            "unlocked_tokens": u_tok, "unlocked_pct": u_pct, "to_unlock_tokens": rem_tok, "to_unlock_pct": rem_pct,
            "unlock_method": u_meth,
            "holders_cnt_hist": h_cnt, "top10_hist_pct": t10, "dist_out_top10_hist_pct": dist,
            "eoa_whale_hist_pct": eoa, "proto_contract_hist_pct": proto, "cex_hist_pct": cex, "burn_hist_pct": burn,
            "hist_holders_source": h_src, "top10_ref_nov24_pct": ref_t10,
            "next_date_code": CODE_BY_ISO[next_dt] if next_dt else "",
            "eur5_at_next": v5_nxt, "ret_eur_to_next_pct": r_nxt_eur, "ret_usd_to_next_pct": r_nxt_usd, "status_at_next": st_nxt or "",
            "eur5_at_d08_peak": v5_d08, "ret_eur_to_d08_pct": r_d08_eur,
            "eur5_at_d14_oct1": v5_d14, "ret_eur_to_d14_pct": r_d14_eur, "status_at_d14": st_d14 or "",
            "eur5_at_d15_nov21": v5_d15, "ret_eur_to_d15_pct": r_d15_eur, "status_at_d15": st_d15 or "",
        }
        rows_d.append(row)
        vistaA_rows.append(row)
    vistaA_by_date[dt] = rows_d

    # Write individual 500-coin cohort CSV for all 12 new dates (D01..D12)!
    if di < 12:
        cpath = BASE / f"coorte_pure500_{code}_{dt}.csv"
        with open(cpath, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_d[0].keys()))
            w.writeheader()
            w.writerows(rows_d)

# Write Vista A Master 7,500-row Long Panel CSV
va_panel_path = BASE / "panel_vistaA_15coorti_7500_righe.csv"
with open(va_panel_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(vistaA_rows[0].keys()))
    w.writeheader()
    w.writerows(vistaA_rows)
print(f"  Saved 12 per-date cohort CSVs + Vista A Master Long Panel ({len(vistaA_rows)} rows) -> {va_panel_path.name}")

# --- 5. BUILD VISTA B (FIXED JUL 1 2026 500 COINS TRACKED ACROSS ALL 15 DATES = 7,500 ROWS + 500-ROW WIDE MASTER!) ---
print("=== [3/6] BUILDING VISTA B (FIXED JUL 1 500 COINS x 15 DATES = 7,500 LONG ROWS + 500 WIDE ROWS) ===")
vistaB_long = []
vistaB_wide = []

for r500 in old_clean500:
    cid = int(r500["cmc_id"])
    fid = r500["forensic_id"]
    rk_jul1 = int(r500["rank_clean_jul1"])
    s3 = old_stor3[cid]
    aud = old_audit[cid]
    wide_row = {
        "forensic_id": fid, "rank_clean_jul1": rk_jul1, "cmc_rank_jul1": int(r500["cmc_rank_jul1"]),
        "cmc_id": cid, "name": r500["name"], "symbol": r500["symbol"], "category": s3.get("category") or "",
        "first_seen_15dates": "", "n_dates_listed": 0,
        "ret_first_to_nov21_eur_pct": None,
        "ret_jul1_to_oct1_eur_pct": round((float(s3["ticket_5eur_oct1_eur"]) / 5.0 - 1.0) * 100.0, 2) if s3.get("ticket_5eur_oct1_eur") is not None else None,
        "ret_jul1_to_nov21_eur_pct": round((float(s3["ticket_5eur_nov21_eur"]) / 5.0 - 1.0) * 100.0, 2) if s3.get("ticket_5eur_nov21_eur") is not None else None,
        "top10_ref_nov24_pct": s3.get("top10_ref_nov24_pct"),
        "reliability_grade_nov24": s3.get("reliability_grade_nov24"),
    }
    first_p_eur = None
    last_p_eur = None
    listed_cnt = 0

    for code, dt, it_lbl, utc_lbl in ALL_15_DATES:
        fx_d = FX[dt]
        c = SNAPS[dt].get(cid)
        # Check reverse migration for POL (28321) <- MATIC (3890), S (32684) <- FTM (3513), SKY (33038) <- MKR (1518), etc.!
        via_predecessor = None
        if (not c or c["price"] <= 0) and dt < "2026-07-01":
            for old_id, (new_id, _, ratio, note) in OFFICIAL_MIGRATIONS.items():
                if new_id == cid and old_id in SNAPS[dt] and SNAPS[dt][old_id]["price"] > 0:
                    c_old = SNAPS[dt][old_id]
                    c = dict(c_old)
                    c["price"] = c_old["price"] / ratio
                    c["circulatingSupply"] = c_old["circulatingSupply"] * ratio
                    c["totalSupply"] = c_old["totalSupply"] * ratio
                    if c_old.get("maxSupply"):
                        c["maxSupply"] = c_old["maxSupply"] * ratio
                    via_predecessor = note
                    break

        if c and c["price"] > 0:
            listed_cnt += 1
            p_usd = float(c["price"])
            p_eur = p_usd / fx_d
            if first_p_eur is None:
                first_p_eur = p_eur
                wide_row["first_seen_15dates"] = f"{code} ({dt})"
            last_p_eur = p_eur
            rk_c = CLEAN_RANK[dt].get(cid)
            u_tok, u_pct, rem_tok, rem_pct, u_meth = get_point_in_time_unlock(cid, dt, c)
            h_cnt, t10, dist, eoa, proto, cex, burn, h_src, ref_t10 = get_point_in_time_holders_and_conc(cid, dt, c)
            st_lbl = f"PREDECESSORE ({via_predecessor})" if via_predecessor else "QUOTATA"
            vistaB_long.append({
                "forensic_id": fid, "rank_clean_jul1": rk_jul1, "cmc_id": cid, "name": r500["name"], "symbol": r500["symbol"],
                "date_code": code, "date_iso": dt, "fx_eur_usd": round(fx_d, 6), "status": st_lbl,
                "rank_clean_at_date": rk_c if rk_c else "", "cmc_rank_at_date": c["cmcRank"],
                "price_usd": p_usd, "price_eur": round(p_eur, 10) if p_eur < 0.01 else round(p_eur, 6),
                "mcap_usd": round(float(c["marketCap"]), 2), "vol24h_usd": round(float(c["volume24h"]), 2),
                "circ_supply": round(float(c["circulatingSupply"]), 4),
                "unlocked_pct": u_pct, "to_unlock_pct": rem_pct, "unlock_method": u_meth,
                "holders_cnt_hist": h_cnt, "top10_hist_pct": t10, "eoa_whale_hist_pct": eoa,
                "hist_holders_source": h_src,
            })
            cl = code.lower()
            wide_row[f"p_usd_{cl}"] = p_usd
            wide_row[f"p_eur_{cl}"] = round(p_eur, 10) if p_eur < 0.01 else round(p_eur, 6)
            wide_row[f"mcap_{cl}"] = round(float(c["marketCap"]), 2)
            wide_row[f"cmc_rk_{cl}"] = c["cmcRank"]
            wide_row[f"clean_rk_{cl}"] = rk_c if rk_c else ""
            wide_row[f"unlk_pct_{cl}"] = u_pct
            wide_row[f"hcnt_{cl}"] = h_cnt
            wide_row[f"t10_{cl}"] = t10
        else:
            st_lbl = "Non ancora quotata" if dt < "2026-07-01" else "DELISTED"
            vistaB_long.append({
                "forensic_id": fid, "rank_clean_jul1": rk_jul1, "cmc_id": cid, "name": r500["name"], "symbol": r500["symbol"],
                "date_code": code, "date_iso": dt, "fx_eur_usd": round(fx_d, 6), "status": st_lbl,
                "rank_clean_at_date": "", "cmc_rank_at_date": "", "price_usd": "", "price_eur": "",
                "mcap_usd": "", "vol24h_usd": "", "circ_supply": "",
                "unlocked_pct": "", "to_unlock_pct": "", "unlock_method": "",
                "holders_cnt_hist": "", "top10_hist_pct": "", "eoa_whale_hist_pct": "", "hist_holders_source": "",
            })
            cl = code.lower()
            for pref in ("p_usd_", "p_eur_", "mcap_", "cmc_rk_", "clean_rk_", "unlk_pct_", "hcnt_", "t10_"):
                wide_row[f"{pref}{cl}"] = ""

    wide_row["n_dates_listed"] = listed_cnt
    if first_p_eur and last_p_eur and first_p_eur > 0:
        wide_row["ret_first_to_nov21_eur_pct"] = round((last_p_eur / first_p_eur - 1.0) * 100.0, 2)
    vistaB_wide.append(wide_row)

vb_long_path = BASE / "panel_vistaB_jul1_500_su_15date_7500_righe.csv"
with open(vb_long_path, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(vistaB_long[0].keys()))
    w.writeheader()
    w.writerows(vistaB_long)

vb_wide_csv = BASE / "storico_15date_vistaB_500_crypto.csv"
with open(vb_wide_csv, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(vistaB_wide[0].keys()))
    w.writeheader()
    w.writerows(vistaB_wide)

vb_wide_json = BASE / "storico_15date_vistaB_500_crypto.json"
vb_wide_json.write_text(json.dumps({
    "metadata": {
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "total_coins": len(vistaB_wide),
        "dates": [{"code": c, "iso": d, "it": it, "fx_eur_usd": FX[d]} for c, d, it, _ in ALL_15_DATES],
    },
    "cryptocurrencies": vistaB_wide,
}, ensure_ascii=False), encoding="utf-8")
print(f"  Saved Vista B Long ({len(vistaB_long)} rows) + Wide CSV/JSON ({len(vistaB_wide)} coins)!")

# --- 6. ZERO-SURVIVORSHIP-BIAS BACKTESTS: FULL 14x15 MATRIX + TRANCHES 50..500 + FACTOR ANALYTICS ---
print("=== [4/6] COMPUTING FULL 14x15 ZERO-SURVIVORSHIP-BIAS BACKTESTS (5 EUR + TRANCHES 50..500 + FACTORS) ===")

def backtest_slice(entry_dt, exit_dt, rank_lo=1, rank_hi=500):
    """Computes exact 5 EUR/coin backtest on Vista A cohort at entry_dt [rank_lo..rank_hi] held to exit_dt."""
    rows = vistaA_by_date[entry_dt][rank_lo - 1:rank_hi]
    n = len(rows)
    cap_in = 5.0 * n
    fx_in = FX[entry_dt]
    fx_out = FX[exit_dt]
    val_cons = 0.0
    val_act_sum = 0.0
    n_active = n_migrated = n_delisted = 0
    rets_cons = []
    winners = 0
    best_c = None
    worst_c = None
    for r in rows:
        p_in_usd = r["price_usd"]
        p_in_eur = p_in_usd / fx_in
        p_out_usd, st = resolve_exit_price_usd(r["cmc_id"], exit_dt)
        if p_out_usd > 0:
            p_out_eur = p_out_usd / fx_out
            v5 = 5.0 * (p_out_eur / p_in_eur)
            ret_pct = (p_out_eur / p_in_eur - 1.0) * 100.0
            val_cons += v5
            val_act_sum += v5
            if st == "ACTIVE":
                n_active += 1
            else:
                n_migrated += 1
            if ret_pct > 0:
                winners += 1
            rets_cons.append(ret_pct)
            if best_c is None or ret_pct > best_c[1]:
                best_c = (f"{r['symbol']} (#{r['rank_clean']})", round(ret_pct, 2), round(v5, 2))
            if worst_c is None or ret_pct < worst_c[1]:
                worst_c = (f"{r['symbol']} (#{r['rank_clean']})", round(ret_pct, 2), round(v5, 2))
        else:
            n_delisted += 1
            rets_cons.append(-100.0)
            if worst_c is None or -100.0 < worst_c[1]:
                worst_c = (f"{r['symbol']} (#{r['rank_clean']})", -100.0, 0.0)

    n_surv = n_active + n_migrated
    pnl_cons_eur = val_cons - cap_in
    ret_cons_eur_pct = (val_cons / cap_in - 1.0) * 100.0
    ret_cons_usd_pct = ((val_cons * fx_out) / (cap_in * fx_in) - 1.0) * 100.0
    ret_act_eur_pct = (val_act_sum / (5.0 * n_surv) - 1.0) * 100.0 if n_surv > 0 else -100.0
    val_act_norm = cap_in * (1.0 + ret_act_eur_pct / 100.0)
    med_ret = statistics.median(rets_cons) if rets_cons else 0.0

    # BTC Buy-and-Hold Benchmark over exact same (entry_dt -> exit_dt) window in EUR!
    btc_in_eur = SNAPS[entry_dt][1]["price"] / fx_in
    btc_out_eur = SNAPS[exit_dt][1]["price"] / fx_out
    btc_ret_eur_pct = (btc_out_eur / btc_in_eur - 1.0) * 100.0
    btc_val_eur = cap_in * (1.0 + btc_ret_eur_pct / 100.0)

    return {
        "entry_code": CODE_BY_ISO[entry_dt], "entry_date": entry_dt,
        "exit_code": CODE_BY_ISO[exit_dt], "exit_date": exit_dt,
        "slice": f"{rank_lo}-{rank_hi}", "n_coins": n, "invested_eur": round(cap_in, 2),
        "final_eur_cons": round(val_cons, 2), "pnl_eur_cons": round(pnl_cons_eur, 2),
        "ret_eur_cons_pct": round(ret_cons_eur_pct, 2), "ret_usd_cons_pct": round(ret_cons_usd_pct, 2),
        "final_eur_active_norm": round(val_act_norm, 2), "ret_eur_active_pct": round(ret_act_eur_pct, 2),
        "median_ret_eur_pct": round(med_ret, 2), "win_rate_pct": round(winners / n * 100.0, 1),
        "n_active": n_active, "n_migrated": n_migrated, "n_delisted_0eur": n_delisted,
        "btc_bench_ret_eur_pct": round(btc_ret_eur_pct, 2), "btc_bench_final_eur": round(btc_val_eur, 2),
        "alpha_vs_btc_pp": round(ret_cons_eur_pct - btc_ret_eur_pct, 2),
        "best_coin": best_c[0] if best_c else "", "best_ret_pct": best_c[1] if best_c else 0,
    }

# Full 14 x 15 Upper-Triangular Matrix (Top 500 = 2,500 EUR per cohort)
matrix_rows = []
for i in range(14):
    for j in range(i + 1, 15):
        matrix_rows.append(backtest_slice(DATE_ISOS[i], DATE_ISOS[j], 1, 500))

mat_csv = BASE / "backtest_matrice_14x15_5eur.csv"
with open(mat_csv, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(matrix_rows[0].keys()))
    w.writeheader()
    w.writerows(matrix_rows)

# Full Tranches 50..500 (Cumulative 1..K AND Marginal 50-coin bands) for ALL key entry->exit horizons!
tranche_rows = []
KEY_EXITS = ["NEXT", "2025-10-07", "2026-10-01", "2026-11-21"]
for i in range(14):
    e_dt = DATE_ISOS[i]
    seen_pairs = set()
    targets = []
    # Next leg
    targets.append(("NEXT_LEG", DATE_ISOS[i + 1]))
    if e_dt < "2025-10-07":
        targets.append(("TO_D08_PEAK", "2025-10-07"))
    if e_dt < "2026-10-01":
        targets.append(("TO_D14_OCT1", "2026-10-01"))
    if e_dt < "2026-11-21":
        targets.append(("TO_D15_NOV21", "2026-11-21"))
    for horizon_lbl, x_dt in targets:
        # Cumulative 1..50, 1..100, ..., 1..500
        for K in range(50, 501, 50):
            r = backtest_slice(e_dt, x_dt, 1, K)
            r["horizon"] = horizon_lbl
            r["tranche_type"] = "CUMULATIVE"
            r["tranche_k"] = K
            tranche_rows.append(r)
        # Marginal 1-50, 51-100, ..., 451-500
        for lo in range(1, 500, 50):
            r = backtest_slice(e_dt, x_dt, lo, lo + 49)
            r["horizon"] = horizon_lbl
            r["tranche_type"] = "MARGINAL_50"
            r["tranche_k"] = lo + 49
            tranche_rows.append(r)

tr_csv = BASE / "backtest_tranche_50_to_500_tutte_date.csv"
with open(tr_csv, "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(tranche_rows[0].keys()))
    w.writeheader()
    w.writerows(tranche_rows)

# --- 7. 4-YEAR ZERO-LOOK-AHEAD FACTOR BACKTEST (UNLOCK OVERHANG & CRYPTOGRAPHIC TOP10 / EOA WHALE) ---
def compute_factor_buckets(entry_dt, exit_dt):
    rows = vistaA_by_date[entry_dt]
    fx_in, fx_out = FX[entry_dt], FX[exit_dt]
    unlk_b = {"0-10% (Matura)": [], "10-30% (Moderato)": [], "30-60% (Alto)": [], ">60% (Overhang Estremo)": []}
    t10_b = {"<35% (Distribuita)": [], "35-65% (Media)": [], "65-85% (Alta)": [], ">85% (Estrema)": []}
    eoa_b = {"<10% EOA Whale": [], "10-35% EOA Whale": [], ">35% EOA Whale": []}
    for r in rows:
        p_out, _ = resolve_exit_price_usd(r["cmc_id"], exit_dt)
        ret = ((p_out / fx_out) / (r["price_usd"] / fx_in) - 1.0) * 100.0 if p_out > 0 else -100.0
        tu = r["to_unlock_pct"]
        if tu is not None:
            if tu <= 10: unlk_b["0-10% (Matura)"].append(ret)
            elif tu <= 30: unlk_b["10-30% (Moderato)"].append(ret)
            elif tu <= 60: unlk_b["30-60% (Alto)"].append(ret)
            else: unlk_b[">60% (Overhang Estremo)"].append(ret)
        t10 = r["top10_hist_pct"]
        if t10 is not None:
            if t10 < 35: t10_b["<35% (Distribuita)"].append(ret)
            elif t10 < 65: t10_b["35-65% (Media)"].append(ret)
            elif t10 < 85: t10_b["65-85% (Alta)"].append(ret)
            else: t10_b[">85% (Estrema)"].append(ret)
        eoa = r["eoa_whale_hist_pct"]
        if eoa is not None:
            if eoa < 10: eoa_b["<10% EOA Whale"].append(ret)
            elif eoa < 35: eoa_b["10-35% EOA Whale"].append(ret)
            else: eoa_b[">35% EOA Whale"].append(ret)

    def summarize(bdict):
        out = {}
        for k, vals in bdict.items():
            if vals:
                out[k] = {
                    "n": len(vals),
                    "mean_eur_pct": round(sum(vals) / len(vals), 2),
                    "median_eur_pct": round(statistics.median(vals), 2),
                    "win_rate_pct": round(sum(1 for v in vals if v > 0) / len(vals) * 100.0, 1),
                }
            else:
                out[k] = {"n": 0, "mean_eur_pct": None, "median_eur_pct": None, "win_rate_pct": None}
        return out
    return {"unlock_overhang": summarize(unlk_b), "hist_top10": summarize(t10_b), "hist_eoa_whale": summarize(eoa_b)}

FACTOR_WINDOWS = [
    ("D01_to_D08_BearToPeak", "2022-12-30", "2025-10-07"),
    ("D01_to_D15_Full4YrHold", "2022-12-30", "2026-11-21"),
    ("D02_to_D08_HalvingToPeak", "2024-04-09", "2025-10-07"),
    ("D06_to_D08_Apr25DipToPeak", "2025-04-08", "2025-10-07"),
    ("D08_to_D15_PeakToBearNov26", "2025-10-07", "2026-11-21"),
    ("D12_to_D15_May26ToNov26", "2026-05-12", "2026-11-21"),
]
factor_results = {lbl: compute_factor_buckets(e, x) for lbl, e, x in FACTOR_WINDOWS}

# Macro & Coverage Census across ALL 15 dates
census_15 = []
for code, dt, it_lbl, utc_lbl in ALL_15_DATES:
    rows = vistaA_by_date[dt]
    btc_p = SNAPS[dt][1]["price"]
    eth_p = SNAPS[dt][1027]["price"]
    tot_mc = sum(r["mcap_usd"] for r in rows)
    tot_vol = sum(r["vol24h_usd"] for r in rows)
    c500 = rows[-1]
    n_ul_off = sum(1 for r in rows if r["unlock_method"] == "CMC_Official_Vesting_Curve")
    n_ul_any = sum(1 for r in rows if r["unlocked_pct"] is not None)
    n_hcnt = sum(1 for r in rows if r["holders_cnt_hist"] is not None)
    n_t10h = sum(1 for r in rows if r["top10_hist_pct"] is not None)
    n_eoah = sum(1 for r in rows if r["eoa_whale_hist_pct"] is not None)
    n_ref = sum(1 for r in rows if r["top10_ref_nov24_pct"] is not None)
    # Count how many of the Jul 1 500 Vista B coins were already listed on this date
    n_vb_listed = sum(1 for r in vistaB_wide if r.get(f"p_usd_{code.lower()}") != "")
    census_15.append({
        "code": code, "date": dt, "it_label": it_lbl, "fx_eur_usd": round(FX[dt], 6),
        "btc_usd": round(btc_p, 2), "btc_eur": round(btc_p / FX[dt], 2),
        "eth_usd": round(eth_p, 2), "cohort_mcap_usd_b": round(tot_mc / 1e9, 2),
        "cohort_vol24h_usd_b": round(tot_vol / 1e9, 2),
        "cutoff_rank500_sym": c500["symbol"], "cutoff_rank500_mcap_m": round(c500["mcap_usd"] / 1e6, 2),
        "n_unlock_official_curve": n_ul_off, "n_unlock_total": n_ul_any,
        "n_hist_holders_cnt": n_hcnt, "n_hist_top10_conc": n_t10h, "n_hist_eoa_whale": n_eoah,
        "n_ref_top10_nov24": n_ref, "n_vistaB_already_listed": n_vb_listed,
        "raw_snapshot_total_coins": len(SNAPS[dt]),
    })

bt_summary = {
    "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "dates": ALL_15_DATES,
    "fx_eur_usd": FX,
    "census_15dates": census_15,
    "official_migrations_count": len(OFFICIAL_MIGRATIONS),
    "official_migrations": {str(k): {"to_cid": v[0], "to_sym": v[1], "ratio": v[2], "note": v[3]} for k, v in OFFICIAL_MIGRATIONS.items()},
    "matrix_14x15": matrix_rows,
    "tranches_50_to_500": tranche_rows,
    "factor_backtests": factor_results,
}
(BASE / "backtest_15date_completo.json").write_text(json.dumps(bt_summary, indent=2, ensure_ascii=False), encoding="utf-8")

# Print Rich Console Summary!
print("\n=== [5/6] 15-DATE MACRO & POINT-IN-TIME COVERAGE CENSUS ===")
for c in census_15:
    print(f"  {c['code']} {c['date']} | FX={c['fx_eur_usd']:.4f} | BTC={c['btc_usd']:9,.1f} | MCap={c['cohort_mcap_usd_b']:7.1f}B | #500={c['cutoff_rank500_sym']:7s} ({c['cutoff_rank500_mcap_m']:5.1f}M) | UL_off={c['n_unlock_official_curve']:3d} | H_cnt={c['n_hist_holders_cnt']:3d} | T10_hist={c['n_hist_top10_conc']:3d} | VB_list={c['n_vistaB_already_listed']:3d}/500")

print("\n=== PERIOD-TO-PERIOD CYCLE LEGS (5 EUR x 500 = 2,500 EUR, CONSERVATIVE SURVIVAL-ADJUSTED) ===")
for r in matrix_rows:
    if DATE_CODES.index(r["exit_code"]) == DATE_CODES.index(r["entry_code"]) + 1:
        print(f"  {r['entry_code']}->{r['exit_code']} ({r['entry_date']}->{r['exit_date']}): {r['final_eur_cons']:8,.2f} EUR ({r['ret_eur_cons_pct']:+7.2f}% EUR | BTC={r['btc_bench_ret_eur_pct']:+7.2f}% | Alpha={r['alpha_vs_btc_pp']:+7.2f}pp) | act={r['n_active']} mig={r['n_migrated']} del={r['n_delisted_0eur']}")

print("\n=== EVERY ENTRY DATE HELD TO D15 (21 NOV 2026 05:30 CET) — TOP 500 vs BEST TRANCHE vs BTC ===")
for i in range(14):
    ec = DATE_CODES[i]
    m = next(x for x in matrix_rows if x["entry_code"] == ec and x["exit_code"] == "D15")
    cums = [x for x in tranche_rows if x["entry_code"] == ec and x["horizon"] == "TO_D15_NOV21" and x["tranche_type"] == "CUMULATIVE"]
    best_tr = max(cums, key=lambda x: x["ret_eur_cons_pct"])
    print(f"  {ec} ({m['entry_date']})->D15: Top500={m['final_eur_cons']:8,.2f} EUR ({m['ret_eur_cons_pct']:+7.2f}% cons / {m['ret_eur_active_pct']:+7.2f}% act) | BestTranche=Top {best_tr['tranche_k']:3d} ({best_tr['ret_eur_cons_pct']:+7.2f}%) | BTC={m['btc_bench_ret_eur_pct']:+7.2f}% | del={m['n_delisted_0eur']}")

# --- 8. GENERATE COMPLETE FORENSIC MARKDOWN REPORT (ZERO BARE $, ZERO FORBIDDEN SHORTCUT PHRASES, 500/500 PARITY!) ---
print("\n=== [6/6] GENERATING COMPLETE FORENSIC MARKDOWN REPORT (PROJECT + ARTIFACT) ===")

def fmt_p(v):
    if v == "" or v is None: return "N/Q"
    v = float(v)
    if v >= 1000: return f"{v:,.0f}"
    if v >= 10: return f"{v:,.2f}"
    if v >= 0.1: return f"{v:.4f}"
    if v >= 0.0001: return f"{v:.6f}"
    return f"{v:.3e}"

def fmt_pct(v):
    if v == "" or v is None: return "N/D"
    return f"{float(v):+.2f}%"

def fmt_opt(v, suf=""):
    if v == "" or v is None: return "N/D"
    return f"{v}{suf}"

def flink(path_obj, label=None):
    p = str(path_obj).replace("\\", "/")
    return f"[{label or path_obj.name}](file:///{p})"

lines = []
lines.append("# Dossier Forense Completo Multi-Ciclo 15 Date (30 Dic 2022 - 21 Nov 2026) — Pure Crypto Top 500")
lines.append("")
lines.append("> [!IMPORTANT]")
lines.append("> **Perimetro Completo a Doppia Vista (Zero Survivorship Bias + Coorte Fissa 500):** Questo dossier integra le **12 nuove date storiche** richieste (`D01 2022-12-30` .. `D12 2026-05-12`, allineate uniformemente alle `00:00:00 UTC` = `01:00 CET` invernale / `02:00 CEST` estivo) con le **3 date già validate** (`D13 2026-07-01`, `D14 2026-10-01`, `D15 2026-11-21 05:30 CET`).")
lines.append("> - **Vista A (Zero Survivorship Bias):** 15 coorti Clean Pure Top 500 ricostruite indipendentemente su ogni singola data (`15 x 500 = 7.500` righe nel panel completo e 12 file CSV dedicati per ciascuna nuova data), applicando lo stesso filtro deterministico di purezza (esclusione stablecoin, wrapped/LST/LRT, ricevute DeFi, RWA/ETF/oro tokenizzati, illiquidi con volume 24h inferiore a `100.000 USD`, zombie falliti, dual-gas e subnet Alpha).")
lines.append("> - **Vista B (Storico Coorte Fissa 1° Luglio 2026):** Tutte le **500/500** criptovalute della coorte pura `2026-07-01` tracciate punto-nel-tempo su tutte le 15 date (`500 x 15 = 7.500` righe, marcate `N/Q` prima del lancio).")
lines.append("> - **Risoluzione Migrazioni Ufficiali & Integrità Anti-Look-Ahead:** Nel motore di backtest 2022-2026 sono mappate **24 migrazioni/rebrand ufficiali** con il loro esatto rapporto di conversione (`MATIC->POL 1:1`, `FTM->S 1:1`, `MKR->SKY 1:24.000`, `EOS->A 1:1`, `KLAY->KAIA 1:1`, `LN->KAIA 1:148,08`, `OCEAN/AGIX/CUDOS->FET`, `1000SATS->SATS 1:1.000`, `1MBABYDOGE->BABYDOGE 1:1.000.000`, `MC->BEAM 1:100`, `MPL->SYRUP 1:100`, ecc.), distinguendo con precisione matematica le migrazioni dai veri delisting (`0 EUR / -100%`). Nessun dato on-chain moderno è mai retro-propagato nelle colonne storiche.")
lines.append("")

# Section 1: Links to All Structured Deliverables
lines.append("## 1. Indice Completo dei File Generati e delle 12 Coorti Pure Top 500")
lines.append("")
lines.append(f"- **Dashboard HTML Interattiva Multi-Ciclo (4 Tab):** {flink(BASE / 'dashboard_15date_ciclo_2022_2026.html')}")
lines.append(f"- **Panel Master Vista A (15 coorti indipendenti x 500 = 7.500 righe):** {flink(va_panel_path)}")
lines.append(f"- **Panel Master Vista B Lungo (500 coin `2026-07-01` x 15 date = 7.500 righe):** {flink(vb_long_path)}")
lines.append(f"- **Master Vista B Tabella Larga 500/500 (CSV & JSON):** {flink(vb_wide_csv)} | {flink(vb_wide_json)}")
lines.append(f"- **Backtest Matrice Completa `14x15` (`5 EUR/coin`, 105 finestre):** {flink(mat_csv)}")
lines.append(f"- **Backtest Tranche `50..500` Cumulative & Marginali (Tutte le Date):** {flink(tr_csv)}")
lines.append(f"- **JSON Master Backtest & Fattori On-Chain 4 Anni:** {flink(BASE / 'backtest_15date_completo.json')}")
lines.append("")
lines.append("### File CSV Individuali delle 12 Nuove Coorti Pure Top 500 (500 righe ciascuno, 6.000 righe totali)")
lines.append("")
lines.append("| Codice | Data (Ora Italiana) | File CSV Coorte Pure Top 500 (500 coin) | Escluse sopra #500 | Cutoff #500 | MCap Coorte (Mld USD) |")
lines.append("|---|---|---|---|---|---:|")
for di in range(12):
    c = census_15[di]
    dt = c["date"]
    ex_n = st2["excl_summary"][dt]["excluded_above_cutoff"]
    fp = BASE / f"coorte_pure500_{c['code']}_{dt}.csv"
    lines.append(f"| **{c['code']}** | {c['it_label']} | {flink(fp)} | {ex_n} | `{c['cutoff_rank500_sym']}` ({c['cutoff_rank500_mcap_m']:.2f}M USD) | {c['cohort_mcap_usd_b']:,.2f} |")
lines.append("")

# Section 2: 15-Date Macro Arc & Point-in-Time Coverage Audit
lines.append("## 2. Censimento Macro e Copertura Point-in-Time sulle 15 Date (2022-2026)")
lines.append("")
lines.append("| Cod | Data (IT) | FX EUR/USD | BTC (USD) | BTC (EUR) | ETH (USD) | MCap Pure500 (Mld USD) | Vol 24h (Mld USD) | Cutoff #500 (M USD) | Unlocks Curva CMC | Unlocks Coperti | Holders Storici | Top10 On-Chain Storici | EOA Whale Storici | Vista B Quotate |")
lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for c in census_15:
    lines.append(
        f"| **{c['code']}** | {c['it_label']} | {c['fx_eur_usd']:.4f} | {c['btc_usd']:,.2f} | {c['btc_eur']:,.2f} | "
        f"{c['eth_usd']:,.2f} | {c['cohort_mcap_usd_b']:,.2f} | {c['cohort_vol24h_usd_b']:,.2f} | "
        f"`{c['cutoff_rank500_sym']}` {c['cutoff_rank500_mcap_m']:.2f}M | {c['n_unlock_official_curve']}/500 | "
        f"{c['n_unlock_total']}/500 | {c['n_hist_holders_cnt']}/500 | {c['n_hist_top10_conc']}/500 | "
        f"{c['n_hist_eoa_whale']}/500 | {c['n_vistaB_already_listed']}/500 |"
    )
lines.append("")

# Section 3: Period-to-Period Cycle Legs (D01->D02 .. D14->D15)
lines.append("## 3. Rendimenti Fase-per-Fase (Tratte Sequentiali `Di -> Di+1`, 5 EUR x 500 = 2.500 EUR)")
lines.append("")
lines.append("| Tratta | Finestra Temporale | Finale Cons. (EUR) | P&L EUR Cons. | Rend. Cons. EUR | Rend. USD | Rend. Attive-Only | Mediana Coin | Win Rate | BTC Benchmark EUR | Alpha vs BTC | Attive / Mig. / Delist | Miglior Coin della Tratta |")
lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|")
for r in matrix_rows:
    if DATE_CODES.index(r["exit_code"]) == DATE_CODES.index(r["entry_code"]) + 1:
        lines.append(
            f"| **{r['entry_code']} -> {r['exit_code']}** | {r['entry_date']} -> {r['exit_date']} | {r['final_eur_cons']:,.2f} | "
            f"{r['pnl_eur_cons']:+,.2f} | **{r['ret_eur_cons_pct']:+.2f}%** | {r['ret_usd_cons_pct']:+.2f}% | "
            f"{r['ret_eur_active_pct']:+.2f}% | {r['median_ret_eur_pct']:+.2f}% | {r['win_rate_pct']:.1f}% | "
            f"{r['btc_bench_ret_eur_pct']:+.2f}% | {r['alpha_vs_btc_pp']:+.2f} pp | "
            f"{r['n_active']} / {r['n_migrated']} / {r['n_delisted_0eur']} | `{r['best_coin']}` ({r['best_ret_pct']:+.1f}%) |"
        )
lines.append("")

# Section 4: Full 14x15 Upper-Triangular Return Matrix (EUR Conservative Survival-Adjusted %)
lines.append("## 4. Matrice Completa `14 x 15` dei Rendimenti EUR (5 EUR x 500 = 2.500 EUR, Zero Survivorship Bias)")
lines.append("")
lines.append("Ogni cella mostra il rendimento percentuale totale in **EUR** (conservativo: delisting/scomparsa = `0 EUR / -100%`, migrazioni ufficiali convertite al tasso reale) investendo `2.500 EUR` nella coorte Pure Top 500 della data di riga (`Entry`) e liquidando alla data di colonna (`Exit`).")
lines.append("")
mat_lookup = {(r["entry_code"], r["exit_code"]): r for r in matrix_rows}
hdr_cols = DATE_CODES[1:]
lines.append("| Entry \\ Exit | " + " | ".join(hdr_cols) + " |")
lines.append("|---|" + "|".join(["---:"] * len(hdr_cols)) + "|")
for i in range(14):
    ec = DATE_CODES[i]
    cells = []
    for xc in hdr_cols:
        r = mat_lookup.get((ec, xc))
        if r is None:
            cells.append("-")
        else:
            val_s = f"**{r['ret_eur_cons_pct']:+.1f}%**" if r["ret_eur_cons_pct"] >= 50 or r["ret_eur_cons_pct"] <= -50 else f"{r['ret_eur_cons_pct']:+.1f}%"
            cells.append(val_s)
    lines.append(f"| **{ec}** ({DATE_ISOS[i]}) | " + " | ".join(cells) + " |")
lines.append("")

# Section 4B: Summary Table of Every Entry Date Held to D08 Peak, D14 Oct 1, and D15 Nov 21
lines.append("### Riepilogo Investimento `2.500 EUR` per Ogni Data di Ingresso fino al Picco `D08`, al `1 Ott 2026 (D14)` e al `21 Nov 2026 (D15)`")
lines.append("")
lines.append("| Ingresso | Finale al Picco `D08` (EUR / %) | Finale al `1 Ott 2026` (EUR / %) | Finale al `21 Nov 2026` (EUR / %) | Attive-Only `21 Nov` | Delist `21 Nov` | BTC Bench `21 Nov` | Miglior Tranche `50..500` (`21 Nov`) |")
lines.append("|---|---:|---:|---:|---:|---:|---:|---|")
for i in range(14):
    ec = DATE_CODES[i]
    ed = DATE_ISOS[i]
    m08 = mat_lookup.get((ec, "D08"))
    m14 = mat_lookup.get((ec, "D14"))
    m15 = mat_lookup.get((ec, "D15"))
    cums = [x for x in tranche_rows if x["entry_code"] == ec and x["horizon"] == "TO_D15_NOV21" and x["tranche_type"] == "CUMULATIVE"]
    btr = max(cums, key=lambda x: x["ret_eur_cons_pct"])
    s08 = f"{m08['final_eur_cons']:,.0f} EUR ({m08['ret_eur_cons_pct']:+.1f}%)" if m08 else "-"
    s14 = f"{m14['final_eur_cons']:,.0f} EUR ({m14['ret_eur_cons_pct']:+.1f}%)" if m14 else "-"
    s15 = f"{m15['final_eur_cons']:,.0f} EUR ({m15['ret_eur_cons_pct']:+.1f}%)"
    lines.append(
        f"| **{ec}** ({ed}) | {s08} | {s14} | **{s15}** | {m15['ret_eur_active_pct']:+.1f}% | "
        f"{m15['n_delisted_0eur']}/500 | {m15['btc_bench_ret_eur_pct']:+.1f}% | **Top {btr['tranche_k']}** ({btr['ret_eur_cons_pct']:+.2f}%) |"
    )
lines.append("")

# Section 5: Complete Tranches 50..500 Cumulative Comparison Across ALL Entry Dates (Exit D15 + Exit D08 Peak!)
lines.append("## 5. Analisi Completa delle Tranche Cumulative (`Top 50` .. `Top 500`) su Tutte le Date")
lines.append("")
lines.append("### 5A. Tranche Cumulative `Top 50..500` tenute fino al `21 Nov 2026 05:30 CET (D15)` (Rend. EUR Conservativo %)")
lines.append("")
lines.append("> [!WARNING]")
lines.append("> **Nota Forense sull'Outlier `DHN` (`Dohrnii`, ID `20279`):** Nelle coorti `D08..D13` (`07 Ott 2025` .. `01 Lug 2026`), la vittoria delle tranche intermedie (`Top 250`, `Top 300`, `Top 450`) rispetto a `Top 50` è interamente guidata dal singolo micro-cap outlier `DHN` (`+8.207%` .. `+13.148%`, ovvero `5 EUR -> 415..662 EUR` su un singolo ticket). Escludendo `DHN`, il rendimento di `D08..D13` scende di `-16` .. `-26` punti percentuali e la fascia large-cap **`Top 50` / `Top 100`** torna sistematicamente superiore anche nel 2026, confermando la regolarità strutturale vista su tutto il ciclo `D01..D07` (2022–2025).")
lines.append("")
ks = list(range(50, 501, 50))
lines.append("| Ingresso -> D15 | " + " | ".join(f"Top {k}" for k in ks) + " | Vincitore | BTC EUR |")
lines.append("|---|" + "|".join(["---:"] * len(ks)) + "|---|---:|")
for i in range(14):
    ec = DATE_CODES[i]
    cums = {x["tranche_k"]: x for x in tranche_rows if x["entry_code"] == ec and x["horizon"] == "TO_D15_NOV21" and x["tranche_type"] == "CUMULATIVE"}
    best_k = max(ks, key=lambda k: cums[k]["ret_eur_cons_pct"])
    row_s = []
    for k in ks:
        v = cums[k]["ret_eur_cons_pct"]
        row_s.append(f"**{v:+.1f}%**" if k == best_k else f"{v:+.1f}%")
    btc_r = cums[500]["btc_bench_ret_eur_pct"]
    lines.append(f"| **{ec}** ({DATE_ISOS[i]}) | " + " | ".join(row_s) + f" | **Top {best_k}** | {btc_r:+.1f}% |")
lines.append("")

lines.append("### 5B. Tranche Cumulative `Top 50..500` nei Cicli Bull fino al Picco `D08 (07 Ott 2025)` (Rend. EUR Conservativo %)")
lines.append("")
lines.append("| Ingresso -> D08 Peak | " + " | ".join(f"Top {k}" for k in ks) + " | Vincitore | BTC EUR |")
lines.append("|---|" + "|".join(["---:"] * len(ks)) + "|---|---:|")
for i in range(7):
    ec = DATE_CODES[i]
    cums = {x["tranche_k"]: x for x in tranche_rows if x["entry_code"] == ec and x["horizon"] == "TO_D08_PEAK" and x["tranche_type"] == "CUMULATIVE"}
    best_k = max(ks, key=lambda k: cums[k]["ret_eur_cons_pct"])
    row_s = [f"**{cums[k]['ret_eur_cons_pct']:+.1f}%**" if k == best_k else f"{cums[k]['ret_eur_cons_pct']:+.1f}%" for k in ks]
    btc_r = cums[500]["btc_bench_ret_eur_pct"]
    lines.append(f"| **{ec}** ({DATE_ISOS[i]}) | " + " | ".join(row_s) + f" | **Top {best_k}** | {btc_r:+.1f}% |")
lines.append("")

lines.append("### 5C. Fasce Marginali da 50 Coin (`1-50` .. `451-500`) tenute fino al `21 Nov 2026 (D15)` (Rend. EUR Conservativo %)")
lines.append("")
bands = [(lo, lo + 49) for lo in range(1, 500, 50)]
lines.append("| Ingresso -> D15 | " + " | ".join(f"{lo}-{hi}" for lo, hi in bands) + " | Fascia Migliore |")
lines.append("|---|" + "|".join(["---:"] * len(bands)) + "|---|")
for i in range(14):
    ec = DATE_CODES[i]
    margs = {x["slice"]: x for x in tranche_rows if x["entry_code"] == ec and x["horizon"] == "TO_D15_NOV21" and x["tranche_type"] == "MARGINAL_50"}
    best_b = max(margs.keys(), key=lambda s: margs[s]["ret_eur_cons_pct"])
    row_s = [f"**{margs[f'{lo}-{hi}']['ret_eur_cons_pct']:+.1f}%**" if f"{lo}-{hi}" == best_b else f"{margs[f'{lo}-{hi}']['ret_eur_cons_pct']:+.1f}%" for lo, hi in bands]
    lines.append(f"| **{ec}** ({DATE_ISOS[i]}) | " + " | ".join(row_s) + f" | **{best_b}** |")
lines.append("")

# Section 6: 4-Year Zero-Look-Ahead Factor Analytics (Unlocks & On-Chain Concentration)
lines.append("## 6. Verifica Empirica Multi-Ciclo dei Fattori Point-in-Time (Unlocks & Concentrazione On-Chain)")
lines.append("")
lines.append("Tutti i bucket sono calcolati rigorosamente con i valori **noti alla data di ingresso** (`zero look-ahead`), utilizzando le curve storiche ufficiali CMC e gli stati crittografici ricostruiti via `EVM Archive RPC Multicall3` (Ethereum, Base, Arbitrum, Optimism) + `CoinCarp` + `CoinMetrics`.")
lines.append("")
for lbl, e_dt, x_dt in FACTOR_WINDOWS:
    fb = factor_results[lbl]
    lines.append(f"### Finestra `{lbl}` ({e_dt} -> {x_dt})")
    lines.append("")
    lines.append("| Fattore Point-in-Time all'Ingresso | Fascia | Coin (N) | Media EUR % | Mediana EUR % | Win Rate % |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for fn, ftitle in [("unlock_overhang", "Token da Sbloccare (%)"), ("hist_top10", "Top-10 On-Chain Storica (%)"), ("hist_eoa_whale", "EOA Whale Residua Storica (%)")]:
        for bname, bval in fb[fn].items():
            if bval["n"] > 0:
                lines.append(f"| {ftitle} | {bname} | {bval['n']} | {bval['mean_eur_pct']:+.2f}% | {bval['median_eur_pct']:+.2f}% | {bval['win_rate_pct']:.1f}% |")
    lines.append("")

# Section 7: Complete 500/500 Vista B Table Across ALL 15 Dates (100% Parity!)
lines.append("## 7. Vista B — Censimento Integrale 500/500 della Coorte Fissa `1° Luglio 2026` sulle 15 Date (2022-2026)")
lines.append("")
lines.append("La tabella seguente elenca **tutte e 500/500 le criptovalute** della coorte pura `2026-07-01` (nessuna omissione), riportando per ciascuna la prima data di quotazione rilevata, il numero di checkpoint coperti (`su 15`), i prezzi esatti in USD sulle principali tappe storiche (`D01` .. `D15`), il rendimento totale EUR dalla prima data disponibile al `21 Nov 2026` e i parametri storici di riferimento. Il tracciamento completo colonna-per-colonna di tutte le 15 date (`128` colonne) è disponibile in " + flink(vb_wide_csv) + " e nel panel da 7.500 righe " + flink(vb_long_path) + ".")
lines.append("")
lines.append("| ID Forense | Rank Lug1 | CMC Lug1 | Nome | Ticker | Prima Data | Date/15 | P USD D01 (Dic22) | P USD D02 (Apr24) | P USD D04 (Nov24) | P USD D06 (Apr25) | P USD D08 (Ott25) | P USD D10 (Gen26) | P USD D12 (Mag26) | P USD D13 (Lug26) | P USD D14 (Ott26) | P USD D15 (Nov26) | Rend. EUR 1a->D15 | Rend. EUR Lug->Nov21 | Top10 Ref % |")
lines.append("|---|---:|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
for r in vistaB_wide:
    nm_clean = str(r["name"]).replace("|", "/")
    lines.append(
        f"| `{r['forensic_id']}` | {r['rank_clean_jul1']} | {r['cmc_rank_jul1']} | {nm_clean} | `{r['symbol']}` | "
        f"{r['first_seen_15dates']} | {r['n_dates_listed']}/15 | "
        f"{fmt_p(r['p_usd_d01'])} | {fmt_p(r['p_usd_d02'])} | {fmt_p(r['p_usd_d04'])} | {fmt_p(r['p_usd_d06'])} | "
        f"{fmt_p(r['p_usd_d08'])} | {fmt_p(r['p_usd_d10'])} | {fmt_p(r['p_usd_d12'])} | {fmt_p(r['p_usd_d13'])} | "
        f"{fmt_p(r['p_usd_d14'])} | {fmt_p(r['p_usd_d15'])} | "
        f"{fmt_pct(r['ret_first_to_nov21_eur_pct'])} | {fmt_pct(r['ret_jul1_to_nov21_eur_pct'])} | "
        f"{fmt_opt(r['top10_ref_nov24_pct'], '%')} |"
    )
lines.append("")

md_text = "\n".join(lines)
# Guard: verify ZERO bare '$' characters anywhere in the report!
assert "$" not in md_text, "Bare $ detected in Markdown report!"

rep_proj = BASE / "report_15date_2022_2026_completo.md"
rep_proj.write_text(md_text, encoding="utf-8")
print(f"Saved Forensic Markdown Report ({len(lines)} lines, {len(md_text):,} chars) -> {rep_proj}")
print("=== STAGE 5 COMPLETE! ===")
