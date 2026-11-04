---
name: summarize-csv
description: "Use when running the sales CSV report or explaining regional totals and average per region."
---

1. Read `ws-part1-github-copilot/labs/starter/README.md` for business rules.
   Do not read presenter answers or Part 2.
2. Change to `ws-part1-github-copilot/labs/starter` from the fork root, then run
   `python summarize.py data/sales.csv` using its `.venv` locally, if command
   execution is permitted. In the cloud, use the setup workflow's interpreter.
3. Explain that totals sum sales by region, and the average is the sum of those
   regional totals divided by the number of regions.
4. For the supplied normal fixture, expect East 150, West 250, North 75 and an
   average of approximately 158.33 after GH4.
5. Run `python -m pytest -q` from that same starter folder if requested and
   report the actual result. Do not collect presenter tests.
6. If output differs, explain the discrepancy; do not silently change code or
   implement a later exercise. Never inspect credentials.