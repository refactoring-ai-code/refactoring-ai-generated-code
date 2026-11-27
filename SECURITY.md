# Security and data handling

Never commit API keys, `.env`, credentials, private academic documents, student identifiers, raw customer/user code or private experiment notes. Use placeholders in `.env.example`. Report sensitive vulnerabilities through the repository owner's private contact channel rather than a public issue; no private vulnerability-reporting service is claimed enabled.

The planned product must treat uploaded code as untrusted: immutable V0, safe archive extraction, separate worker sandbox, no host execution, network denied by default, resource/time limits, read-only frozen tests, masking and explicit cloud/dynamic-execution consent. See the [architecture](docs/ARCHITECTURE.md).

Governance CI uses ephemeral GitHub-hosted runners and read-only tokens. The task dependency audit runs only code from current trusted main and checks head and policy freshness. Product changes must stay within their task scope. The issue-graph sync is the sole issue-write job, owner-only on pushes to main or manual dispatch on main; it never checks out external PR code. All workflows avoid persistent checkout credentials and pin the official checkout action commit.

`security-checks` is a deterministic credential/private-artefact hygiene check, not a full SAST/SCA or proof of security. Real application dependency scanning, sandbox validation and security analysis belong to F01-ENV/F06/F07A. No self-hosted runner or external API spend is enabled by this setup.

The hygiene checker rejects symlinks rather than following host paths, checks uploads/private directories at any depth, and retains ASCII credential detection in invalid-UTF-8 files. It remains a limited deterministic check: a real scanner, dependency audit, security review and isolated product execution are separate tasks.
