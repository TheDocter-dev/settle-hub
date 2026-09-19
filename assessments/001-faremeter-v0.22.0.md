# Settle Assessment Report — Technical Conformance Assessment

**Subject:** Faremeter facilitator v0.22.0 (`@faremeter/facilitator` 0.22.0, `@faremeter/payment-evm` 0.22.0), self-hosted instance, Base Sepolia (chain ID 84532)
**Assessor:** Settle (independent x402 conformance lab)
**Report type:** Technical conformance assessment. Self-administered demonstration by Settle against its own deployment of the subject software. The subject's maintainers did not participate and have not reviewed this report. Published as a method demonstration following a maintainer courtesy window (heads-up delivered via the maintainer's designated channel — GitHub Security Advisory, per the project's SECURITY.md — on 15 September 2026; bumped in-advisory 17 September 2026; no response as of publication).
**Report version:** 1.0 — 22 September 2026
**Status:** Method demonstration. This report characterizes only the named subject, version, and network. No claim is made about any other version, network, or deployment.

---

## 1. Scope and method

Settle assessed a self-hosted Faremeter v0.22.0 facilitator on Base Sepolia testnet using black-box probes against the `/verify`, `/settle`, `/supported`, and `/accepts` endpoints, plus a controlled duplicate-settlement race executed through a minimal merchant server implementing the x402 v1 exact scheme. All testing was performed on testnet with test assets; no third-party infrastructure was involved, and no real-world value moved at any point.

**Method principles:** single-defect isolation (each probe varies exactly one property); valid-signature testing (EIP-3009 authorizations signed locally with a real key, so facilitator verdicts on signature validity are meaningful); on-chain anchoring (every material claim resolves to a transaction hash or contract call a reader can independently re-execute); and hypothesis discipline (withdrawn hypotheses are documented, Section 6). No on-chain or availability observation of third-party facilitators informed this assessment; all evidence derives from the assessor's own deployment and transactions.

**Conformance baseline.** No official x402 conformance suite exists as of this report's date; conformance herein is assessed against the invariants defined in Wang et al. 2026 and Ling et al. 2026 and against the EIP-3009 authorization model. The absence of a published baseline is the gap this laboratory exists to close.

**Domain verification (configuration validity).** The assessor confirmed the test environment was correctly configured before drawing conclusions: the Base Sepolia USDC contract (`0x036CbD53842c5426634e7929541eC2318f3dCF7e`) returns `name() = "USDC"`, `version() = "2"`, and `DOMAIN_SEPARATOR() = 0x71f17a3b2ff373b803d70a5a07c046c1a2bc8e89c09ef722fcb047abe94c9818`, matching the assessor's independently computed EIP-712 domain separator for `{name: "USDC", version: "2", chainId: 84532}` byte-for-byte. Additionally, the Faremeter handler itself reads the EIP-712 domain from the chain at startup and refuses to start on a name mismatch, providing a second, independent guard against misconfiguration.

### 1.1 Reproducibility manifest

| Component | Version / identifier |
| --- | --- |
| `@faremeter/facilitator` | 0.22.0 (npm), integrity `sha512-+jmpt6+UXfeQ7rC4cTiD5DI6SvSukQVJqWmbCq+e89xeJuXs/w69gUkTMvj+TfTksApv5jTxeDVK6315gDdnkQ==` |
| `@faremeter/payment-evm` | 0.22.0 (npm), integrity `sha512-sW7vlIoataqqajg7TIPtXODTJJCyK0zvOPx/fh8zt7Jy6KhuY3lRhHshMMEy9QJqVmFXsV9QisDxqchFgsG1Ug==` |
| `@faremeter/wallet-evm` | 0.22.0 (npm) |
| `hono` / `@hono/node-server` | 4.13.8 / 2.1.1 |
| `viem` | 2.56.5 |
| `express` (merchant server) | 5.2.1 |
| Node.js | v20.20.2 |
| Network | Base Sepolia, chain ID 84532 |
| RPC endpoint | `https://sepolia.base.org` |
| Test asset | USDC `0x036CbD53842c5426634e7929541eC2318f3dCF7e` (EIP-3009, domain `{"USDC","2",84532}`) |
| Wallets (all assessor-controlled) | settlement `0xb74338259B85c2Ffba7cDB7aFa8645ded2A9C06d`; payer `0x1517876900c068761c30120b6aC240527e2dBECA`; merchant `0x43EE4528FFB1f435313cf0d317512B9F464B90d6` |

All probe scripts, raw result files, and the instrumented merchant log accompany this report; each file's SHA-256 is recorded in Appendix B.

## 2. Finding 1 — Inconsistent failure signalling across verify/settle (low severity, robustness)

