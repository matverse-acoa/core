# CRITICAL PATH

## Sequence

```text
SECRET_REF_NORMALIZATION
    -> ZK_PROVENANCE
        -> EXTERNAL_ANCHOR
            -> QUORUM_RUNTIME
                -> TESTNET
                    -> WHITEPAPER + DOI
                        -> EXTERNAL REVIEW
```

## Gate Logic

```text
CVaR > 0.05 => BLOCK
PoLE < 0.80 => BLOCK
plaintext(secret) => BLOCK
```

## Fail-Closed Rule

If provenance is incomplete:

```text
EXECUTION = BLOCK
MERGE = HOLD
```

## Success Conditions

Target state:

```text
CVaR <= 0.02
PoLE >= 0.90
Ω >= 0.85
```

## Institutional Constraint

No claim of institutional equivalence to Ethereum, academia, or sovereign infrastructure is considered admissible without:

- public runtime evidence
- external validators
- external anchors
- reproducible documentation
- independent review
