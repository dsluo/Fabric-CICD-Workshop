from pathlib import Path

from summarize import load_rows as load, summarize, top_region


DATA = Path(__file__).resolve().parents[1] / "data"


def test_load_sales():
    rows = load(DATA / "sales.csv")
    assert len(rows) == 4
    assert rows[0] == {"region": "East", "amount": "100"}


def test_totals_by_region():
    totals, _ = summarize(load(DATA / "sales.csv"))
    assert totals == {"East": 150.0, "West": 250.0, "North": 75.0}


def test_top_region_with_normal_totals():
    assert top_region({"East": 150.0, "West": 250.0, "North": 75.0}) == (
        "West",
        250.0,
    )


def test_top_region_breaks_ties_alphabetically():
    assert top_region({"West": 100.0, "East": 100.0}) == ("East", 100.0)


def test_top_region_with_no_totals():
    assert top_region({}) is None
