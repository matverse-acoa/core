# Causal Authority v1

Status: EXPERIMENTAL / HOLD for production binding.

This contract is orthogonal to RB-Ω `envelope.v1`. The existing envelope governs
residual admissibility; `causal_authority.v1` governs whether an already proposed
external effect has authority to execute.

Invariant:

```
Intelligence != Authority != Execution
```

An effect is admissible only when the payload hash, principal, action, resource,
lease expiry and authority signature all validate, and the nonce has not already
been consumed by the execution boundary.

The module intentionally injects its signing implementation. The included HMAC
adapter exists only for deterministic local tests. Production binding MUST use an
approved MatVerse trust root and remains HOLD until that binding and integrated
Gate/Bridge/Executor tests exist.
