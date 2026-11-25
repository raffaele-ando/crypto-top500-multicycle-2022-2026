#!/usr/bin/env python3
"""10-second exact binary search fix for Base archive blocks (jul1 & oct1) + Multicall3 for all Base tokens."""
import datetime, json, os, urllib.request
from concurrent.futures import ThreadPoolExecutor

PROJ_DIR = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
RAW_DIR = os.path.join(PROJ_DIR, "raw")
OUT_PATH = os.path.join(RAW_DIR, "evm_archive_holders_3dates.json")
MULTICALL3 = "0xcA11bde05977b3631167028862bE2a173976CA11"
BASE_RPC = "https://mainnet.base.org"
HDR = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 Chrome/130.0.0.0"}

TS = {
    "jul1":  int(datetime.datetime(2026, 7, 1, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()),
    "oct1":  int(datetime.datetime(2026, 10, 1, 23, 59, 59, tzinfo=datetime.timezone.utc).timestamp()),
    "nov21": int(datetime.datetime(2026, 11, 21, 4, 30, 0, tzinfo=datetime.timezone.utc).timestamp()),
}

def rpc(payload):
    req = urllib.request.Request(BASE_RPC, data=json.dumps(payload).encode(), headers=HDR)
    with urllib.request.urlopen(req, timeout=16) as r:
        return json.loads(r.read().decode())

def bsearch_block(target_ts, lo, hi):
    while hi - lo > 4:
        mid = (lo + hi) // 2
        t = int(rpc({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(mid), False]})["result"]["timestamp"], 16)
        if t <= target_ts:
            lo = mid
        else:
            hi = mid
    t_lo = int(rpc({"jsonrpc":"2.0","id":1,"method":"eth_getBlockByNumber","params":[hex(lo), False]})["result"]["timestamp"], 16)
    return lo, t_lo

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

latest = int(rpc({"jsonrpc":"2.0","id":1,"method":"eth_blockNumber","params":[]})["result"], 16)
bj, tj = bsearch_block(TS["jul1"], 1, latest)
bo, to = bsearch_block(TS["oct1"], bj, latest)
bn, tn = bsearch_block(TS["nov21"], bo, latest)
print(f"Base EXACT blocks: jul1={bj} (dt={tj-TS['jul1']:+d}s) | oct1={bo} (dt={to-TS['oct1']:+d}s) | nov21={bn} (dt={tn-TS['nov21']:+d}s)")

out = json.load(open(OUT_PATH, encoding="utf-8"))
out["meta_chains"]["Base"] = {"rpc": BASE_RPC, "blocks": {"jul1": bj, "oct1": bo, "nov21": bn}}

clean500 = json.load(open(os.path.join(PROJ_DIR, "clean500_crypto_2026-07-01_vs_2026-10-01.json"), encoding="utf-8"))["cryptocurrencies"]
details = json.load(open(os.path.join(RAW_DIR, "cmc_tokenomics_holders_clean500.json"), encoding="utf-8"))
wd_p2 = json.load(open(os.path.join(RAW_DIR, "wallet_decomp_part2.json"), encoding="utf-8"))

base_targets = []
for r in clean500:
    cid = str(r["cmc_id"])
    wrec = wd_p2.get(cid)
    if not wrec or wrec.get("chain") != "Base":
        continue
    d = details[cid]
    addr = next((p["address"].strip() for p in (d.get("platforms") or []) if p.get("platform") == "Base" and p.get("address")), None)
    if not addr:
        continue
    wlist = [w for w in (wrec.get("wallets") or []) if (w.get("address") or "").startswith("0x") and len(w["address"]) == 42]
    if len(wlist) >= 5:
        base_targets.append((r, addr, wlist[:25]))

print(f"Reconstructing {len(base_targets)} Base tokens with exact blocks...")
ok = 0
for r, tok_addr, wlist in base_targets:
    cid = str(r["cmc_id"])
    calls = [(tok_addr, bytes.fromhex("18160ddd"))] + [(tok_addr, bytes.fromhex("70a08231" + w["address"][2:].lower().zfill(64))) for w in wlist]
    cdata = encode_try_aggregate(calls)
    tres = {"symbol": r["symbol"], "chain": "Base", "contract": tok_addr, "n_tracked_wallets": len(wlist)}
    for dkey, blk in [("jul1", bj), ("oct1", bo), ("nov21", bn)]:
        try:
            res = rpc({"jsonrpc":"2.0","id":1,"method":"eth_call","params":[{"to":MULTICALL3,"data":cdata}, hex(blk)]})
            dec = decode_try_aggregate(res["result"])
            if not dec[0][0] or len(dec[0][1]) < 32:
                tres[dkey] = {"status": "NOT_DEPLOYED_OR_MIGRATED"}
                continue
            ts_int = int.from_bytes(dec[0][1][-32:], "big")
            if ts_int <= 0:
                tres[dkey] = {"status": "ZERO_SUPPLY"}
                continue
            w_out = []
            for wi, w in enumerate(wlist, 1):
                bint = int.from_bytes(dec[wi][1][-32:], "big") if (dec[wi][0] and len(dec[wi][1]) >= 32) else 0
                w_out.append({"address": w["address"], "pct": round(min(100.0, bint / ts_int * 100.0), 4), "label": w.get("label"), "is_contract": bool(w.get("is_contract")), "is_locked": bool(w.get("is_locked"))})
            w_out.sort(key=lambda x: x["pct"], reverse=True)
            tres[dkey] = {"status": "OK", "block": blk, "total_supply_raw": str(ts_int), "top10_pct": round(min(100.0, sum(x["pct"] for x in w_out[:10])), 2), "top10_wallets": w_out[:10]}
        except Exception as e:
            tres[dkey] = {"status": "ERR", "err": str(e)[:60]}
    out["tokens"][cid] = tres
    ok += 1
    print(f"  Base OK: {r['symbol']:8s} | jul1={tres['jul1'].get('top10_pct')}% | oct1={tres['oct1'].get('top10_pct')}% | nov21={tres['nov21'].get('top10_pct')}%")

with open(OUT_PATH, "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"Base done ({ok} tokens)! Total Archive EVM assets now: {len(out['tokens'])}")
