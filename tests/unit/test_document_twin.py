"""Testes do Document Twin — protocolo bilíngue (MATVERSE 2.0, §2)."""

import pytest

from acoa.twin.document_twin import DocumentTwin, Stage


def build_twin() -> DocumentTwin:
    return DocumentTwin(
        source_text="A federação resolve a reflexividade do Trust Vector.",
        source_lang="pt-BR",
        author="autor",
    )


class TestDocumentTwin:
    def test_x0_recorded_on_init(self):
        twin = build_twin()
        assert twin.records[0].stage is Stage.ORIGINAL
        assert twin.records[0].actor == "autor"

    def test_x0_hash_stable(self):
        twin = build_twin()
        assert twin.x0_hash == build_twin().x0_hash

    def test_translate_then_review_then_confirm(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "Federation resolves...")
        twin.review("revisor", "meaning preserved")
        twin.confirm("autor", True)

        assert twin.confirmed is True
        assert twin.latest() == "ok"
        assert [r.stage for r in twin.records] == [
            Stage.ORIGINAL,
            Stage.TRANSLATION,
            Stage.SEMANTIC_REVIEW,
            Stage.AUTHOR_CONFIRMATION,
        ]

    def test_i_f1_reviewer_cannot_be_translator(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        with pytest.raises(ValueError):
            twin.review("tradutor", "self-review")

    def test_i_t4_only_original_author_confirms(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("revisor", "...")
        with pytest.raises(ValueError):
            twin.confirm("outra_pessoa", True)

    def test_cannot_translate_after_confirmation(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("revisor", "...")
        twin.confirm("autor", True)
        with pytest.raises(RuntimeError):
            twin.translate("outro_tradutor", "en", "...")

    def test_t_independence_zero_without_review(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        assert twin.t_independence == 0.0

    def test_t_independence_zero_when_reviewer_is_author(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("autor", "...")
        assert twin.t_independence == 0.0

    def test_t_independence_one_for_distinct_reviewer(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("revisor", "...")
        assert twin.t_independence == 1.0

    def test_cost_non_negative(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        assert twin.cost >= 0.0

    def test_divergence_notes_preserved_on_rejection(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("revisor", "...")
        twin.confirm("autor", False, notes="perdeu a nuance de 'reflexividade'")
        assert twin.confirmed is False
        assert "reflexividade" in twin.divergence_notes

    def test_to_dict_shape(self):
        twin = build_twin()
        twin.translate("tradutor", "en", "...")
        twin.review("revisor", "...")
        twin.confirm("autor", True)
        payload = twin.to_dict()

        assert payload["confirmed"] is True
        assert payload["t_independence"] == 1.0
        assert len(payload["stages"]) == 4
