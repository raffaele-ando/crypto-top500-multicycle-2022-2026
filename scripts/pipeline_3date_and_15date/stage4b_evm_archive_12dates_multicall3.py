#!/usr/bin/env python3
"""
STAGE 4B: Cryptographic Point-in-Time EVM Archive RPC Multicall3 Reconstruction Across ALL 12 New Dates
(D01 2022-12-30 00:00:00 UTC .. D12 2026-05-12 00:00:00 UTC)!
Reconstructs exact on-chain totalSupply() + Top-25 balanceOf(addr) on:
  - Ethereum (https://eth.drpc.org) -> D01..D12
  - Optimism (https://mainnet.optimism.io) -> D01..D12
  - Avalanche C-Chain (https://avalanche.drpc.org) -> D01..D12
  - Arbitrum (https://arb-pokt.nodies.app) -> D01..D12
  - Base (https://mainnet.base.org) -> D02..D12 (launched Aug 2023)
  + Native ETH Top-15 balances via Multicall3.getEthBalance across D01..D12!

Saves to multidate_15_2022_2026/raw/evm_archive_12dates_holders.json.
"""
import datetime, json, time, urllib.request
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ = Path(r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026")
BASE = PROJ / "multidate_15_2022_2026"
RAW = BASE / "raw"
OUT_PATH = RAW / "evm_archive_12dates_holders.json"
MULTICALL3 = "0xcA11bde05977b3631167028862bE2a173976CA11"

HDR = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
}

NEW_12_DATES = [
    ("D01", "2022-12-30"), ("D02", "2024-04-09"), ("D03", "2024-09-10"), ("D04", "2024-11-22"),
    ("D05", "2025-01-24"), ("D06", "2025-04-08"), ("D07", "2025-09-19"), ("D08", "2025-10-07"),
    ("D09", "2025-12-26"), ("D10", "2026-01-15"), ("D11", "2026-02-13"), ("D12", "2026-05-12"),
]
TS_MAP = {
    dt: int(datetime.datetime.fromisoformat(dt + "T00:00:00+00:00").timestamp())
    for _, dt in NEW_12_DATES
}

CHAINS = {
    "Ethereum":          {"rpc": "https://eth.drpc.org",           "llama": "ethereum", "min_date": "2022-12-30"},
    "Optimism":          {"rpc": "https://mainnet.optimism.io",    "llama": "optimism", "min_date": "2022-12-30"},
    "Avalanche C-Chain": {"rpc": "https://avalanche.drpc.org",     "llama": "avax",     "min_date": "2022-12-30"},
    "Arbitrum":          {"rpc": "https://arb-pokt.nodies.app",    "llama": "arbitrum", "min_date": "2022-12-30"},
    "Base":              {"rpc": "https://mainnet.base.org",       "llama": "base",     "min_date": "2024-04-09"},
}

def rpc(url, payload, retries=3, timeout=16):
    last_err = None
    for att in range(retries):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.loads(r.read().decode("utf-8"))
            if isinstance(res, dict) and res.get("error"):
                last_err = RuntimeError(str(res["error"]))
                time.sleep(0.45 * (att + 1))
                continue
            return res
        except Exception as e:
            last_err = e
            time.sleep(0.55 * (att + 1))
    raise last_err

def u256(n): return n.to_bytes(32, "big")

