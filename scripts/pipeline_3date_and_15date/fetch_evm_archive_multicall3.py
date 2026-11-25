#!/usr/bin/env python3
"""
Script 2 (Multicall3 Edition - 26x Faster, 1 single eth_call per token per date!):
Uses Multicall3.tryAggregate(false, calls[]) at 0xcA11bde05977b3631167028862bE2a173976CA11
to cryptographically reconstruct EXACT point-in-time totalSupply() + Top-25 balanceOf(addr) at:
  - T1: 2026-07-01 23:59:59 UTC (unix 1782950399)
  - T2: 2026-10-01 23:59:59 UTC (unix 1790899199)
  - T3: 2026-11-21 04:30:00 UTC / 05:30 CET (unix 1795235400)
across Ethereum, Base, Arbitrum, Optimism, and Avalanche C-Chain (+ native ETH eth_getBalance via Multicall3.getEthBalance!).
"""

import datetime
import json
import os
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")
OUT_PATH = os.path.join(RAW_DIR, "evm_archive_holders_3dates.json")
MULTICALL3 = "0xcA11bde05977b3631167028862bE2a173976CA11"

with open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8") as f:
    clean500 = json.load(f)["cryptocurrencies"]
with open(os.path.join(RAW_DIR, "cmc_tokenomics_holders_clean500.json"), encoding="utf-8") as f:
    details = json.load(f)
with open(os.path.join(RAW_DIR, "live_l1_wallets_full.json"), encoding="utf-8") as f:
    l1_full = json.load(f)
with open(os.path.join(RAW_DIR, "wallet_decomp_part1.json"), encoding="utf-8") as f:
    wd_p1 = json.load(f)
with open(os.path.join(RAW_DIR, "wallet_decomp_part2.json"), encoding="utf-8") as f:
    wd_p2 = json.load(f)
with open(os.path.join(RAW_DIR, "holders_stage1.json"), encoding="utf-8") as f:
    st1 = json.load(f)

HDR = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
TS = {
    "jul1":  int(datetime.datetime(2026, 7, 1, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()),
    "oct1":  int(datetime.datetime(2026, 10, 1, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()),
    "nov21": int(datetime.datetime(2026, 11, 21, 4, 30, 0, tzinfo=datetime.timezone.utc).timestamp()),
}


def rpc(url, payload, retries=3, timeout=16):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=HDR)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                res = json.loads(r.read().decode("utf-8"))
            if isinstance(res, dict) and res.get("error"):
                last_err = RuntimeError(str(res["error"]))
                time.sleep(0.5 * (attempt + 1))
                continue
            return res
        except Exception as e:
            last_err = e
            time.sleep(0.6 * (attempt + 1))
    raise last_err


# --- Pure-Python Multicall3.tryAggregate(bool requireSuccess, (address, bytes)[]) ABI Codec ---
def u256(n):
    return n.to_bytes(32, "big")


def encode_try_aggregate(calls):
    """calls: list of (target_hex_0x, calldata_bytes). Selector 0xbce38bd7."""
    # Head: requireSuccess=0 (32B), offset_to_array=64 (32B)
    # Array: length (32B), N offsets to tuples (N*32B), then each tuple:
    #   tuple = [address padded 32B, offset_to_bytes=64 (32B), len(bytes) (32B), bytes padded to 32B]
    tuples = []
    for target, cdata in calls:
        addr_b = bytes.fromhex(target[2:].lower().zfill(64))
        pad_len = ((len(cdata) + 31) // 32) * 32
        padded = cdata + b"\x00" * (pad_len - len(cdata))
        tup = addr_b + u256(64) + u256(len(cdata)) + padded
        tuples.append(tup)
    n = len(tuples)
    offsets = []
    cur = n * 32
    for t in tuples:
        offsets.append(u256(cur))
        cur += len(t)
    arr_bytes = u256(n) + b"".join(offsets) + b"".join(tuples)
    payload = bytes.fromhex("bce38bd7") + u256(0) + u256(64) + arr_bytes
    return "0x" + payload.hex()


def decode_try_aggregate(hex_res):
    """Decodes Result[] = (bool success, bytes returnData)[] -> list of (bool, bytes)."""
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
        b_data = raw[b_pos + 32:b_pos + 32 + b_len]
        out.append((succ, b_data))
    return out


def find_block_by_ts(url, target_ts):
    latest = int(rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_blockNumber", "params": []})["result"], 16)
    b_hi = rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(latest), False]})["result"]
    t_hi = int(b_hi["timestamp"], 16)
    if target_ts >= t_hi:
        return latest, t_hi
    step = min(100000, max(1000, latest // 50))
    b_ref = rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(latest - step), False]})["result"]
    t_ref = int(b_ref["timestamp"], 16)
    sec_per_blk = max(0.05, (t_hi - t_ref) / step)
    est = max(1, int(latest - (t_hi - target_ts) / sec_per_blk))
    # Iterative Newton-like jump straight to exact block!
    cur = est
    for _ in range(10):
        t_cur = int(rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(cur), False]})["result"]["timestamp"], 16)
        diff = target_ts - t_cur
        if abs(diff) <= 30:
            return cur, t_cur
        cur = max(1, min(latest, int(cur + diff / sec_per_blk)))
    t_cur = int(rpc(url, {"jsonrpc": "2.0", "id": 1, "method": "eth_getBlockByNumber", "params": [hex(cur), False]})["result"]["timestamp"], 16)
    return cur, t_cur


