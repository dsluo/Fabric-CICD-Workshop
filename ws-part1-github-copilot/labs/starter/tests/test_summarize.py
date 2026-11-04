import subprocess
import sys
from pathlib import Path

import pytest

from summarize import load_rows as load, summarize, top_region


DATA = Path(__file__).resolve().parents[1] / "data"
SCRIPT = Path(__file__).resolve().parents[1] / "summarize.py"


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *arguments],
        cwd=SCRIPT.parent,
        capture_output=True,
        text=True,
        check=False,
    )


def test_load_sales():
    rows = load(DATA / "sales.csv")
    assert len(rows) == 4
    assert rows[0] == {"region": "East", "amount": "100"}


def test_totals_by_region():
    totals, _ = summarize(load(DATA / "sales.csv"))
    assert totals == {"East": 150.0, "West": 250.0, "North": 75.0}


def test_average_is_mean_of_regional_totals():
    _, average = summarize(load(DATA / "sales.csv"))
    assert average == (150.0 + 250.0 + 75.0) / 3


def test_top_region_with_normal_totals():
    assert top_region({"East": 150.0, "West": 250.0, "North": 75.0}) == (
        "West",
        250.0,
    )


def test_top_region_breaks_ties_alphabetically():
    assert top_region({"West": 100.0, "East": 100.0}) == ("East", 100.0)


def test_top_region_with_no_totals():
    assert top_region({}) is None


def test_cli_filters_to_east():
    result = run_cli("--region", "East", str(DATA / "sales.csv"))

    assert result.returncode == 0
    assert result.stdout == "East: 150.00\nAverage per region: 150.00\n"
    assert result.stderr == ""


def test_cli_rejects_unknown_case_sensitive_region():
    result = run_cli("--region", "east", str(DATA / "sales.csv"))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "unknown region 'east'" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_default_output_is_unchanged():
    result = run_cli(str(DATA / "sales.csv"))

    assert result.returncode == 0
    assert result.stdout == (
        "East: 150.00\n"
        "North: 75.00\n"
        "West: 250.00\n"
        "Average per region: 158.33\n"
    )
    assert result.stderr == ""


def test_load_trims_regions_and_accepts_zero_amount(tmp_path: Path):
    path = tmp_path / "sales.csv"
    path.write_text("region,amount\n  East  ,0\n", encoding="utf-8")

    assert load(path) == [{"region": "East", "amount": "0"}]


@pytest.mark.parametrize(
    ("content", "message"),
    [
        ("region,amount\n   ,10\n", "line 2: region must not be blank"),
        ("region,amount\nEast,not-a-number\n", "line 2: invalid amount"),
        ("region,amount\nEast,-1\n", "line 2: amount must be nonnegative"),
        ("region,amount\nEast,nan\n", "line 2: amount must be finite"),
        ("region,amount\nEast,inf\n", "line 2: amount must be finite"),
        ("region,amount\nEast,-inf\n", "line 2: amount must be finite"),
        ("region,amount\nEast\n", "line 2: malformed row"),
        ("region,amount\nEast,1,extra\n", "line 2: malformed row"),
    ],
)
def test_load_rejects_invalid_rows(tmp_path: Path, content: str, message: str):
    path = tmp_path / "invalid.csv"
    path.write_text(content, encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load(path)


@pytest.mark.parametrize(
    ("path", "message"),
    [
        (DATA / "invalid-amount.csv", "line 3: invalid amount"),
        (DATA / "missing-column.csv", "missing required column"),
    ],
)
def test_cli_rejects_supplied_invalid_files(path: Path, message: str):
    result = run_cli(str(path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert message in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_rejects_zero_byte_file(tmp_path: Path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    result = run_cli(str(path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "missing required column" in result.stderr
    assert "Traceback" not in result.stderr


def test_cli_rejects_malformed_row_without_partial_report(tmp_path: Path):
    path = tmp_path / "malformed.csv"
    path.write_text("region,amount\nEast,100\nWest\n", encoding="utf-8")

    result = run_cli(str(path))

    assert result.returncode != 0
    assert result.stdout == ""
    assert "line 3: malformed row" in result.stderr
    assert "Traceback" not in result.stderr
