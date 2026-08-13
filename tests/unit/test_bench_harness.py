"""Testes do harness de três braços (C_K)."""

from acoa.twin.document_twin import DocumentTwin
from bench.harness import (
    BenchHarness,
    document_twin_arm,
    ome1_traversal_arm,
    synthetic_baseline_arm,
)


class TestBenchHarness:
    def test_synthetic_baseline_is_near_zero_cost(self):
        result = synthetic_baseline_arm()
        assert result.arm == "synthetic_baseline"
        assert result.cost_seconds >= 0.0
        assert result.delta_i == 0.0

    def test_document_twin_arm_reflects_confirmation(self):
        twin = DocumentTwin(source_text="x", source_lang="pt-BR", author="autor")
        twin.translate("tradutor", "en", "x")
        twin.review("revisor", "ok")
        twin.confirm("autor", True)

        result = document_twin_arm(twin)
        assert result.delta_i == 0.0
        assert result.t_independence == 1.0

    def test_document_twin_arm_reports_divergence(self):
        twin = DocumentTwin(source_text="x", source_lang="pt-BR", author="autor")
        twin.translate("tradutor", "en", "x")
        twin.review("revisor", "ok")
        twin.confirm("autor", False)

        result = document_twin_arm(twin)
        assert result.delta_i == 1.0

    def test_ome1_arm_uses_provided_cost_not_fabricated(self):
        result = ome1_traversal_arm(cost_seconds=42.0)
        assert result.cost_seconds == 42.0
        assert result.delta_i == 0.0

    def test_harness_runs_all_three_arms(self):
        harness = BenchHarness()
        harness.register("synthetic_baseline", synthetic_baseline_arm)
        harness.register("ome1_traversal", lambda: ome1_traversal_arm(1.0))

        twin = DocumentTwin(source_text="x", source_lang="pt-BR", author="autor")
        twin.translate("tradutor", "en", "x")
        twin.review("revisor", "ok")
        twin.confirm("autor", True)
        harness.register("document_twin", lambda: document_twin_arm(twin))

        results = harness.run_all()
        assert set(results) == {
            "synthetic_baseline",
            "ome1_traversal",
            "document_twin",
        }

    def test_unknown_arm_raises(self):
        harness = BenchHarness()
        try:
            harness.run("nope")
            assert False, "esperava KeyError"
        except KeyError:
            pass
