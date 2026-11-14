/* Generated from approved CIR/OpenAPI 1.0.0. Run npm run contracts:sync; do not edit. */

/**
 * artifact: identifier resolved by the future authorized artifact service.
 */
export type Id = string;
/**
 * Artifact MIME type.
 */
export type MediaType = string;
/**
 * Masking/review status; not a claim of scanner success.
 */
export type Redaction = "MASKED" | "NO_SENSITIVE_CONTENT" | "UNREVIEWED" | "FAILED";
/**
 * SHA-256 of actual artifact bytes, distinct from a Git object ID.
 */
export type Sha256 = string;
/**
 * Opaque artifact inventory with actual content hashes and redaction metadata.
 */
export type Artifacts = Artifact[];
/**
 * artifact: redacted failure/raw-rejection receipts; invalid proposals need not be admitted as valid PatchCandidates.
 */
export type ArtifactIds = string[];
/**
 * evidence: references retaining the failure or actual attempt outcome.
 */
export type EvidenceIds = string[];
/**
 * Execution outcome, independent of behavioral and quality results.
 */
export type ExecutionStatus = "COMPLETED" | "FAILED" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * Explicit failure category, or null for completed/not-yet-failed work.
 */
export type FailureKind =
  | (
      | "PROVIDER_ERROR"
      | "TIMEOUT"
      | "COMPILATION_FAILURE"
      | "TEST_FAILURE"
      | "SECURITY_REJECTION"
      | "CONFLICT_REJECTION"
      | "CANCELLED"
      | "ENVIRONMENT_BLOCKER"
      | "CONTRACT_REJECTION"
    )
  | null;
/**
 * attempt: identifier; never erased after failure.
 */
export type Id1 = string;
/**
 * job: parent refactoring job.
 */
export type JobId = string;
/**
 * One initial candidate plus at most two corrections.
 */
export type Number = number;
/**
 * Failure/unavailable/not-run explanation, or null after completion.
 */
export type Reason = string | null;
/**
 * Whether this planned attempt actually started.
 */
export type Started = boolean;
/**
 * Failure-inclusive attempt ledger; started and planned populations remain distinct.
 */
export type Attempts = Attempt[];
/**
 * Trusted immutable/frozen artifact flag.
 */
export type Frozen = boolean;
/**
 * file: identity of one source file in the snapshot.
 */
export type Id2 = string;
/**
 * True for a linked entry; never eligible as a patch target.
 */
export type IsSymlink = boolean;
/**
 * Canonical repository-relative path, with forward slashes.
 */
export type Path = string;
/**
 * Trusted frozen or protected test flag.
 */
export type ProtectedTest = boolean;
/**
 * SHA-256 of the original file bytes.
 */
export type Sha2561 = string;
/**
 * Manifest snapshot that owns this file identity.
 */
export type SubjectSha256 = string;
/**
 * Source file inventory by snapshot/path, including symlink, frozen and protected-test flags.
 */
export type Files = FileIdentity[];
/**
 * FIXTURE examples do not claim real tool/model execution.
 */
export type Mode = "FIXTURE" | "INTERCHANGE";
/**
 * Typed CIR records in a closed graph; duplicate or wrong-kind identifiers are rejected.
 *
 * @minItems 1
 */
export type Records = [
  (
    | SourceLocation
    | Symbol
    | DependencyEdge
    | Evidence
    | Finding
    | Metric
    | TestResult
    | Capability
    | LanguageAdapterCapabilities
    | IssueSelection
    | ContextPackage
    | PatchCandidate
    | ValidationResult
  ),
  ...(
    | SourceLocation
    | Symbol
    | DependencyEdge
    | Evidence
    | Finding
    | Metric
    | TestResult
    | Capability
    | LanguageAdapterCapabilities
    | IssueSelection
    | ContextPackage
    | PatchCandidate
    | ValidationResult
  )[]
];
/**
 * Exclusive 1-based Unicode-scalar column; null only for unresolved coordinates.
 */
export type EndColumn = number | null;
/**
 * 1-based end line; range end must lexicographically follow range start.
 */
export type EndLine = number | null;
/**
 * file: reference, or null when unresolved.
 */
export type FileId = string | null;
/**
 * Original source-file SHA-256, or null when unresolved.
 */
export type FileSha256 = string | null;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id3 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind = "SourceLocation";
/**
 * Portable source path; null only for an unresolved location.
 */
export type Path1 = string | null;
/**
 * Explicit unresolved reason, otherwise null.
 */
export type Reason1 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt = string;
/**
 * RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved.
 */
export type Resolution = "RESOLVED" | "UNRESOLVED";
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion = "1.0.0";
/**
 * Analysis ID; analysis: prefix; fresh for a repeat analysis.
 */
export type AnalysisId = string;
/**
 * SHA-256 of the immutable source manifest bytes.
 */
export type BaselineSha256 = string;
/**
 * Project registry ID; project: prefix.
 */
export type ProjectId = string;
/**
 * Execution run ID; run: prefix; never reused for a retry.
 */
export type RunId = string;
/**
 * Git object SHA-1 of the source, not a file SHA-256.
 */
export type SourceRevision = string;
/**
 * Immutable project version ID; version: prefix.
 */
export type VersionId = string;
/**
 * Inclusive 1-based Unicode-scalar column; a tab and an emoji each count as one scalar.
 */
export type StartColumn = number | null;
/**
 * Inclusive 1-based line; LF and CRLF each separate one logical line.
 */
export type StartLine = number | null;
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2561 = string;
/**
 * Optional symbol: reference; null means no resolved symbol.
 */
export type SymbolId = string | null;
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds1 = string[];
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id4 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind1 = "Symbol";
/**
 * One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing.
 */
export type Language = "JAVA" | "PYTHON" | "JAVASCRIPT" | "TYPESCRIPT" | "CSHARP" | "GO" | "CPP";
/**
 * location: source range associated with a symbol.
 */
export type LocationId = string;
/**
 * Observed human-readable identity or metric name; not a substitute for stable typed IDs.
 */
export type Name = string;
/**
 * Null means visibility is unknown; it is not equivalent to private.
 */
export type PublicApi = boolean | null;
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason2 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt1 = string;
/**
 * RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved.
 */
