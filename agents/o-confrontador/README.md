# O_CONFRONTADOR / NEMESIS-Ω

O_CONFRONTADOR / NEMESIS-Ω is a corpus-blind adversarial governance agent for MatVerse ACOA Core.

Its role is to confront artifacts, claims, evidence packs, schemas, and policy before promotion to Ω-Gate. It does not create narrative, defend the corpus, promote claims, or make final release decisions. It produces structured objections and a decision recommendation for Ω-Gate.

## Placement

```text
REPO_CANÔNICO: matverse-acoa/core
PATH: agents/o-confrontador/
STATUS: PASS_PLACEMENT
```

O_CONFRONTADOR belongs in core because it is a governance organ for confrontation, falsification, admissibility, validation, risk, and decision support.

## Corpus-blind operating rule

The agent may receive only the following inputs:

```text
artifact/
claims.json
evidence_pack/
schemas/
policy/
```

The agent must not receive or rely on:

```text
history of the project
author intention
value declarations
validation narratives
externally unverifiable claims
emotional or institutional context
```

This preserves impartiality. Callers such as Cassandra may invoke the agent, but must not contaminate its input with narrative memory.

## Maturity flow

```text
RAW_ARTIFACT
  ↓
O_CONFRONTADOR
  ↓
NO_CONTEST / WEAK_CONTEST / MATERIAL_CONTEST / FATAL_CONTEST
  ↓
Ω-GATE
  ↓
PASS / PASS_WITH_NOTES / HOLD / BLOCK
  ↓
LEDGER / REPLAY / RELEASE
```

## Ω-Gate mapping

```text
NO_CONTEST        → PASS_CANDIDATE
WEAK_CONTEST      → PASS_WITH_NOTES
MATERIAL_CONTEST  → HOLD
FATAL_CONTEST     → BLOCK
```

## CLI usage

```bash
python agents/o-confrontador/scripts/o_confrontador.py \
  --artifact agents/o-confrontador/examples/sample_artifact \
  --claims agents/o-confrontador/examples/claims.json \
  --out /tmp/o_confrontador_out
```

The command writes `confrontation_report.json` to the output directory.

## Validation

```bash
python -m unittest discover -s agents/o-confrontador/tests -p "test_*.py"
python agents/o-confrontador/scripts/o_confrontador.py \
  --artifact agents/o-confrontador/examples/sample_artifact \
  --claims agents/o-confrontador/examples/claims.json \
  --out /tmp/o_confrontador_out
grep -RIn --exclude-dir=.git -e '<forbidden-string>' .
```
