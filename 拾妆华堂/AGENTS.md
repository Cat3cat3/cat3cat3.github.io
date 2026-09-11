# 01-拾妆华堂 Instructions

## Owner Agent
`studio-ops` owns this project. `content-growth` may prepare content drafts within this project but does not replace the owner for operational data.

## Permissions
- L0/L1 allowed: read and summarize project materials; prepare product, service, reception, order-process, and content drafts; update task status and run logs without copying sensitive data.
- L2 examples: writing customer records, operating-database records, prices, orders, or formal service commitments requires a specific approval.
- L3 examples: deleting or overwriting project records, sending external messages, publishing content, or pushing related code requires a separate specific approval.

## Data boundaries
权威数据仅位于 `01-拾妆华堂/` 的 approved authoritative files named by the task. `共享代码库/` is read-only technical backing storage unless a separately approved engineering task names it. Cross-project access is read-only and limited to the minimum referenced path; do not copy data into this project or a public log.

## Validation and escalation
For any write, re-read the named target and check the task's required fields or document structure; L2/L3 additionally require `taskctl snapshot` before writing. Escalate to `catmaker-orchestrator` for an unclear authority, a cross-project write, an active writer, missing source SHA-256, or any L2/L3 action awaiting approval; escalate technical multi-file or high-risk review to Codex.
