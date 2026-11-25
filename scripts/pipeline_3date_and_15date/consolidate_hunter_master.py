import json, re, ssl, urllib.request
from pathlib import Path
from urllib.parse import urlparse

BASE = Path(r'C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026')
RAW = BASE / 'raw'
OUT_PATH = RAW / 'holders_hunter_master_consolidated.json'

audit = json.loads((BASE / 'audit_forense_500_crypto.json').read_text(encoding='utf-8'))['cryptocurrencies']
cmc_det = json.loads((RAW / 'cmc_tokenomics_holders_clean500.json').read_text(encoding='utf-8'))
dapi = json.loads((RAW / 'cmc_dapi_holders_all500.json').read_text(encoding='utf-8'))
cm_3d = json.loads((RAW / 'coinmetrics_3dates.json').read_text(encoding='utf-8'))
CTX = ssl._create_unverified_context()

def load_j(fn):
    p = RAW / fn
    return json.loads(p.read_text(encoding='utf-8')) if p.exists() else {}

# Verify CoinLore text for WAVES, BORA, DYDX (extract exact Top 10 & Top 11-100 & chain!)
cl_extra = {}
for cid, sym, slug in [(1274, 'WAVES', 'waves'), (3801, 'BORA', 'bora'), (28324, 'DYDX', 'dydx')]:
    try:
        html = urllib.request.urlopen(urllib.request.Request(f'https://www.coinlore.com/coin/{slug}', headers={'User-Agent':'Mozilla/5.0'}), context=CTX, timeout=12).read().decode('utf-8','replace')
        txt = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', html))
        idx = txt.lower().find('top 10')
        snip = txt[max(0, idx-80):idx+360] if idx > 0 else ''
        print(f"[CoinLore verify] {sym:6s} -> {snip}")
        m10 = re.search(r'top 10[^%]{0,80}?(\d{1,3}\.\d+)\s*%', snip, re.I)
        m11 = re.search(r'(?:top 11\s*[-–]\s*100|next 90)[^%]{0,80}?(\d{1,3}\.\d+)\s*%', snip, re.I)
        m100 = re.search(r'top 100[^%]{0,80}?(\d{1,3}\.\d+)\s*%', snip, re.I)
        if m10:
            t10 = float(m10.group(1))
            t100 = round(min(100.0, t10 + float(m11.group(1))), 2) if m11 else (float(m100.group(1)) if m100 else None)
            cl_extra[str(cid)] = (t10, t100, snip)
    except Exception as e:
        print(f"[CoinLore err] {sym}: {e}")

# Load all 11 wave files in ascending priority (later overrides earlier!)
wave_order = [
    'holders_hunter_apis.json',         # BB, SOMI, DATA, STRAX, TAC, ZIL, RVN, QUBIC, TIA, HBAR
    'holders_hunter_apis_wave2.json',   # BEAT, SENTIS, ATM, MTL, MEGA, HBAR-full, TIA-fix, XPR, A
    'holders_hunter_apis_wave3.json',   # XEC
    'holders_hunter_apis_wave3b.json',  # GCOIN, MANTRA
    'holders_hunter_apis_wave4.json',   # CFX, SMART, BEAT-OKX, SENTIS-OKX
    'holders_hunter_apis_wave5.json',   # RON, DATA-datanetscan, SMART-100
    'holders_hunter_apis_wave6.json',   # 0G
    'holders_hunter_playwright.json',   # M, DOT, OKB, MON, SEI, XPL, KSM, S, PEAQ, CCD, MINA, POLYX, XVG, CSPR
    'holders_hunter_wave7_final.json',  # XLM-ex-burn, RON-ex-predeploy, CFX-ex-burn, STEEM
    'holders_hunter_wave8.json',        # LBT, FOGO
    'holders_hunter_wave9.json',        # SRX
    'holders_hunter_wave10.json',       # XNO, WAVES/BORA
    'holders_hunter_wave11.json',       # RUNE-labeled
    'holders_hunter_wave12.json',       # TAO-Bittensor, SNEK-AdaStat
]

