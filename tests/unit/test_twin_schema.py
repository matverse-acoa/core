"""Testes do schema Twin genérico ⟨X₀, 𝒯, I, Λ, X_t⟩."""

import pytest

from acoa.twin.schema import Twin, TwinInstance, TwinState


class TestTwin:
    def test_xt_defaults_to_x0(self):
        twin = Twin(instance=TwinInstance.DOCUMENT, x0="original")
        assert twin.xt == "original"

    def test_apply_updates_xt_and_transformations(self):
        twin = Twin(instance=TwinInstance.MODEL, x0={"v": 1})
        twin.apply("fine-tune", "engenheiro", {"v": 2})

        assert twin.xt == {"v": 2}
        assert len(twin.transformations) == 1
        assert twin.transformations[0].actor == "engenheiro"

    def test_state_defaults_to_twin(self):
        twin = Twin(instance=TwinInstance.WORK, x0="x")
        assert twin.state is TwinState.TWIN

    def test_advance_forward_ok(self):
        twin = Twin(instance=TwinInstance.ARTIFACT, x0="x")
        twin.advance(TwinState.ARTIFACT)
        twin.advance(TwinState.ASSET)
        assert twin.state is TwinState.ASSET

    def test_advance_cannot_regress(self):
        twin = Twin(instance=TwinInstance.ARTIFACT, x0="x", state=TwinState.ARTIFACT)
        with pytest.raises(ValueError):
            twin.advance(TwinState.TWIN)

    def test_preserved_true_when_no_invariants_checked(self):
        twin = Twin(instance=TwinInstance.POLICY, x0="x")
        assert twin.preserved is True

    def test_preserved_false_when_any_invariant_fails(self):
        twin = Twin(instance=TwinInstance.SYSTEM, x0="x")
        twin.check_invariant("I-T1", True)
        twin.check_invariant("I-T4", False)
        assert twin.preserved is False

    def test_all_eight_instances_available(self):
        expected = {
            "work",
            "model",
            "dataset",
            "algorithm",
            "system",
            "policy",
            "artifact",
            "document",
        }
        assert {inst.value for inst in TwinInstance} == expected