export type Resolution1 = "RESOLVED" | "UNRESOLVED";
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion1 = "1.0.0";
/**
 * Observed symbol signature; null when it cannot be established.
 */
export type Signature = string | null;
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2562 = string;
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds2 = string[];
/**
 * symbol: source of the observed dependency relationship.
 */
export type FromSymbolId = string;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id5 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind2 = "DependencyEdge";
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason3 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt2 = string;
/**
 * CALL, READ, WRITE, IMPORT, INHERIT or UNKNOWN; uncertain targets remain unresolved.
 */
export type Relationship = "CALL" | "READ" | "WRITE" | "IMPORT" | "INHERIT" | "UNKNOWN";
/**
 * RESOLVED versus UNRESOLVED; coordinates or dependency targets cannot be fabricated to appear resolved.
 */
export type Resolution2 = "RESOLVED" | "UNRESOLVED";
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion2 = "1.0.0";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2563 = string;
/**
 * symbol: dependency target, or null with an unresolved reason.
 */
export type ToSymbolId = string | null;
/**
 * actor: authenticated human reviewer identity for HUMAN evidence; otherwise null.
 */
export type ActorId = string | null;
/**
 * artifact: opaque reference to the attributed evidence artifact, never a local absolute path.
 */
export type ArtifactId = string;
/**
 * Required when confidence is unknown; otherwise null.
 */
export type Reason4 = string | null;
/**
 * Normalized confidence or explicit null.
 */
export type Value = number | null;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id6 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind3 = "Evidence";
/**
 * location: source references; duplication findings require both source locations.
 */
export type LocationIds = string[];
/**
 * Reported model name; not proof that an integration exists.
 */
export type Model = string;
/**
 * Provider identity; local providers are allowed.
 */
export type Provider = string;
/**
 * Exact observed model revision, or null.
 */
export type Revision = string | null;
/**
 * Why the exact revision is unknown, or null.
 */
export type RevisionReason = string | null;
/**
 * Observed non-secret generation settings, or null.
 */
export type Settings = {
  [k: string]: string | number | boolean | null;
} | null;
/**
 * Why settings are unknown, or null when known.
 */
export type SettingsReason = string | null;
/**
 * DETERMINISTIC_TOOL, HUMAN or LLM; an LLM claim cannot independently be VERIFIED.
 */
export type ProducerKind = "DETERMINISTIC_TOOL" | "HUMAN" | "LLM";
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt3 = string;
/**
 * MASKED, NO_SENSITIVE_CONTENT, UNREVIEWED or FAILED; a declaration does not implement a redactor.
 */
export type Redaction1 = "MASKED" | "NO_SENSITIVE_CONTENT" | "UNREVIEWED" | "FAILED";
/**
 * Stable originating rule identity, or null where a producer has no applicable rule.
 */
export type RuleId = string | null;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion3 = "1.0.0";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2564 = string;
/**
 * symbol: references supporting the attributed evidence.
 */
export type SymbolIds = string[];
/**
 * Why configuration is unavailable, or null when known.
 */
export type ConfigReason = string | null;
/**
 * Actual configuration fingerprint, never an invented default.
 */
export type ConfigSha256 = string | null;
/**
 * Tool product or adapter identity.
 */
export type ToolId = string;
/**
 * Observed tool version; null if unknown.
 */
export type Version = string | null;
/**
 * Why the version is unknown, or null when known.
 */
export type VersionReason = string | null;
/**
 * VERIFIED, UNCONFIRMED, REJECTED or UNAVAILABLE evidence state.
 */
export type Verification = "VERIFIED" | "UNCONFIRMED" | "REJECTED" | "UNAVAILABLE";
/**
 * UI/filter category; SECURITY and BASELINE must match the corresponding classification.
 */
export type Category = "QUALITY" | "COMPLEXITY" | "DUPLICATION" | "SECURITY" | "BASELINE";
/**
 * QUALITY_REFACTOR, SECURITY_REVIEW or BASELINE; only eligible quality findings may enter ordinary Gate 1.
 */
export type Classification = "QUALITY_REFACTOR" | "SECURITY_REVIEW" | "BASELINE";
/**
 * Finding/selection gate state; not equivalent to successful execution or product approval by itself.
 */
export type Eligibility = "ELIGIBLE" | "INELIGIBLE" | "UNRESOLVED";
/**
 * Explicit explanation when a finding is ineligible or unresolved.
 */
export type EligibilityReason = string | null;
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 *
 * @minItems 1
 */
export type EvidenceIds3 = [string, ...string[]];
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id7 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind4 = "Finding";
/**
 * location: source references; duplication findings require both source locations.
 *
 * @minItems 1
 */
export type LocationIds1 = [string, ...string[]];
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt4 = string;
/**
 * Stable originating rule identity, or null where a producer has no applicable rule.
 */
export type RuleId1 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion4 = "1.0.0";
/**
 * Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states.
 */
export type Status = "OPEN" | "RESOLVED" | "SUPPRESSED" | "UNVERIFIED";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2565 = string;
/**
 * Exactly the attempt population used by this measurement, retaining failed attempts.
 */
export type AttemptIds = string[];
/**
 * Why the environment fingerprint is unknown; otherwise null.
 */
export type EnvironmentReason = string | null;
/**
 * Observed execution environment fingerprint, or null.
 */
export type EnvironmentSha256 = string | null;
/**
 * Fingerprint of the same target files/symbols/measurement definition, not their changing contents.
 */
export type MeasurementScopeSha256 = string;
/**
 * Why the ruleset version is unknown; otherwise null.
 */
export type RuleSetReason = string | null;
/**
 * Observed ruleset/metric definition version; null if unknown.
 */
export type RuleSetVersion = string | null;
/**
 * Frozen suite fingerprint for test/coverage comparisons; null when not applicable or unknown.
 */
export type TestSuiteSha256 = string | null;
/**
 * Distinguishes an inapplicable suite from missing comparison context.
 */
export type TestSuiteState = "KNOWN" | "NOT_APPLICABLE" | "UNKNOWN";
/**
 * Fingerprint of tool/rules/config/measurement scope; excludes measured value.
 */