# Known explicit overrides / corrections / holder counts from verified live logs
KNOWN_COUNTS = {
    '30746': 32001049,   # BB BounceBit Blockscout /stats
    '35626': 18121212,   # DATA Data Network Blockscout /stats
    '30168': 33868,      # STRAX Xertra Blockscout /stats
    '37338': 728017,     # TAC Blockscout /stats
    '2469':  32112832,   # ZIL Zilliqa EVM Blockscout /stats
    '29169': 670543,     # QUBIC Official RPC activeAddresses
}

consolidated = {}

for fn in wave_order:
    d = load_j(fn)
    for cid, v in d.items():
        cid = str(cid)
        sym = v.get('symbol', '')
        src = v.get('source', '')
        # Strict quality filters (prevent bridge/wrong-chain/partial contamination!)
        if cid == '4847' and 'coincarp' in src.lower():
            continue  # Reject CoinCarp 0xa1ad... EVM STX!
        if cid == '4558' and 'Flow EVM' in src and (v.get('top10_pct') or 0) < 10.0:
            continue  # Reject tiny 6.7% Flow EVM subset!
        if cid == '25264' and (v.get('top10_pct') or 0) < 1.0:
            continue  # Reject unpaginated Koios SNEK subset!
        if cid == '20964' and (v.get('top10_pct') or 0) < 1.0:
            continue  # Reject unparsed 0.00% LBT!
        if cid == '28324' and 'coinlore' in src.lower():
            # DYDX on CoinLore is 96.96% -> check if it's ethDYDX migration bridge (90%+ locked in bridge!)
            # Note: ethDYDX 96.96% is dominated by the official Ethereum->dYdX Chain migration bridge; skip as native dYdX Chain!
            continue
        if cid == '39689' and 'PlayBlock Mainnet' in src and (v.get('top10_pct') or 0) < 10.0:
            continue  # Reject native gas PBG 3.69%, keep PlayBlock GCOIN ERC-20 (54.14%)!
        if (v.get('top10_pct') or 0) <= 0:
            continue

        item = dict(v)
        # Clean top100_pct if fewer than 95 wallets AND not an explicit official summary bucket (like XDCScan LBT/SRX or CoinLore)
        ws = item.get('wallets') or []
        is_official_bucket = any(k in src for k in ('XDCScan', 'CoinLore', 'Cryptoscope'))
        if not is_official_bucket and len(ws) < 95:
            item['top100_pct'] = None
        if len(ws) < 50 and not is_official_bucket:
            item['top50_pct'] = None
        if len(ws) < 20 and not is_official_bucket:
            item['top20_pct'] = None

        # Fix CSPR supply-as-count bug
        if cid == '5899' and (item.get('holder_count') or 0) > 1_000_000_000:
            item['holder_count'] = None
        # Fix missing Blockscout counts
        if cid in KNOWN_COUNTS and not item.get('holder_count'):
            item['holder_count'] = KNOWN_COUNTS[cid]
        # Fix holderCount field alias for run_forensic_verification_500.py compatibility!
        item['holderCount'] = item.get('holder_count')
        item['updatedate'] = '2026-11-24'

        # Special TAO normalization on MINED circulatingSupply (~10.6M TAO, NOT 21M unmined max cap!)
        if cid == '22974' and ws:
            circ_tao = float((cmc_det.get('22974') or {}).get('statistics', {}).get('circulatingSupply') or 0)
            if circ_tao > 1e6:
                for w in ws:
                    w['pct'] = round(float(w['balance']) / circ_tao * 100.0, 4)
                ws.sort(key=lambda z: z['pct'], reverse=True)
                item['base_supply'] = circ_tao
                item['top10_pct'] = round(sum(w['pct'] for w in ws[:10]), 2)
                item['top20_pct'] = round(sum(w['pct'] for w in ws[:20]), 2) if len(ws) >= 20 else None
                item['top100_pct'] = None
                item['special_note'] = f"Bittensor.ai native coldkeys (free + staked TAO, esclude subnet pool/treasury; % calcolata su {circ_tao/1e6:.2f}M TAO effettivamente minati)"

        # Special DATA (Story/Data Network) fix: label 0x0000... genesis/cosmos bridge & cap sum<=100%
        if cid == '35626' and ws:
            tot_bal = sum(float(w['balance']) for w in ws)
            denom = max(float(item.get('base_supply') or 0), tot_bal)
            for w in ws:
                if w['address'].lower() == '0x0000000000000000000000000000000000000000':
                    w['label'] = 'Data Network Genesis/Staking Bridge (0x0000)'
                    w['is_contract'] = True
                w['pct'] = round(float(w['balance']) / denom * 100.0, 4)
            ws.sort(key=lambda z: z['pct'], reverse=True)
            item['top10_pct'] = round(min(100.0, sum(w['pct'] for w in ws[:10])), 2)
            item['top20_pct'] = round(min(100.0, sum(w['pct'] for w in ws[:20])), 2) if len(ws) >= 20 else None
            item['top50_pct'] = round(min(100.0, sum(w['pct'] for w in ws[:50])), 2) if len(ws) >= 50 else None
            item['top100_pct'] = round(min(100.0, sum(w['pct'] for w in ws[:100])), 2) if len(ws) >= 95 else None
            item['special_note'] = "Blockscout datanetscan.io nativo (#1 0x0000 e bridge/staking pool Cosmos-EVM, 81%+)"

        # Special CoinLore WAVES / BORA enrichment with exact Top 100 if parsed
        if cid in cl_extra and 'coinlore' in src.lower():
            t10, t100, _ = cl_extra[cid]
            item['top10_pct'] = t10
            if t100: item['top100_pct'] = t100

        # Preserve special_note from note if not set
        if item.get('note') and not item.get('special_note'):
            if any(k in item['note'] for k in ('Excluded', 'Scanned', 'Bittensor')):
                item['special_note'] = item['note']

        consolidated[cid] = item

