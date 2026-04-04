"""
Script di debug per il recupero dei loghi.
Esegui con F5 in VS Code oppure: python3 debug_logos.py
"""
import json
import requests
from bs4 import BeautifulSoup
from app import fetch_logos, _try_api_endpoints, _scrape_page_for_logos

LEAGUE_URL = 'https://leghe.fantacalcio.it/fantaregazquercioli/calendario'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36',
    'Accept-Language': 'it-IT,it;q=0.9,en;q=0.8',
}

def debug_step1_api():
    """Prova gli endpoint API REST con lo slug della lega."""
    print('\n=== STEP 1: API REST ===')
    slug = 'fantaregazquercioli'
    endpoints = [
        f'https://leghe.fantacalcio.it/api/v1/leagues/{slug}/participants',
        f'https://leghe.fantacalcio.it/api/v1/leagues/{slug}/ranking',
        f'https://leghe.fantacalcio.it/api/v1/leagues/{slug}/teams',
        f'https://leghe.fantacalcio.it/api/leagues/{slug}/participants',
        f'https://leghe.fantacalcio.it/api/{slug}/teams',
    ]
    for url in endpoints:
        try:
            r = requests.get(url, headers={**HEADERS, 'Accept': 'application/json'}, timeout=8)
            print(f'  {r.status_code}  {url}')
            if r.status_code == 200:
                print(f'    → risposta: {r.text[:300]}')
        except Exception as e:
            print(f'  ERR  {url}  → {e}')


def debug_step2_html(page_url):
    """Scarica la pagina e ispeziona HTML grezzo + script tag."""
    print(f'\n=== STEP 2: HTML di {page_url} ===')
    try:
        r = requests.get(page_url, headers={**HEADERS, 'Accept': 'text/html'}, timeout=12)
        print(f'  status: {r.status_code}')
        soup = BeautifulSoup(r.text, 'html.parser')

        # Script tag
        scripts = soup.find_all('script')
        print(f'  script tag trovati: {len(scripts)}')
        for i, s in enumerate(scripts):
            t = s.get('type', '')
            src = s.get('src', '')
            content_preview = (s.string or '')[:120].replace('\n', ' ')
            print(f'    [{i}] type={t!r} src={src!r}  content={content_preview!r}')

        # Img tag con parole chiave
        imgs = soup.find_all('img')
        print(f'\n  img tag trovati: {len(imgs)}')
        for img in imgs:
            src = img.get('src', '') or img.get('data-src', '')
            alt = img.get('alt', '')
            if any(kw in src.lower() for kw in ['logo', 'team', 'squadra', 'crest', 'shield', 'avatar']):
                print(f'    alt={alt!r}  src={src!r}')

    except Exception as e:
        print(f'  ERRORE: {e}')


def debug_step3_nuxt(page_url):
    """Cerca JSON Nuxt/__NUXT_DATA__ nella pagina e mostra le chiavi di primo livello."""
    import re
    print(f'\n=== STEP 3: JSON embedded in {page_url} ===')
    try:
        r = requests.get(page_url, headers={**HEADERS, 'Accept': 'text/html'}, timeout=12)
        soup = BeautifulSoup(r.text, 'html.parser')
        for script in soup.find_all('script'):
            content = script.string or ''
            # Nuxt data tag
            if script.get('id') in ('__NUXT_DATA__',) or 'type' == 'application/json':
                print(f'  trovato script id={script.get("id")} type={script.get("type")}')
                print(f'  preview: {content[:500]}')
            # window.__NUXT__
            m = re.search(r'window\.__NUXT__\s*=\s*(\{.+)', content, re.DOTALL)
            if m:
                print(f'  trovato window.__NUXT__')
                print(f'  preview: {m.group(1)[:500]}')
    except Exception as e:
        print(f'  ERRORE: {e}')


def debug_step4_full():
    """Esegue fetch_logos completo e mostra il risultato."""
    print(f'\n=== STEP 4: fetch_logos completo ===')
    logos = fetch_logos(LEAGUE_URL)
    print(f'  Loghi trovati: {len(logos)}')
    for name, url in logos.items():
        print(f'    {name!r}: {url}')
    return logos


if __name__ == '__main__':
    pages = [
        'https://leghe.fantacalcio.it/fantaregazquercioli/classifica',
        'https://leghe.fantacalcio.it/fantaregazquercioli/squadre',
        LEAGUE_URL,
    ]

    debug_step1_api()
    for page in pages:
        debug_step2_html(page)
        debug_step3_nuxt(page)

    logos = debug_step4_full()

    print('\n=== RISULTATO FINALE ===')
    print(json.dumps(logos, indent=2, ensure_ascii=False))
