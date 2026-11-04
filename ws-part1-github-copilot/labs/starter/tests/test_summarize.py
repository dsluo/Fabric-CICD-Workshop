import subprocess
import sys
from pathlib import Path

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
