#!/usr/bin/env python3
"""Verify the workbook writer: headers exact, geo columns blank, helpers filled."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import build_sheet  # noqa: E402
from openpyxl import load_workbook  # noqa: E402

SAMPLE = [{
    "date_of_finding": "2026-07-02", "url": "https://t.me/x", "vendor_name": "@seller",
    "account_type": "AdSense", "details": "verified adsense $150", "cost": "$150",
    "verified": "verified", "quantity": "5", "confidence": "high", "needs_review": False,
    "clue_language": "Russian", "clue_country_words": ["United States", "Spain"],
    "clue_handles": ["@seller"], "source_channel": "@market", "message_id": "42",
    "text_original": "Продам adsense", "text_english": "Selling adsense",
}]


def test_headers_and_values():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "out.xlsx"
        build_sheet.save_sheet(SAMPLE, out, invites=[
            {"invite_link": "https://t.me/+abc", "source_channel": "@market", "first_seen": "2026-07-02"}
        ])
        workbook = load_workbook(out)
        sheet = workbook["Account Procurement"]
        headers = [c.value for c in sheet[1]]

        # The 23 client columns must appear first, in order.
        assert headers[:23] == build_sheet.TEMPLATE_COLUMNS
        # Row 2 = our sample listing.
        row = {headers[i]: sheet[2][i].value for i in range(len(headers))}
        assert row["Account Type"] == "AdSense"
        assert row["Cost"] == "$150"
        assert row["Verified"] == "verified"
        assert row["No. Available"] == 5 or row["No. Available"] == "5"
        # Geo columns are intentionally blank (human fills them).
        assert row["Geo of Acc."] in (None, "")
        assert row["Ecosystem (Geo)"] in (None, "")
        # Clues are present in helper columns.
        assert row["» Clue: Language"] == "Russian"
        assert "United States" in row["» Clue: Country Words"]
        # Second tab exists with the invite link.
        groups = workbook["Telegram Groups"]
        assert [c.value for c in groups[1]] == ["Invite Link", "Source Channel", "First Seen"]
        assert groups[2][0].value == "https://t.me/+abc"
        print("PASS test_headers_and_values")


if __name__ == "__main__":
    test_headers_and_values()
    print("\n1/1 passed")
