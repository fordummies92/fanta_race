# fanta_race — Fantagazzetta Chart Race

## Descrizione
Webapp che genera bar chart race e line chart race dinamici
dai file Excel esportati da Fantagazzetta (lega Serie A italiana).

L'utente carica il proprio file `.xlsx` dalla lega Fantagazzetta
e ottiene una visualizzazione animata dell'andamento della classifica
giornata per giornata.

## Stack
- **Backend**: Python — FastAPI
- **Frontend**: HTML + JavaScript (D3.js per le animazioni)
- **Parsing Excel**: pandas + openpyxl

## Funzionalità principali
- Upload file `.xlsx` da Fantagazzetta
- Parsing automatico dei dati per giornata
- Bar chart race — classifica animata nel tempo
- Line chart race — andamento punti nel tempo

## Setup
```bash
pip install -r requirements.txt
uvicorn app:app --reload
```

## Variabili d'ambiente
- nessuna per ora (aggiungere in `.env` quando necessario)

## Comandi principali
- **Avviare il server**: `uvicorn app:app --reload`
- **Eseguire i test**: `python -m pytest tests/`
- **Linter**: `python -m flake8 app.py`

## Architettura
- `app.py` — server FastAPI, endpoint upload e rendering
- `parser.py` — logica parsing file Excel Fantagazzetta
- `static/` — frontend HTML/CSS/JS
- `tests/` — test automatizzati

## Convenzioni
- Python 3.10+, PEP8
- Non committare mai file `.xlsx` o `.env`
