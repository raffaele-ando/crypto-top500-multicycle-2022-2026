import json
import os
import time
import datetime
import urllib.request

proj = r"C:\Users\Administrator\.gemini\antigravity\scratch\crypto_top500_jul_oct_2026"
raw_dir = os.path.join(proj, "raw")

with open(os.path.join(raw_dir, "cmc_full_2026-07-01.json"), encoding="utf-8") as f:
    jul_top500 = json.load(f)["data"][:500]
with open(os.path.join(raw_dir, "cmc_full_2026-10-01.json"), encoding="utf-8") as f:
    oct_all = json.load(f)["data"]
oct_by_id = {r["id"]: r for r in oct_all}

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

ts_jul_s = int(datetime.datetime(2026, 6, 30, tzinfo=datetime.timezone.utc).timestamp())
ts_jul_e = int(datetime.datetime(2026, 7, 3, tzinfo=datetime.timezone.utc).timestamp())
ts_oct_s = int(datetime.datetime(2026, 9, 30, tzinfo=datetime.timezone.utc).timestamp())
ts_oct_e = int(datetime.datetime(2026, 10, 3, tzinfo=datetime.timezone.utc).timestamp())

# Collect all IDs where either Jul 1 or Oct 1 price < 0.01
target_ids = []
for r in jul_top500:
    cid = r["id"]
    pj = r["quotes"][0]["price"]
    ro = oct_by_id.get(cid)
    po = ro["quotes"][0]["price"] if ro else 1.0
    if pj < 0.01 or po < 0.01:
        target_ids.append((cid, r["symbol"], r["name"]))

print(f"Fetching exact unrounded v3.1/historical for {len(target_ids)} sub-$0.01 coins...")
exact_quotes = {}
for cid, sym, name in target_ids:
    exact_quotes[str(cid)] = {"symbol": sym, "name": name}
    for label, s, e, match_str in [("2026-07-01", ts_jul_s, ts_jul_e, "2026-07-01"), ("2026-10-01", ts_oct_s, ts_oct_e, "2026-10-01")]:
        url = f"https://api.coinmarketcap.com/data-api/v3.1/cryptocurrency/historical?id={cid}&convertId=2781&timeStart={s}&timeEnd={e}&interval=1d"
        try:
            d = fetch(url)
            for q in d.get("data", {}).get("quotes", []):
                if match_str in q.get("timeClose", ""):
                    exact_quotes[str(cid)][label] = q["quote"]
        except Exception as ex:
            exact_quotes[str(cid)][f"{label}_err"] = str(ex)
    time.sleep(0.15)

out_f = os.path.join(raw_dir, "cmc_subcent_exact_v31.json")
with open(out_f, "w", encoding="utf-8") as f:
    json.dump(exact_quotes, f, indent=2)
print("Saved exact sub-cent quotes:", len(exact_quotes))
