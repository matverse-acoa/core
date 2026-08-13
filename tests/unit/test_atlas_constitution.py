"""Testes das invariantes constitucionais do Atlas."""

import pytest

from atlas.constitution import (
    INVARIANTS,
    NO_FOURTH_ORGANISM,
    Domain,
    Organism,
    check,
    invariants_by_group,
    organism_domain_matrix,
)


class TestConstitution:
    def test_thirteen_invariants(self):
        assert len(INVARIANTS) == 13

    def test_federation_group_has_four(self):
        assert len(invariants_by_group("federation")) == 4

    def test_check_known_code(self):
        assert check("I-F1").group == "federation"

    def test_check_unknown_code_raises(self):
        with pytest.raises(KeyError):
            check("I-Z9")

    def test_organism_domain_matrix_is_orthogonal(self):
        matrix = organism_domain_matrix()
        assert len(matrix) == len(Organism) * len(Domain)
        assert (Organism.SCIENCE, Domain.HUMAN) in matrix

    def test_no_fourth_organism_is_declared(self):
        assert isinstance(NO_FOURTH_ORGANISM, str)
        assert len(list(Organism)) == 3