# Add 3 100%-Native CMC DAPI hits (BTW, ZK, BR) + SOL live Nov 2026 DAPI upgrade!
for cid, sym, chname in [
    ('39158', 'BTW', 'BNB Smart Chain (CMC Native)'),
    ('24091', 'ZK',  'zkSync Era (CMC Native)'),
    ('36063', 'BR',  'BNB Smart Chain (CMC Native)'),
    ('5426',  'SOL', 'Solana Mainnet (CMC Native)'),
]:
    dd = dapi.get(cid) or {}
    hd = dd.get('holder_data') or {}
    hh = dd.get('hist_holders') or {}
    if hd.get('fgp') is not None:
        real_ws = [w for w in (hd.get('wallets') or []) if w.get('platform_id') is not None]
        ws_clean = []
        for w in real_ws:
            ws_clean.append({
                'address': w.get('address') or '',
                'balance': float(w.get('balance') or 0),
                'pct': round(float(w.get('pct') or 0), 4),
                'label': w.get('label') or None,
                'is_contract': False,
                'is_locked': False,
            })
        cnt = hh.get('latest_count')
        st = (cmc_det.get(cid) or {}).get('statistics') or {}
        tot = float(st.get('totalSupply') or st.get('circulatingSupply') or 0)
        consolidated[cid] = {
            'cmc_id': int(cid),
            'symbol': sym,
            'source': 'CoinMarketCap Holders Live DAPI (Nov 2026)',
            'chain': chname,
            'holder_count': int(cnt) if cnt else None,
            'holderCount': int(cnt) if cnt else None,
            'base_supply': tot,
            'top10_pct': round(float(hd['fgp']), 2),
            'top20_pct': None,
            'top50_pct': None,
            'top100_pct': None,
            'wallets': ws_clean,
            'updatedate': '2026-11-24',
            'special_note': 'CMC DAPI Live (fgp esatto ex-Others; etichette ufficiali CMC incluse)' if sym == 'SOL' else None,
        }

