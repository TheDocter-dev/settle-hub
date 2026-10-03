# MECHANISMS.md — mechanism inventory (internal)

One row per mechanism any public artifact claims. Types: **job** (runs unattended), **procedure** (a human does it), **planned** (no implementation yet — public text must use future tense with a date). The consistency gate fails any present-tense mechanism claim in a public artifact that has no job/procedure row here with an observed run.

| name | type | implementing path / document | owner | last-observed run |
|---|---|---|---|---|
| Liveness observer | job | `/root/settle-catalog/liveness.py`, root crontab `*/15 * * * *` | root | 2026-09-22 (crontab verified on-box) |
| Chain catalog | job | `/home/settlecat/catalog/cron-ledger-wrapper.sh`, settlecat crontab `17 6 * * *` | settlecat | 2026-09-22 (crontab verified on-box) |
| Dormancy banner (manual interim) | procedure | superseded 2026-10-02 by the automated row below; retained as fallback only | operator | never triggered (superseded) |
| Key escrow | planned | target 2026-10-31; design in independence-policy.md §Key escrow (planned) | operator + trustee (TBD) | — |
| PyPI release poll (manual) | procedure | manual check; date recorded in Ledger README ("Last manual check") | operator | 2026-09-22 |
| PyPI release poll (automated) | job | `/home/settlecat/poll-pypi.py`, settlecat crontab `23 6 * * *`; staged rows to `/home/settlecat/poll-staging/releases` (settlecat-owned; never the Ledger clone); public detection = issue opened via issues:write-only PAT on TheDocter-dev/settle-ledger (`/home/settlecat/.poll-issue-token`, settlecat:settlecat 600, **rotate 2026-10-30**); no Contents access, no git ops in job | settlecat | 2026-09-30 (first live run); holder migration to settlecat + staging dir 2026-10-02 |
| Dormancy banner (automated) | job | scheduled GitHub Pages rebuild of settle-site (GitHub Actions; push + daily schedule + dispatch triggers); dormancy signal = age of newest signed commit on TheDocter-dev/settle-ledger > 30d via public API; banner injected at edge when dormant; no commits, no stored credentials | GitHub Actions | 2026-10-02T08:58:26Z (first run) |
| OTS stamping | procedure | manual step in the freeze procedure; outputs in `settle-ledger` `anchors/001/` | operator | 2026-09-19 (anchor-001) |
| Consistency gate | procedure | no implementing script — manual diff across governing documents | operator + AI assistance | 2026-09-19 |
| Deploy verification gate | procedure | after any hosting or DNS change: (1) hash deployed output vs previous deploy; (2) verify BOTH https://settleverify.com/ and https://www.settleverify.com/ return 200, or a 301 whose target returns 200, each with a valid certificate | operator + AI assistance | 2026-10-03 (dual-hostname line added after accuracy entry 13) |
| Ledger anchor procedure | procedure | manual; artifacts in `settle-ledger` `anchors/` | operator | 2026-09-19 (anchor-001) |
