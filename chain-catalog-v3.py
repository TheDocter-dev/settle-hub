#!/usr/bin/env python3
"""
Settle Chain Catalog v3.2.1 - passive on-chain observation of x402 facilitator
settlement activity on Base mainnet. Declared method per Settle Disclosure
Policy v1.0 S.1 ("On-chain observation"): public ledger data only, facilitator
settlement activity only, no profiling of individual payers or merchants.

v3.2.1 changes (Fable batch-bucket review, 17 Sep 2026):
7. Batch-shaped bucket requires measured transaction shape: >=20 cumulative
   events AND >0 AND <10 distinct txs. Senders with empty migrated tx sets, or
   with tx breadth but low payer/payee breadth, fall to plain-unattributed.

v3.2 changes (Fable cluster false-positive review, 17 Sep 2026):
6. Cluster criteria add transaction breadth: >=10 distinct txs per sender,
   alongside >=10 payers, >=5 payees, >=20 cumulative events. Serialized rows
   report distinct_txs and events_per_tx. Bulk-shaped senders are reported
   separately and are not counted as x402 relayers unless seeded.

v3.1 changes (Fable source review, 17 Sep 2026):
1. Payee decode moved to eth_getTransactionReceipt: payTo taken from the ERC-20
   Transfer event (to = topic2) of the USDC contract in the same receipt.
   Routing-independent: works for direct EOA calls, batch/multicall, and
   settlement contracts. Replaces calldata parsing entirely.
2. Seeded uniform-random sample of unique tx hashes (sample seed recorded in
   output; headline reports "sampled N of M unique transactions"). Fixes the
   log-order time bias of the v3 cap.
3. Cumulative state file (catalog-state.json): per-sender payer/payee sets and
   event counts persist across runs; classification is computed on merged
   state, so attribution genuinely improves over time. State file hash is
   included in the output.
4. Cluster thresholds: >=10 distinct payers AND >=5 distinct payees AND
   >=20 cumulative events (volume-breadth gate), all on cumulative state.
5. unresolved_cap and unresolved_rpc_error are separate counters.

Negative filter (unchanged from v3): if tx.from equals the authorizer (topic1)
or any USDC Transfer recipient in the same receipt, the tx is self-relayed or
app-relayed and is excluded before clustering.
"""
import json, time, urllib.request, os, random, hashlib

RPCS = ["https://base-rpc.publicnode.com", "https://base.drpc.org"]
USDC = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913".lower()
# AuthorizationUsed(address indexed authorizer, bytes32 indexed nonce) - Circle USDC
TOPIC0 = "0x98de503528ee59b575ef0c0a2576a82497bfc029a5685b209e9ec333479b10a5"
# ERC-20 Transfer(address,address,uint256)
TRANSFER_TOPIC0 = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

WINDOW_BLOCKS = 5000       # ~2.8 hours on Base (2s blocks)
CHUNK0 = 250
MIN_CHUNK = 10
MAX_TX_LOOKUPS = 400
SAMPLE_SEED = None         # set to an int to reproduce; None = derive from window start
CLUSTER_MIN_PAYERS = 10
CLUSTER_MIN_PAYEES = 5
CLUSTER_MIN_EVENTS = 20
CLUSTER_MIN_TXS = 10
MIGRATION_NOTE = ("v3.1->v3.2.1 17 Sep 2026: distinct_txs tracking starts empty for "
                  "pre-existing state; empty tx sets are treated as insufficient "
                  "breadth data (plain-unattributed), and cluster attribution may "
                  "drop and re-earn over subsequent runs. "
                  "v3.2.1->v3.2.2 18 Sep 2026: same-basis accounting - events_tracked "
                  "accrues only when txs are tracked; batch rule and events_per_tx use "
                  "events_tracked/len(txs). Migration: events_tracked = len(txs) for the "
                  "21 backfilled senders (measured 1.0 event/tx in v5b inspection), "
                  "0 for all other pre-existing senders; legacy events unchanged "
                  "(cluster threshold only).")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "chain-catalog.json")
STATE = os.path.join(HERE, "catalog-state.json")
SEED_FILE = os.path.join(HERE, "catalog-seed.json")

