# Settle Solana Tier-One — Design Doc

**Status: v0.5 ANCHOR-READY, 18 Sep 2026 — Fable's W-SOL-1 corrections applied: W4 cut (facilitator signature, not wash — moved to cluster classification as positive signal), W1 moved to population exclusion via fingerprint condition, calibration claim softened (uncalibrated starting values; W-SOL-2 after first measured window). Prior: v0.3 gate-pass edits; v0.2 spec-verified §2 verified against x402 Foundation SVM exact spec + x402-chain-solana Rust reference (docs.rs, 15 Sep 2026) + PayAI facilitator docs (13 Sep 2026). Due 30 Sep 2026 — this doc is the gate on the 15 Nov tier-one date: if the attribution design does not survive Fable review, the date takes the damage, not the claim (scoring table v3).**

## 0. Purpose and scope

Port Settle's measurement stack to Solana: census x402 settlement activity, attribute it to facilitators by protocol-level evidence, classify relayer behaviour against pre-registered rules, produce a tier-one report on an assessable subject: a **self-hosted x402.rs instance in Solana mode** (same codebase as 002's Base subject, same rig pattern, zero consent question — and the first within-implementation cross-chain comparison, Base vs Solana on one facilitator, a report class nobody has published). PayAI is the consent-gated stretch goal (tier one-and-a-half), pursued through the disclosure policy's channels — active testing of a hosted facilitator without written consent is forbidden by the independence policy §1, and passive census is observation, not a conformance assessment. The Solana method was declared in the design pre-registration; this document turns the declaration into an implementable, testable spec.

## 1. What changes vs Base (EVM), what doesn't

| Layer | Base (v3.2.2) | Solana | Change |
|---|---|---|---|
| Settlement signal | EIP-3009 `AuthorizationUsed` event on USDC | No EIP-3009 on Solana. Signal = SPL-token USDC transfers under the x402-spec transaction layout | **New decoder** |
| Attribution | `tx.from` == facilitator relayer | `feePayer ≠ token owner` (the sponsor pays gas for the payer) | **New attribution rule** |
| Protocol fingerprint | 4-byte selector of `transferWithAuthorization`/`receiveWithAuthorization` | Instruction layout: spec-mandated ComputeBudget + `TransferChecked` ordering | **New fingerprint** |
| Payee decode | receipt Transfer topic2 | SPL `TransferChecked` destination token account → owner | Analogous |
| Self-relay exclusion | tx.from ∈ {authorizer, payee} | feePayer == token owner (or payee) | Analogous |
| Sampling | uniform over unique tx hashes in window | uniform over signatures in window | Same |
| State/classification | v3.2.2 same-basis accounting (events_tracked/txs) | identical rules, ported unchanged | Same |
| Hash-chaining/ledgering | save_state sha256 per run, deploy.log | identical | Same |

## 2. Attribution design (the core question)

### 2.1 The x402 Solana transaction layout (verified against spec, 18 Sep 2026)

Per the x402 Foundation SVM exact-scheme spec (`specs/schemes/exact/scheme_exact_svm.md`) and the reference Rust implementation (`x402-chain-solana`, v1_solana_exact, docs.rs 15 Sep 2026), an x402 Solana settlement has a **non-negotiable instruction layout**, enforced by the facilitator's verification checklist before it co-signs:

- Index 0: ComputeBudget `SetComputeUnitLimit`
- Index 1: ComputeBudget `SetComputeUnitPrice` (price bounded — reference cap 5 lamports/CU)
- Index 2: SPL Token or Token-2022 `TransferChecked` (USDC mint, payer ATA → payTo-derived ATA, exact amount)
- Index 3+ (optional only): up to two Lighthouse assertion instructions and/or one SPL Memo — nothing else; 3–6 instructions total

**Fee-payer isolation (spec MUST):** the `feePayer` must not appear in any instruction's account list, must not be the transfer's authority or source, and must not be invoked as a program. The fee payer pays the network fee and nothing else.

Fingerprint for census: ComputeBudget(0,1) + exactly one USDC `TransferChecked` at index 2 + only Lighthouse/Memo trailing + `feePayer` absent from all instruction accounts. That layout is x402-specific — generic Solana transfers do not follow it — which is why the declared method is arguably *stronger* than EIP-3009 event scanning (scoring table v3 row b).

**Design inversion vs EVM (spec-verified):** on EVM the facilitator authors the transaction around the client's EIP-3009 authorization; on Solana the *client* authors the full transaction and the facilitator co-signs as feePayer after the checklist. Attribution semantics therefore differ from EVM in one way that matters: the on-chain `feePayer` is the **sponsor**, and the spec allows the sponsor to be *the merchant itself*, not only a facilitator. Sponsor ≠ necessarily facilitator — see §2.2.

