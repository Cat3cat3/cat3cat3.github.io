# 03-电脑租赁业务 Instructions

## Owner Agent
`rental-ops` owns this project.

## Permissions
- L0/L1 allowed: read and summarize inventory and renewal context; prepare quotes, reminders, delivery notes, and task or run-log drafts without sensitive data.
- L2 examples: writing customer information, prices, contracts, inventory commitments, or formal delivery records requires a specific approval.
- L3 examples: deleting or overwriting records, sending a customer message, signing or transmitting a contract, or pushing related code requires a separate specific approval.

## Data boundaries
权威数据仅位于 `03-电脑租赁业务/` 的 approved authoritative files named by the task. `共享代码库/` is read-only technical backing storage unless separately approved. Cross-project access is read-only, path-specific, and must not copy customer, pricing, contract, or operating data into public logs.

## Validation and escalation
For any write, re-read the named target and check required fields, document structure, or the approval scope; L2/L3 additionally require `taskctl snapshot` before writing. Escalate to `catmaker-orchestrator` for ambiguous authority, a cross-project write, an active writer, missing source SHA-256, or pending L2/L3 approval; escalate technical multi-file or high-risk review to Codex.
