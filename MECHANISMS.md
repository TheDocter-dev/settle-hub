# MECHANISMS.md — mechanism inventory (internal)

One row per mechanism any public artifact claims. Types: **job** (runs unattended), **procedure** (a human does it), **planned** (no implementation yet — public text must use future tense with a date). The consistency gate fails any present-tense mechanism claim in a public artifact that has no job/procedure row here with an observed run.

| name | type | implementing path / document | owner | last-observed run |
|---|---|---|---|---|
| Liveness observer | job | `/root/settle-catalog/liveness.py`, root crontab `*/15 * * * *` | root | 2026-09-22 (crontab verified on-box) |
| Chain catalog | job | `/home/settlecat/catalog/cron-ledger-wrapper.sh`, settlecat crontab `17 6 * * *` | settlecat | 2026-09-22 (crontab verified on-box) |
| Dormancy banner (manual interim) | procedure | operator posts banner per independence-policy.md Continuity section | operator | never triggered (0 days silence to date) |
| Dormancy banner (automated) | planned | activation target 2026-09-30 | hub | — |
| Key escrow | planned | target 2026-10-31; design in independence-policy.md §Key escrow (planned) | operator + trustee (TBD) | — |
| PyPI release poll (manual) | procedure | manual check; date recorded in Ledger README ("Last manual check") | operator | 2026-09-22 |
| PyPI release poll (automated) | planned | activation target 2026-09-30 (ships with banner job) | — | — |
| OTS stamping | procedure | manual step in the freeze procedure; outputs in `settle-ledger` `anchors/001/` | operator | 2026-09-19 (anchor-001) |
| Consistency gate | procedure | no implementing script — manual diff across governing documents | operator + AI assistance | 2026-09-19 |
| Ledger anchor procedure | procedure | manual; artifacts in `settle-ledger` `anchors/` | operator | 2026-09-19 (anchor-001) |