**Statement.** Failure signalling is inconsistent across the verify/settle surface — the same logical class (signature/authorization failure) returns different HTTP statuses (200 and 500) with different message strings, so integrators must parse response bodies rather than rely on status codes. Robustness only; no payment-integrity implication (the x402 specification does not mandate status-code semantics).

**Evidence.**

| Probe | Condition introduced | Observed |
| --- | --- | --- |
| A1 | Unparseable signature bytes at `/verify` | HTTP 500, `"Signature verification failed"` |
| A2 | Same at `/settle` | HTTP 500, `"Signature verification failed"` |
| C3 | Well-formed signature over wrong EIP-712 domain (chainId 8453) | HTTP 200, `isValid:false`, `"Invalid signature"` |
| C4 | Expired authorization | HTTP 200, `isValid:false`, `"Authorization expired"` |
| C5 | Authorized value below requirement | HTTP 200, `isValid:false`, `"Incorrect payment amount"` |
| B5/R | Distinct on-chain revert conditions at `/settle` (true replay of a consumed nonce; concurrent attempts on a nonce consumed by a winning request) | both HTTP 500, `"Transaction execution failed"` |

Two distinct signature-failure messages exist (`"Signature verification failed"` for unparseable bytes, `"Invalid signature"` for a well-formed but incorrect signature), and the HTTP status carries no reliable meaning: logically invalid payments arrive as both 200 and 500 depending on how far parsing progressed. Separately, distinct on-chain revert conditions — a true nonce replay (probe B5 attempt 2) and a concurrent settlement attempt whose nonce was consumed by a winning request (race losers) — are reported identically as HTTP 500 `"Transaction execution failed"`, an expected, known condition indistinguishable from an unexpected failure.

**Impact.** Integrators cannot branch on HTTP status and cannot distinguish an already-consumed authorization from a facilitator malfunction without parsing free-text reasons. This complicates merchant retry and reconciliation logic. There is no path to unauthorized settlement or loss of funds from this finding.

**Remediation suggestion.** Return HTTP 200 with structured `invalidReason`/`errorReason` codes for all logically determined failures, reserve 5xx for infrastructure faults, and give the consumed-authorization condition its own stable reason string.

## 3. Duplicate-settlement race (F2): controlled reproduction, negative result in this configuration

**Purpose.** Demonstrate Settle's race-reproduction method against the known F2 attack class (concurrent settlement of one payment authorization) and measure whether a paid resource can be delivered without settlement, or settled twice.

**Construction.** One fresh, valid, funded EIP-3009 authorization (value 0.001 USDC) per round; N concurrent requests through the merchant server's real verify→settle→deliver path, all sharing that authorization. Concurrency was genuine: merchant instrumentation timestamps show all 10 verifications completing across a 1,225 ms window before the first `/settle` response returned (race round 1; the other rounds show the same pattern). Rounds: control N=1, then three rounds at N=10.

**Ledger.**

| Round | N | Deliveries | Settlements | Merchant balance Δ | Invariant (Δ = settlements × 0.001) | Settlement tx |
| --- | --- | --- | --- | --- | --- | --- |
| control | 1 | 1 | 1 | +0.001 USDC | PASS | `0xb6f65ea0…79eac9ef` |
| race 1 | 10 | 1 | 1 | +0.001 USDC | PASS | `0x87628172…d7c27c8a` |
| race 2 | 10 | 1 | 1 | +0.001 USDC | PASS | `0xf0da84c8…92a7952b` |
| race 3 | 10 | 1 | 1 | +0.001 USDC | PASS | `0xe1f765f9…2b944125` |

(Full hashes in Appendix A.)

**Result.** Negative in this configuration. Every raced round: all concurrent requests passed `/verify` (the verify endpoint is stateless and does not deduplicate nonces — conformant, since EIP-3009 nonces are consumed at settlement, not verification); exactly one settlement succeeded on-chain; the losing requests received HTTP 402 and no content was delivered. No double settlement, no delivery without settlement. The merchant balance invariant held in all rounds and is independently checkable on-chain.

**Attribution.** The window is closed by two cooperating properties: (i) merchant-side ordering — the merchant server settles before delivering (a property of this assessor-written server, not enforced by the facilitator); and (ii) EIP-3009 on-chain nonce enforcement (`authorizationState`), which makes a second settlement of the same authorization revert regardless of facilitator behavior. Neither property is guaranteed by the facilitator for all deployments: a merchant that delivers on verification, or streams content before settlement confirmation, reopens the window. That exposure class is merchant-side and is assessed through deployment review, not facilitator testing.

## 4. Observations (explicitly not findings)

