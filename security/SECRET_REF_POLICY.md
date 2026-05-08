# SECRET_REF POLICY

## Canonical Rule

```text
secret_ref-only
```

Secrets MUST NOT exist in plaintext form anywhere in the organism.

Forbidden:

```text
API_KEY="..."
PRIVATE_KEY="..."
TOKEN="..."
PASSWORD="..."
SUA_CHAVE_PRIVADA_AQUI
YOUR_SECRET_HERE
```

Required:

```text
os.environ["SECRET_REF"]
vault://reference/path
kms://reference/path
```

## Ω-Gate Rule

```text
plaintext(secret) => BLOCK
CVaR > 0.05 => BLOCK
```

## Admissibility

Artifacts containing plaintext secret placeholders are not admissible into runtime execution.

Allowed state:

```text
STATIC_AUDIT_ONLY
```

Forbidden state:

```text
DEPLOY
RUNTIME_EXECUTION
PRODUCTION_BINDING
```

## Constitutional Security Flow

```text
artifact -> scan -> hash -> gate -> ledger -> PR/review
```

## Enforcement

1. recursive regex scan
2. fail-closed if match exists
3. mandatory replacement to SECRET_REF
4. immutable ledger registration
5. review before merge
