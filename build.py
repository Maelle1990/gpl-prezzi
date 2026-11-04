"""Scarica i dati aperti del Ministero (impianti + prezzi) e scrive data.json con i soli distributori che hanno il GPL."""
import json, re, sys, time, urllib.request

BASE = "https://www.mimit.gov.it/images/exportCSV/"
UA = "Mozilla/5.0 (compatible; DiarioGPL/1.0; uso personale)"

def scarica(nome):
    for tentativo in range(4):
        try:
            req = urllib.request.Request(BASE + nome + ".csv", headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read().decode("utf-8", errors="replace").split("\n")
        except Exception as e:
            print(f"{nome}: tentativo {tentativo + 1} fallito ({e})", file=sys.stderr)
            time.sleep(10 * (tentativo + 1))
    sys.exit(f"Impossibile scaricare {nome}")

righe_prezzi = scarica("prezzo_alle_8")
data_estrazione = righe_prezzi[0].replace("Estrazione del", "").strip()
prezzi = {}
for r in righe_prezzi[2:]:
    f = r.split("|")
    if len(f) < 5 or f[1] != "GPL":
        continue
    try:
        p = float(f[2])
    except ValueError:
        continue
    if 0.3 < p < 3 and (f[0] not in prezzi or p < prezzi[f[0]]):
        prezzi[f[0]] = p

marchi, comuni = [], []
def indice(lista, v):
    if v not in lista:
        lista.append(v)
    return lista.index(v)

def titolo(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s.title() if s.isupper() else s

stazioni = []
for r in scarica("anagrafica_impianti_attivi")[2:]:
    f = r.split("|")
    if len(f) < 10 or f[0] not in prezzi:
        continue
    try:
        lat, lon = float(f[8]), float(f[9])
    except ValueError:
        continue
    if not (35 < lat < 48 and 6 < lon < 19):
        continue
    bandiera = f[2].strip()
    nome = bandiera if bandiera and bandiera != "Pompe Bianche" else titolo(f[1])[:28]
    indirizzo = titolo(f[5])[:60]
    stazioni.append([indice(marchi, nome), indirizzo, indice(comuni, titolo(f[6])), round(lat, 4), round(lon, 4), prezzi[f[0]]])

if len(stazioni) < 1000:
    sys.exit(f"Dati sospetti: solo {len(stazioni)} distributori, non aggiorno")

with open("data.json", "w", encoding="utf-8") as fh:
    json.dump({"d": data_estrazione, "b": marchi, "c": comuni, "s": stazioni}, fh, ensure_ascii=False, separators=(",", ":"))
print(f"OK: {len(stazioni)} distributori con GPL, dati del {data_estrazione}")
