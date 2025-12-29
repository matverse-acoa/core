# MATVERSE-OMEGA-GATE v2.1 (CANÔNICO)

**Status:** Proposta executável para congelar o núcleo de governança verificável (RB-Ω, PoSE, PoLE, Ω-GATE) e o ciclo OME-1.

## 1. Fundamentação

* Sistema de governança: \(\mathcal{M} = (\mathcal{D}, \Omega, \mathcal{H}, \Pi_{PQC})\)
  * \(\Omega\): função de score composto.
  * \(\mathcal{H}\): família de hashes (ex.: SHA-256).
  * \(\Pi_{PQC}\): esquema de assinatura (ex.: Dilithium3).
* Prova verificável de decisão = payload canônico + hashes + assinatura PQC + (opcional) âncora externa. Hash sozinho **não** prova autoria.

## 2. Métricas

* **Ψ (qualidade)**: \( \Psi = w_1 C + w_2 K + w_3 T \), \(\sum w_i = 1\).
* **Θ (latência)**: escolha única e congelada (exponencial \(\exp(-\gamma \theta)\) ou hiperbólica \(1/(1+\theta/\tau)\)).
* **CVaR**: \( \widehat{CVaR}_\alpha = \frac{1}{m} \sum_{i=n-m+1}^n l_{(i)} \), \(m=\lceil n(1-\alpha)\rceil\).
* **PoLE**: evolução verificável exige deltas (ΔΨ, ΔCVaR, etc.) + assinatura + referência a versão anterior.

## 3. RB-Ω (Régua Bidirecional)

### 3.1 Contrato do resíduo (residue.v1)
```json
{
  "version": "residue.v1",
  "symmetry_delta": 0.0,
  "entropy_increase": 0.0,
  "energy_barrier": 0.0,
  "residue_vector": [0.0],
  "residue_hash": "sha256(canon(payload_sem_hash))",
  "producer": "DSBD.v2",
  "producer_sig_pqc": "base64...",
  "timestamp": "2025-12-29T00:00:00Z"
}
```

### 3.2 Envelope (envelope.v1)
```json
{
  "version": "envelope.v1",
  "class": "organism.digital.default",
  "limits": {
    "symmetry_delta_max": 0.10,
    "entropy_increase_max": 0.20,
    "energy_barrier_min": 0.00,
    "residue_norm_max": 0.30
  },
  "envelope_hash": "sha256(canon(payload_sem_hash))"
}
```

### 3.3 Teste canônico
`verify_residue` deve recomputar `residue_hash`, validar assinatura PQC do produtor (opcional) e checar limites do envelope (norma do vetor e limites escalares).

## 4. Ω-GATE (Admissibilidade)

* Score: \(\Omega = w_1 \Psi + w_2 \Theta + w_3 (1-CVaR_\alpha) + w_4 I_{PoLE}\).
* Pesos padrão: \(w = (0.4, 0.3, 0.2, 0.1)\), \(\Omega_{min}=0.85\), \(\Psi_{min}=0.85\), \(CVaR_{max}=0.05\).
* Decisão: BLOCK (viola hard-rules), QUARANTINE (hard-rules ok, \(\Omega<\Omega_{min}\)), ADMIT (tudo ok, gera PoSE).

## 5. PoSE (Proof of Sovereign Evidence)

Schema mínimo:
```json
{
  "version": "pose.v1",
  "evidence_id": "uuid",
  "timestamp": "2025-12-29T14:23:45Z",
  "chain": { "name": "polygon-amoy", "tx_hash": "0x...", "merkle_root": "0x..." },
  "metrics": { "psi": 0.92, "theta_norm": 0.88, "cvar_0.95": 0.023, "pole_ok": true, "omega": 0.90 },
  "rb_omega": { "residue": { ...residue.v1... }, "envelope": { ...envelope.v1... } },
  "ledger_head": "sha256(rb_ledger.sqlite3)",
  "artifacts": { "receipt_sha256": "...", "ledger_sha256": "..." },
  "signatures": { "pqc": { "alg": "Dilithium3", "pk": "base64...", "sig": "base64..." } }
}
```
Assinatura PQC é sobre o payload **sem** o bloco `signatures` (evita auto-referência).

## 6. OME-1 (Engine)

* Produz: `rb_ledger.sqlite3` (append-only), `receipt_ome1.json`, `hashes.json`.
* `make verify` falha se qualquer hash/assinatura/resíduo/envelope/ledger_head não fechar.
* Evolução (PoLE) só promove nova versão com delta positivo nos critérios configurados.

## 7. Imutabilidade (declaração precisa)

Imutabilidade = qualquer alteração detectável por máquina via `make verify`. Evolução só é válida com PoLE + prova (hash + assinatura +, opcionalmente, âncora).

## 8. Segurança

* Assinador: Dilithium3 (PQC) para PoSE/PoLE.
* Hashes: SHA-256 (ou SHA3-256, se configurado).
* “Probabilidade de quebra” depende dos parâmetros do algoritmo PQC, não de um número fixo; deve ser referenciada à instância/nível documentado.

## 9. Execução recomendada (git/CI)

* `make ome1` → ciclo mínimo com receipt + ledger.
* `make auditpack` → empacota hashes, receipt, ledger.
* `make verify` → juiz final (hashes + PQC + resíduo + ledger_head).

## 10. Roadmap imediato

1) Congelar `constitution.json` com parâmetros (pesos, limites, esquema de hash/assinatura).  
2) Declarar `envelopes.yaml` por classe de organismo/ação.  
3) Plugar produtor real do resíduo (DSBD v2/UMJAM).  
4) Opcional: âncora on-chain (PoSE) em Polygon após `make verify` verde.