def load_seed():
    try:
        with open(SEED_FILE) as f:
            return {k.lower(): v for k, v in json.load(f).items()}
    except FileNotFoundError:
        return {}

def load_state():
    try:
        with open(STATE) as f:
            d = json.load(f)
        for rec in d.values():
            rec["payers"] = set(rec["payers"]); rec["payees"] = set(rec["payees"])
            rec["txs"] = set(rec.get("txs", []))
        return d
    except FileNotFoundError:
        return {}

def save_state(state):
    ser = {k: {**v, "payers": sorted(v["payers"]), "payees": sorted(v["payees"]),
               "txs": sorted(v.get("txs", set()))}
           for k, v in sorted(state.items())}
    blob = json.dumps(ser, indent=2, sort_keys=True)
    with open(STATE, "w") as f:
        f.write(blob)
    return hashlib.sha256(blob.encode()).hexdigest()

_rpc_idx = 0

def rpc(method, params, retries=4):
    global _rpc_idx
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params}).encode()
    last = None
    for attempt in range(retries):
        url = RPCS[_rpc_idx % len(RPCS)]
        try:
            req = urllib.request.Request(url, data=body, headers={
                "Content-Type": "application/json",
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) SettleChainCatalog/3.1",
            })
            with urllib.request.urlopen(req, timeout=30) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(out["error"])
            return out["result"]
        except Exception as e:
            last = e
            _rpc_idx += 1
            time.sleep(1.5 * (attempt + 1))
    raise last