export type ComparisonKey = string;
/**
 * Explicit ISO-style three-letter currency code for CURRENCY, otherwise null; never inferred from a provider name.
 */
export type CurrencyCode = string | null;
/**
 * Actual size of the declared attempt population; zero yields N/A rather than a fabricated zero ratio.
 */
export type Denominator = number | null;
/**
 * How a comparable measurement changes quality: lower, higher, or contextual with no automatic ranking.
 */
export type Direction = "LOWER_IS_BETTER" | "HIGHER_IS_BETTER" | "CONTEXTUAL";
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds4 = string[];
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id8 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind5 = "Metric";
/**
 * Whether a value was actually MEASURED or remains explicitly UNKNOWN/UNAVAILABLE/NOT_APPLICABLE.
 */
export type Measurement = "MEASURED" | "UNKNOWN" | "UNAVAILABLE" | "NOT_APPLICABLE";
/**
 * Observed human-readable identity or metric name; not a substitute for stable typed IDs.
 */
export type Name1 = string;
/**
 * Whether the metric measures BASELINE or CANDIDATE bytes.
 */
export type Phase = "BASELINE" | "CANDIDATE";
/**
 * NONE, STARTED_ATTEMPTS or PLANNED_ATTEMPTS; determines the required failure-inclusive denominator.
 */
export type Population = "NONE" | "STARTED_ATTEMPTS" | "PLANNED_ATTEMPTS";
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason5 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt5 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion5 = "1.0.0";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2566 = string;
/**
 * Explicit COUNT, PERCENT, MILLISECONDS, TOKENS or CURRENCY unit; consumers must not mix denominators.
 */
export type Unit = "COUNT" | "PERCENT" | "MILLISECONDS" | "TOKENS" | "CURRENCY";
/**
 * Observed value or explicit null; confidence and metric domains define their own constraints.
 */
export type Value1 = number | null;
/**
 * Observed test environment fingerprint, or null when execution cannot establish it.
 */
export type EnvironmentSha2561 = string | null;
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds5 = string[];
/**
 * COMPLETED, FAILED, NOT_RUN, UNAVAILABLE or INCOMPLETE; distinct from result dimensions.
 */
export type ExecutionStatus1 = "COMPLETED" | "FAILED" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * Observed failing test count, or null when unknown; execution failure alone is not a failing test case.
 */
export type Failed = number | null;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id9 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind6 = "TestResult";
/**
 * Observed test-suite result; a nonempty completed suite is required for PASSED.
 */
export type Outcome = "PASSED" | "FAILED" | "UNVERIFIED";
/**
 * Observed passing test count, or null when unknown.
 */
export type Passed = number | null;
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason6 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt6 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion6 = "1.0.0";
/**
 * Observed skipped-test count; skipped cases do not establish full behavioral PASS.
 */
export type Skipped = number | null;
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2567 = string;
/**
 * suite: immutable frozen baseline test-suite identity.
 */
export type SuiteId = string;
/**
 * SHA-256 of frozen test-suite manifest bytes, matched to the suite inventory.
 */
export type SuiteSha256 = string;
/**
 * Observed total test cases; must equal passed+failed+skipped and the frozen suite case inventory.
 */
export type Total = number | null;
/**
 * One independently declared operation; support for another operation does not imply support for this one.
 */
export type Capability1 =
  "parse" | "symbol" | "quality" | "dependency" | "build" | "test" | "coverage" | "safe_patch" | "security";
/**
 * component: boundary for per-language routing and capability evidence.
 */
export type ComponentId = string;
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds6 = string[];
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id10 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind7 = "Capability";
/**
 * One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing.
 */
export type Language1 = "JAVA" | "PYTHON" | "JAVASCRIPT" | "TYPESCRIPT" | "CSHARP" | "GO" | "CPP";
/**
 * Explicit capability restrictions and unmeasured assumptions.
 */
export type Limitations = string[];
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason7 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt7 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion7 = "1.0.0";
/**
 * Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states.
 */
export type Status1 = "SUPPORTED" | "UNSUPPORTED" | "UNAVAILABLE" | "UNRESOLVED" | "NOT_IMPLEMENTED";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2568 = string;
/**
 * Observed human-readable identity or metric name; not a substitute for stable typed IDs.
 */
export type Name2 = string;
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason8 = string | null;
/**
 * Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states.
 */
export type Status2 = "AVAILABLE" | "UNAVAILABLE" | "UNRESOLVED";
/**
 * Observed toolchain/tool version, with explicit unavailable/unknown semantics.
 */
export type Version1 = string | null;
/**
 * Required tools with observed availability/version; missing tools cannot imply support.
 */
export type Toolchain = ToolchainRequirement[];
/**
 * adapter: stable implementation/interface identity; a declaration does not prove runtime availability.
 */
export type AdapterId = string;
/**
 * Exactly one reference for each of parse, symbol, quality, dependency, build, test, coverage, safe_patch and security.
 *
 * @minItems 9
 * @maxItems 9
 */
export type CapabilityIds = [string, string, string, string, string, string, string, string, string];
/**
 * component: boundary for per-language routing and capability evidence.
 */
export type ComponentId1 = string;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id11 = string;
/**
 * CONTRACT_DEFINED versus RUNTIME_IMPLEMENTED; the latter needs at least one genuinely supported capability.
 */
export type ImplementationState = "CONTRACT_DEFINED" | "RUNTIME_IMPLEMENTED";
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind8 = "LanguageAdapterCapabilities";
/**
 * One of JAVA, PYTHON, JAVASCRIPT, TYPESCRIPT, CSHARP, GO or CPP; no silent language routing.
 */
export type Language2 = "JAVA" | "PYTHON" | "JAVASCRIPT" | "TYPESCRIPT" | "CSHARP" | "GO" | "CPP";
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt8 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion8 = "1.0.0";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha2569 = string;
/**
 * actor: identity of the human making the product selection; authenticate outside this data contract.
 */
export type ActorId1 = string;
/**
 * approval: audit reference for Gate 1; the string itself does not authenticate an approval.
 */
export type ApprovalRef = string;
/**
 * test: baseline executions supporting Gate 1; eligible selections require nonempty passing baseline evidence.
 *
 * @minItems 1
 */
