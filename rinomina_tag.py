"""
Rinomina le immagini .png della cartella "tag" usando CC_2027SCH.csv.
Il nome attuale dell'immagine (es. 12345.png) viene cercato nella colonna COD
e il file viene rinominato con il valore della colonna EAN13 (es. 8001234567890.png).

Struttura attesa:
    cartella_principale/
        rinomina_tag.py
        CC_2027SCH.csv
        tag/
            12345.png
            ...

Uso:
    python rinomina_tag.py          -> rinomina i file
    python rinomina_tag.py --prova  -> mostra solo cosa farebbe, senza rinominare
"""
import csv
import sys
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
CSV_FILE = BASE / "CC_2027SCH.csv"
TAG_DIR = BASE / "tag"
PROVA = "--prova" in sys.argv


def normalizza(valore):
    """Normalizza COD e nome file per confronto robusto."""
    if valore is None:
        return ""
    v = str(valore).strip().strip('"').strip("'").upper()
    v = v.replace(" ", "").replace("_", "").replace("-", "").replace(".", "")
    v = re.sub(r"^0+", "", v)
    return v or "0"


def leggi_csv():
    raw = CSV_FILE.read_bytes()
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            testo = raw.decode(enc)
            break
        except UnicodeDecodeError:
            continue

    righe = [r.strip() for r in testo.splitlines() if r.strip()]
    if not righe:
        sys.exit("CSV vuoto.")

    # Trova il separatore giusto: ; oppure ,
    contatori = {sep: 0 for sep in (";", ",", "\t")}
    for riga in righe:
        for sep in contatori:
            parti = [p.strip() for p in riga.split(sep)]
            if len(parti) == 2:
                contatori[sep] += 1

    separatore = max(contatori, key=contatori.get)
    if contatori[separatore] == 0:
        sys.exit("Impossibile capire il separatore del CSV.")

    reader = csv.reader(righe, delimiter=separatore)

    rows = list(reader)
    if len(rows) < 2:
        sys.exit("CSV senza dati.")

    header = [h.strip().upper() for h in rows[0]]
    if "COD" not in header or "EAN13" not in header:
        sys.exit(f"Colonne COD/EAN13 non trovate. Header: {rows[0]}")

    idx_cod = header.index("COD")
    idx_ean = header.index("EAN13")

    mappa = {}
    for riga in rows[1:]:
        if len(riga) <= max(idx_cod, idx_ean):
            continue
        cod = (riga[idx_cod] if idx_cod < len(riga) else "").strip()
        ean = (riga[idx_ean] if idx_ean < len(riga) else "").strip().strip('"')

        if not cod or not ean:
            continue
        if "E+" in ean.upper():
            print(f"ATTENZIONE: EAN in notazione scientifica per COD {cod} ({ean}). "
                  "Riesporta il CSV con la colonna EAN13 formattata come testo.")
            continue
        mappa[normalizza(cod)] = ean

    return mappa


def main():
    if not CSV_FILE.exists():
        sys.exit(f"File non trovato: {CSV_FILE}")
    if not TAG_DIR.is_dir():
        sys.exit(f"Cartella non trovata: {TAG_DIR}")

    mappa = leggi_csv()
    print(f"Codici letti dal CSV: {len(mappa)}")

    rinominati, non_trovati, saltati = 0, [], []
    for img in sorted(TAG_DIR.iterdir()):
        if not img.is_file() or img.suffix.lower() != ".png":
            continue

        chiave_file = normalizza(img.stem)
        ean = mappa.get(chiave_file)

        if ean is None:
            non_trovati.append(f"{img.name} (chiave cercata: {chiave_file})")
            continue

        nuovo = img.with_name(f"{ean}{img.suffix.lower()}")
        if nuovo == img:
            continue
        if nuovo.exists():
            saltati.append(f"{img.name} -> {nuovo.name} (esiste già)")
            continue

        print(f"{img.name} -> {nuovo.name}")
        if not PROVA:
            img.rename(nuovo)
        rinominati += 1

    print("\n--- Riepilogo ---")
    print(f"{'Da rinominare' if PROVA else 'Rinominati'}: {rinominati}")
    if non_trovati:
        print(f"Senza corrispondenza nel CSV ({len(non_trovati)}):")
        for n in non_trovati[:20]:
            print("  " + n)
        if len(non_trovati) > 20:
            print("  ...")
    if saltati:
        print(f"Saltati ({len(saltati)}):")
        for s in saltati:
            print("  " + s)
    if PROVA:
        print("\nModalità prova: nessun file è stato modificato.")


if __name__ == "__main__":
    main()