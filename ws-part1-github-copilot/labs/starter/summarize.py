import argparse
import csv


def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as source:
        return list(csv.DictReader(source))


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