export type BaselineTestResultIds = [string, ...string[]];
/**
 * UTC timestamp of the immutable issue-selection decision, using a Z suffix.
 */
export type CreatedAt = string;
/**
 * Finding/selection gate state; not equivalent to successful execution or product approval by itself.
 */
export type Eligibility1 = "ELIGIBLE" | "REJECTED" | "UNRESOLVED";
/**
 * Canonical scope+sorted snapshot fingerprint; excludes this field itself.
 */
export type Fingerprint = string;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id12 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind9 = "IssueSelection";
/**
 * Human-readable rejection/incompleteness explanations; empty only when the relevant gate is satisfied.
 */
export type Reasons = string[];
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt9 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion9 = "1.0.0";
/**
 * finding: Gate 1 choices; only current eligible QUALITY_REFACTOR findings can be approved.
 *
 * @minItems 1
 */
export type SelectedFindingIds = [string, ...string[]];
/**
 * Selected finding IDs plus complete-record RFC 8785/SHA-256 fingerprints, sorted for the selection fingerprint.
 *
 * @minItems 1
 */
export type Snapshots = [FindingSnapshot, ...FindingSnapshot[]];
/**
 * finding: reference bound by the adjacent immutable snapshot fingerprint.
 */
export type FindingId = string;
/**
 * SHA-256 of canonical JSON of the complete selected Finding record.
 */
export type Fingerprint1 = string;
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha25610 = string;
/**
 * artifact: references included in bounded context; complete context requires reviewed redaction states.
 */
export type ArtifactIds1 = string[];
/**
 * Positive context budget supplied for this request; never silently expanded.
 */
export type MaxTokens = number;
/**
 * Whether a value was actually MEASURED or remains explicitly UNKNOWN/UNAVAILABLE/NOT_APPLICABLE.
 */
export type Measurement1 = "MEASURED" | "UNKNOWN";
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason9 = string | null;
/**
 * Observed token usage, or explicit null; never fabricate missing usage as zero.
 */
export type UsedTokens = number | null;
/**
 * symbol: callees of the target, supported by corresponding CALL edges in complete context.
 */
export type CalleeSymbolIds = string[];
/**
 * symbol: callers of the target, supported by corresponding CALL edges in complete context.
 */
export type CallerSymbolIds = string[];
/**
 * COMPLETE only when critical references, side effects, redaction and budget are known; otherwise INCOMPLETE.
 */
export type Completeness = "COMPLETE" | "INCOMPLETE";
/**
 * dependency: relationships included in context; unresolved relationships prevent COMPLETE.
 */
export type DependencyIds = string[];
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds7 = string[];
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason10 = string;
/**
 * Opaque context reference recorded as excluded with an explicit reason.
 */
export type ReferenceId = string;
/**
 * Explicitly excluded context references with reasons; never also listed as included.
 */
export type Excluded = ContextExclusion[];
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id13 = string;
/**
 * Closed set of included context references; must contain every declared critical reference when COMPLETE.
 */
export type IncludedIds = string[];
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind10 = "ContextPackage";
/**
 * Observed side-effect descriptions; empty means known none only when side_effect_status is KNOWN.
 */
export type KnownSideEffects = string[];
/**
 * Critical context references that could not be supplied; nonempty forbids COMPLETE.
 */
export type MissingCriticalIds = string[];
/**
 * symbol: references whose public_api value is explicitly true in complete context.
 */
export type PublicApiSymbolIds = string[];
/**
 * Human-readable rejection/incompleteness explanations; empty only when the relevant gate is satisfied.
 */
export type Reasons1 = string[];
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt10 = string;
/**
 * MASKED, NO_SENSITIVE_CONTENT, UNREVIEWED or FAILED; a declaration does not implement a redactor.
 */
export type Redaction2 = "MASKED" | "NO_SENSITIVE_CONTENT" | "UNREVIEWED" | "FAILED";
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion10 = "1.0.0";
/**
 * selection: reference to the immutable Gate 1 selection snapshot.
 */
export type SelectionId = string;
/**
 * KNOWN or UNKNOWN; unknown effects prevent COMPLETE context.
 */
export type SideEffectStatus = "KNOWN" | "UNKNOWN";
/**
 * location: ranges supplied as bounded source context.
 */
export type SourceLocationIds = string[];
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha25611 = string;
/**
 * finding: one target present in the approved source-bound selection.
 */
export type TargetFindingId = string;
/**
 * symbol: source-aligned target, or null for explicitly incomplete context.
 */
export type TargetSymbolId = string | null;
/**
 * test: actual executions on the validated source snapshot, not merely passing baseline tests.
 */
export type TestResultIds = string[];
/**
 * Explicit unresolved relationships; nonempty forbids COMPLETE context.
 */
export type UnresolvedDependencyIds = string[];
/**
 * Candidate-declared exact paths or directory prefixes ending in slash; intersect with independent PatchPolicy.
 *
 * @minItems 1
 */
export type AllowedPaths = [string, ...string[]];
/**
 * Patch metadata applicability, independent of approval, behavioral safety and quality improvement.
 */
export type Applicability = "APPLICABLE" | "REJECTED" | "UNVERIFIED";
/**
 * attempt: reference to a started attempt belonging to the same job.
 */
export type AttemptId = string;
/**
 * PASSED, FAILED or UNVERIFIED, based on actual snapshot-matched test evidence.
 */
export type BehaviorStatus = "PASSED" | "FAILED" | "UNVERIFIED";
/**
 * Explicit file/operation/before/after manifest checked against independently trusted source metadata.
 *
 * @minItems 1
 */
export type ChangedFiles = [ChangedFile, ...ChangedFile[]];
/**
 * Resulting file-byte SHA-256; null only for deletion.
 */
export type AfterSha256 = string | null;
/**
 * Original file-byte SHA-256; null only when adding a new file.
 */
export type BeforeSha256 = string | null;
/**
 * file: identity in the appropriate source-snapshot manifest.
 */
export type FileId1 = string;
/**
 * Adapter capability being requested, or the changed-file operation ADD/MODIFY/DELETE.
 */