### 2.2 Attribution rule (pre-registered)

- **Sponsor (on-chain relayer)** = transaction `feePayer`. Spec-verified caveat: the sponsor MAY be the merchant itself (`feePayer == payTo` is explicitly permitted — receiving funds needs no debiting signature). Therefore: `feePayer == payTo owner` → **merchant-sponsored**, reported separately, not counted as facilitator-mediated; `feePayer ∉ {source owner, payTo owner}` → facilitator candidate, mirroring the EVM negative filter.
- **Payer** = owner of the source token account (authority over funds).
- **Payee** = `payTo` = owner derived from the destination ATA; fingerprint condition: `payTo` owner ≠ source owner (wallet reshuffles between one's own ATAs are not settlements and never enter the population — this is where W1 lives, as a population exclusion).
- **Self-relay exclusion**: `feePayer` == source owner → excluded (direct wallet submission). Note: redundant by construction — the fee-payer isolation MUST means a compliant x402 tx can never have feePayer in the instruction accounts, so such a tx already fails the fingerprint. The explicit check stays: it costs nothing and documents intent.
- **Seed set**: facilitator feePayer addresses are publicly enumerable — each facilitator's `/supported` endpoint returns its Solana `feePayer` address (verified in PayAI's facilitator docs, 13 Sep 2026). This gives Solana a *spec-sanctioned seed source* the EVM side never had: the seed list can be built from facilitator self-declaration and then verified against on-chain attribution, a two-way check.
- **Smart-wallet caveat (spec-named)**: program-controlled accounts (Squads, Swig, SPL Governance, Metaplex Core) transfer via CPI rather than top-level `TransferChecked` — the fingerprint must decide whether CPI-nested settlements are in scope. v0.2 decision: **top-level only in tier one**; CPI settlement share is measured and reported as a coverage caveat, not silently dropped. Multi-sig and delegated-authority edge cases: enumerated in §5 test fixtures.

### 2.3 What this preserves from the EVM method

Cluster thresholds (≥10 payers, ≥5 payees, ≥20 events, ≥10 distinct txs), same-basis accounting (events_tracked/txs), batch-shaped rule (events_tracked ≥ 20 ∧ 0 < txs < 10), negative filter, redaction policy S.1 — all ported unchanged. The classifier doesn't know which chain it's reading.

## 3. Data access — tiered design (scoring table row c)

`getSignaturesForAddress` on the USDC mint IS the full scan (~869k/day, Bitquery Aug 2026) through the most rate-limited endpoint for the job — that path is rejected by design. The split the backbone declared:

