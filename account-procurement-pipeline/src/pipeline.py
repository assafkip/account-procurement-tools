#!/usr/bin/env python3
"""End-to-end pipeline: channels -> scrape -> translate -> extract -> workbook.

No LLM, no external API. Runs headless on the AWS box. Country columns are
never filled by the machine; the geo clues are surfaced for a human decision.

Usage:
    python3 src/pipeline.py --channels config/channels.txt --out output/Account-Procurement.xlsx
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

SRC = Path(__file__).resolve().parent
sys.path.insert(0, str(SRC))

import extract  # noqa: E402
import geo_clues  # noqa: E402
import build_sheet  # noqa: E402
import scrape  # noqa: E402
import lang_translate  # noqa: E402

PACKAGE_ROOT = SRC.parent


def read_channels(path):
    """Read non-blank, non-comment lines from the channel list."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]


def score_confidence(fields):
    """Confidence for a listing row, and whether a human must review it."""
    has_type = bool(fields["account_type"])
    has_price = bool(fields["cost"])
    extras = sum(bool(fields[key]) for key in ("verified", "quantity", "payment_attached", "handles"))
    if has_type and has_price and extras >= 1:
        return ("high", False)
    if has_type and (has_price or extras >= 1):
        return ("medium", True)
    return ("low", True)


def build_record(message, channel, keywords, countries, run_date):
    """Turn one scraped message into a listing record, or None if not a listing."""
    original = message.get("text", "") or ""
    language_name, iso = lang_translate.detect_language(original)
    english = lang_translate.translate_to_english(original, iso)
    combined_lower = (original + "\n" + english).lower()

    if not extract.is_listing(combined_lower, keywords):
        return None

    fields = extract.extract_listing(original, english, keywords)
    clues = geo_clues.gather_clues(original, english, language_name, countries)
    confidence, needs_review = score_confidence(fields)

    return {
        "date_of_finding": run_date,
        "url": _message_url(channel, message.get("message_id", "")),
        "vendor_name": channel,
        "account_type": fields["account_type"],
        "details": english[:500] if english else original[:500],
        "age": fields["age"],
        "verified": fields["verified"],
        "farmed": fields["farmed"],
        "spend": fields["spend"],
        "payment_attached": fields["payment_attached"],
        "pin": fields["pin"],
        "history": fields["history"],
        "transfer_method": fields["transfer_method"],
        "cost": fields["cost"],
        "quantity": fields["quantity"],
        "payment_method": fields["payment_method"],
        "clue_language": clues["language"],
        "clue_country_words": clues["country_words"],
        "clue_handles": fields["handles"],
        "clue_phone_country": "",
        "confidence": confidence,
        "needs_review": needs_review,
        "source_channel": channel,
        "message_id": message.get("message_id", ""),
        "message_date": message.get("date", ""),
        "text_original": original[:2000],
        "text_english": english[:2000] if english else "",
    }


def _message_url(channel, message_id):
    handle = channel.lstrip("@").rstrip("/").split("/")[-1]
    if handle and message_id:
        return f"https://t.me/{handle}/{message_id}"
    return channel


def run(channels_path, out_path, workdir, proxy=None, run_date=None):
    """Run the full pipeline over every channel and write the workbook."""
    run_date = run_date or datetime.now().strftime("%Y-%m-%d")
    keywords = extract.load_keywords()
    countries = geo_clues.load_countries()

    ready, missing = lang_translate.ensure_ready()
    if not ready:
        print(f"[FAIL] offline translation not ready. Missing: {', '.join(missing)}", file=sys.stderr)
        print("       Run ./setup.sh to install detection + translation models.", file=sys.stderr)
        return 1

    records = []
    invites = []
    channels = read_channels(channels_path)
    if not channels:
        print("[FAIL] no channels to scrape. Add targets to the channel list.", file=sys.stderr)
        return 1

    for channel in channels:
        print(f"[*] scraping {channel}")
        scrape.run_target(channel, workdir, proxy=proxy)
        messages = scrape.read_messages(scrape.newest_csv(workdir, "chats", "messages"))
        for message in messages:
            record = build_record(message, channel, keywords, countries, run_date)
            if record:
                records.append(record)
        for link in scrape.read_invites(scrape.newest_csv(workdir, "crawled_links", "crawled_links")):
            invites.append({"invite_link": link, "source_channel": channel, "first_seen": run_date})
        print(f"    {len(messages)} messages, {len(records)} listings so far")

    out = build_sheet.save_sheet(records, out_path, invites=invites)
    review_count = sum(1 for record in records if record["needs_review"])
    print(f"[OK] {len(records)} listings ({review_count} need review), "
          f"{len(invites)} invite links -> {out}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Telegram account-procurement pipeline (no LLM).")
    parser.add_argument("--channels", default=str(PACKAGE_ROOT / "config" / "channels.txt"))
    parser.add_argument("--out", default=str(PACKAGE_ROOT / "output" / "Account-Procurement.xlsx"))
    parser.add_argument("--workdir", default=str(PACKAGE_ROOT / "output" / "scrape"))
    parser.add_argument("--proxy", default=None, help="SOCKS proxy, e.g. socks5://127.0.0.1:9050")
    args = parser.parse_args()
    return run(args.channels, args.out, args.workdir, proxy=args.proxy)


if __name__ == "__main__":
    sys.exit(main())
