import csv,hashlib,html,json,pathlib,shutil,sys,zipfile,xml.etree.ElementTree as ET
from bildentscheidungen import PAGE_NOTES
B=pathlib.Path(__file__).resolve().parent;O=B/'ausgabe';V=B/'vergleich'
changes=json.loads((O/'Aenderungsprotokoll.json').read_text());val=json.loads((O/'Validierung.json').read_text());payload=json.loads((V/'Vergleich.json').read_text())
for p in payload['pages']:
 n=p['pdf'];kind,note=PAGE_NOTES[n];p.update(visual_review='image-viewed-selective-collation',font_classification=kind,visual_note=note,local_corrections=sum(r['pdf']==n for r in changes))
 f=V/'seiten'/f'seite-{n:03}.html'
 if n==2:f.write_text('<!doctype html><meta charset="utf-8"><title>PDF 2 Stempelseite</title><a href="../vergleich.html">Übersicht</a> · <a href="seite-003.html">Nächste</a><h1>PDF 2: Stempelseite</h1><img style="max-width:100%" src="../scans/p-002.png">')
 doc=f.read_text();start='<!-- BEGIN MANUAL -->';end='<!-- END MANUAL -->'
 if start in doc:doc=doc[:doc.index(start)]+doc[doc.index(end)+len(end):]
 panel=start+'<aside style="padding:1em;border:2px solid #387760;background:#f4fff8"><h2>Bildsichtung und lokale Entscheidungen</h2><p>'+html.escape(note)+'</p><p>Umfang: Bildsichtung und punktuelle Kollation; keine vollständige Zeichen- oder Niqqud-Freigabe. Der farbige Vergleich darunter zeigt die ursprüngliche Prüffassung gegen die neue OCR.</p><a href="../../ausgabe/Aenderungsprotokoll.md">Änderungsprotokoll</a> · <a href="../../ausgabe/Offene_Stellen.csv">Offene Stellen</a>'
 for r in changes:
  if r['pdf']==n:panel+='<p>'+html.escape(r['element_id'])+': <span dir="rtl">'+html.escape(r['before'])+'</span> → <strong dir="rtl">'+html.escape(r['after'])+'</strong><br>'+html.escape(r['reason'])+'</p>'
 panel+='</aside>'+end
 pos=doc.index('<h1>');doc=doc[:pos]+panel+doc[pos:];f.write_text(doc)
