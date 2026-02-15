"""Parse SSA Wage Statistics HTML files into CSV datasets."""

import csv
import glob
import os
import re
from html.parser import HTMLParser


class SSATableParser(HTMLParser):
    """Extract the wage distribution table and summary stats from SSA HTML."""

    def __init__(self):
        super().__init__()
        self._in_table = False
        self._in_row = False
        self._in_cell = False
        self._current_row = []
        self._cell_text = ""
        self._rows = []
        self._found_distribution_table = False
        self._table_depth = 0
        self._body_text = ""
        self._capture_body = False

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._table_depth += 1
        if tag == "caption":
            self._capture_body = True
            self._body_text = ""
        if tag == "tr" and self._found_distribution_table:
            self._in_row = True
            self._current_row = []
        if tag in ("td", "th") and self._in_row:
            self._in_cell = True
            self._cell_text = ""
        # Capture paragraph text for summary stats
        if tag == "p":
            self._capture_body = True
            self._body_text = ""

    def handle_endtag(self, tag):
        if tag == "caption" and self._capture_body:
            self._capture_body = False
            if "Distribution of wage earners" in self._body_text:
                self._found_distribution_table = True
        if tag == "table":
            if self._found_distribution_table and self._table_depth == self._table_depth:
                pass
            self._table_depth -= 1
        if tag in ("td", "th") and self._in_cell:
            self._in_cell = False
            self._current_row.append(self._cell_text.strip())
        if tag == "tr" and self._in_row:
            self._in_row = False
            if self._current_row and self._found_distribution_table:
                self._rows.append(self._current_row)
        if tag == "p":
            self._capture_body = False

    def handle_data(self, data):
        if self._in_cell:
            self._cell_text += data
        if self._capture_body:
            self._body_text += data


def parse_number(s):
    """Remove $, commas, whitespace and parse as float."""
    s = s.replace("$", "").replace(",", "").strip()
    if not s:
        return None
    return float(s)


def parse_bracket(interval_text):
    """Parse bracket text like '$0.01 — 4,999.99' into (lower, upper)."""
    text = interval_text.replace("$", "").replace(",", "").replace("\xa0", " ").strip()
    if "and over" in text.lower():
        lower = float(text.split()[0])
        return lower, None
    parts = re.split(r"\s*[—–-]\s*", text)
    if len(parts) == 2:
        return float(parts[0]), float(parts[1])
    return None, None


def extract_summary(html_text, year):
    """Extract median wage, average wage, and total earners from HTML text."""
    summary = {"year": year}

    m = re.search(r"divided by\s+([\d,]+),\s+or\s+\$([\d,]+\.\d+)", html_text)
    if m:
        summary["total_earners"] = int(m.group(1).replace(",", ""))
        summary["avg_wage"] = float(m.group(2).replace(",", ""))

    m = re.search(r"median.*?wage.*?estimated to be\s+\$([\d,]+\.\d+)", html_text, re.IGNORECASE)
    if m:
        summary["median_wage"] = float(m.group(1).replace(",", ""))

    m = re.search(r"about\s+([\d.]+)\s+percent.*?less than or equal", html_text)
    if m:
        summary["pct_below_avg"] = float(m.group(1))

    m = re.search(r"\$([\d,]+,[\d,]+,[\d,]+\.\d+)\s+divided by", html_text)
    if m:
        summary["total_net_compensation"] = float(m.group(1).replace(",", ""))

    return summary


def parse_file(filepath):
    """Parse a single SSA HTML file, returning (year, rows, summary)."""
    year_match = re.search(r"(\d{4})", os.path.basename(filepath))
    year = int(year_match.group(1)) if year_match else None

    with open(filepath, "r", encoding="utf-8") as f:
        html_text = f.read()

    parser = SSATableParser()
    parser.feed(html_text)

    summary = extract_summary(html_text, year)

    rows = []
    for raw_row in parser._rows:
        if len(raw_row) < 6:
            continue
        # Skip header rows
        if "Number" in raw_row[1] or "Cumulative" in raw_row[1]:
            continue

        lower, upper = parse_bracket(raw_row[0])
        if lower is None:
            continue

        rows.append({
            "year": year,
            "bracket_lower": lower,
            "bracket_upper": upper,
            "num_earners": int(parse_number(raw_row[1])),
            "cumulative_num": int(parse_number(raw_row[2])),
            "pct_of_total": parse_number(raw_row[3]),
            "aggregate_amount": parse_number(raw_row[4]),
            "avg_amount": parse_number(raw_row[5]),
        })

    return year, rows, summary


def main():
    data_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "dashboard", "data")
    os.makedirs(output_dir, exist_ok=True)

    html_files = sorted(glob.glob(os.path.join(data_dir, "Wage Statistics for *.html")))
    print(f"Found {len(html_files)} HTML files")

    all_rows = []
    all_summaries = []

    for filepath in html_files:
        year, rows, summary = parse_file(filepath)
        print(f"  {year}: {len(rows)} brackets, "
              f"median=${summary.get('median_wage', 'N/A'):,.2f}, "
              f"avg=${summary.get('avg_wage', 'N/A'):,.2f}, "
              f"earners={summary.get('total_earners', 'N/A'):,}")
        all_rows.extend(rows)
        all_summaries.append(summary)

    # Write distribution CSV
    dist_path = os.path.join(output_dir, "ssa_wage_distribution.csv")
    with open(dist_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "year", "bracket_lower", "bracket_upper", "num_earners",
            "cumulative_num", "pct_of_total", "aggregate_amount", "avg_amount",
        ])
        writer.writeheader()
        writer.writerows(all_rows)
    print(f"\nWrote {len(all_rows)} rows to {dist_path}")

    # Write summary CSV
    summary_path = os.path.join(output_dir, "ssa_wage_summary.csv")
    with open(summary_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "year", "total_earners", "avg_wage", "median_wage",
            "pct_below_avg", "total_net_compensation",
        ])
        writer.writeheader()
        writer.writerows(all_summaries)
    print(f"Wrote {len(all_summaries)} rows to {summary_path}")


if __name__ == "__main__":
    main()