def encode_try_aggregate(calls):
    tuples = []
    for target, cdata in calls:
        addr_b = bytes.fromhex(target[2:].lower().zfill(64))
        pad_len = ((len(cdata) + 31) // 32) * 32
        tuples.append(addr_b + u256(64) + u256(len(cdata)) + cdata + b"\x00" * (pad_len - len(cdata)))
    n = len(tuples)
    offsets, cur = [], n * 32
    for t in tuples:
        offsets.append(u256(cur)); cur += len(t)
    return "0x" + (bytes.fromhex("bce38bd7") + u256(0) + u256(64) + u256(n) + b"".join(offsets) + b"".join(tuples)).hex()

def decode_try_aggregate(hex_res):
    raw = bytes.fromhex(hex_res[2:])
    arr_off = int.from_bytes(raw[0:32], "big")
    n = int.from_bytes(raw[arr_off:arr_off + 32], "big")
    base = arr_off + 32
    out = []
    for i in range(n):
        rel = int.from_bytes(raw[base + i * 32:base + (i + 1) * 32], "big")
        tpos = base + rel
        succ = int.from_bytes(raw[tpos:tpos + 32], "big") != 0
        b_off = int.from_bytes(raw[tpos + 32:tpos + 64], "big")
        b_pos = tpos + b_off
        b_len = int.from_bytes(raw[b_pos:b_pos + 32], "big")
        out.append((succ, raw[b_pos + 32:b_pos + 32 + b_len]))
    return out

def bsearch_block(url, target_ts, lo, hi):
    while hi - lo > 4:
        mid = (lo + hi) // 2
        blk = rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(mid), False]})["result"]
        t = int(blk["timestamp"], 16)
        if t <= target_ts:
            lo = mid
        else:
            hi = mid
    t_lo = int(rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(lo), False]})["result"]["timestamp"], 16)
    return lo, t_lo