(V/'Vergleich.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
with (V/'Seitenstatus.csv').open('w',newline='',encoding='utf-8-sig') as f:
 keys=['pdf','folio','token_similarity','differences','source_uncertainty_markers','visual_review','font_classification','local_corrections','visual_note'];w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(payload['pages'])
readme='''# Siddur HaRashash Teil 1 – Scanabgleich, 26.10.2026

Ergebnis: 56 lokale Korrekturen in 43 Textelementen. 177 Scanbilder gesichtet, davon 171 mit Raschi-Schrift einschließlich kleiner Glossen und Errata. 176 Textseiten; PDF 2 ist die ausgelassene Stempelseite.

**Prüfstand: Bildsichtung mit punktueller Kollation, keine vollständig zeichenweise kollationierte oder fachlich freigegebene Ausgabe.** Die 143 bisherigen [?]-Markierungen bleiben erhalten. Schwer lesbare Stellen, besonders dichte Fachabkürzungen, sind weiterhin offen; die Sichtung bestätigt keineswegs jeden unveränderten Buchstaben. Auch unmarkierte Restfehler sind möglich. Die neue OCR ist ein fehlbarer Vergleichszeuge.

## Dateien öffnen

- `ausgabe/Siddur_HaRashash_Teil_1_HB21376_Niqqud_Tags_Scanabgleich.txt`: neue UTF-8-Fassung mit XML-Tags und Niqqud.
- `ausgabe/Aenderungsprotokoll.md` und `.json`: jeder Eingriff mit PDF-Seite, Element-ID, Vorher/Nachher und Begründung.
- `ausgabe/Seitensichtung.csv`: Umfang und Beobachtungen für jede einzelne Scanseite.
- `ausgabe/Offene_Stellen.csv` und `.json`: alle weiterhin markierten Textelemente.
- `vergleich/vergleich.html`: lokale Seitenübersicht; jede Seite zeigt Scan, Prüffassung und neue OCR. Ordner vollständig entpacken, dann im Browser öffnen. Kein Server erforderlich.
- `vergleich/Unterschiede.csv` und `Vergleich.json`: alle 5.204 maschinell ermittelten Differenzblöcke der Ausgangsfassung gegen die neue OCR. Das sind Kandidaten, keine 5.204 nachgewiesenen Fehler. Die Blöcke wurden nicht alle einzeln abschließend entschieden.
- `ausgabe/Validierung.json`: technische Prüfungen und Prüfsummen.

## Methode und Grenzen

Das Vergleichsskript ordnet Seiten über `Seite_NNN.png` zu. Niqqud, Anführungszeichen und Leerraum werden nur für den Vergleich normalisiert; Wortfolgen werden mit SequenceMatcher verglichen. Die Originaltexte bleiben erhalten. Mehrspaltige Namen- und Vokaltabellen können durch lineare OCR falsch angeordnet sein. Kein OCR-Vorschlag wird automatisch übernommen.

Alle vorgenommenen Konsonantenänderungen sind im Bildentscheidungsprotokoll verzeichnet. Neu gelesene gewöhnliche Wörter erhalten redaktionelle Vokalisierung; die unpunktierten Raschi-Abschnitte des Drucks bestätigen diese Vokalisierung nicht. Die übrige automatische Niqqud-Fassung wurde nicht vollständig neu vokalisiert. Technische Kürzel und die offene aramäische Folge auf PDF 43/48 erhalten keine erfundene Aussprache. Die Zahl שע״ח dort ist durch Bildlesung, Parallelstelle und חשמל=378 gestützt; der Absatz bleibt ausdrücklich unsicher.

Bereits die Ausgangsfassung zieht mehrseitige Absätze und Fußnoten zusammen: PDF 11–14 unter 11; 19–23 unter 19; Teile um 50–59 unter 51; 94–96 unter 94; 97–98 unter 97; Haupttextfortsetzung 113–114 unter 113; Fußnote 168–171 unter 168; 174–175 unter 174. Die Seitenvergleichsdifferenzen enthalten daher Layoutartefakte. Diese Texte wurden nicht doppelt ergänzt oder stillschweigend neu verteilt.

Die gedruckte Errata-Tabelle auf PDF 177 bleibt als Quellenbestand erhalten. Ihre Einträge sind keine automatisch auf die PDF-Nummerierung übertragbaren Änderungsbefehle. Die jetzige Fassung wendet sie nicht zusätzlich pauschal an.

Alle Tags, IDs, Attribute und geschützten `shem`-Texte sind unverändert. Nicht betroffene Textelemente wurden auf unveränderte Serialisierung geprüft. Alte Datei bleibt als Ausgangsstand im Paket erhalten.

## Skripte erneut ausführen

Python 3, nur Standardbibliothek; keine Netzwerkverbindung und keine zusätzlichen Pakete erforderlich.

```sh
python vergleichen.py --text vergleich/Siddur_HaRashash_Teil_1_HB21376_Niqqud_Tags_Kontextgeprueft.txt --ocr vergleich/OCR_Anlage_original.txt --scans vergleich/scans --out neuer_vergleich
python anwenden.py --text vergleich/Siddur_HaRashash_Teil_1_HB21376_Niqqud_Tags_Kontextgeprueft.txt --out neue_ausgabe
```

`bildentscheidungen.py` enthält die manuell festgehaltenen Entscheidungen; `anwenden.py` setzt ausschließlich diese um und prüft die strukturelle Integrität. `fertigstellen.py` ergänzt den vorhandenen Vergleich um Seitenbeobachtungen und das Ergebnispaket.
'''
(B/'README.md').write_text(readme)
index='<!doctype html><meta charset="utf-8"><title>Siddur Scanabgleich</title><style>body{font:18px system-ui;max-width:900px;margin:3em auto;padding:1em;line-height:1.6}a{color:#075b78}</style><h1>Siddur HaRashash: Scanabgleich</h1><p>56 lokale Korrekturen · 177 Bildseiten gesichtet · 143 [?] weiterhin offen.</p><p><strong>Bildsichtung mit punktueller Kollation. Keine vollständige Zeichen- oder Niqqud-Freigabe.</strong></p><ul><li><a href="ausgabe/'+next(O.glob('Siddur*.txt')).name+'">Neue Textfassung</a></li><li><a href="vergleich/vergleich.html">Scan und Texte pro Seite vergleichen</a></li><li><a href="ausgabe/Aenderungsprotokoll.md">Alle Korrekturen mit Begründungen</a></li><li><a href="ausgabe/Seitensichtung.csv">Beobachtungen für jede Seite</a></li><li><a href="ausgabe/Offene_Stellen.csv">Offene Stellen</a></li><li><a href="README.md">Methode, Grenzen und Skriptanleitung</a></li></ul>'
(B/'START.html').write_text(index)
package=pathlib.Path('/workspace/ergebnisse/Scanabgleich_Teil_1_HB21376');package.mkdir(exist_ok=True)
for name in ['ausgabe','vergleich']:
 shutil.copytree(B/name,package/name,dirs_exist_ok=True)
for name in ['README.md','START.html','vergleichen.py','anwenden.py','bildentscheidungen.py','fertigstellen.py']:shutil.copy2(B/name,package/name)
manifest={str(f.relative_to(package)):hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(package.rglob('*')) if f.is_file() and f.name!='SHA256.json'}
(package/'SHA256.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
zippath=package.with_suffix('.zip')
with zipfile.ZipFile(zippath,'w',zipfile.ZIP_DEFLATED) as z:
 for f in sorted(package.rglob('*')):
  if f.is_file():z.write(f,str(f.relative_to(package.parent)))
with zipfile.ZipFile(zippath) as z:assert z.testzip() is None
for f in O.iterdir():
 if f.is_file():shutil.copy2(f,pathlib.Path('/workspace/ergebnisse')/f.name)
print(json.dumps(dict(package=str(package),zip=str(zippath),zip_bytes=zippath.stat().st_size,files=len(manifest),**val),ensure_ascii=False,indent=2))
