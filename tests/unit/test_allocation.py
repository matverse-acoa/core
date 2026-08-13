"""Testes do registry configs/allocation.json."""

from atlas.allocation import load_allocation
from atlas.constitution import Domain, Organism


class TestAllocation:
    def test_loads_default_registry(self):
        allocation = load_allocation()
        assert allocation.version == "allocation.v1"
        assert len(allocation.entries) >= 6

    def test_atlas_and_acoa_are_transversal(self):
        allocation = load_allocation()
        atlas_entry = allocation.get("atlas")
        acoa_entry = allocation.get("acoa")

        assert atlas_entry.organism is None
        assert atlas_entry.domain is None
        assert acoa_entry.organism is None
        assert acoa_entry.domain is None
        assert atlas_entry.sphere == "constitution"
        assert acoa_entry.sphere == "capability"

    def test_document_twin_is_science_human(self):
        allocation = load_allocation()
        entry = allocation.get("document_twin")
        assert entry.organism is Organism.SCIENCE
        assert entry.domain is Domain.HUMAN

    def test_unknown_id_raises(self):
        allocation = load_allocation()
        try:
            allocation.get("does_not_exist")
            assert False, "esperava KeyError"
        except KeyError:
            pass

    def test_by_organism_filters_correctly(self):
        allocation = load_allocation()
        engineering_entries = allocation.by_organism(Organism.ENGINEERING)
        assert {e.id for e in engineering_entries} == {
            "ome1_traversal",
            "bench_harness",
        }