export type Operation = "ADD" | "MODIFY" | "DELETE";
/**
 * Canonical NFC repository-relative source path; absolute, traversal, encoded separators and reserved filenames are rejected.
 */
export type Path2 = string;
/**
 * artifact: opaque reference to proposed unified-diff bytes; metadata validation never applies the diff.
 */
export type DiffArtifactId = string;
/**
 * SHA-256 of the diff artifact bytes, matched to the artifact inventory.
 */
export type DiffSha256 = string;
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id14 = string;
/**
 * job: parent refactoring job identity; separate from attempts and provider transport retries.
 */
export type JobId1 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind11 = "PatchCandidate";
/**
 * artifact: reference to the materialized candidate source manifest; null before it exists.
 */
export type OutputManifestArtifactId = string | null;
/**
 * Why the candidate source snapshot is unknown; null when its hash and artifact are known.
 */
export type OutputSnapshotReason = string | null;
/**
 * Observed candidate source-manifest hash; null before materialization.
 */
export type OutputSnapshotSha256 = string | null;
/**
 * IMPROVED, UNCHANGED, WORSE or NOT_COMPARABLE, independently from behavior_status.
 */
export type QualityOutcome = "IMPROVED" | "UNCHANGED" | "WORSE" | "NOT_COMPARABLE";
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt11 = string;
/**
 * Reasons why a proposed patch is rejected or remains unverified.
 */
export type RejectionReasons = string[];
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion11 = "1.0.0";
/**
 * finding: references restricted to SECURITY_REVIEW findings.
 */
export type SecurityFindingIds = string[];
/**
 * CLEAN or FINDINGS only after a completed evidenced scan; absence is explicit.
 */
export type SecurityStatus = "CLEAN" | "FINDINGS" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * selection: reference to the immutable Gate 1 selection snapshot.
 */
export type SelectionId1 = string;
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha25612 = string;
/**
 * finding: one target present in the approved source-bound selection.
 */
export type TargetFindingId1 = string;
/**
 * Named proposed refactoring technique; not proof of quality improvement.
 */
export type Technique = string;
/**
 * validation: reciprocal references to actual assessments of this candidate.
 */
export type ValidationIds = string[];
/**
 * Explanation when behavior is UNVERIFIED; a build alone cannot establish preservation.
 */
export type BehaviorReason = string | null;
/**
 * PASSED, FAILED or UNVERIFIED, based on actual snapshot-matched test evidence.
 */
export type BehaviorStatus1 = "PASSED" | "FAILED" | "UNVERIFIED";
/**
 * Build outcome, kept separate from behavioral and quality outcomes.
 */
export type BuildStatus = "PASSED" | "FAILED" | "UNVERIFIED";
/**
 * patch: candidates assessed by this result; individual validation requires exactly one.
 *
 * @minItems 1
 */
export type CandidateIds = [string, ...string[]];
/**
 * evidence: provenance links; verification gates require independent VERIFIED evidence for the same snapshot.
 */
export type EvidenceIds8 = string[];
/**
 * COMPLETED, FAILED, NOT_RUN, UNAVAILABLE or INCOMPLETE; distinct from result dimensions.
 */
export type ExecutionStatus2 = "COMPLETED" | "FAILED" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * Globally unique, type-prefixed immutable entity ID.
 */
export type Id15 = string;
/**
 * Discriminator naming the exact CIR entity schema; no implicit fallback to another entity.
 */
export type Kind12 = "ValidationResult";
/**
 * metric: comparable before/after measurements supporting the quality outcome.
 */
export type MetricIds = string[];
/**
 * IMPROVED, UNCHANGED, WORSE or NOT_COMPARABLE, independently from behavior_status.
 */
export type QualityOutcome1 = "IMPROVED" | "UNCHANGED" | "WORSE" | "NOT_COMPARABLE";
/**
 * Explanation when the measurements cannot support a comparison.
 */
export type QualityReason = string | null;
/**
 * Explicit explanation for an unknown, unresolved, unavailable, incomplete or failed state; null when inapplicable.
 */
export type Reason11 = string | null;
/**
 * Actual UTC record timestamp; fixtures use an explicitly synthetic fixed timestamp.
 */
export type RecordedAt12 = string;
/**
 * Exact supported contract version. Unknown versions are rejected.
 */
export type SchemaVersion12 = "1.0.0";
/**
 * evidence: independent deterministic/human scan evidence for the exact validated snapshot.
 */
export type SecurityEvidenceIds = string[];
/**
 * Whether the security scan actually completed, independent of overall execution.
 */
export type SecurityExecutionStatus = "COMPLETED" | "FAILED" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * finding: references restricted to SECURITY_REVIEW findings.
 */
export type SecurityFindingIds1 = string[];
/**
 * Explanation when scanning is unavailable, incomplete or not run.
 */
export type SecurityReason = string | null;
/**
 * CLEAN or FINDINGS only after a completed evidenced scan; absence is explicit.
 */
export type SecurityStatus1 = "CLEAN" | "FINDINGS" | "NOT_RUN" | "UNAVAILABLE" | "INCOMPLETE";
/**
 * Actual observed source-manifest snapshot; baseline and candidate evidence must not be interchanged.
 */
export type SubjectSha25613 = string;
/**
 * test: actual executions on the validated source snapshot, not merely passing baseline tests.
 */
export type TestResultIds1 = string[];
/**
 * CANDIDATE versus COMBINED; individual success does not establish combined success.
 */
export type ValidationScope = "CANDIDATE" | "COMBINED";
/**
 * CANDIDATE_DERIVATIVE versus FRESH_V0_COMBINATION; combined results require a fresh V0 workspace.
 */
export type WorkspaceKind = "CANDIDATE_DERIVATIVE" | "FRESH_V0_COMBINATION";
/**
 * artifact: validated workspace manifest, whose hash must match the result subject snapshot.
 */
export type WorkspaceManifestArtifactId = string;
/**
 * Exact supported schema version; v1 readers reject unknown versions and fields.
 */
export type SchemaVersion13 = "1.0.0";
/**
 * Stable case: identifiers, including failed cases.
 */
export type CaseIds = string[];
/**
 * suite: immutable baseline test-suite identifier.
 */
