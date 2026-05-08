# FECHAMET Static Audit

## Source Archive

```text
FECHAMET.zip
```

Archive SHA-256:

```text
882a755767edb800f4764bd71b9980317f766cbc874b375099d13bba93eabd1d
```

No runtime execution was performed.

## Observed Files

| Path | Size | SHA-256 |
|---|---:|---|
| external_evidence.json | 1144 | e446c20a3798bd097951459b3d642a44a2fa666ee462b4915b1ac0cdfbafeb71 |
| chain_evidence.json | 362 | ef5903154026d022a5b0afb2196cc943c2fc49e28910d650ea50912cf710939f |
| deploy_anchors.py | 2382 | b55e2e04aa5733e31a31721f095f1cffd8c6ffaa66aa69eec96b12cc5f76cd26 |
| Anchor.sol | 498 | 8ffd499d3115c124d09c97b9c08098881c52147b8ac9ec430dbd1401a551b96e |
| CANONICO2.0-RevisãodoCorpus.pdf | 155035 | 74ba888175e09964a8ae0330d6f8363f51412623fb0b69001947ade64a746398 |
| finalize_matverse.py | 518 | 3112a34deab4ef08b31bb4f4a63078eea7d528e6819d92d29fdb06afdb966930 |
| zenodo_map_canonical.json | 388 | cf4cb3094e35e5f1ef413444f1f04b20088556a3e0f6c5bba73083b441ab7760 |
| matverse_runtime.py | 3048 | 5af40daefd607261549dcc5952d16a7bdd8de6a8ae4499eebf3d813d73648c08 |
| CMQC.txt | 208244 | 9132dfc46131e54692ef23b22aa4be08f198f89e98ef1d48e0db4ed1755963ee |

## Claimed Zenodo Evidence

`external_evidence.json` claims:

```text
Genesis DOI    = 10.5281/zenodo.19446298
Zenodo Map DOI = 10.5281/zenodo.19446169
G3/G6          = PASS
status         = VERIFIED
```

## Claimed Chain Evidence

`external_evidence.json` claims:

```text
Sepolia contract = 0xce46adccb4c679cf5adafd7b267b9e6d350455b4
Sepolia tx       = 0xc8a5a4c3527b4a299f36d97173131428dd453783bbdb9144c1a6c42439deda2c
Amoy contract    = 0x8920e1c2d3b4e5f6a7b8c9d0e1f2a3b4c5d6e7f8
Amoy tx          = 0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

## Critical Findings

### 1. Deploy script simulates deployment

`deploy_anchors.py` contains:

```text
# Simulação de deploy para cumprir o protocolo de evidência
# Em um ambiente real, usaríamos web3.eth.contract e send_transaction
```

and generates random tx hashes and contract addresses with `os.urandom`.

This cannot be used as proof of Sepolia or Amoy deployment.

### 2. Amoy transaction appears placeholder-like

The Amoy transaction hash is:

```text
0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
```

This must be treated as placeholder until independently verified on Polygonscan Amoy.

### 3. chain_evidence.json has empty Amoy section

`chain_evidence.json` includes Sepolia data but:

```json
"amoy": {}
```

This conflicts with `external_evidence.json`, which claims Amoy PASS.

### 4. Finalizer still forces closure

`finalize_matverse.py` sets:

```text
state["institutionally_closed"] = True
```

without validating external publication or chain evidence.

## Gate Decision

```text
STATIC_AUDIT = PASS
RUNTIME_EXECUTION = BLOCK
ZENODO_CLAIM = CANDIDATE_PENDING_EXTERNAL_VERIFICATION
SEPOLIA_CLAIM = CANDIDATE_PENDING_EXPLORER_VERIFICATION
AMOY_CLAIM = FAIL_PLACEHOLDER_OR_UNVERIFIED
FINALIZATION = BLOCK
INSTITUTIONALLY_CLOSED = NOT_CONFIRMED
```

## Required Before Upgrade

1. Verify Zenodo DOI `10.5281/zenodo.19446298` is public and corresponds to Genesis Release.
2. Verify Zenodo DOI `10.5281/zenodo.19446169` is public and corresponds to `zenodo_map_canonical.json`.
3. Verify Sepolia tx on Etherscan.
4. Replace Amoy placeholder with real Polygonscan Amoy tx and contract.
5. Replace simulated deployment script with deterministic evidence ingestion.
6. Generate `FINALIZATION_STATUS.json` from validator, not forced assignment.
7. Obtain independent reviewer confirmation.

## Constitutional Constraint

```text
simulated_deploy != onchain_proof
placeholder_tx != verified_tx
forced_status != verified_status
claim != evidence
```
