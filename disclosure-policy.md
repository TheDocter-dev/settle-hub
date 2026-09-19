# Settle — Coordinated Disclosure Policy (v1.0 — PUBLICATION-READY, HOLD for 22 Sep 2026)

*Version 1.0 — September 2026. Effective on publication. This policy governs all Settle assessments from its effective date onward, including Assessment 001 (Faremeter v0.22.0), which publishes alongside it and is governed by v1.0. It is a standing commitment, not a per-report arrangement.*

## 1. What Settle does (scope)

Settle is an independent conformance and security laboratory for x402 agent-payment infrastructure. We assess facilitator implementations, merchant integrations, and related protocol components against the x402 specification, the EIP-3009 authorization model, and published protocol invariants.

We assess:
- **Our own deployments** of published open-source software (self-hosted instances on public test networks), or
- **Third-party deployments with the operator's prior written consent** (staging or production, scope agreed in writing).

We do not conduct active testing of third-party production infrastructure without written authorization.

**Discovery carve-out (narrow).** The only unauthorized network interaction we permit ourselves is a single unauthenticated read-only request to a protocol-standard discovery endpoint (`/supported`, `/accepts`) of a public facilitator — exactly what any x402 client sends in normal operation. Discovery is never a predicate for any active test, never repeated at volume, and never reported as a finding. Anything beyond it requires consent, full stop.

**Availability observation (bounded).** Separately from discovery, we may periodically issue unauthenticated, payload-free liveness requests to public facilitator endpoints at a rate no greater than once per 15 minutes per endpoint — ordinary status-monitoring cadence, comparable to what block explorers and ecosystem dashboards already do. Permitted endpoints are exactly: `/supported`, `/accepts`, and `/health` (where the implementation exposes it). Any endpoint not on this list is out of bounds. These requests never carry payment payloads, are never a predicate for any active test, and produce only up/down and response-time observations. Everything payload-bearing — including a valid payment payload at `/verify` — remains behind the consent line above.

**On-chain observation (declared method).** We maintain observations of public facilitator on-chain activity — settlement addresses, volume, timing, relayer patterns — derived solely from public ledger data. This involves no interaction with any operator's systems. Observation is of facilitator settlement activity only; we do not attempt to identify or profile individual payers or merchants. Attribution is by known-facilitator relayer address, seeded from public documentation and Settle's own settlements, and extended by clustering: a sending address relaying authorizations from many distinct payers to many distinct recipients is classified as a facilitator relayer. Unattributed EIP-3009 activity is not counted; attribution improves over time and figures are dated. The method is public and aggregate figures are publishable; the address-to-facilitator mapping is internal unless the facilitator has published the address themselves. It informs subject selection and our monitoring work, and any such observation used as evidence in a report is cited with its query and block range and is reproducible like any other claim we publish (see §10).

## 2. Safe harbor (ours, and what we respect)

Our testing follows these constraints:

- Test networks and test assets only, unless a written engagement explicitly scopes mainnet observation
- No denial-of-service, load testing, or resource exhaustion against systems we do not operate
- No access to, or exfiltration of, data belonging to third parties
- No social engineering of any kind
- Every material claim in a published report resolves to an on-chain artifact (transaction hash or re-executable contract call) or a hash-committed raw artifact in our evidence manifest
- **We withhold weaponizable detail.** Published reports characterize findings at the level needed to understand and fix them. Exploit-ready payloads against unpatched live systems are shared only with the maintainer, never published.

We expect maintainers to extend the same good faith: research conducted under this policy and reported through the channel in §3 should not be met with legal threats. We disclose to fix and to inform. We do not accept payment conditional on withholding or altering findings.

## 3. Contact channel

To reach Settle about an assessment, a finding, or this policy:
- **GitHub Security Advisory** on the relevant Settle repository (private by default), or
- **The Settle Ledger repository** issue tracker for non-sensitive process questions.

We aim to acknowledge within 72 hours (Malaysia time, UTC+8). Acknowledgment targets are intent, not guarantees; a slow week is not a policy breach.

## 4. Disclosure windows — scaled by severity

The notice period between private delivery of a draft report and publication scales with the finding's impact:

| Class | Definition | Notice before publication |
|---|---|---|
| **Method demonstration / informational** | No payment-integrity or security impact; robustness, conformance, or documentation observations; negative results | **14 days minimum** |
| **Security impact** | Credible path to loss of funds, unauthorized settlement, or payment-integrity violation | **45 days** (aligned with CERT/CC) |
| **Complex remediation** | Security impact where the fix is architectural or cross-party | **Up to 90 days**, negotiated with the maintainer |