export type Id16 = string;
/**
 * SHA-256 of the frozen test-suite manifest bytes.
 */
export type Sha2562 = string;
/**
 * Frozen suite inventory; does not claim the suite has been executed.
 */
export type TestSuites = TestSuite[];
/**
 * Opaque cursor; null means no additional page.
 */
export type NextCursor = string | null;
/**
 * request: identifier for correlating a safe API result/error with its request.
 */
export type RequestId = string;
/**
 * Exact supported schema version; v1 readers reject unknown versions and fields.
 */
export type SchemaVersion14 = "1.0.0";
/**
 * Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states.
 */
export type Status3 = "OK";
/**
 * Stable machine-readable error code; clients must branch on this value rather than message text.
 */
export type Code =
  | "INVALID_CONTRACT"
  | "BROKEN_REFERENCE"
  | "SCOPE_MISMATCH"
  | "STALE_SELECTION"
  | "FORBIDDEN_SCOPE"
  | "UNAVAILABLE_CAPABILITY"
  | "INCOMPLETE_CONTEXT"
  | "VALIDATION_FAILED"
  | "INTERNAL_ERROR";
/**
 * Originating subsystem for an API error.
 */
export type Component = "API" | "CONTRACT" | "ADAPTER" | "CONTEXT" | "VALIDATION";
/**
 * Optional type-prefixed entity reference; safe generated errors use null rather than reflecting untrusted input.
 */
export type EntityId = string | null;
/**
 * Safe field name identifying the contract failure without raw source content.
 */
export type Field = string | null;
/**
 * Safe structured entity/field error metadata; no raw input, stack trace, host path or credential.
 */
export type Details = ErrorDetail[];
/**
 * Static safe user message; never reflect raw validation input.
 */
export type Message = string;
/**
 * request: identifier for correlating a safe API result/error with its request.
 */
export type RequestId1 = string;
/**
 * Whether retry after resolving the reported condition may succeed; not permission for unbounded retries.
 */
export type Retryable = boolean;
/**
 * Exact supported schema version; v1 readers reject unknown versions and fields.
 */
export type SchemaVersion15 = "1.0.0";
/**
 * Context-specific exact state enum; never collapse execution, behavior, quality, security and evidence states.
 */
export type Status4 = "ERROR";

export interface UIContracts {
  result: ResultEnvelope;
  error: ErrorEnvelope;
  selection: IssueSelection;
}
/**
 * Versioned successful API result; references are validated as a closed graph.
 */
export interface ResultEnvelope {
  data: ContractBundle;
  next_cursor: NextCursor;
  request_id: RequestId;
  schema_version: SchemaVersion14;
  status: Status3;
}
/**
 * Versioned result bundle; gates additionally require cross-record validation with trusted policy inputs.
 */
export interface ContractBundle {
  artifacts: Artifacts;
  attempts: Attempts;
  files: Files;
  mode: Mode;
  records: Records;
  schema_version: SchemaVersion13;
  scope: Scope13;
  test_suites: TestSuites;
}
/**
 * Content-addressed opaque artifact reference; no local path or raw secret content.
 */
export interface Artifact {
  id: Id;
  media_type: MediaType;
  redaction: Redaction;
  sha256: Sha256;
}
/**
 * Failure-inclusive denominator ledger; not a worker implementation.
 */
export interface Attempt {
  artifact_ids: ArtifactIds;
  evidence_ids: EvidenceIds;
  execution_status: ExecutionStatus;
  failure_kind: FailureKind;
  id: Id1;
  job_id: JobId;
  number: Number;
  reason: Reason;
  started: Started;
}
/**
 * Trusted input manifest entry; candidate metadata cannot redefine this policy.
 */
export interface FileIdentity {
  frozen: Frozen;
  id: Id2;
  is_symlink: IsSymlink;
  path: Path;
  protected_test: ProtectedTest;
  sha256: Sha2561;
  subject_sha256: SubjectSha256;
}
/**
 * 1-based lines and Unicode-scalar columns; range end is exclusive.
 */
