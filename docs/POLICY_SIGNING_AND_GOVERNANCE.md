# 🔐 Política de Assinatura e Governança (Canônica)

**Status:** ATIVA – OBRIGATÓRIA – NÃO NEGOCIÁVEL

---

## 1. Princípio Fundamental

Este projeto adota **governança antifrágil e soberana**.

- Identidade ≠ Máquina  
- Assinatura ≠ Backend  
- Verdade ≠ Interface  

A autoridade final **não reside** em notebooks, servidores, APIs ou dashboards.  
Ela reside exclusivamente em **assinaturas criptográficas válidas** e **provas on-chain verificáveis**.

---

## 2. Assinador Oficial (Signer)

O **único assinador suportado** é a extensão oficial do **MetaMask** (**Chrome Web Store**).

**Identificador canônico da extensão:**
```
nkbihfbeogaeaoehlefnkodbefgpgknn
```

Qualquer UI, script ou serviço que **não utilize este signer** é considerado **não-autorizado**.

---

## 3. Papel do MetaMask

O MetaMask é responsável **exclusivamente** por:

- Custódia da chave privada  
- Assinatura de transações e mensagens (EIP-1193)  
- Identidade soberana do operador  

O MetaMask **NÃO é**:
- Fonte de verdade  
- Armazenamento de estado  
- Motor de decisão  
- Ledger  

A chave **nunca sai da wallet**.  
A wallet **não confia** em backend algum.

---

## 4. Fonte Única de Verdade (Hard Gate)

A **única fonte de verdade** do sistema é a blockchain (**Polygon**).

Uma ação, execução ou decisão **só é válida** se as seguintes provas **existirem on-chain**:

- **PoSE** — Proof of Semantic Evidence  
- **PoLE** — Proof of Logical Evolution  
- **COG** — Snapshot Cognitivo  

Formalmente:
```
EXECUTE ⇔ exists(POSE) ∧ exists(POLE) ∧ exists(COG)
```
Se qualquer uma falhar → **INTERDICT**.

---

## 5. Ω-GATE (Regra Binária)

O Ω-GATE é **binário e determinístico**:

- `true` → execução permitida  
- `false` → execução interditada  

Não há:
- Exceções  
- “Modo manual”  
- Override humano  
- Fallback subjetivo  

---

## 6. Interfaces e Máquinas

Interfaces gráficas, notebooks, servidores e pipelines são tratados como:

- **Clientes fracos e descartáveis**

Eles podem:
- Falhar  
- Ser substituídos  
- Ser recriados  
- Desaparecer  

Isso **não compromete o sistema**.

---

## 7. Segurança Operacional (Obrigatória)

- **Nunca** inserir seed phrase em sites (`https://`)  
- Seed phrase **somente** dentro da extensão/app oficial  
- Links de suporte **somente** via `support.metamask.io`  
- Nenhuma chave privada é armazenada em disco, CI ou backend  
- Violação desta política **invalida qualquer prova gerada**

---

## 8. Consequência Arquitetural

Este projeto assume explicitamente que:

- A wallet sobrevive à máquina  
- A chain sobrevive ao operador  
- A prova sobrevive ao código  

Isso é **governança antifrágil por construção**.

---

## 9. Estado Final

- **Signer:** MetaMask oficial  
- **Gate:** on-chain  
- **Decisão:** binária  
- **Verdade:** imutável  

Nada local é crítico.  
Nada subjetivo é aceito.