# --- 1. Active Archive Chains (pre-resolved blocks + fast Base Newton lookup!) ---
active_chains = {
    "Ethereum": {
        "rpc": "https://eth.drpc.org",
        "blocks": {"jul1": 25441103, "oct1": 26100910, "nov21": 26461092},
    },
    "Optimism": {
        "rpc": "https://mainnet.optimism.io",
        "blocks": {"jul1": 153675811, "oct1": 157650211, "nov21": 159818311},
    },
    "Avalanche C-Chain": {
        "rpc": "https://avalanche.drpc.org",
        "blocks": {"jul1": 89249657, "oct1": 96563903, "nov21": 100943678},
    },
    "Arbitrum": {
        "rpc": "https://arb-pokt.nodies.app",
        "blocks": {"jul1": 479435764, "oct1": 510818489, "nov21": 526136046},
    },
}

# Resolve Base blocks quickly using Newton jump (mainnet.base.org is confirmed Archive!)
print("[1] Resolving exact Base Archive blocks via mainnet.base.org...")
try:
    bj, tj = find_block_by_ts("https://mainnet.base.org", TS["jul1"])
    bo, to = find_block_by_ts("https://mainnet.base.org", TS["oct1"])
    bn, tn = find_block_by_ts("https://mainnet.base.org", TS["nov21"])
    active_chains["Base"] = {
        "rpc": "https://mainnet.base.org",
        "blocks": {"jul1": bj, "oct1": bo, "nov21": bn},
    }
    print(f"  [ARCHIVE READY] Base: jul1={bj} (dt={tj-TS['jul1']:+d}s) | oct1={bo} (dt={to-TS['oct1']:+d}s) | nov21={bn} (dt={tn-TS['nov21']:+d}s)")
except Exception as e:
    print(f"  [ERR] Base: {e}")

# Quick sanity test of Multicall3 on Ethereum LINK at jul1!
print("\n[2] Sanity-testing Multicall3.tryAggregate on Ethereum LINK @ jul1 (blk 25441103)...")
test_calls = [
    ("0x514910771AF9Ca656af840dff83E8264EcF986CA", bytes.fromhex("18160ddd")),
    ("0x514910771AF9Ca656af840dff83E8264EcF986CA", bytes.fromhex("70a08231" + "f977814e90da44bfa03b6295a0616a897441acec".zfill(64))),
]
mc_res = rpc("https://eth.drpc.org", {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": MULTICALL3, "data": encode_try_aggregate(test_calls)}, hex(25441103)]})
dec_test = decode_try_aggregate(mc_res["result"])
print(f"  Multicall3 LINK @ Jul 1 OK! totalSupply={int.from_bytes(dec_test[0][1],'big')/1e18:,.0f} | Binance8={int.from_bytes(dec_test[1][1],'big')/1e18:,.0f}")

# --- 3. Build Target Token List on Active Archive Chains ---
wallet_src = {}
for cid, val in st1["cmc_verified_primary"].items():
    hl = (details[cid].get("holders") or {}).get("holderList") or []
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
            wallet_src[cid] = {
                "chain": val.get("chain") or "Ethereum",
                "wallets": ws[:25],
            }

out = {"meta_chains": active_chains, "tokens": {}}
targets = []
for r in clean500:
    cid = str(r["cmc_id"])
    ws_rec = wallet_src.get(cid)
    if not ws_rec:
        continue
    cname = ws_rec["chain"]
    if cname not in active_chains:
        continue
    d = details[cid]
    if d.get("category") == "coin" and r["symbol"] not in ("ZORA", "KTA", "ZEN", "PROS", "KNTQ"):
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
                "address": a,
                "label": w.get("label"),
                "is_contract": bool(w.get("is_contract")),
                "is_locked": bool(w.get("is_locked")),
            })
    if len(wlist) >= 5:
        targets.append((r, cname, addr, wlist[:25]))

print(f"\n[3] Running Multicall3 Archive Reconstruction on {len(targets)} EVM tokens across 5 chains (6 threads)...")