export interface SourceLocation {
  end_column: EndColumn;
  end_line: EndLine;
  file_id: FileId;
  file_sha256: FileSha256;
  id: Id3;
  kind: Kind;
  path: Path1;
  reason: Reason1;
  recorded_at: RecordedAt;
  resolution: Resolution;
  schema_version: SchemaVersion;
  scope: Scope;
  start_column: StartColumn;
  start_line: StartLine;
  subject_sha256: SubjectSha2561;
  symbol_id: SymbolId;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Language-independent symbol identity with explicit resolution uncertainty.
 */
export interface Symbol {
  evidence_ids: EvidenceIds1;
  id: Id4;
  kind: Kind1;
  language: Language;
  location_id: LocationId;
  name: Name;
  public_api: PublicApi;
  reason: Reason2;
  recorded_at: RecordedAt1;
  resolution: Resolution1;
  schema_version: SchemaVersion1;
  scope: Scope1;
  signature: Signature;
  subject_sha256: SubjectSha2562;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope1 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Observed or unresolved symbol relationship; unknown edges remain visible.
 */
export interface DependencyEdge {
  evidence_ids: EvidenceIds2;
  from_symbol_id: FromSymbolId;
  id: Id5;
  kind: Kind2;
  reason: Reason3;
  recorded_at: RecordedAt2;
  relationship: Relationship;
  resolution: Resolution2;
  schema_version: SchemaVersion2;
  scope: Scope2;
  subject_sha256: SubjectSha2563;
  to_symbol_id: ToSymbolId;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope2 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Attributable evidence; an LLM claim is never independent verified evidence.
 */
export interface Evidence {
  actor_id: ActorId;
  artifact_id: ArtifactId;
  confidence: Confidence;
  id: Id6;
  kind: Kind3;
  location_ids: LocationIds;
  /**
   * Provider/model/revision/settings provenance, with explicit reasons for unknown values.
   */
  model: ModelProvenance | null;
  producer_kind: ProducerKind;
  recorded_at: RecordedAt3;
  redaction: Redaction1;
  rule_id: RuleId;
  schema_version: SchemaVersion3;
  scope: Scope3;
  subject_sha256: SubjectSha2564;
  symbol_ids: SymbolIds;
  tool: ToolProvenance;
  verification: Verification;
}
/**
 * Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability.
 */
export interface Confidence {
  reason: Reason4;
  value: Value;
}
/**
 * Provider/model attribution without guessing deployment or generation settings.
 */
export interface ModelProvenance {
  model: Model;
  provider: Provider;
  revision: Revision;
  revision_reason: RevisionReason;
  settings: Settings;
  settings_reason: SettingsReason;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope3 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Observed tool identity/version/config provenance, or null for an unavailable capability.
 */
export interface ToolProvenance {
  config_reason: ConfigReason;
  config_sha256: ConfigSha256;
  tool_id: ToolId;
  version: Version;
  version_reason: VersionReason;
}
/**
 * Normalized quality/security/baseline observation with stable rule and evidence lineage.
 */
export interface Finding {
  category: Category;
  classification: Classification;
  confidence: Confidence1;
  eligibility: Eligibility;
  eligibility_reason: EligibilityReason;
  evidence_ids: EvidenceIds3;
  id: Id7;
  kind: Kind4;
  location_ids: LocationIds1;
  recorded_at: RecordedAt4;
  rule_id: RuleId1;
  schema_version: SchemaVersion4;
  scope: Scope4;
  status: Status;
  subject_sha256: SubjectSha2565;
  tool: ToolProvenance1;
}
/**
 * Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability.
 */
export interface Confidence1 {
  reason: Reason4;
  value: Value;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope4 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Observed tool identity/version/config provenance, or null for an unavailable capability.
 */
export interface ToolProvenance1 {
  config_reason: ConfigReason;
  config_sha256: ConfigSha256;
  tool_id: ToolId;
  version: Version;
  version_reason: VersionReason;
}
/**
 * Measured quantity with comparison fingerprint and failure-inclusive population.
 */
export interface Metric {
  attempt_ids: AttemptIds;
  comparison: ComparisonContext;
  comparison_key: ComparisonKey;
  currency_code: CurrencyCode;
  denominator: Denominator;
  direction: Direction;
  evidence_ids: EvidenceIds4;
  id: Id8;
  kind: Kind5;
  measurement: Measurement;
  name: Name1;
  phase: Phase;
  population: Population;
  reason: Reason5;
  recorded_at: RecordedAt5;
  schema_version: SchemaVersion5;
  scope: Scope5;
  subject_sha256: SubjectSha2566;
  unit: Unit;
  value: Value1;
}
/**
 * Actual comparable inputs; comparison_key is checked against these fields, not trusted as an opaque claim.
 */
export interface ComparisonContext {
  environment_reason: EnvironmentReason;
  environment_sha256: EnvironmentSha256;
  measurement_scope_sha256: MeasurementScopeSha256;
  rule_set_reason: RuleSetReason;
  rule_set_version: RuleSetVersion;
  test_suite_sha256: TestSuiteSha256;
  test_suite_state: TestSuiteState;
  tool: ToolProvenance2;
}
/**
 * Observed tool identity/version/config provenance, or null for an unavailable capability.
 */
export interface ToolProvenance2 {
  config_reason: ConfigReason;
  config_sha256: ConfigSha256;
  tool_id: ToolId;
  version: Version;
  version_reason: VersionReason;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope5 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * One actual frozen-suite execution; a build is not a test result.
 */
export interface TestResult {
  environment_sha256: EnvironmentSha2561;
  evidence_ids: EvidenceIds5;
  execution_status: ExecutionStatus1;
  failed: Failed;
  id: Id9;
  kind: Kind6;
  outcome: Outcome;
  passed: Passed;
  reason: Reason6;
  recorded_at: RecordedAt6;
  schema_version: SchemaVersion6;
  scope: Scope6;
  skipped: Skipped;
  subject_sha256: SubjectSha2567;
  suite_id: SuiteId;
  suite_sha256: SuiteSha256;
  tool: ToolProvenance3;
  total: Total;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope6 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Observed tool identity/version/config provenance, or null for an unavailable capability.
 */
export interface ToolProvenance3 {
  config_reason: ConfigReason;
  config_sha256: ConfigSha256;
  tool_id: ToolId;
  version: Version;
  version_reason: VersionReason;
}
/**
 * One language/component capability; parser support implies no other support.
 */
export interface Capability {
  capability: Capability1;
  component_id: ComponentId;
  confidence: Confidence2;
  evidence_ids: EvidenceIds6;
  id: Id10;
  kind: Kind7;
  language: Language1;
  limitations: Limitations;
  reason: Reason7;
  recorded_at: RecordedAt7;
  schema_version: SchemaVersion7;
  scope: Scope7;
  status: Status1;
  subject_sha256: SubjectSha2568;
  /**
   * Observed tool identity/version/config provenance, or null for an unavailable capability.
   */
  tool: ToolProvenance4 | null;
  toolchain: Toolchain;
}
/**
 * Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability.
 */
export interface Confidence2 {
  reason: Reason4;
  value: Value;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope7 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Actual tool/version/config lineage; unavailable values stay unknown.
 */
export interface ToolProvenance4 {
  config_reason: ConfigReason;
  config_sha256: ConfigSha256;
  tool_id: ToolId;
  version: Version;
  version_reason: VersionReason;
}
/**
 * Observed availability and version of a required toolchain component.
 */
export interface ToolchainRequirement {
  name: Name2;
  reason: Reason8;
  status: Status2;
  version: Version1;
}
/**
 * Shared adapter declaration, independently covering all nine capability dimensions.
 */
export interface LanguageAdapterCapabilities {
  adapter_id: AdapterId;
  capability_ids: CapabilityIds;
  component_id: ComponentId1;
  id: Id11;
  implementation_state: ImplementationState;
  kind: Kind8;
  language: Language2;
  recorded_at: RecordedAt8;
  schema_version: SchemaVersion8;
  scope: Scope8;
  subject_sha256: SubjectSha2569;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope8 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Approval Gate 1: immutable, source-bound selection snapshot, not an approval service.
 */
export interface IssueSelection {
  actor_id: ActorId1;
  approval_ref: ApprovalRef;
  baseline_test_result_ids: BaselineTestResultIds;
  created_at: CreatedAt;
  eligibility: Eligibility1;
  fingerprint: Fingerprint;
  id: Id12;
  kind: Kind9;
  reasons: Reasons;
  recorded_at: RecordedAt9;
  schema_version: SchemaVersion9;
  scope: Scope9;
  selected_finding_ids: SelectedFindingIds;
  snapshots: Snapshots;
  subject_sha256: SubjectSha25610;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope9 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Immutable complete-Finding fingerprint recorded by Gate 1.
 */
export interface FindingSnapshot {
  finding_id: FindingId;
  fingerprint: Fingerprint1;
}
/**
 * Bounded reference-only context; sensitive raw source is not a contract field.
 */
export interface ContextPackage {
  artifact_ids: ArtifactIds1;
  budget: ContextBudget;
  callee_symbol_ids: CalleeSymbolIds;
  caller_symbol_ids: CallerSymbolIds;
  completeness: Completeness;
  dependency_ids: DependencyIds;
  evidence_ids: EvidenceIds7;
  excluded: Excluded;
  id: Id13;
  included_ids: IncludedIds;
  kind: Kind10;
  known_side_effects: KnownSideEffects;
  missing_critical_ids: MissingCriticalIds;
  public_api_symbol_ids: PublicApiSymbolIds;
  reasons: Reasons1;
  recorded_at: RecordedAt10;
  redaction: Redaction2;
  schema_version: SchemaVersion10;
  scope: Scope10;
  selection_id: SelectionId;
  side_effect_status: SideEffectStatus;
  source_location_ids: SourceLocationIds;
  subject_sha256: SubjectSha25611;
  target_finding_id: TargetFindingId;
  target_symbol_id: TargetSymbolId;
  test_result_ids: TestResultIds;
  unresolved_dependency_ids: UnresolvedDependencyIds;
}
/**
 * Explicit context token limit and observed usage or unknown-usage reason.
 */
export interface ContextBudget {
  max_tokens: MaxTokens;
  measurement: Measurement1;
  reason: Reason9;
  used_tokens: UsedTokens;
}
/**
 * A deliberately excluded context reference and its reason.
 */
export interface ContextExclusion {
  reason: Reason10;
  reference_id: ReferenceId;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope10 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Proposed derivative patch metadata; never applies a patch or changes V0.
 */
export interface PatchCandidate {
  allowed_paths: AllowedPaths;
  applicability: Applicability;
  attempt_id: AttemptId;
  behavior_status: BehaviorStatus;
  changed_files: ChangedFiles;
  confidence: Confidence3;
  diff_artifact_id: DiffArtifactId;
  diff_sha256: DiffSha256;
  id: Id14;
  job_id: JobId1;
  kind: Kind11;
  model: ModelProvenance1;
  output_manifest_artifact_id: OutputManifestArtifactId;
  output_snapshot_reason: OutputSnapshotReason;
  output_snapshot_sha256: OutputSnapshotSha256;
  quality_outcome: QualityOutcome;
  recorded_at: RecordedAt11;
  rejection_reasons: RejectionReasons;
  schema_version: SchemaVersion11;
  scope: Scope11;
  security_finding_ids: SecurityFindingIds;
  security_status: SecurityStatus;
  selection_id: SelectionId1;
  subject_sha256: SubjectSha25612;
  target_finding_id: TargetFindingId1;
  technique: Technique;
  validation_ids: ValidationIds;
}
/**
 * One portable source file operation with explicit before/after integrity metadata.
 */
export interface ChangedFile {
  after_sha256: AfterSha256;
  before_sha256: BeforeSha256;
  file_id: FileId1;
  operation: Operation;
  path: Path2;
}
/**
 * Producer-reported score in [0,1] or explicit unknown reason; not an automatically calibrated probability.
 */
export interface Confidence3 {
  reason: Reason4;
  value: Value;
}
/**
 * Provider/model attribution without guessing deployment or generation settings.
 */
export interface ModelProvenance1 {
  model: Model;
  provider: Provider;
  revision: Revision;
  revision_reason: RevisionReason;
  settings: Settings;
  settings_reason: SettingsReason;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope11 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Evidence-backed independent behavior, quality, security and execution dimensions.
 */
export interface ValidationResult {
  behavior_reason: BehaviorReason;
  behavior_status: BehaviorStatus1;
  build_status: BuildStatus;
  candidate_ids: CandidateIds;
  evidence_ids: EvidenceIds8;
  execution_status: ExecutionStatus2;
  id: Id15;
  kind: Kind12;
  metric_ids: MetricIds;
  quality_outcome: QualityOutcome1;
  quality_reason: QualityReason;
  reason: Reason11;
  recorded_at: RecordedAt12;
  schema_version: SchemaVersion12;
  scope: Scope12;
  security_evidence_ids: SecurityEvidenceIds;
  security_execution_status: SecurityExecutionStatus;
  security_finding_ids: SecurityFindingIds1;
  security_reason: SecurityReason;
  security_status: SecurityStatus1;
  subject_sha256: SubjectSha25613;
  test_result_ids: TestResultIds1;
  validation_scope: ValidationScope;
  workspace_kind: WorkspaceKind;
  workspace_manifest_artifact_id: WorkspaceManifestArtifactId;
}
/**
 * Source/project/version/analysis/run binding.
 */
export interface Scope12 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Immutable project/version/analysis/run and baseline source binding.
 */
export interface Scope13 {
  analysis_id: AnalysisId;
  baseline_sha256: BaselineSha256;
  project_id: ProjectId;
  run_id: RunId;
  source_revision: SourceRevision;
  version_id: VersionId;
}
/**
 * Frozen test identity, separate from a particular test execution.
 */
export interface TestSuite {
  case_ids: CaseIds;
  id: Id16;
  sha256: Sha2562;
}
/**
 * Safe API error without raw source, stack trace, credentials or host filesystem paths.
 */
export interface ErrorEnvelope {
  code: Code;
  component: Component;
  details: Details;
  message: Message;
  request_id: RequestId1;
  retryable: Retryable;
  schema_version: SchemaVersion15;
  status: Status4;
}
/**
 * Safe structured failure metadata without reflecting raw inputs.
 */
export interface ErrorDetail {
  entity_id: EntityId;
  field: Field;
}
