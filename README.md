# Irish public sector jobs scan

Every Monday morning a GitHub Action opens a list of public job-listing pages in a
headless browser and saves what they show to `data/`:

- `data/index.json` – one row per page: loaded, blocked, empty or error.
- `data/pages/<slug>.md` – the job-like links and the visible page text.

A scheduled Claude task reads these files later on Monday and updates the tracker.

## Rules it follows

Read only. It opens public listing pages, can click a "Next" link or button to page through
results, and does nothing else: no sign-in, no forms, no applications. A login wall,
403 or CAPTCHA is recorded as `blocked` and left alone. It pauses a few seconds
between pages.

## Changing what it reads

Edit `scraper/sources.py`. Each entry is a name, a file slug and a public URL.

## Running it by hand

Actions tab → "Weekly jobs scan" → Run workflow.

Locally: `pip install -r requirements.txt && python -m playwright install chromium && python scraper/scrape.py`
(add slugs to run only some pages, e.g. `python scraper/scrape.py hse-limerick tus`).
