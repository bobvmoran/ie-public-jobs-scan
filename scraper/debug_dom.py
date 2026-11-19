"""Temporary: print page structure facts to the Actions log."""
import json, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
sys.path.insert(0, str(Path(__file__).parent))
from sources import SOURCES

PROBES = {
    "hse-limerick": ["Accountant 076Y", "Grade VII Project Manager"],
    "tusla-live": [],
    "localgovernmentjobs": ["Marketing Officer (AO Grade VII)"],
    "central-bank": [],
    "staffline-getgot": ["Public Sector"],
    "jobs-ac-uk-ireland": [],
    "publicjobs-news": [],
    "jobsie-public-sector": [],
}
JS = r"""(probes) => {
  const chain = el => { const out=[]; while (el && el !== document.body && out.length < 8) {
      out.push(el.tagName.toLowerCase() + (el.id ? '#'+el.id : '') + (el.className && typeof el.className==='string' ? '.'+el.className.trim().split(/\s+/).slice(0,3).join('.') : '') + (el.getAttribute('role') ? '[role='+el.getAttribute('role')+']' : ''));
      el = el.parentElement; } return out.join(' < '); };
  const res = {probes: {}, pager: [], counts: {}, links: []};
  for (const p of probes) {
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT); let n, hits = [];
    while ((n = w.nextNode()) && hits.length < 2) if (n.textContent.includes(p)) hits.push(chain(n.parentElement));
    res.probes[p] = hits;
  }
  const re = /^(next.*|previous.*|\d{1,2}|›|»|>|load more.*|show more.*|view more.*|all)$/i;
  for (const el of document.querySelectorAll('a,button,[role=button],[role=link],input[type=submit],li')) {
    const t = ((el.innerText || el.value || '') + '').trim().replace(/\s+/g,' ');
    const a = el.getAttribute('aria-label') || '';
    if ((re.test(t) || /next|page/i.test(a)) && res.pager.length < 25 && t.length < 40)
      res.pager.push({tag: el.tagName.toLowerCase(), text: t, aria: a, href: el.getAttribute('href'), cls: (el.className+'').slice(0,60), vis: !!(el.offsetWidth||el.offsetHeight), chain: chain(el).slice(0,160)});
  }
  for (const s of ['select','option','main','form','[role=listbox]','[role=option]','input[type=checkbox]','nav','header','footer','iframe'])
    res.counts[s] = document.querySelectorAll(s).length;
  res.textLen = (document.body.innerText||'').length;
  res.mainLen = document.querySelector('main') ? document.querySelector('main').innerText.length : null;
  res.formLens = Array.from(document.querySelectorAll('form')).map(f => [chain(f).slice(0,80), f.innerText.length]);
  res.links = Array.from(document.querySelectorAll('a[href]')).filter(a => /candidatemanager|proceed/i.test(a.href + a.innerText)).map(a => [a.innerText.trim().slice(0,50), a.href]).slice(0,5);
  res.title = document.title; res.url = location.href;
  return res; }"""
with sync_playwright() as p:
    b = p.chromium.launch()
    for src in SOURCES:
        if src["slug"] not in PROBES: continue
        ctx = b.new_context(locale="en-IE", timezone_id="Europe/Dublin"); page = ctx.new_page()
        print("=====", src["slug"])
        try:
            r = page.goto(src["url"], wait_until="domcontentloaded", timeout=45000)
            try: page.wait_for_load_state("networkidle", timeout=15000)
            except Exception: pass
            print("status", r.status if r else None)
            print(json.dumps(page.evaluate(JS, PROBES[src["slug"]]), indent=1)[:6000])
        except Exception as e:
            print("ERR", type(e).__name__, str(e)[:200])
        ctx.close(); time.sleep(3)
    b.close()
