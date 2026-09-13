from astra_pcb.datasheets.registry import Document, Registry
from astra_pcb.models.decision_links import validate_links
from astra_pcb.models.engineering import Decision
from astra_pcb.models.provenance import file_digest


def test_decision_links_detect_stale_missing_and_escape(tmp_path):
    (tmp_path / "datasheet.txt").write_text("Synthetic evidence")
    (tmp_path / "calc.py").write_text("print(2 * 3)")
    doc = Document(
        id="D",
        components=("TEST",),
        manufacturer="Test",
        title="Limits",
        revision="1",
        local_path="datasheet.txt",
        sha256=file_digest(tmp_path / "datasheet.txt"),
    )
    registry = Registry(tmp_path, (doc,))
    decision = Decision(
        id="D1",
        decision="Test",
        context="Test",
        alternatives=("Other",),
        evidence=(registry.citation("D", constraint="Synthetic limit", page="1"),),
        calculations=("[calculation](calc.py)",),
        risks=(),
        chosen_solution="Test",
        consequences=("Test",),
        invalidated_by=("Changed limits",),
    )
    assert (
        validate_links(Decision.from_markdown(decision.to_markdown()), tmp_path, registry).exit_code
        == 0
    )
    assert (
        validate_links(
            decision.model_copy(update={"calculations": ("[bad](../escape)",)}), tmp_path, registry
        ).exit_code
        == 1
    )
    (tmp_path / "calc.py").unlink()
    assert validate_links(decision, tmp_path, registry).exit_code == 1
    (tmp_path / "datasheet.txt").write_text("Changed revision")
    assert validate_links(decision, tmp_path, registry).results[0].status == "ERROR"
