"""Public sourcing contracts use a reduced observed response, never a live CI requirement."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from astra_pcb.bom.adafruit import Adafruit
from astra_pcb.bom.sourcing import SourcingRecord
from astra_pcb.cli import main


@pytest.fixture
def row():
    return json.loads(Path("tests/fixtures/sourcing/adafruit.json").read_text())


def test_exact_identity_no_credentials_or_invented_package_price(row):
    urls = []

    def fetch(url):
        urls.append(url)
        return row

    record, check = Adafruit(fetch=fetch).lookup("2821", expected_mpn="ADA2821")
    assert check.status == "WARN"
    assert urls == ["https://www.adafruit.com/api/products/2821"]
    assert record.supplier == "Adafruit" and record.stock == 27
    assert record.package is None and record.unit_cost is None and record.currency is None
    assert record.stock_updated_at is None and record.lifecycle == "unknown"
    assert record.manufacturer == "Adafruit" and record.mpn == "ADA2821"
    assert SourcingRecord.model_validate_json(record.model_dump_json()) == record
    with pytest.raises(ValidationError):
        SourcingRecord.model_validate({**record.model_dump(), "supplier": "LCSC"})


@pytest.mark.parametrize("stock", ["in stock", "out of stock", None, 0, "0"])
def test_availability_text_is_not_a_quantity(row, stock):
    record, check = Adafruit(fetch=lambda _: {**row, "product_stock": stock}).lookup("2821")
    assert check.status == "WARN"
    assert record.stock == (0 if stock in (0, "0") else None)


@pytest.mark.parametrize(
    "change",
    [
        {"product_id": "1500"},
        {"product_mpn": ""},
        {"product_mpn": "OTHER"},
        {"product_stock": -1},
        {"product_stock": True},
        {"product_stock": "many"},
        {"product_stock": []},
    ],
)
def test_refuse_mismatch_and_malformed_inventory(row, change):
    record, check = Adafruit(fetch=lambda _: {**row, **change}).lookup(
        "2821", expected_mpn="ADA2821"
    )
    assert record is None and check.status == "ERROR"


def test_invalid_identifier_and_offline():
    with pytest.raises(ValueError):
        Adafruit().lookup("../../secret")

    def offline(_):
        raise OSError("offline")

    assert Adafruit(fetch=offline).lookup("2821")[1].status == "ERROR"


def test_cli_selects_explicit_supplier(row, monkeypatch, capsys):
    monkeypatch.setattr("astra_pcb.cli.Adafruit", lambda: Adafruit(fetch=lambda _: row))
    assert main(["source-part", "2821", "--provider", "adafruit", "--expected-mpn", "ADA2821"]) == 2
    result = json.loads(capsys.readouterr().out)
    assert result["results"][0]["source"] == "Adafruit public product API"
