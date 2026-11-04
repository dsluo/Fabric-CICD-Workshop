import argparse
import csv
import math
from pathlib import Path


def load_rows(path: str | Path) -> list[dict[str, str]]:
    with open(path, newline="", encoding="utf-8-sig") as source:
        reader = csv.reader(source, strict=True)
        try:
            headers = next(reader)
        except StopIteration:
            headers = []
        except csv.Error as error:
            raise ValueError(
                f"line {reader.line_num}: malformed CSV header: {error}"
            ) from error

        missing_columns = {"region", "amount"} - set(headers)
        if missing_columns:
            missing = ", ".join(sorted(missing_columns))
            raise ValueError(f"missing required column(s): {missing}")

        rows = []
        while True:
            try:
                values = next(reader)
            except StopIteration:
                break
            except csv.Error as error:
                raise ValueError(
                    f"line {reader.line_num}: malformed CSV: {error}"
                ) from error

            line_number = reader.line_num
            if len(values) != len(headers):
                raise ValueError(
                    f"line {line_number}: malformed row "
                    f"(expected {len(headers)} fields, found {len(values)})"
                )

            row = dict(zip(headers, values))
            region = row["region"].strip()
            if not region:
                raise ValueError(f"line {line_number}: region must not be blank")

            try:
                amount = float(row["amount"])
            except ValueError as error:
                raise ValueError(
                    f"line {line_number}: invalid amount {row['amount']!r}"
                ) from error
            if not math.isfinite(amount):
                raise ValueError(f"line {line_number}: amount must be finite")
            if amount < 0:
                raise ValueError(f"line {line_number}: amount must be nonnegative")

            row["region"] = region
            rows.append(row)
        return rows


def summarize(rows: list[dict[str, str]]) -> tuple[dict[str, float], float]:
    """Return regional sales totals and their mean."""
    totals = {}
    for row in rows:
        region = row["region"]
        totals[region] = totals.get(region, 0) + float(row["amount"])
    average = sum(totals.values()) / len(totals)
    return totals, average


def top_region(totals: dict[str, float]) -> tuple[str, float] | None:
    """Return the region with the highest total, if any."""
    # Return the highest-total region and amount; break ties alphabetically.
    if not totals:
        return None
    return max(sorted(totals.items()), key=lambda item: item[1])


def main():
    parser = argparse.ArgumentParser(description="Summarize sales by region.")
    parser.add_argument("path", help="Path to the sales CSV")
    parser.add_argument("--region", help="Summarize only this region")
    args = parser.parse_args()
    try:
        rows = load_rows(args.path)
        if args.region is not None:
            if not any(row["region"] == args.region for row in rows):
                parser.exit(2, f"Error: unknown region {args.region!r}\n")
            rows = [row for row in rows if row["region"] == args.region]
        totals, average = summarize(rows)
    except (OSError, ValueError) as error:
        parser.exit(2, f"Error: {error}\n")
    for region, amount in sorted(totals.items()):
        print(f"{region}: {amount:.2f}")
    print(f"Average per region: {average:.2f}")


if __name__ == "__main__":
    main()