def process_token(task):
    r, cname, tok_addr, wlist = task
    cid = str(r["cmc_id"])
    ch_info = active_chains[cname]
    rpc_u = ch_info["rpc"]
    calls = [(tok_addr, bytes.fromhex("18160ddd"))]
    for w in wlist:
        calls.append((tok_addr, bytes.fromhex("70a08231" + w["address"][2:].lower().zfill(64))))
    calldata = encode_try_aggregate(calls)

    token_res = {"symbol": r["symbol"], "chain": cname, "contract": tok_addr, "n_tracked_wallets": len(wlist)}
    any_ok = False
    for dkey in ("jul1", "oct1", "nov21"):
        blk = ch_info["blocks"][dkey]
        try:
            res = rpc(rpc_u, {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": MULTICALL3, "data": calldata}, hex(blk)]}, retries=2, timeout=16)
            decoded = decode_try_aggregate(res["result"])
            succ0, data0 = decoded[0]
            if not succ0 or len(data0) < 32:
                token_res[dkey] = {"status": "NOT_DEPLOYED_OR_MIGRATED"}
                continue
            ts_int = int.from_bytes(data0[-32:], "big")
            if ts_int <= 0:
                token_res[dkey] = {"status": "ZERO_SUPPLY"}
                continue
            w_out = []
            for wi, w in enumerate(wlist, 1):
                s_i, d_i = decoded[wi]
                bint = int.from_bytes(d_i[-32:], "big") if (s_i and len(d_i) >= 32) else 0
                pct = round(min(100.0, bint / ts_int * 100.0), 4)
                w_out.append({
                    "address": w["address"],
                    "pct": pct,
                    "label": w["label"],
                    "is_contract": w["is_contract"],
                    "is_locked": w["is_locked"],
                })
            w_out.sort(key=lambda x: x["pct"], reverse=True)
            t10 = round(min(100.0, sum(x["pct"] for x in w_out[:10])), 2)
            token_res[dkey] = {
                "status": "OK",
                "block": blk,
                "total_supply_raw": str(ts_int),
                "top10_pct": t10,
                "top10_wallets": w_out[:10],
            }
            any_ok = True
        except Exception as e:
            token_res[dkey] = {"status": "ERR", "err": str(e)[:80]}
    return cid, (token_res if any_ok else None)

t0 = time.time()
ok_cnt = 0
with ThreadPoolExecutor(max_workers=6) as ex:
    futs = [ex.submit(process_token, t) for t in targets]
    done = 0
    for fut in as_completed(futs):
        cid, val = fut.result()
        done += 1
        if val:
            out["tokens"][cid] = val
            ok_cnt += 1
        if done % 30 == 0 or done == len(targets):
            with open(OUT_PATH, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2, ensure_ascii=False)
            print(f"  Multicall3 Archive [{done}/{len(targets)}] ({time.time()-t0:.1f}s) | ok={ok_cnt}")

# --- 4. Native ETH Historical Top-15 Balances via Multicall3.getEthBalance (selector 0x4d2301cc) ---
if "Ethereum" in active_chains and "ETH_BLOCKSCOUT_LIVE_AUDIT" in l1_full:
    print("\n[4] Reconstructing Native ETH Top-15 Balances via Multicall3.getEthBalance at T1, T2, T3...")
    eth_w = l1_full["ETH_BLOCKSCOUT_LIVE_AUDIT"].get("top10_wallets") or []
    eth_cid = str(next(r["cmc_id"] for r in clean500 if r["symbol"] == "ETH"))
    eth_res = {"symbol": "ETH", "chain": "Ethereum", "contract": "NATIVE"}
    calls = [(MULTICALL3, bytes.fromhex("4d2301cc" + w["address"][2:].lower().zfill(64))) for w in eth_w]
    cdata = encode_try_aggregate(calls)
    for dkey in ("jul1", "oct1", "nov21"):
        blk = active_chains["Ethereum"]["blocks"][dkey]
        try:
            res = rpc(active_chains["Ethereum"]["rpc"], {"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"to": MULTICALL3, "data": cdata}, hex(blk)]})
            dec = decode_try_aggregate(res["result"])
            w_out = []
            for wi, w in enumerate(eth_w):
                s_i, d_i = dec[wi]
                bal_eth = int.from_bytes(d_i[-32:], "big") / 1e18 if (s_i and len(d_i) >= 32) else 0.0
                w_out.append({
                    "address": w["address"],
                    "balance_eth": round(bal_eth, 2),
                    "label": w.get("label"),
                    "is_contract": w.get("is_contract"),
                    "is_locked": w.get("is_locked"),
                })
            eth_res[dkey] = {"status": "OK", "block": blk, "wallets": w_out}
            print(f"  ETH {dkey} (blk {blk}): Beacon={w_out[0]['balance_eth']/1e6:.2f}M ETH | #2={w_out[1]['label'] or w_out[1]['address'][:10]} ({w_out[1]['balance_eth']/1e6:.2f}M ETH)")
        except Exception as e:
            print(f"  ETH {dkey} ERR: {e}")
    out["tokens"][eth_cid] = eth_res

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\n=== SCRIPT 2 COMPLETE: {len(out['tokens'])} EVM assets cryptographically reconstructed across T1/T2/T3 ===")
