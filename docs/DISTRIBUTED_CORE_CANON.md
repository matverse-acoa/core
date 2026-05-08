# DISTRIBUTED CORE CANON

## Status

```text
DISTRIBUTED_CORE = TRUE
CENTER_OF_ATTACK = NONE
CORE_DIRECT_MUTATION = BLOCK
PR_ONLY = REQUIRED
FAIL_CLOSED = ENABLED
```

## Canonical Principle

The repository `matverse-acoa/core` is treated as a constitutional registry and coordination surface for a distributed mesh of auditable nodes.

```text
core != absolute authority
core = constitutional registry
```

## Canonical Pipeline

```text
PRIMORDIAL -> SVCA -> MNB -> MOTOR -> LEDGER
```

## Canonical Terms

```text
MNB = mem-nano-bit
```

## Secret Policy

```text
secret_ref-only
```

Decision rule:

```text
plaintext(secret) => BLOCK
```

## Artifact Governance

Artifacts from ZIP containers, nested archives, ZK circuits, proving keys, witness files, compiled bytecode or native libraries MUST NOT be executed before:

1. hash registration
2. provenance audit
3. dependency inspection
4. policy review
5. PR-based admission

Execution policy:

```text
STATIC_AUDIT_ALLOWED
EXECUTION_BLOCKED_UNTIL_PROVENANCE_VERIFIED
```

## Governance Flow

```text
branch/twin -> patch -> test -> ledger -> PR/review
```

Forbidden:

```text
merge_without_review
main_direct_mutation
untracked_binary_execution
```

## Closure State

```text
RUNTIME_CLOSED_INSTITUTION_OPEN
```

Residual blockers:

```text
G3 = Genesis promotion
G6 = Zenodo map publication
```
