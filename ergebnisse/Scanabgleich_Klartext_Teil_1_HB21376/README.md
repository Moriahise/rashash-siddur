# Scanabgleich der Klartextdatei Siddur_HaRashash_Teil_1_HB21376.txt

Datum: 2026-10-26.

Die hochgeladene Datei ist bytegleich mit der bereits vorhandenen Klartext-Ausgangsfassung (SHA-256 f050f4ef6024332275107055feea1832f2156ebc6501c22fd1fd939bf579bfaf). Die zuvor am Scan belegten Lesarten wurden gezielt auf diese Datei neu zugeordnet. Abweichende Ausgangslesarten auf PDF 6, 7, 19 sowie die bereits richtige Stelle auf PDF 119 wurden erneut am Bild angesehen. **Dies ist keine neue vollständige Zeichenkollation aller Scanseiten.** Die frühere Bildsichtung und ihre Grenzen gelten weiterhin; auch unmarkierte Restfehler sind möglich.

55 lokale Korrekturen auf 21 Textseiten. 176 Textseiten und 177 Scanbilder; PDF 2 ist die ausgelassene Stempelseite. Alle 150 Unsicherheitszeichen im eigentlichen Text bleiben erhalten. Das zusätzliche [?] in der Zeichenlegende ist kein Textbefund. Keine neue Niqqud-Ergänzung und keine XML-Tags. Tabellen, vorhandene Vokalzeichen, Seitenüberschriften und unveränderte Seiten bleiben erhalten. Die spätere Kontextfassung wurde nicht pauschal übernommen.

## Dateien

- `Siddur_HaRashash_Teil_1_HB21376_Scanabgleich_Klartext.txt`: korrigierter Klartext.
- `Eingabe_original.txt`: unveränderte hochgeladene Datei.
- `Aenderungsprotokoll.md`, `.csv`, `.json`: sämtliche Eingriffe mit PDF-Seite, genauer Eingabezeile, Vorher/Nachher und Begründung. Die source_reference verweist zusätzlich auf die entsprechende Element-ID der früheren getaggten Ausgabe; der Klartext selbst hat keine IDs.
- `bereits_richtig.json`: dokumentiert die in dieser Ausgangsdatei bereits richtige Lesung auf PDF 119.
- `START.html`: nach vollständigem Entpacken im Browser öffnen. Für jede Seite: Scanbild, neue Klartextfassung, lokale Korrekturen und ausklappbarer Vergleich Original gegen OCR.
- `OCR_Differenzen.csv` und `.json`: 5.200 maschinell ermittelte Differenzblöcke zwischen dieser Ausgangsfassung und dem früher bereitgestellten OCR-Zeugen. **Kandidaten, keine 5.200 nachgewiesenen Fehler.** Nicht alle Blöcke wurden einzeln abschließend entschieden.
- `Seitenstatus.csv` und `.json`: übernommene Beobachtungen aus der früheren Bildsichtung und Kennzeichnung der jetzt erneut angesehenen Seiten. Die Notizen bestätigen nicht jeden unveränderten Buchstaben.
- `Offene_Stellen.csv` und `.json`: weiterhin mit [?] markierte Textzeilen.
- `Validierung.json`: technische Prüfungen und Dateiprüfsummen.
- `entscheidungen.json`: ausschließlich explizit freigegebene lokale Lesarten für diese Klartextdatei.
- `scanabgleich.py`: reproduzierbarer Vergleich und Anwendung der protokollierten Lesarten, nur Python-Standardbibliothek.

## Methode und Grenzen

Seitenzuordnung über die vorhandenen `(PDF N)`-Überschriften und die Dateinamen des OCR-Zeugen. Niqqud, Anführungszeichen und Leerraum werden nur zum Wortvergleich normalisiert. Die OCR ist fehlbar und wird nie automatisch als richtige Lesung übernommen. Vor jeder Änderung muss der alte Ausdruck genau einmal auf der betreffenden Seite vorkommen. Mehrspaltige Namenfelder können durch OCR in falscher Reihenfolge erscheinen.

Mehrseitige Absätze und Fußnoten sind bereits in der Ausgangsdatei teilweise unter ihrer Anfangsseite zusammengezogen: insbesondere PDF 11–14, 19–23, um 50–59, 94–96, 97–98, 113–114, 168–171 und 174–175. Deshalb sind viele Differenzen Layoutabweichungen. Die Texte werden nicht doppelt ergänzt. Die gedruckte Errata-Tabelle auf PDF 177 bleibt als Quellenbestand erhalten und wird nicht zusätzlich pauschal in den Haupttext eingearbeitet.

Die schwierige aramäische Wendung auf PDF 43/48 und die Zahl שע״ח bleiben im weiterhin markierten Absatz als offene Lesung dokumentiert. Es wird keine vollständig geklärte Fachausgabe oder Niqqud-Freigabe behauptet.

## Erneut ausführen

Im entpackten Paket:

```sh
python scanabgleich.py --text Eingabe_original.txt --ocr OCR_Vergleichszeuge_original.txt --scans scans --out neue_ausgabe
```

Eine geänderte Eingabedatei kann absichtlich eine Prüfung abbrechen lassen, wenn ein alter Ausdruck nicht mehr eindeutig vorkommt. In diesem Fall die Entscheidungen erneut gegen den Scan prüfen; nicht die Eindeutigkeitsprüfung entfernen.
