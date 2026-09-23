# Rinomina immagini PNG da CSV

Questo script legge un file CSV contenente i codici prodotto (`COD`) e i relativi codici EAN13, poi rinomina i file `.png` presenti nella cartella `tag` usando come nuovo nome il valore `EAN13`.

## Obiettivo

L’idea è semplice:

- ogni file PNG nella cartella `tag` ha un nome come `54454.png`
- nel CSV esiste una riga del tipo:
  `54454;80000000000`
- lo script cerca il codice `77546` nella colonna `COD`
- se lo trova, rinomina il file in:
  `80000000000.png`

## Struttura dei file

Il programma si aspetta questa struttura:

```text
cartella_progetto/
├── rinomina_tag.py
├── LISTA-CODICI.csv
└── tag/
    ├── 54454.png
    ├── 54454PR.png
    └── ...
```

## Esempio CSV

Il file CSV deve avere una struttura simile a questa:

```csv
COD;EAN
54454;80000000000
```

## Come funziona

Lo script esegue questi passaggi:

1. Verifica che il file CSV esista.
2. Verifica che la cartella `tag` esista.
3. Legge il CSV e costruisce una mappa:
   - chiave: codice prodotto normalizzato
   - valore: EAN13
4. Scorre tutti i file `.png` della cartella `tag`.
5. Normalizza il nome del file (es. rimuove spazi, trattini, punti, zeri iniziali).
6. Cerca quel valore nella mappa letta dal CSV.
7. Se trova una corrispondenza:
   - rinomina il file con il nuovo nome EAN13
8. Se non trova una corrispondenza:
   - lo segnala come “senza corrispondenza nel CSV”

## Normalizzazione

Per evitare problemi dovuti a piccole differenze nei formati, lo script normalizza sia i codici del CSV sia i nomi dei file:

- rimuove spazi
- rimuove underscore
- rimuove trattini
- rimuove punti
- rimuove zeri iniziali
- converte in maiuscolo

Questo permette di confrontare stringhe come:

- `001234`
- `1234`
- `1234-5`
- `1234_5`

come se fossero lo stesso codice.

## Modalità prova

Il programma supporta una modalità sicura:

```bash
python rinomina_tag.py --prova
```

In questo modo:

- mostra i file che verrebbero rinominati
- non modifica realmente i file

Per eseguire il rinomino effettivo:

```bash
python rinomina_tag.py
```

## Note importanti

- il programma rinomina solo file `.png`
- se un file destinazione già esiste, viene saltato
- se il CSV ha separatori misti o dati non ben formattati, potrebbe essere necessario correggere il formato dei dati

## Esempio di output

```text
Codici letti dal CSV: 150
54454.png -> 80000000000.png

--- Riepilogo ---
Rinominati: 1
```

## Requisiti

- Python 3
- librerie standard Python (`csv`, `re`, `pathlib`)

## Licenza

Questo progetto è rilasciato senza una licenza specifica, salvo diversa indicazione del proprietario del repository.
