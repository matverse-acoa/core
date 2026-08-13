"""Document Twin — o protocolo bilíngue como instância mínima do schema Twin.

ORIGINAL → TRANSLATION → SEMANTIC REVIEW → AUTHOR CONFIRMATION

Aplicado ao schema ⟨X₀, 𝒯, I, Λ, X_t⟩:

    X₀  texto original em pt-BR
    𝒯   tradução, revisão semântica, confirmação do autor
    I   intenção, autoria, precisão, estrutura epistemológica
    Λ   o original permanece fonte primária; a tradução é representação
        vinculada, nunca substitui X₀
    C_T custo de manter o significado verificável através da língua

É a instância mais barata do schema: não exige EEG, QPU nem GPU — exige
dois humanos, dois idiomas e um registro. E tem a propriedade que falta às
outras: uma contraparte independente viva, capaz de dizer "não foi isso que
eu quis dizer" — o sinal de perda de invariante mais direto que existe.

Referências: MATVERSE 2.0, invariantes de federação I-F1..I-F4.
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class Stage(Enum):
    ORIGINAL = "original"
    TRANSLATION = "translation"
    SEMANTIC_REVIEW = "semantic_review"
    AUTHOR_CONFIRMATION = "author_confirmation"


@dataclass(frozen=True)
class StageRecord:
    stage: Stage
    actor: str
    content: str
    timestamp: float = field(default_factory=time.time)


@dataclass
class DocumentTwin:
    source_text: str
    source_lang: str
    author: str
    target_lang: Optional[str] = None
    records: List[StageRecord] = field(default_factory=list)
    confirmed: Optional[bool] = None
    divergence_notes: str = ""

    def __post_init__(self) -> None:
        self.records.append(StageRecord(Stage.ORIGINAL, self.author, self.source_text))

    @property
    def x0_hash(self) -> str:
        """Hash de X₀ — ponto fixo contra o qual toda tradução é aferida."""
        return hashlib.sha256(self.source_text.encode("utf-8")).hexdigest()

    def translate(self, translator: str, target_lang: str, translation: str) -> None:
        if self.confirmed is not None:
            raise RuntimeError("twin já encerrado por confirmação do autor")
        self.target_lang = target_lang
        self.records.append(StageRecord(Stage.TRANSLATION, translator, translation))

    def review(self, reviewer: str, notes: str) -> None:
        """I-F1: quem revisa não pode ser quem traduziu — senão não há T_I."""
        if reviewer == self._actor_of(Stage.TRANSLATION):
            raise ValueError("I-F1: revisor não pode ser o próprio tradutor")
        self.records.append(StageRecord(Stage.SEMANTIC_REVIEW, reviewer, notes))

    def confirm(self, author: str, confirmed: bool, notes: str = "") -> None:
        """I-T4/I-T5: só a autoria original fecha o twin, nunca em seu nome."""
        if author != self.author:
            raise ValueError("I-T4: confirmação pertence à autoria original")
        self.records.append(
            StageRecord(
                Stage.AUTHOR_CONFIRMATION,
                author,
                notes or ("ok" if confirmed else "divergent"),
            )
        )
        self.confirmed = confirmed
        self.divergence_notes = notes

    def _actor_of(self, stage: Stage) -> Optional[str]:
        for record in self.records:
            if record.stage is stage:
                return record.actor
        return None

    @property
    def t_independence(self) -> float:
        """T_I — só positivo se o revisor é contraparte distinta (I-F1..F4).

        Repetição não gera T_I (I-F3): tradutor e revisor idênticos, ou
        revisão ausente, resultam em T_I = 0.
        """
        translator = self._actor_of(Stage.TRANSLATION)
        reviewer = self._actor_of(Stage.SEMANTIC_REVIEW)
        if translator is None or reviewer is None:
            return 0.0
        if reviewer in (translator, self.author):
            return 0.0
        return 1.0

    @property
    def cost(self) -> float:
        """C_T — segundos entre X₀ e o último estágio registrado."""
        if len(self.records) < 2:
            return 0.0
        return self.records[-1].timestamp - self.records[0].timestamp

    def latest(self) -> str:
        """X_t — conteúdo do estágio mais recente."""
        return self.records[-1].content

    def to_dict(self) -> dict:
        return {
            "x0_hash": self.x0_hash,
            "source_lang": self.source_lang,
            "target_lang": self.target_lang,
            "author": self.author,
            "stages": [
                {
                    "stage": record.stage.value,
                    "actor": record.actor,
                    "timestamp": record.timestamp,
                }
                for record in self.records
            ],
            "confirmed": self.confirmed,
            "divergence_notes": self.divergence_notes,
            "t_independence": self.t_independence,
            "cost_seconds": self.cost,
        }
