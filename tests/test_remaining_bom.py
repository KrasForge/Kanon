import pytest

from astra_pcb.bom import BOMItem
from astra_pcb.bom.policy import BOMPolicy, OrderingRule, audit_bom
from astra_pcb.datasheets import DatasheetEvidence


def test_bom_policy_suffix_exclusion_alias_and_supplier_conflict():
    evidence = DatasheetEvidence(
        document="Synthetic ordering",
        manufacturer="Test",
        revision="1",
        page="1",
        extracted_constraint="Test suffixes",
        source_location="test",
    )
    rule = OrderingRule(
        manufacturer="Maker", base_mpn="TEST", allowed_suffixes=("-A", "-B"), evidence=evidence
    )
    row = BOMItem(reference="U1", value="test", package="QFN", manufacturer="maker inc", mpn="TEST")
    policy = BOMPolicy(manufacturer_aliases={"maker inc": "Maker"}, ordering_rules=(rule,))
    assert audit_bom([row], policy).exit_code == 1
    fitted = row.model_copy(
        update={"mpn": "TEST-A", "supplier": "Store", "supplier_part_number": "1"}
    )
    assert audit_bom([fitted], policy).exit_code == 0
    unfitted = BOMItem(reference="U2", value="optional", package="QFN")
    with pytest.raises(ValueError):
        BOMPolicy(unfitted_references={"U2"})
    excluded = policy.model_copy(
        update={
            "unfitted_references": frozenset({"U2"}),
            "exclusion_evidence": {"U2": "Explicit variant DNP"},
        }
    )
    assert audit_bom([fitted, unfitted], excluded).exit_code == 0
    conflicting = fitted.model_copy(update={"reference": "U3", "manufacturer": "Other"})
    assert audit_bom([fitted, conflicting], policy).exit_code == 1
    same = fitted.model_copy(
        update={"reference": "U3", "manufacturer": "Maker", "value": "different"}
    )
    assert audit_bom([fitted, same], policy).exit_code == 1
