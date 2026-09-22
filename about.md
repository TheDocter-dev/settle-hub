# About Settle

**Status: DRAFT v2 for 22 Sep 2026 launch package — anchors at freeze (21 Sep, anchor-001)**

## What we do

Settle is an independent, protocol-level facilitator conformance and verification lab for the x402 agent-payment protocol. We measure the protocol as it actually settles on-chain. Starting from raw chain data, we attribute settlements to facilitators by chain-appropriate protocol-level evidence (transaction-submitter addresses and authorization patterns on EVM chains; fee-payer and instruction-layout evidence on Solana), classify relayer behaviour against pre-registered rules, and publish dated, hash-anchored figures that anyone can recompute.

## Why

Agent payments only work if buyers and sellers can trust the settlement layer. Trust requires measurement that is independent of the parties being measured. Settle exists to be that measurement: a lab whose incentive is accuracy, whose method is published, and whose record cannot be silently revised.

## How publications are made

1. **Pre-registration.** Before each measurement run or publication, the expected invariants are written down — over named entities and bounded conditions, never totals over open sets.
2. **Frozen method.** The measurement code is hashed and logged before its first run; every change ships as a new version with a new recorded hash.
3. **Hash-chained state.** Each run logs the hash of the state it consumed and produced, so the sequence of runs is provable link by link.
4. **Freeze and anchor.** Reports are frozen, hashed, and timestamped (OpenTimestamps) in the Settle Ledger before publication. Publication day publishes the anchor, not just the document.
5. **External review.** An external reviewer seat exists for hostile-reading pre-registrations, method changes, and drafts. It is vacant at launch and will be filled before Settle issues any commissioned assessment; until then, none is issued (see Independence Policy). The internal accuracy record — every error caught, including ones caught before publication — is kept and summarized with each published report.

## AI authorship disclosure

Settle's code, analysis, and drafts are produced with substantial AI assistance (large language models), under the direction and review of the human founder. We disclose this because readers deserve to know how the text and code were produced — and because our answer to the obvious follow-up ("so why trust it?") is structural, not rhetorical: no figure depends on trusting an author. Every number traces to code with a recorded hash, state with a logged hash, and a report with a public timestamp. Verify, don't trust — that applies to us first.

## Who

Settle is operated by one person, with AI tooling as described above. Continuity arrangements — a dormancy banner rule and a planned key-escrow arrangement — are described in the Independence Policy, together with their current status.

## Independence

See the Independence Policy. Short version: public observation is never commissioned; commissioned assessments are firewalled from the catalog and grades, disclosed in the report header, and held to identical standards; no measured party can delay, veto, or edit a publication; corrections by dated errata only.

## Contact

GitHub Security Advisory on the relevant Settle repo (sensitive matters, per disclosure policy §3); Ledger issue tracker (non-sensitive matters) — corrections, disputes, verification requests, and disclosure reports.
