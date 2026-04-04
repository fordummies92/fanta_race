# Fanta Race

Webapp per visualizzare la classifica della tua lega di Fantacalcio con animazioni interattive.

Carica il file Excel esportato da Fantagazzetta o Fantacalcio e ottieni due grafici animati:

- **Bar Chart Race** — classifica cumulativa giornata per giornata con le barre che si riordinano in tempo reale
- **Line Chart** — punti accumulati nel tempo con le linee che si disegnano progressivamente

---

## Screenshot

| Upload | Dashboard |
|--------|-----------|
| Trascina il file Excel | Bar Chart Race + Line Chart animati |

---

## Requisiti

- Python 3.9+
- pip

---

## Installazione

```bash
git clone https://github.com/fordummies92/fanta_race.git
cd fanta_race
pip install flask openpyxl requests beautifulsoup4
```

---

## Avvio

```bash
python3 app.py
```

Apri il browser su [http://localhost:5050](http://localhost:5050).

---

## Come si usa

1. Esporta il calendario dalla tua lega su **Fantagazzetta** o **Fantacalcio** (file `.xlsx`)
2. Trascina il file nella pagina di upload
3. (Opzionale) Incolla l'URL della tua lega per caricare i loghi delle squadre
4. Clicca **Genera Grafici**

Nella dashboard:
- Premi **▶ Play** per avviare entrambe le animazioni in sincronia
- Usa **🐢 / 1× / ⚡** per cambiare velocità
- Trascina lo slider sotto ogni grafico per saltare a una giornata specifica

---

## Struttura del progetto

```
fanta_race/
├── app.py              # Backend Flask: parsing Excel, fetching loghi, routing
├── fanta_race.py       # Script originale: genera GIF/MP4 con matplotlib
├── templates/
│   ├── index.html      # Pagina di upload
│   └── dashboard.html  # Dashboard con i due grafici Plotly
└── README.md
```

---

## Formato Excel supportato

Il file deve contenere un foglio con righe nel formato Fantagazzetta/Fantacalcio (`Xª Giornata lega`). Il foglio può chiamarsi in qualsiasi modo — l'app lo individua automaticamente.

---

## Loghi squadre

Se inserisci l'URL della tua lega, l'app tenta di recuperare i loghi dalle API o dal sito:

- `https://leghe.fantacalcio.it/nome-lega/calendario`
- `https://leghe.fantagazzetta.com/nome-lega/12345`

Se i loghi non vengono trovati (le SPA non sempre espongono i dati nell'HTML), i grafici funzionano comunque con i colori assegnati automaticamente a ogni squadra.