Rules governing every window:
- **Engagement extends (objective test).** The clock pauses while the maintainer is engaging substantively, and resumes otherwise. Test: within any rolling 7-day span, the maintainer has taken at least one substantive action — a technical question about the evidence, a proposed fix, a patch, or a request for re-test with a date. Holding replies ("we're looking into it") do not pause the clock. We log the test's application and will show the log if asked.
- **When in doubt, longer.** If severity classification is uncertain, the longer window applies. Mis-classification never accelerates publication.
- **Silent-patch trigger.** If a maintainer ships a quiet fix for a reported issue without acknowledging the report, we may publish immediately, noting the patch and the timeline.
- **Active-exploitation trigger.** If an issue we discover is already being exploited in the wild, we compress to whatever window the situation demands, including immediate publication, with the maintainer notified simultaneously.
- **Total-duration cap.** Engagement may extend a window, but total time from private delivery to publication will not exceed twice the base window (28 days method-demonstration, 90 security, 180 complex), regardless of ongoing engagement, absent a written agreement to extend further that is signed by both parties — a maintainer's request alone does not extend the cap. Good-faith work buys real time; the cap is the wall slow-walking hits.
- Classification rationale is stated in the published report itself.

## 5. What maintainers receive, and when

Before any publication, the maintainer of the subject software receives, privately:
1. The complete draft report,
2. The raw artifacts and reproduction material we relied on, with the reproduction method documented,
3. The classification (§4) and intended publication date,
4. An explicit invitation to correct anything we mischaracterized — we fix factual errors regardless of where the correction comes from, and corrections are logged in the report's method-transparency section.

If a maintainer does not respond within the window, we publish on schedule; readers of payment infrastructure have a legitimate interest in timely, evidence-backed information. The report states only that the courtesy window was given and elapsed. We do not editorialize about non-response.

## 6. Multi-party coordination

x402 findings can span the specification, an SDK, and a facilitator simultaneously. When a finding touches more than one party:
- All affected parties we can identify receive the draft at the same time, and we say so in each delivery.
- The window is governed by the most severe affected component's classification.
- If parties disagree about ownership of the fix, we describe the disagreement factually in the report; we do not adjudicate it.
- Where a finding is in the x402 specification itself, the report says so and characterizes implementations as affected-by-spec, not defective.

## 7. Conflicts of interest

Settle is, or intends to become, a commercial laboratory. The parties we assess may be current customers, prospective customers, or operators of competing stacks. Rules:

- **No paid suppression, ever** (§2). This includes existing customers.
- Classification, evidence, and publication timing are determined by this policy, never by commercial relationship. A finding against a paying customer is classified and published exactly as a finding against anyone else.
- Every report's header states the nature of any existing commercial or consent relationship with the subject (paid engagement, consent-based assessment, or none/self-administered), so a reader can weight independence for themselves.
- We do not assess any implementation in which Settle holds equity, tokens, a revenue share, an advisory seat, or any other interest whose value depends on the subject's commercial success — as distinct from a fixed fee for an assessment itself.
- **Equal rigor, demonstrably.** A paid engagement that yields a published report publishes its evidence manifest and falsified-hypothesis log on the same terms as a self-administered assessment, so any reader can check whether paid work meets the same standard as independent work.

## 8. CVEs and coordination

For findings with security impact, we support CVE assignment and will request one where a CNA is available (typically via the maintainer's GitHub Security Advisory, which can serve as CNA), referencing the CVE in the published report. Settle is not itself a CNA. Where no CVE is issued for an eligible finding, we publish under a GitHub Security Advisory identifier or a documented Settle-ID (format: SETTLE-YYYY-NNN) and note the attempt.

## 9. Attribution and credit

- Reporters, maintainers, and collaborators who contribute materially to a finding or its fix are credited by name in the published report, unless they ask not to be.
- Settle's assessments are self-administered unless explicitly stated otherwise. Reports always state whether the subject's maintainers participated, reviewed, or consented — in the header, not the footnotes.

## 10. What we publish

Every published assessment includes: the subject (implementation, version/pinned artifact digest, network), the method, the evidence manifest (SHA-256 committed, anchored in the Settle Ledger), findings with classification, explicitly-labeled observations, limitations, and a falsified-hypothesis log recording any claims we formed and withdrew during testing.

When our declared on-chain observation (§1) informs a report — whether it drove subject selection or supplied a claim — the report says so, with the query and block range, under the same evidence discipline as every other claim. When it did not inform the report, there is nothing to disclose.

Reports are technical conformance assessments, not audits, attestations, or assurance engagements. Assessments are provided as-is; Settle makes no warranty and accepts no liability for decisions made in reliance on them.

## 11. Changes to this policy

Changes are versioned, dated, and published in the Settle Ledger with a change log. Reports published under a given policy version remain governed by that version.

---

*Settle — independent x402 conformance laboratory. Evidence over assertion.*
