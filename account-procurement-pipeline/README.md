# Account Procurement Pipeline

Programmatic, no-LLM pipeline for account-fraud OSINT. It scrapes
Telegram channels for AdSense / AdMob / Ad Manager / YouTube Partner account
listings, translates them offline, extracts the fields by rules, and fills the
client's **Account Procurement** spreadsheet.

Built to run headless on the AWS box. No LLM, no external API calls at run time
(constraint: LLM research traffic is an attribution/licence risk).

## What it does

```
config/channels.txt
      │
      ▼
  tgspyder (scrape messages + invite links)   ← vendored at ../tgspyder
      │
      ▼
  detect language (lingua)  →  translate to English (Argos / CTranslate2, offline)
      │
      ▼
  rule extractor (account type, price, PIN, verified, qty, handles, …)
      │
      ▼
  Account-Procurement.xlsx   +   Telegram Groups tab (invite links)
```

## The one rule about country

The tool **never decides the account or actor country.** By design,
that is a human call made from clues: the language used, the Telegram account
location, and what the seller says. So the two geo columns
(**Ecosystem (Geo)**, **Geo of Acc.**) are left blank and highlighted. The clues
land in helper columns (`» Clue: Language`, `» Clue: Country Words`,
`» Clue: Phone Country`, `» Clue: TG Handles`) for you to make the call.

## Output columns

The sheet keeps the client's 23 columns in their exact order, then appends
helper columns (prefixed `»`):

- `» Confidence` — high / medium / low
- `» Needs Review` — YES when the row is sparse or low-confidence
- `» Clue: *` — the geo + handle clues
- `» Source Channel`, `» Message ID`, `» Message Date`
- `» Original Text`, `» English Text` — so every row is auditable

## Setup (once, per machine)

```bash
./setup.sh
```

Creates `.venv`, installs deps, installs the vendored tgspyder, and downloads the
offline translation models. The model download is the only step needing network;
on an air-gapped box, run it elsewhere and copy `~/.local/share/argos-translate/`.

### Windows (AWS Windows Server)

Prereqs: **Git** and **Python 3.10+** on PATH (`git --version`, `python --version`).
If missing: `winget install Git.Git` and `winget install Python.Python.3.12`.

```powershell
git clone https://github.com/assafkip/account-procurement-tools.git
cd account-procurement-tools\account-procurement-pipeline
powershell -ExecutionPolicy Bypass -File .\setup.ps1
```

Authenticate tgspyder once, then run:

```powershell
.\.venv\Scripts\python.exe -m tgspyder.cli "@admobbygoogleplatform" --chats
powershell -ExecutionPolicy Bypass -File .\run.ps1 --channels config\channels.txt
```

`setup.ps1` / `run.ps1` mirror the `.sh` scripts. They call the venv Python
directly, so you never have to activate the venv.

### Authenticate tgspyder once

tgspyder logs into Telegram interactively the first time and reuses the session.
Do this once before batch runs, or a fresh run will block on a login code:

```bash
source .venv/bin/activate
tgspyder @somechannel --chats
```

### Vietnamese

Argos ships RU/ZH/ES→EN etc. Vietnamese (`vi→en`) is often not in the default
index. Two options:
1. Convert the Helsinki-NLP `opus-mt-vi-en` model to `.argosmodel` and install it.
2. Skip it: Vietnamese posts still get detected and keyword-matched in their own
   language (the keyword dictionaries include Vietnamese terms).

## Run

```bash
./run.sh                                   # uses config/channels.txt
./run.sh --proxy socks5://127.0.0.1:9050   # via SOCKS proxy
./run.sh --channels /path/to/list.txt --out /path/to/out.xlsx
```

Add targets to `config/channels.txt` (one per line; `@handle`, `t.me/name`, or
`t.me/+invite`).

## Extending the rules

- `config/keywords.json` — account-type synonyms, flags, payment/transfer terms.
  Add terms in any language; matching is case-insensitive with word boundaries
  for short Latin terms and substring for CJK.
- `config/countries.json` — country name/demonym/local terms for the clue column.

## Tests

```bash
python3 tests/test_extract.py       # rule extractor + geo clues (no deps)
python3 tests/test_build_sheet.py   # workbook writer (needs openpyxl)
```

Both run offline with no Telegram, no models, no network.

## Files

| Path | Role |
|------|------|
| `src/scrape.py` | drive tgspyder, read its CSVs |
| `src/lang_translate.py` | offline detect + translate (lazy heavy imports) |
| `src/extract.py` | rule-based field extraction |
| `src/geo_clues.py` | gather geo clues, never decide |
| `src/build_sheet.py` | write the client workbook |
| `src/pipeline.py` | orchestrate end to end |
| `config/*.json` | keyword + country dictionaries |
| `config/channels.txt` | your target list |