def get_logs(a, b):
    size = CHUNK0
    results = []
    lo = a
    while lo <= b:
        hi = min(lo + size - 1, b)
        try:
            chunk = rpc("eth_getLogs", [{
                "address": USDC, "topics": [TOPIC0],
                "fromBlock": hex(lo), "toBlock": hex(hi),
            }])
            results.extend(chunk)
            print(f"  blocks {lo}-{hi}: {len(chunk)} events (total {len(results)})")
            lo = hi + 1
            time.sleep(0.3)
        except Exception as e:
            if size <= MIN_CHUNK:
                raise
            size = max(MIN_CHUNK, size // 2)
            print(f"  ...range cap hit at {size*2} blocks, halving to {size} ({type(e).__name__})")
            time.sleep(1)
    return results

def resolve_tx(txh):
    """Returns (sender, payees:set) or None on RPC failure.
    sender = tx.from; payees = recipients of USDC Transfer events in the receipt."""
    tx = rpc("eth_getTransactionByHash", [txh])
    if not tx:
        return None
    rcpt = rpc("eth_getTransactionReceipt", [txh])
    if not rcpt:
        return None
    payees = set()
    for log in rcpt.get("logs", []):
        if log.get("address", "").lower() != USDC:
            continue
        topics = log.get("topics", [])
        if len(topics) >= 3 and topics[0].lower() == TRANSFER_TOPIC0:
            payees.add(("0x" + topics[2][-40:]).lower())
    return tx["from"].lower(), payees

def main():
    seed = load_seed()
    state = load_state()
    latest = int(rpc("eth_blockNumber", []), 16)
    start = latest - WINDOW_BLOCKS
    print(f"latest block: {latest} | window: {start}..{latest} ({WINDOW_BLOCKS} blocks)")
    print(f"seed relayers: {len(seed)} | state senders: {len(state)}")

    logs = get_logs(start, latest)
    total_events = len(logs)

    # authorizer per tx from log topic1; events per tx
    tx_info = {}  # txh -> {"authorizer": str|None, "events": int, "first_blk": int, "last_blk": int}
    for lg in logs:
        txh = lg["transactionHash"]
        blk = int(lg["blockNumber"], 16)
        topics = lg.get("topics", [])
        auth = ("0x" + topics[1][-40:]).lower() if len(topics) > 1 else None
        rec = tx_info.setdefault(txh, {"authorizer": auth, "events": 0,
                                       "first_blk": blk, "last_blk": blk})
        rec["events"] += 1
        rec["first_blk"] = min(rec["first_blk"], blk)
        rec["last_blk"] = max(rec["last_blk"], blk)
        if auth and not rec["authorizer"]:
            rec["authorizer"] = auth

    unique_txs = sorted(tx_info.keys())
    M = len(unique_txs)
    seed_val = SAMPLE_SEED if SAMPLE_SEED is not None else start
    rng = random.Random(seed_val)
    sample = set(rng.sample(unique_txs, min(MAX_TX_LOOKUPS, M)))
    print(f"unique txs: {M} | sampled: {len(sample)} (seed {seed_val})")

    excluded_self_relayed = 0
    unresolved_cap = M - len(sample)
    unresolved_rpc_error = 0
    resolved = 0
    for i, txh in enumerate(unique_txs):
        if txh not in sample:
            continue
        try:
            r = resolve_tx(txh)
        except Exception:
            r = None
        if r is None:
            unresolved_rpc_error += 1
            continue
        resolved += 1
        sender, payees = r
        info = tx_info[txh]

        # Negative filter: sender is a party to the transfer -> not facilitator-mediated
        if (info["authorizer"] and sender == info["authorizer"]) or sender in payees:
            excluded_self_relayed += info["events"]
            continue

        rec = state.setdefault(sender, {"payers": set(), "payees": set(), "txs": set(),
                                        "events": 0, "events_tracked": 0,
                                        "first_seen": None, "last_seen": None})
        rec["events"] += info["events"]
        # same-basis accounting (v3.2.2): events_tracked accrues only where txs tracked
        rec["events_tracked"] = rec.get("events_tracked", 0) + info["events"]
        rec["txs"].add(txh)
        if info["authorizer"]:
            rec["payers"].add(info["authorizer"])
        rec["payees"] |= payees
        rec["first_seen"] = info["first_blk"] if rec["first_seen"] is None else min(rec["first_seen"], info["first_blk"])
        rec["last_seen"] = info["last_blk"] if rec["last_seen"] is None else max(rec["last_seen"], info["last_blk"])
        if i % 50 == 0:
            print(f"  resolved {i+1}/{M} ...")
        time.sleep(0.12)

    state_hash = save_state(state)

    # Classification on cumulative state
    attributed, cluster_new, batch_new = {}, [], []
    for sender, rec in state.items():
        if sender in seed:
            attributed[sender] = {**rec, "attribution": "seed", "label": seed.get(sender)}
        elif (len(rec["payers"]) >= CLUSTER_MIN_PAYERS
              and len(rec["payees"]) >= CLUSTER_MIN_PAYEES
              and rec["events"] >= CLUSTER_MIN_EVENTS
              and len(rec.get("txs", set())) >= CLUSTER_MIN_TXS):
            attributed[sender] = {**rec, "attribution": "cluster", "label": None}
            cluster_new.append(sender)
        elif (rec.get("events_tracked", 0) >= CLUSTER_MIN_EVENTS
              and len(rec.get("txs", set())) > 0
              and len(rec.get("txs", set())) < CLUSTER_MIN_TXS):
            batch_new.append(sender)

    attributed_events = sum(rec["events"] for rec in attributed.values())
    batch_events = sum(state[addr].get("events_tracked", 0) for addr in batch_new)
    total_state_events = sum(rec["events"] for rec in state.values())
    plain_unattributed_events = total_state_events - attributed_events - batch_events

    def serialize(rec):
        tx_count = len(rec.get("txs", set()))
        events_tracked = rec.get("events_tracked", 0)
        return {"events_cumulative": rec["events"],
                "events_tracked_same_basis": events_tracked,
                "distinct_payers": len(rec["payers"]),
                "distinct_payees": len(rec["payees"]),
                "distinct_txs": tx_count,
                "events_per_tx": (round(events_tracked / tx_count, 3) if tx_count else None),
                "first_seen_block": rec["first_seen"], "last_seen_block": rec["last_seen"],
                "attribution": rec["attribution"], "label": rec["label"]}

    catalog = {
        "generated_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "method": ("Settle chain catalog v3.2.2 - eth_getLogs AuthorizationUsed on Base USDC; "
                   f"sampled {resolved} of {M} unique transactions (uniform random, seed {seed_val}); "
                   "x402 attribution via tx.from relayer match against seed + cumulative clustering "
                   "(>=10 payers, >=5 payees, >=20 events, >=10 distinct txs, merged state); "
                   "negative filter excludes self/app-relayed transfers (payee from receipt Transfer); "
                   "bulk-shaped senders reported separately, not counted as x402 unless seeded "
                   "(batch rule uses events_tracked accumulated over the same runs as txs); "
                   "ratio-based classification uses events and transactions accumulated over the "
                   "same runs; pre-migration event counts do not enter ratios; "
                   "unattributed EIP-3009 activity not counted; figures dated; "
                   "address-to-facilitator mapping internal per policy S.1"),
        "chain": "eip155:8453 (Base mainnet)",
        "rpc_endpoints_used": RPCS,
        "usdc_contract": USDC,
        "event_topic0": TOPIC0,
        "window": {"from_block": start, "to_block": latest, "blocks": WINDOW_BLOCKS},
        "authorizationUsed_events_in_window": total_events,
        "unique_txs_in_window": M,
        "unique_txs_sampled": len(sample),
        "unique_txs_resolved": resolved,
        "sample_seed": seed_val,
        "unresolved_cap": unresolved_cap,
        "unresolved_rpc_error": unresolved_rpc_error,
        "excluded_self_or_app_relayed_events": excluded_self_relayed,
        "cumulative_state_senders": len(state),
        "catalog_state_sha256": state_hash,
        "migration_note": MIGRATION_NOTE,
        "event_populations_cumulative": {
            "x402_attributed_events": attributed_events,
            "batch_shaped_events_not_counted": batch_events,
            "plain_unattributed_events_not_counted": plain_unattributed_events,
            "total_events_in_state": total_state_events,
        },
        "attributed_relayers_cumulative": [
            ({"address": addr, **serialize(info)} if info["attribution"] == "seed"
             else {"address": "REDACTED-internal-per-S.1", **serialize(info)})
            for addr, info in sorted(attributed.items(), key=lambda kv: -kv[1]["events"])
        ],
        "batch_shaped_senders_cumulative": [
            {"address": "REDACTED-internal-per-S.1",
             **serialize({**state[addr], "attribution": "batch-shaped-unattributed", "label": None})}
            for addr in sorted(batch_new, key=lambda a: -state[a]["events"])
        ],
        "new_cluster_candidates_count": len(cluster_new),
        "redaction_note": ("Cluster-attributed and batch-shaped addresses are internal "
                           "(de-anonymization index) per Policy S.1; public output carries "
                           "counts, statistics, and seeded addresses only."),
        "limitations": [
            "Relayer rotation: facilitators using addresses outside seed+cluster are under-attributed until cumulative clustering identifies them; attribution improves over time and figures are dated.",
            "Batch/contract settlement: attribution is at transaction-sender level; contract senders are attributed to their operator when known (seed), unattributed otherwise - for contract senders the payee signal comes from receipt Transfer events, so clustering still applies.",
            "Sampling: counts derive from a uniform random sample of unique transactions (N of M recorded above); window totals are event counts, attribution is sample-based.",
            "Bulk EIP-3009 senders (batch settlement or non-x402 disbursement) are distinguishable from single-payment facilitators by events-per-transaction but not from each other; batch-shaped senders are reported separately and not counted as x402 unless seeded.",
        ],
    }
    with open(OUT, "w") as f:
        json.dump(catalog, f, indent=2)
    print(f"\nwrote {OUT} (state sha256 {state_hash[:16]}...)")
    print(f"events: {total_events} | resolved {resolved}/{len(sample)} sampled of {M} unique | "
          f"self-relayed excluded: {excluded_self_relayed} | rpc errors: {unresolved_rpc_error}")
    print(f"attributed relayers (cumulative): {len(attributed)} (new cluster candidates: {len(cluster_new)}; "
          f"batch-shaped unattributed: {len(batch_new)})")
    for addr, info in sorted(attributed.items(), key=lambda kv: -kv[1]["events"])[:10]:
        tx_count = len(info.get("txs", set()))
        ept = info["events"] / tx_count if tx_count else 0
        print(f"  {addr}  events={info['events']} txs={tx_count} events/tx={ept:.2f} "
              f"payers={len(info['payers'])} payees={len(info['payees'])} via={info['attribution']}")

if __name__ == "__main__":
    main()
