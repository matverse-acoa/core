# FINALIZATION EVIDENCE GATE

## Canonical State

```text
STATUS = RUNTIME_CLOSED_INSTITUTION_OPEN
READINESS_SCORE = 0.85
```

## Fail-Closed Rule

Institutional closure MUST NOT be declared from narrative claims alone.

The following artifacts are REQUIRED before any transition to:

```text
INSTITUTIONALLY_CLOSED
```

## Required Evidence

1. Published Genesis Release DOI.
2. Published zenodo_map_canonical.json DOI or record_id.
3. external_evidence.json committed.
4. FINALIZATION_STATUS.json committed.
5. Reconciliation output proving:

```text
G3: PARTIAL -> PASS
G6: PARTIAL -> PASS
```

6. Independent reviewer confirmation.

## Constitutional Constraint

```text
claim != evidence
DOI_reserved != DOI_published
```

## Governance Decision

Until evidence is committed and independently reviewable:

```text
PUBLIC_CLAIM = BLOCK
MERGE = HOLD
STATE = RUNTIME_CLOSED_INSTITUTION_OPEN
```

## Objective

The objective is not narrative inflation.

The objective is institutional equivalence between:

```text
internal_state == externally_verifiable_state
```