# Also save verified-primary DAPI metadata (310 coins!) for 3-date historical holderCount & wallet-label enrichment!
dapi_verified_primary = {}
for r in audit:
    cid = str(r['cmc_id'])
    dd = dapi.get(cid) or {}
    hd = dd.get('holder_data') or {}
    hh = dd.get('hist_holders') or {}
    st = (cmc_det.get(cid) or {}).get('statistics') or {}
    tot_sup = float(st.get('totalSupply') or st.get('circulatingSupply') or 0)
    ws = hd.get('wallets') or []
    dapi_bal = sum(float(w.get('balance') or 0) for w in ws)
    ratio = (dapi_bal / tot_sup) if (tot_sup > 0 and dapi_bal > 0) else None
    is_primary = (ratio is not None and ratio >= 0.45) or (r.get('holder_source','').startswith('CoinMarketCap') and 'bridge' not in (r.get('coin_audit_note') or '').lower())
    if is_primary and (hh or any(w.get('label') for w in ws if w.get('platform_id') is not None)):
        dapi_verified_primary[cid] = {
            'symbol': r['symbol'],
            'ratio_pct': round(ratio * 100.0, 2) if ratio is not None else None,
            'latest_count': hh.get('latest_count'),
            'jul1_count': (hh.get('jul1') or {}).get('holderCount'),
            'jul1_date': (hh.get('jul1') or {}).get('date'),
            'oct1_count': (hh.get('oct1') or {}).get('holderCount'),
            'oct1_date': (hh.get('oct1') or {}).get('date'),
            'nov21_count': (hh.get('nov21') or {}).get('holderCount'),
            'nov21_date': (hh.get('nov21') or {}).get('date'),
            'named_wallets': [
                {'pct': round(float(w.get('pct') or 0), 4), 'label': w.get('label'), 'balance': float(w.get('balance') or 0)}
                for w in ws if w.get('platform_id') is not None and w.get('label')
            ],
        }

out_doc = {
    'metadata': {
        'new_or_upgraded_coins': len(consolidated),
        'dapi_verified_primary_hist_coins': len(dapi_verified_primary),
    },
    'coins': consolidated,
    'dapi_verified_primary': dapi_verified_primary,
}
OUT_PATH.write_text(json.dumps(out_doc, indent=2, ensure_ascii=False), encoding='utf-8')

# Final exact tally!
already = {str(r['cmc_id']) for r in audit if r.get('top10_holders_pct') is not None}
after = already | set(consolidated.keys())
PRIV = {'XMR', 'ZANO', 'BDX', 'CC'}
rem = [r for r in audit if str(r['cmc_id']) not in after and r['symbol'] not in PRIV]

print(f"\n================ MASTER CONSOLIDATION COMPLETE ================")
print(f"BEFORE COVERAGE:         {len(already)} / 500 ({len(already)/5:.1f}%)")
print(f"NEW COINS RECOVERED:     +{len(after) - len(already)} (+ SOL upgraded to live Nov 2026)")
print(f"AFTER COVERAGE (ALL):    {len(after)} / 500 ({len(after)/5:.1f}%)")
print(f"AFTER (496 NON-PRIVACY): {len(after)} / 496 ({len(after)/4.96:.1f}%)")
print(f"PRIVACY/PRIVATE (N/D):   4 (XMR, ZANO, BDX, CC)")
print(f"DAPI 3-DATE VERIFIED:    {len(dapi_verified_primary)} primary/native coins (Jul 1 / Oct 1 / Nov 21 holderCount!)")
print(f"STILL MISSING ({len(rem)}):")
for r in rem:
    print(f"  #{r['rank_clean_jul1']:03d} {r['symbol']:7s} | {r['name'][:22]:22s} | cid={r['cmc_id']}")
print(f"\n--- ALL {len(consolidated)} CONSOLIDATED NEW/UPGRADED COINS ---")
for cid, v in sorted(consolidated.items(), key=lambda kv: next((r['rank_clean_jul1'] for r in audit if str(r['cmc_id'])==kv[0]), 999)):
    rk = next((r['rank_clean_jul1'] for r in audit if str(r['cmc_id'])==cid), 0)
    print(f"  #{rk:03d} {v['symbol']:7s} | top10={v['top10_pct']:6.2f}% | top100={str(v['top100_pct']):6s} | cnt={str(v['holderCount']):10s} | nw={len(v.get('wallets',[])):3d} | {v['source'][:44]}")
