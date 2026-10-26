# Siddur HaRashash Teil 1 – Scanabgleich, 26.10.2026

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
