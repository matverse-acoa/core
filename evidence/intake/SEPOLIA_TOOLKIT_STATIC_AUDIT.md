# Sepolia Toolkit Static Audit

## Scope

Archives inspected:

```text
EPOLIA with a Script_.zip
PI SEPOLIA com um script.zip
```

No runtime execution was performed by Cassandra. No private key was used. No transaction was signed.

## Archive Hashes

```text
EPOLIA with a Script_.zip
SHA-256 = 70c3754f9381ad3b3439d402000f31587b30fa2ad2479628a3f4e1990dfd8e39
```

## Notable Evidence Candidates

### Sepolia calldata anchor report

File:

```text
final_sepolia_report.json
```

Claims:

```text
status     = SUCCESS
network    = Sepolia Testnet
block      = 10577173
tx_hash    = 0xe7a354486c8770e16772e30af614f17d5c8c51b5a64a142d9449563175232997
payload    = MATVERSE_ANCHOR:0xf2d62670fa23b41e1787a3f7e4420cf74b0445845ad977c5e619821b76071621
explorer   = https://sepolia.etherscan.io/tx/0xe7a354486c8770e16772e30af614f17d5c8c51b5a64a142d9449563175232997
verdict    = INTEGRIDADE CONFIRMADA
```

File SHA-256:

```text
5037d7dcd20d66fd8d0c0367b5cbfa8cde914eb3b4016cc4c10f132d8bb87c67
```

### Older/local receipt candidate

File:

```text
matverse_anchor_receipt.json
```

Claims:

```text
tx_hash = 4d0c8471cbbd451ca3c7ad2ac65faef8d36d0a5316ab8b7be0304d880b53d653
block   = 10536945
network = Sepolia Testnet
payload = MATVERSE_ANCHOR:f2d62670fa23b41e1787a3f7e4420cf74b0445845ad977c5e619821b76071621
status  = ANCHORED_VIA_CALLDATA
```

File SHA-256:

```text
77af6831dec0875f0f536ab080aaeffe3ab55bec09814f2429e09af9b432d247
```

## Contract / ABI Findings

A contract address appears repeatedly:

```text
0x237a92953c85716d5578a553d76209De2FB35d2C
```

However, the material also reports ABI/call-level divergence and fallback to calldata anchoring. Therefore contract-state claims must not be promoted without direct explorer/RPC verification.

## Security Finding

`real_sepolia_anchor.py` reads a private key from:

```text
/home/ubuntu/.clean_key
```

This is not committed as a key value, but the workflow implies private-key material existed in the execution environment. Any future production workflow must use `secret_ref` or managed signer policy.

## Gate Decision

```text
STATIC_AUDIT = PASS
RUNTIME_EXECUTION_BY_CASSANDRA = BLOCK
SEPOLIA_CALLDATA_ANCHOR = CANDIDATE_PENDING_EXPLORER_VERIFICATION
CONTRACT_STATE = PARTIAL_OR_DIVERGENT
AMOY_EVIDENCE = ABSENT_IN_THIS_INTAKE
INSTITUTIONALLY_CLOSED = NOT_CONFIRMED
```

## Required Verification

1. Open explorer URL and confirm transaction exists.
2. Confirm transaction status success.
3. Confirm input/calldata contains `MATVERSE_ANCHOR:f2d62670...` or equivalent expected payload.
4. Confirm block number and sender/recipient.
5. Attach independent reviewer validation.
6. Add Amoy evidence separately; this package does not close Amoy.

## Constitutional Constraint

```text
calldata_anchor_candidate != verified_chain_evidence
ABI_divergence != contract_state_closure
private_key_file_workflow != production_secret_policy
```
