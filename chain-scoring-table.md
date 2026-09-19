# Chain-Scoring Table — Solana / Polygon / Arbitrum / Ethereum / Optimism

**Status: v3 FINAL, 18 Sep 2026 — Fable-confirmed. v2 corrections held; v3 fixes the queue chronology (port moved to 31 Oct so the arrows match the dates; Solana genuinely last at 15 Nov) and the withdrawal now lives in backbone amendment v1.4. Backbone v1.2 §2: chains enter the build queue by EV on the seven parameters. Every figure carries denominator, source, date.**

## Denominator discipline (read before any number below)

- **Bitquery figures = EIP-3009 activity, not x402-attributed activity.** "USDC signed-authorisation settlements" (Bitquery, 6 Sep 2026, August 2026 window) counts *every* `transferWithAuthorization` on the chain — exactly the population Settle's v3 attribution layer exists to filter. All Bitquery-sourced cells below are **upper bounds on x402 activity**, labeled as such.
- **TRM Labs figures = facilitator-attributed** (TRM, 9 Sep 2026: ~$52.7M across 198.9M settlements mediated by *known x402 facilitators* since May 2025, Base+Solana+Polygon). The ~50× dollar gap between TRM's cumulative attributed figure and Bitquery's single-month raw count ($2.59B, Aug 2026) *is* the denominator difference. For any x402 claim, prefer the attributed figure; cite Bitquery only as the labeled upper bound.
- **Internal March 2026 wash figure (36%)** was measured on raw EIP-3009 counts pre-attribution — it is a wash **upper bound**, not an estimate.

## Headline activity data (upper-bound EIP-3009 population unless labeled attributed)

