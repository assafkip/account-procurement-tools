#!/usr/bin/env python3
"""Deterministic tests for the rule extractor and geo-clue gatherer.

No network, no LLM, no telegram. Run: python3 -m pytest tests/ -q
or: python3 tests/test_extract.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import extract  # noqa: E402
import geo_clues  # noqa: E402

KW = extract.load_keywords()
COUNTRIES = geo_clues.load_countries()


def test_english_adsense_listing():
    post = "Selling verified Google AdSense account, payment attached, $150 each. 5 in stock. DM @seller_ads"
    lower = post.lower()
    assert extract.is_listing(lower, KW)
    assert extract.detect_account_type(lower, KW) == "AdSense"
    fields = extract.extract_listing(post, "", KW)
    assert fields["verified"] == "verified"
    assert fields["payment_attached"] == "payment attached"
    assert fields["cost"] == "$150"
    assert fields["quantity"] == "5"
    assert "@seller_ads" in fields["handles"]


def test_russian_adsense_translated():
    original = "Продам аккаунты гугл адсенс, верифицирован, цена 50$"
    english = "Selling google adsense accounts, verified, price 50$"
    lower = (original + "\n" + english).lower()
    assert extract.is_listing(lower, KW)
    assert extract.detect_account_type(lower, KW) == "AdSense"
    fields = extract.extract_listing(original, english, KW)
    assert fields["verified"] in ("verified", "верифиц")
    assert "50$" in " ".join(fields["all_prices"])


def test_vietnamese_admob():
    post = "Bán tài khoản admob, có thẻ, 200 usd"
    lower = post.lower()
    assert extract.detect_account_type(lower, KW) == "AdMob"
    fields = extract.extract_listing(post, "", KW)
    assert fields["payment_attached"] == "có thẻ"
    assert "200 usd" in " ".join(fields["all_prices"]).lower()


def test_chinese_youtube_partner():
    post = "出售 油管 partner 账号 已验证"
    lower = post.lower()
    assert extract.detect_account_type(lower, KW) == "YouTube Partner"
    fields = extract.extract_listing(post, "", KW)
    assert fields["verified"] == "已验证"


def test_non_listing_is_skipped():
    post = "Good morning everyone, how is the weather today?"
    assert not extract.is_listing(post.lower(), KW)


def test_no_pin_is_more_specific_than_pin():
    post = "AdSense account, no pin, aged 2019"
    fields = extract.extract_listing(post, "", KW)
    assert fields["pin"] == "no pin"
    assert fields["age"] in ("2019", "aged")


def test_country_words_are_clues_not_decisions():
    original = "US and Spain adsense accounts, seller is russian"
    clues = geo_clues.gather_clues(original, "", "Russian", COUNTRIES)
    assert "United States" in clues["country_words"]
    assert "Spain" in clues["country_words"]
    assert "Russia" in clues["country_words"]
    assert clues["language"] == "Russian"


def test_phone_country_prefix():
    assert geo_clues.phone_country("+1 415 555 0100") == "United States/Canada"
    assert geo_clues.phone_country("+79161234567") == "Russia/Kazakhstan"
    assert geo_clues.phone_country("") == ""


def test_focus_does_not_false_match_us():
    # 'us' must not match inside 'focus' (word-boundary guard)
    clues = geo_clues.gather_clues("stay focused on the task", "", "English", COUNTRIES)
    assert "United States" not in clues["country_words"]


def _run_all():
    tests = [value for name, value in sorted(globals().items()) if name.startswith("test_")]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as error:
            failed += 1
            print(f"FAIL {test.__name__}: {error}")
        except Exception as error:  # noqa: BLE001
            failed += 1
            print(f"ERROR {test.__name__}: {type(error).__name__}: {error}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(_run_all())
