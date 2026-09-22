# Settle Independence Policy

**Status: DRAFT v5 for 22 Sep 2026 launch package — anchors at freeze (21 Sep, anchor-001)**

## What Settle is

Settle is an independent, protocol-level facilitator conformance and verification lab for the x402 agent-payment protocol. We measure what settles on-chain, attribute it to facilitators by chain-appropriate protocol-level evidence (for example, transaction-submitter addresses and authorization patterns on EVM chains; fee-payer and instruction-layout evidence on Solana), and publish the results with a hash-chained audit trail. Settle does not operate a facilitator, does not sell facilitation, and does not process payments.

## Funding and conflicts

- Settle is self-funded by its founder. No facilitator, chain, token issuer, or protocol maintainer funds, sponsors, or has preview rights over Settle publications.
- **Public observation is never commissioned.** The catalog, liveness feed, release watch, and any published grade are funded solely by Settle; no measured party pays for, sponsors, or influences them. **Commissioned assessments** — reports a facilitator pays Settle to produce against its own systems — are permitted under these rules: procedures agreed in advance, findings only, results restricted to named parties, the commercial relationship stated in the report header, and identical disclosure windows and evidence standards to uncommissioned work. Commissioned work never feeds the public catalog, seeds, or grades, and the catalog's seed data is drawn only from facilitator-published sources.
- Settle holds no tokens whose value depends on the facilitators or chains it measures, beyond de-minimis amounts used to pay gas for measurement transactions, disclosed per-chain in the method note.
- The operator's personal wallets and on-chain activity are segregated from all Settle measurement and signing infrastructure; the operator holds no position in any assessed subject or its token, and will not trade on unpublished findings.

## Editorial independence

- Publication decisions follow the pre-registered method and the freeze anchor. No measured party can delay, veto, or edit a publication. Corrections after publication are made by dated errata, never by silent edits — the Ledger makes silent edits detectable by construction.
- Drafts shared with any measured party before publication are shared for factual correction only, under the disclosure policy's embargo terms, and the fact of sharing is recorded in the publication's methods section.

## Evidence standard

- Every published figure traces to a hash in the public audit trail: the deployed measurement code (hash in deploy log), the state it produced (sha256 logged per run), and the freeze anchor (OpenTimestamps) for the report itself.
- Method changes are versioned and each version's hash is recorded before its first run. Pre-registrations state invariants over named entities and bounded conditions, never totals over open sets that new data can legitimately grow.

## External review

- An external reviewer holds a standing seat to hostile-read pre-registrations, method changes, and draft publications before they ship. **The seat is vacant at launch. It will be filled before Settle issues its first commissioned assessment; until it is filled, no commissioned assessment will be issued.** Interim arrangement, disclosed as interim: pre-registrations, method changes, and drafts pass an adversarial review loop (external-model hostile read), with rulings recorded in the project handoff log.
- Where the internal accuracy record disagrees with a published figure, the correction is published with the same prominence as the original figure.

## AI authorship

Settle's measurement code, analysis, and drafts are produced with AI assistance under human direction and review. See the About page for the full disclosure. No figure is published without a hash-chained provenance that a reader can verify without trusting either the human or the AI.

## Continuity

Settle is operated by one person. Two arrangements address single-operator risk — one in force today in manual form, one planned — and both are public in existence, trigger, and powers:

- **Key escrow (planned).** Settle is currently operated by one person. The Ledger signing key exists in two locations under the operator's sole control: the signing host's keyring and an off-host backup. No trustee arrangement is in place yet. Escrow is planned by 31 October 2026 with a named trustee whose powers will be enumerated and bounded — publish the dormancy banner, and publish a signed revocation of the signing key — and nothing else. The trustee will not be able to issue anchors, findings, or corrections as Settle; a key holder who could publish as Settle would be a second unaccountable operator, not a safeguard. The trustee's identity will remain private; the existence, trigger, and powers of the arrangement will be public. Until escrow is executed, loss of the operator means the key is revoked by no one and the record simply stops — which the anchors and the banner rule make visible rather than hide.
- **Dormancy banner (automated, planned).** A job on the hub will check the liveness feed daily and, if it shows no Settle activity for 30 consecutive days, post the banner without human involvement. Activation target: 30 September 2026. Until activation, the same 30-day rule applies and the banner is posted manually by the operator.

An unmaintained record is still a verifiable record — the anchors stand — but readers are told, not left to assume.

## Contact

Corrections, disputes, and verification requests: GitHub Security Advisory on the relevant Settle repo (sensitive matters, per disclosure policy §3); Ledger issue tracker (non-sensitive matters). Private Vulnerability Reporting is enabled on settle-hub before this page goes live, per the launch sequence.
