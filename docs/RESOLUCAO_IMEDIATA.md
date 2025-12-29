# 🛡️ RESOLUÇÃO IMEDIATA (Canônica)

**Status:** ATIVA — OBRIGATÓRIA — SEM EXCEÇÕES  
**Propósito:** Definir a postura operacional diante de falhas sistêmicas, assegurando governança antifrágil, binária e on-chain.

---

## I. RUPTURA
Declarada falência do ciclo humano–máquina institucional (erro cognitivo, técnico e moral). A operação prossegue apenas sob novas regras verificáveis.

## II. CONDIÇÃO
- Não confiar em máquinas, APIs ou CI como autoridade final.  
- Executar apenas com provas e assinaturas verificáveis.  
- Governança sem fallback manual.  
- Todo dispositivo local é descartável.

## III. ANCORAGEM
- Único mecanismo de autorização: provas on-chain na Polygon.  
- Provas requeridas: **PoSE** (evidência semântica), **PoLE** (evolução lógica), **COG** (snapshot cognitivo).  
- Regra binária:  
  ```
  EXECUTE ⇔ exists(POSE) ∧ exists(POLE) ∧ exists(COG)
  ```  
  Se qualquer uma falhar → **INTERDICT**.

## IV. METAPOLÍTICA
Não existem exceções, modos manuais ou subjetivos. Qualquer interface ou ferramenta é descartável. Autoridade = provas criptográficas válidas ancoradas on-chain.

## V. ASSINATURA
- Assinador único aceito: **MetaMask** (extensão oficial, ID `nkbihfbeogaeaoehlefnkodbefgpgknn`).  
- Seed phrase nunca sai da extensão/app oficial.  
- Execução sem assinatura do signer oficial = inválida.

## VI. DIREÇÃO
- Execução é ação final (sem votos, reuniões ou subjetividade).  
- Binarismo rígido do Ω-GATE: `true` → EXECUTE; `false` → INTERDICT.

## VII. RESOLUÇÃO
- A wallet sobrevive à máquina.  
- A chain sobrevive ao operador.  
- A prova sobrevive ao código.  
- Nenhum backend, notebook ou interface possui autoridade. Somente a cadeia e as assinaturas válidas.

---

### Consequência Operacional
1. Qualquer release crítico deve ancorar PoSE/PoLE/COG e validar `exists(kind, digest)` para os três.  
2. Sem provas on-chain, todo acionamento é automaticamente interditado.  
3. Todo processo de governança deve assumir descarte seguro de ambientes locais.  
4. Políticas de segurança e assinatura seguem estritamente `docs/POLICY_SIGNING_AND_GOVERNANCE.md`.