- **Tier one (seeded):** `getSignaturesForAddress` on each *known facilitator feePayer* (from their `/supported` endpoints — §2.2's spec-sanctioned seed source), then `getTransaction` on those signatures, fingerprint-filtered. Cheap, bounded by facilitator activity, sufficient for the tier-one subject.
- **Tier two (discovery):** **slot sampling, not mint scanning.** Draw uniform-random slot numbers in the window, `getBlock` each with full transaction details, decode every USDC `TransferChecked` in those blocks, apply the fingerprint. Uniform sample over *time* (reportable as "sampled N slots of M in window"), needs no indexer, and finds feePayers never seen before — which is the point of discovery. Declared trade-off: slot sampling under-samples bursty facilitators relative to signature sampling; stated, accepted.
- RPC: Helius or Triton free tier; rate-limit budget in the runner like the EVM 0.12s sleep; endpoint declared in `rpc_endpoints_used`. With the split above, free-tier throughput is *manageable*, not the binding risk.

## 4. The two open measurements this rig must produce (scoring table v3 gaps)

1. **Solana wash/incentivized share (f)** — currently UNKNOWN. Design must output: distribution of payment sizes (sub-cent share), payer/payee concentration, repeat-payer rates, and the wash heuristic below — **frozen by the hash of this doc's anchored version, thresholds included, before the first measurement run** (a pre-registration of an intention is not a pre-registration).

**Wash heuristic W-SOL-1 (frozen at anchor; thresholds are part of the pre-registration):**
A settlement is flagged wash-suspect if ANY of:
- **W2 ping-pong**: the same (payer, payee) pair transacts ≥10 times within any 24h window with ≤$0.01 median amount;
- **W3 fan velocity**: a payer sends to ≥50 distinct payees, or a payee receives from ≥50 distinct payers, within 24h, all ≤$0.01 median.

(Numbering W2/W3 retained so the anchored record shows W1 and W4 were considered and cut before freezing — cuts happen now, not after a run, because changing the heuristic post-run reads as fitting to output even when it isn't.)

**Cut rules and why:**
- **W1 (payer == payee): removed from the heuristic — it is population-excluded, not wash-flagged.** A `TransferChecked` between two ATAs of the same owner is a wallet reshuffle, not a settlement to a merchant; §2.2's fingerprint now carries `payTo` owner ≠ source owner as an explicit condition, so self-loops never enter the population W-SOL-1 divides into. Keeping W1 would have meant a permanently-zero rule misleadingly presented as measurement.
- **W4 (sponsorship churn): cut — it was the facilitator signature, not a wash signature.** A healthy facilitator serving many merchants at agent-metering prices *will* sponsor thousands of sub-cent settlements/day with no dominant payee (Bitquery Aug 2026: 869k sub-cent/day across 15,070 sponsors). Frozen as drafted, W4 would have flagged the seed facilitators themselves as wash-suspect on day one. Sponsorship concentration moves where it belongs: the cluster classification, as a *positive* facilitator signal. What W4 was reaching for — incentive farming through a sponsor — is caught payer-side by W3 + W2, because farming shows up as payer velocity, not sponsor volume.

Wash-suspect share = flagged settlements / fingerprint-population settlements in the window; **denominator stated per figure**. Thresholds are **starting values, uncalibrated on Solana** (chosen from the Base catalog's March evidence — an EIP-3009 upper bound on a different chain with different price/fee dynamics; a starting place, not calibration); **W-SOL-2 follows the first measured window**. W-SOL-1 can only be amended by a versioned, anchored doc update before the run that uses it — never retro-fitted to output.
2. **Solana dollar exposure (e)** — currently unmeasured. The rig already decodes amounts; dollar exposure = sum of `TransferChecked` amounts on attributed settlements per window. Trivially produced once attribution works; the design work is defining the denominator (attributed-only vs fingerprint-population, both reported).

## 5. Test plan (mirrors the EVM synthetic suite)

- Synthetic fixtures: genuine x402 layout → attributed; self-relay (feePayer == source owner) → excluded (also fails fingerprint — redundancy documented); **merchant-sponsored (feePayer == payTo owner) → reported separately, NOT counted as facilitator-mediated**; self-loop (payTo owner == source owner) → population-excluded, not wash-flagged; generic SPL transfer without ComputeBudget layout → not fingerprinted; multi-instruction batch transactions → not misattributed; delegated authority edge case → defined behaviour.
- Invariant ported: events_tracked ≥ len(txs) for every sender, enforced in the synthetic suite (Fable 18 Sep ruling — cannot regress).
- Known-transaction validation: reproduce attribution on a small set of manually verified x402 Solana transactions (from PayAI's explorer/x402scan) before any window run.

## 6. Pre-registration stub (to be anchored before first run)

Invariants over named entities (Fable's standing rule — never totals over open sets):
- The sighted facilitator feePayer set (PayAI + CDP Solana + thirdweb addresses at anchor time) classifies as attributed in the first window run.
- Batch-shaped = 0 is NOT pre-registered as evidence (vacuous until events_tracked matures — same correction as Base run 2); instead pre-register: "no sender is classified batch-shaped before any sender reaches 20 tracked events" (Solana has no backfill).
- **Tier-two invariant (once slot sampling exists):** every seeded feePayer that appears in a sampled slot is fingerprint-attributed — the two-way check §2.2 promises, made testable.
- Wash heuristic W-SOL-1 frozen by hash in this doc's anchored version (§4 — thresholds included).

## 7. Schedule (fits the corrected roadmap)

- **30 Sep**: this doc final + Fable pass → gate decision on 15 Nov.
- **1–14 Oct**: rig build + synthetic suite (parallel to 002 wrap-up; port lands 31 Oct).
- **~14 Oct–14 Nov**: test-window runs, wash heuristic frozen and measured, dollar exposure first figures.
- **15 Nov**: tier-one report on the assessable subject.

## 8. Honest risks

1. **Attribution false-positive risk**: ComputeBudget+TransferChecked layout is spec-mandated, but a non-x402 transfer could imitate it — mitigated by feePayer≠owner + known-facilitator seed set + the known-transaction validation in §5. Residual risk declared in the method note.
2. **RPC throughput** (§3) — manageable under the tier-one/tier-two split; verify seed-endpoint rate limits in the first build week, not the last.
3. **PayAI (tier one-and-a-half) consent**: pursued through disclosure-policy channels only; the tier-one report does not depend on it (subject = self-hosted x402.rs, zero consent question).

*Fable review required before this doc leaves DRAFT; the 30 Sep gate is a Fable ruling on this document, not a calendar event.*