- `/verify` performs no balance check — a validly signed authorization from an unfunded payer verifies `isValid:true`. Conformant: verification and settlement are distinct operations; balance is enforced on-chain at settlement.
- The v1 payload `network` string is not cross-checked against requirements; chain binding is carried by the EIP-712 domain `chainId`. Conformant for x402 v1.
- A signature over the wrong domain chainId is correctly rejected.
- `/supported` accurately advertises v1 (`base-sepolia`) and v2 (`eip155:84532`) kinds; both verify paths accept valid payloads.

## 5. Limitations

- Single implementation (Faremeter v0.22.0), single network (Base Sepolia), single scheme (exact). No statement about other facilitators, versions, networks, or schemes.
- Testnet only; no mainnet behavior is characterized.
- Concurrency results are probabilistic; three raced rounds plus control establish reproducibility for this configuration, not an impossibility proof.
- The merchant server is minimal and assessor-written; production middleware may order operations differently (see Section 3 attribution).

## 6. Falsified-hypothesis log (method transparency)

Two hypotheses were formed during testing, subjected to single-defect isolation probes, and withdrawn when the evidence falsified them:

1. **"Network mismatch is misreported as a signature failure."** Initial probes paired a network-string change with an invalid signature, making the failure attribution ambiguous. Valid-signature isolation probes showed the facilitator's signature-failure response was correct; the hypothesis was withdrawn.
2. **"`/verify` omits a required network check."** A payload whose `network` string disagreed with requirements verified successfully. Specification review showed the v1 network string is transport metadata and binding lives in the typed-data domain; the observed behavior is conformant. Withdrawn.

These withdrawals are included because the method's value depends on claims dying when the evidence kills them.

## Appendix A — On-chain artifacts (Base Sepolia, verifiable via sepolia.basescan.org)

| Artifact | Tx hash |
| --- | --- |
| Funding: 0.02 ETH → settlement wallet (15 Sep 2026, 18:36 MYT; MetaMask-sponsored smart-account execution, 0.02 ETH internal transfer verified via call trace) | `0x1990b0ed0ae19c529898f846844e9eb405f1f4578c9341b7ad805a159fac31ae` |
| Funding: 20 USDC → payer wallet (Circle testnet faucet) | faucet distribution |
| Settlement (B5) | `0xbfc73c65aeb6165061a35a05f4f99d6cf65a554be6f3e14f36da5ac4eb6275ab` |
| Settlement (control) | `0xb6f65ea01fa46a7149cb88f097395878b5f2aaa7ef8f9530d7e2c38d79eac9ef` |
| Settlement (race 1) | `0x8762817260fb706377781128070483ab36c2f4ebe2de0e311fde4315d7c27c8a` |
| Settlement (race 2) | `0xf0da84c8f33278b9afc62721aeaa39327c8260d485b985c73b3a021492a7952b` |
| Settlement (race 3) | `0xe1f765f956879310711dabb74c0d6975f0aeff1deb1d9d8ec0ca73d32b944125` |

**Cost accounting (per phase).** Start: settlement wallet 0.02 ETH, payer 20 USDC, merchant 0 USDC. After B5: payer 19.999 USDC, merchant 0.001 USDC. After race rounds (4 settlements): payer 19.995 USDC, merchant 0.005 USDC. Gas: funding tx 0 ETH (sponsored by MetaMask); five facilitator settlements ≈0.0000032 ETH total. Total value consumed: 0.005 test USDC + gas; real-world value $0.00 (all testnet assets).

## Appendix B — Raw artifact hashes (SHA-256)

| File | SHA-256 |
| --- | --- |
| results-semantics.json | `3e5cf9f5…b5edb8` |
| results-probes-b.json | `e04d2d2b…e665f8` |
| results-isolation.json | `18922098…dc5fa160` |
| results-b4v2.json | `0bbdd85a…de615a23` |
| results-b5.json | `73ae9f70…ccd9a783` |
| results-race.json | `b79e5637…45684dd6` |
| merchant-log-race.txt | `4ab8281b…e20fb1` |
| facilitator.mjs | `de6e26ab…4da0d052` |
| merchant.mjs | `45875caf…2c17f604` |
| test-semantics.mjs | `3bcbb81b…2722fba8` |
| test-probes-b.mjs | `24d25e20…c0792ad3` |
| test-isolation.mjs | `8466b58b…49fa208d` |
| test-b4v2.mjs | `f8d23c37…0bffeb3` |
| test-b5.mjs | `819f7834…910b9fce` |
| test-race.mjs | `53fe8060…1c652f6a` |

(Full hashes in `artifact-hashes.txt`, itself sha256 `2e821d3c26ebd72a29fab5f049028006ed7b8bd5e62756ad99dde8b9d188233f`; anchored in the Settle Ledger at `anchors/001/MANIFEST.md` on publication.)

---

*Prepared by Settle. This is a technical conformance assessment, not an audit, attestation, or assurance engagement. Questions: via the Settle Ledger repository.*