| Chain | Share of payments | Share of dollars | Payments | Dollars | Median | Characterization (source, date) |
|---|---|---|---|---|---|---|
| Base | 53.1%* | 1.4%* | 9,698,150* | $35.9M* | $0.006* | Agent metering + only merchant checkout (Bitquery, Aug 2026*) |
| Polygon | 44.5%* | 5.3%* | 8,132,190* | $136.5M* | $0.01* | "Trading venue on top, one-cent cycle underneath" (Bitquery, Aug 2026*) |
| Arbitrum | 1.9%* | 90.0%* | 339,249* | $2.33B* | $25.61* | "Almost entirely one contract: cross-chain bridging" (Bitquery, Aug 2026*) — **bridge EIP-3009 flow, out of scope of x402 attribution by Settle's own filter** |
| Ethereum | 0.3%* | 3.4%* | ~55k* | ~$88M* | — | Rounding error in denominator (Bitquery, Aug 2026*) |
| Optimism | 0.2%* | 0.01%* | ~37k* | ~$0.26M* | — | Rounding error in denominator (Bitquery, Aug 2026*) |
| Solana | contested: ~50–65% of x402 tx volume by source and window (Dune 49.7% weekly, 9 Feb 2026 — stale; Solana Foundation self-report ~65% of 2026; the backbone's "~70%" has no source and is withdrawn) | unmeasured | 869,392 sub-cent payments/day, 15,070 sponsors, no payee >5.4% (Bitquery, Aug 2026, separate SVM method) | unmeasured | sub-cent | Broad distribution; see (f) — does not rule out wash |

*Bitquery EIP-3009 upper bound, shares of 18.3M payments / $2.59B across the 5 measured EVM chains, Aug 2026.

## Seven-parameter scoring

| # | Parameter | Solana | Polygon | Arbitrum |
|---|---|---|---|---|
| a | **Activity share** | Large by count (869k sub-cent/day, Bitquery Aug 2026); share contested 50–65% by source/window | 44.5% of payments, 5.3% of dollars (upper bound*) | 1.9% of payments (upper bound*); dollar figure excluded from x402 reasoning — bridge flow |
| b | **Attribution-method fit** | **Known, declared in the Solana design pre-registration** (feePayer ≠ token owner + spec-mandated ComputeBudget/TransferChecked layout fingerprint — arguably better than EIP-3009 because the layout is x402-specific); **unproven in implementation** | Excellent: same EIP-3009 `AuthorizationUsed` on Circle native USDC as Base; port = chain config + USDC address; must declare native vs bridged USDC.e | Excellent: same as Polygon; same declaration requirement |
| c | **Data-access cost** | Higher: high-throughput RPC for SPL scan (Helius/Triton tier); this, not method, is Solana's real cost row | Low: public RPCs | Low: public RPCs |
| d | **Facilitator presence** | CDP (exact only on Solana, CDP docs Sep 2026); PayAI (largest Solana x402 facilitator, Jun 2026); thirdweb | CDP; PayAI (hosted-only — no consent path yet) | CDP; PayAI (added 12 Jun 2026, hosted-only) |
| e | **Dollar exposure** | Unmeasured — open gap, needs SPL-USDC value scan or dated third-party figure with clean denominator | $136.5M/mo (upper bound*) | **Unmeasured for x402** — Bitquery's $2.33B is bridge EIP-3009, out of scope by Settle's filter; agentic dollar exposure likely small; honest expectation: **sparse catalog, mostly bridge-excluded — a near-empty first run is the method working, not failing** |
| f | **Wash/incentivized share** | **Unknown, pending own measurement.** Sub-cent scale + broad distribution rules out a single operator but NOT wash: sub-cent at this scale is also the incentive-farming/airdrop-churn signature — Polygon's one-cent cycle one decimal place smaller | High signature: median $0.01 one-cent cycle (Bitquery Aug 2026); internal March figure (36%) is an upper bound; current-window estimate comes from the port's first runs — count claims gated on it | Structurally concentrated (bridge), not wash; bridge flow excluded by pre-registered filter |
| g | **Subject availability** | Yes: PayAI (Solana-first, independent) | **Self-hosted x402.rs on Polygon — exactly as assessable as 002's Base instance (x402.rs supports multiple EVM chains by configuration); shares a rig with the port itself** | Same: self-hosted x402.rs on Arbitrum |

## Scoring outcome (v2, post-Fable)

**What to build is unchanged; why is corrected.**

1. **Polygon + Arbitrum combined EVM port — SCORED GO, 31 Oct** (moved earlier: near-zero marginal cost means there is no reason to wait for 30 Nov; landing in October also builds the multi-chain scaffolding the Solana report cites)**.** Grounds: near-zero marginal cost (same code, second chain free) and subject availability (self-hosted x402.rs on either chain). ~~Polygon gives count, Arbitrum gives dollars~~ — **deleted**: Arbitrum's dollar share is the false positive the catalog exists to catch (bridge flow, not x402). Honest expectation set in advance: the Arbitrum attribution catalog will be sparse and mostly bridge-excluded; that is the filter working.
2. **Solana tier one — SCORED, 15 Nov, gated on the 30 Sep design doc.** Case rests on count share and the declared (pre-registered) attribution method; open measurements are wash share (f) and dollar exposure (e). If the SPL-attribution design does not survive Fable review, the date takes the damage, not the claim.
3. **Queue, chronological (dates match the arrows):** Base (live) → **Polygon+Arbitrum port (31 Oct)** → **Solana tier one (15 Nov, gated on the 30 Sep design doc)**. Ethereum and Optimism stay on the watch list — rounding-error shares in the current denominator.

## Open data gaps

- Solana dollar exposure (e): SPL-USDC value scan or clean-denominator third-party figure.
- Polygon wash share (f): port's first runs replace the upper bound with a measurement.
- Solana wash share (f): first tier-one runs measure it; no third-party figure with a clean denominator exists as of 18 Sep 2026.
- Solana facilitator census beyond PayAI/CDP/thirdweb (d): x402scan registry pull at design-doc time.

## Sources (all dated)

- Bitquery, "x402 Protocol: $2.6B a Month Across 5 Chains", 6 Sep 2026 (Aug 2026 window; EIP-3009 population — upper bound, not x402-attributed)
- TRM Labs, "Who's Actually Paying? Measuring AI Agent Payments Onchain", 9 Sep 2026 (facilitator-attributed; preferred method)
- Coinbase CDP Facilitator docs, supported networks/schemes, Sep 2026
- PayAI blog/docs, 12 Jun 2026
- Dune/SolanaFloor, 9 Feb 2026 (Solana weekly share 49.7% — stale); Solana Foundation self-report ~65% of 2026
- Internal: March 2026 wash figure = upper bound (pre-attribution raw counts)
