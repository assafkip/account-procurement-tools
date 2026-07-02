# account-procurement-tools

Programmatic, no-LLM Telegram OSINT pipeline: scrape channels, translate offline,
rule-extract account listings into a spreadsheet. Runs headless.

## Layout
- `account-procurement-pipeline/` — the pipeline (scrape → translate → extract → xlsx).
  See its `README.md` for setup and usage.
- `tgspyder/` — vendored Telegram scraper (Darksight Analytics, MIT), used by the pipeline.

## Quick start
```bash
cd account-procurement-pipeline
./setup.sh
./run.sh --channels config/channels.txt
```