# --- 1. RESOLVE EXACT BLOCKS ACROSS ALL 5 ARCHIVE CHAINS VIA DEFILLAMA (INSTANT ~2s!) ---
print("=== [1/4] RESOLVING EXACT BLOCKS FOR ALL 12 DATES ACROSS 5 ARCHIVE CHAINS (DEFILLAMA) ===")
def resolve_one_block(cname, llama_slug, dt, ts):
    u = f"https://coins.llama.fi/block/{llama_slug}/{ts}"
    for att in range(3):
        try:
            req = urllib.request.Request(u, headers={"User-Agent": HDR["User-Agent"], "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=12) as r:
                j = json.loads(r.read().decode("utf-8"))
            return cname, dt, {"block": int(j["height"]), "ts": int(j["timestamp"]), "delta_s": int(j["timestamp"]) - ts}
        except Exception:
            time.sleep(0.4 * (att + 1))
    return cname, dt, None

block_tasks = []
for cn, cfg in CHAINS.items():
    for _, dt in NEW_12_DATES:
        if dt >= cfg["min_date"]:
            block_tasks.append((cn, cfg["llama"], dt, TS_MAP[dt]))

active_chains = {cn: {"rpc": cfg["rpc"], "blocks": {}} for cn, cfg in CHAINS.items()}
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = [ex.submit(resolve_one_block, *t) for t in block_tasks]
    for f in as_completed(futs):
        cn, dt, val = f.result()
        if val:
            active_chains[cn]["blocks"][dt] = val

# Verify Multicall3 + Archive state at earliest resolved block for each chain
for cn, info in list(active_chains.items()):
    if not info["blocks"]:
        del active_chains[cn]
        continue
    d_first = sorted(info["blocks"].keys())[0]
    d_last = sorted(info["blocks"].keys())[-1]
    fb = info["blocks"][d_first]["block"]
    try:
        mc_code = rpc(info["rpc"], {"jsonrpc": "2.0", "id": 1, "method": "eth_getCode", "params": [MULTICALL3, hex(fb)]}, retries=2, timeout=10)["result"]
        info["mc3_at_first"] = len(mc_code) > 10
        info["archive_at_first"] = True
    except Exception as e:
        info["mc3_at_first"] = False
        info["archive_at_first"] = False
        print(f"  [WARN] {cn} earliest check failed: {str(e)[:60]}")
    print(f"  [READY] {cn:18s} | {len(info['blocks']):2d} dates ({d_first} blk={fb} dt={info['blocks'][d_first]['delta_s']:+d}s .. {d_last} blk={info['blocks'][d_last]['block']}) | mc3={info['mc3_at_first']} | arch={info['archive_at_first']}")

# --- 2. BUILD TARGET LIST (ALL JUL 1 ARCHIVE TOKENS + ALL VERIFIED NEW679 ARCHIVE TOKENS!) ---
print("\n=== [2/4] ASSEMBLING EVM ARCHIVE TARGETS ACROSS THE 1,180-COIN UNION ===")
st2 = json.loads((RAW / "stage2_cohorts_12dates_pre_audit.json").read_text(encoding="utf-8"))
old_clean500 = json.loads((PROJ / "clean500_crypto_2026-07-01_vs_2026-10-01.json").read_text(encoding="utf-8"))["cryptocurrencies"]
old_clean_ids = {str(r["cmc_id"]) for r in old_clean500}
old_details = json.loads((PROJ / "raw" / "cmc_tokenomics_holders_clean500.json").read_text(encoding="utf-8"))
new_details = json.loads((RAW / "new679_cmc_details.json").read_text(encoding="utf-8"))
old_arch3 = json.loads((PROJ / "raw" / "evm_archive_holders_3dates.json").read_text(encoding="utf-8"))
l1_full = json.loads((PROJ / "raw" / "live_l1_wallets_full.json").read_text(encoding="utf-8"))
wd_p1 = json.loads((PROJ / "raw" / "wallet_decomp_part1.json").read_text(encoding="utf-8"))
wd_p2 = json.loads((PROJ / "raw" / "wallet_decomp_part2.json").read_text(encoding="utf-8"))
st1 = json.loads((PROJ / "raw" / "holders_stage1.json").read_text(encoding="utf-8"))

# Map cid -> which of the 12 dates it appears in Vista A!
appear_dates = {}
for dt, cids in st2["cohort_ids_by_date"].items():
    for cid in cids:
        appear_dates.setdefault(str(cid), set()).add(dt)

# Build wallet sources for Jul 1 coins (preserve rich labels + contract/locked flags!)
wallet_src = {}
for cid, val in st1["cmc_verified_primary"].items():
    hl = (old_details.get(cid, {}).get("holders") or {}).get("holderList") or []
    if hl and str(hl[0].get("address", "")).startswith("0x"):
        wallet_src[cid] = {
            "chain": "Ethereum",
            "wallets": [{"address": h["address"], "label": None, "is_contract": False, "is_locked": False} for h in hl[:25]],
        }
for src in (wd_p2, wd_p1, l1_full):
    for cid, val in src.items():
        if cid == "ETH_BLOCKSCOUT_LIVE_AUDIT":
            continue
        ws = val.get("wallets") or []
        if ws and str(ws[0].get("address", "")).startswith("0x"):
            wallet_src[cid] = {"chain": val.get("chain") or "Ethereum", "wallets": ws[:25]}

# Also add all verified-primary EVM coins from new679_cmc_details!
# Verify supply ratio on CMC detail holderList to prevent wrapped/bridged contamination of native L1s!
KEEP_EVM_COINS = {"MATIC", "ARB", "OP", "MNT", "IMX", "STRK", "ZK", "METIS", "BOBA", "ZORA", "KTA", "ZEN", "PROS", "KNTQ"}
for scid, d in new_details.items():
    if scid in wallet_src:
        continue
    hl = (d.get("holders") or {}).get("holderList") or []
    if not hl or not str(hl[0].get("address", "")).startswith("0x"):
        continue
    sym = str(d.get("symbol") or "").upper()
    if d.get("category") == "coin" and sym not in KEEP_EVM_COINS:
        continue
    # Supply parity sanity check: implied total supply from top holder balance/share vs CMC totalSupply
    st = d.get("statistics") or {}
    tot_sup = float(st.get("totalSupply") or st.get("circulatingSupply") or 0)
    h0_bal = float(hl[0].get("balance") or 0)
    h0_sh = float(hl[0].get("share") or 0)
    if tot_sup > 0 and h0_bal > 0 and h0_sh > 0.01:
        imp_sup = h0_bal / (h0_sh / 100.0)
        ratio = imp_sup / tot_sup
        if not (0.20 <= ratio <= 3.0):
            continue
    # Identify chain (CMC detail holderList is Ethereum ERC-20 unless Ethereum platform absent!)
    plats = d.get("platforms") or []
    chosen_chain = None
    for pref in ("Ethereum", "Arbitrum", "Base", "Optimism", "Avalanche C-Chain"):
        if any(p.get("platform") == pref and (p.get("address") or "").strip().startswith("0x") for p in plats):
            chosen_chain = pref
            break
    if not chosen_chain:
        continue
    wallet_src[scid] = {
        "chain": chosen_chain,
        "wallets": [{"address": h["address"], "label": None, "is_contract": False, "is_locked": False} for h in hl[:25]],
    }

all_details = {}
all_details.update(old_details)
all_details.update(new_details)

all_12_list = [dt for _, dt in NEW_12_DATES]
targets = []
for scid, ws_rec in wallet_src.items():
    cname = ws_rec["chain"]
    if cname not in active_chains:
        continue
    d = all_details.get(scid)
    if not d:
        continue
    sym = str(d.get("symbol") or "")
    if d.get("category") == "coin" and sym.upper() not in KEEP_EVM_COINS:
        continue
    addr = next((p["address"].strip() for p in (d.get("platforms") or []) if p.get("platform") == cname and p.get("address") and p["address"].strip().startswith("0x")), None)
    if not addr:
        continue
    seen_a = set()
    wlist = []
    for w in ws_rec["wallets"]:
        a = (w.get("address") or "").strip()
        if a.startswith("0x") and len(a) == 42 and a.lower() not in seen_a:
            seen_a.add(a.lower())
            wlist.append({
                "address": a, "label": w.get("label"),
                "is_contract": bool(w.get("is_contract")), "is_locked": bool(w.get("is_locked")),
            })
    if len(wlist) < 5:
        continue
    # Dates to reconstruct: ALL 12 dates for Jul 1 Vista B coins; active appearance dates for new679 historical coins!
    if scid in old_clean_ids:
        dates_to_run = [dt for dt in all_12_list if dt in active_chains[cname]["blocks"]]
    else:
        dates_to_run = sorted(dt for dt in appear_dates.get(scid, set()) if dt in active_chains[cname]["blocks"])
    if dates_to_run:
        targets.append((scid, sym, cname, addr, wlist[:25], dates_to_run))

tot_calls = sum(len(t[5]) for t in targets)
print(f"  Total Archive EVM targets: {len(targets)} tokens ({sum(1 for t in targets if t[0] in old_clean_ids)} Vista-B full-12d + {sum(1 for t in targets if t[0] not in old_clean_ids)} historical Vista-A) | {tot_calls} Multicall3 RPC calls total!")

# --- 3. EXECUTE MULTICALL3 RECONSTRUCTION ACROSS ALL TARGETS ---
print("\n=== [3/4] RUNNING CRYPTOGRAPHIC MULTICALL3 RECONSTRUCTION (10 threads) ===")
out = {"meta_chains": active_chains, "tokens": {}}
if OUT_PATH.exists():
    try:
        prev = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        out["tokens"] = prev.get("tokens") or {}
    except Exception:
        pass

def process_token(task):
    scid, sym, cname, tok_addr, wlist, dates_to_run = task
    if scid in out["tokens"] and all(dt in out["tokens"][scid].get("dates", {}) for dt in dates_to_run):
        return scid, out["tokens"][scid]
    ch_info = active_chains[cname]
    rpc_u = ch_info["rpc"]
    calls = [(tok_addr, bytes.fromhex("18160ddd"))] + [
        (tok_addr, bytes.fromhex("70a08231" + w["address"][2:].lower().zfill(64))) for w in wlist
    ]
    calldata = encode_try_aggregate(calls)
    res_dates = {}
    ok_n = 0
    for dt in dates_to_run:
        blk = ch_info["blocks"][dt]["block"]
        try:
            res = rpc(rpc_u, {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": MULTICALL3, "data": calldata}, hex(blk)]}, retries=2, timeout=16)
            dec = decode_try_aggregate(res["result"])
            if not dec[0][0] or len(dec[0][1]) < 32:
                res_dates[dt] = {"status": "NOT_DEPLOYED"}
                continue
            ts_int = int.from_bytes(dec[0][1][-32:], "big")
            if ts_int <= 0:
                res_dates[dt] = {"status": "ZERO_SUPPLY"}
                continue
            w_out = []
            for wi, w in enumerate(wlist, 1):
                s_i, d_i = dec[wi]
                bint = int.from_bytes(d_i[-32:], "big") if (s_i and len(d_i) >= 32) else 0
                w_out.append({
                    "address": w["address"],
                    "pct": round(min(100.0, bint / ts_int * 100.0), 4),
                    "label": w["label"],
                    "is_contract": w["is_contract"],
                    "is_locked": w["is_locked"],
                })
            w_out.sort(key=lambda x: x["pct"], reverse=True)
            t10 = round(min(100.0, sum(x["pct"] for x in w_out[:10])), 2)
            res_dates[dt] = {
                "status": "OK", "block": blk, "total_supply_raw": str(ts_int),
                "top10_pct": t10, "top10_wallets": w_out[:10],
            }
            ok_n += 1
        except Exception as e:
            res_dates[dt] = {"status": "ERR", "err": str(e)[:70]}
    return scid, {"symbol": sym, "chain": cname, "contract": tok_addr, "n_tracked": len(wlist), "ok_dates": ok_n, "dates": res_dates}

t0 = time.time()
with ThreadPoolExecutor(max_workers=10) as ex:
    futs = [ex.submit(process_token, t) for t in targets]
    done = 0
    for f in as_completed(futs):
        scid, val = f.result()
        done += 1
        if val["ok_dates"] > 0:
            out["tokens"][scid] = val
        if done % 60 == 0 or done == len(targets):
            OUT_PATH.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
            print(f"  Multicall3 [{done}/{len(targets)}] ok_tokens={len(out['tokens'])} ({time.time()-t0:.1f}s)")

# --- 4. NATIVE ETH TOP-15 BALANCES VIA MULTICALL3.getEthBalance ACROSS ALL 12 NEW DATES ---
if "Ethereum" in active_chains and "ETH_BLOCKSCOUT_LIVE_AUDIT" in l1_full:
    print("\n=== [4/4] RECONSTRUCTING NATIVE ETH TOP-15 BALANCES ACROSS D01..D12 ===")
    eth_w = l1_full["ETH_BLOCKSCOUT_LIVE_AUDIT"].get("top10_wallets") or []
    calls = [(MULTICALL3, bytes.fromhex("4d2301cc" + w["address"][2:].lower().zfill(64))) for w in eth_w]
    cdata = encode_try_aggregate(calls)
    eth_dates = {}
    for code, dt in NEW_12_DATES:
        blk = active_chains["Ethereum"]["blocks"][dt]["block"]
        try:
            res = rpc(active_chains["Ethereum"]["rpc"], {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": MULTICALL3, "data": cdata}, hex(blk)]})
            dec = decode_try_aggregate(res["result"])
            w_out = []
            for wi, w in enumerate(eth_w):
                bal_eth = int.from_bytes(dec[wi][1][-32:], "big") / 1e18 if (dec[wi][0] and len(dec[wi][1]) >= 32) else 0.0
                w_out.append({
                    "address": w["address"], "balance_eth": round(bal_eth, 2),
                    "label": w.get("label"), "is_contract": w.get("is_contract"), "is_locked": w.get("is_locked"),
                })
            eth_dates[dt] = {"status": "OK", "block": blk, "wallets": w_out}
            print(f"  ETH {code} {dt} (blk {blk}): Beacon={w_out[0]['balance_eth']/1e6:.2f}M ETH")
        except Exception as e:
            eth_dates[dt] = {"status": "ERR", "err": str(e)[:70]}
    out["tokens"]["1027"] = {"symbol": "ETH", "chain": "Ethereum", "contract": "NATIVE", "ok_dates": sum(1 for v in eth_dates.values() if v.get("status")=="OK"), "dates": eth_dates}

OUT_PATH.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
# Per-date summary
print(f"\n=== STAGE 4B COMPLETE: {len(out['tokens'])} CRYPTOGRAPHIC EVM ARCHIVE ASSETS RECONSTRUCTED! ===")
for code, dt in NEW_12_DATES:
    n_ok = sum(1 for v in out["tokens"].values() if (v.get("dates", {}).get(dt) or {}).get("status") == "OK")
    print(f"  {code} {dt}: {n_ok} coins with cryptographic on-chain Top-10 concentration!")
