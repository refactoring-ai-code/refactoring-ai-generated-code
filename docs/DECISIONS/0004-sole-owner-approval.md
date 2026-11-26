# ADR 0004 — Sole project-owner approval authority

**Decision date:** 2026-10-27  
**Status:** APPROVED by Burkay Çakar (@cakarburkayy)  
**Superseded:** 2026-11-25 by [ADR 0007](0007-local-llm-and-approval-authority.md). The single-final-approver rule and the `GENESIS-OWNER-APPROVED` marker below are historical; approvals follow the v3 GitHub development workflow.  
**Supersedes:** Requirements for an independent approval from İsmail, Uğur or any other team member during implementation/release transitions.

Burkay Çakar is the project planner and **only required final approver** for architecture, requirements, developer handoffs and PR merges. Peer reviews remain optional and may still identify defects; they do not independently authorize code. For ordinary future PRs, the trusted governance gate expects an authenticated GitHub PR conversation comment with the exact body `GENESIS-OWNER-APPROVED: <CURRENT_PR_HEAD_SHA>` from `@cakarburkayy`. A changed head requires fresh owner approval. Approval does not waive genuine applicable CI, required dependencies, safe Git publication, sandbox/security validation or evidence-based product release gates.

The owner approved both Turkish and English SRS v0.4.0 (62 FR + 17 NFR each), the complete seven-language P0 scope, and merging PR #38/#39. PR #38 was merged into main at `5754ed6eeaeef0cce9bc46264c8baeddfb62f88c`, as **pre-Genesis preparation that consumes no rotation turn**. PR #39 is a separate governance/SRS migration which must be merged after successful current-head checks, with the accepted code history preserved.

Developer ownership rotation remains Burkay → Cafer → Alperen Enes Yaman → İsmail → Taha Uğur Toyran → Burkay. No transition occurs without verified task completion and an accepted handoff. **Two end-user approval gates inside the product remain distinct mandatory functional requirements.**

The 34-task/69-edge **planned** dependency graph and original 31-task/54-edge native graph must be reconciled and independently audited; mere approval cannot promote unverified implementation or links to VERIFIED.
