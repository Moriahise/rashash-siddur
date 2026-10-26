"""Export einer am Scan gelesenen Etappe. python3 -I etappe_exportieren.py --bis 50

Neben dem Skript werden transkription.json, scans/pNNN.png und ocr/oNNN.txt
erwartet. Der Wortvergleich ist Diagnosematerial, keine automatische Korrektur.
"""
from pathlib import Path
import argparse,csv,difflib,hashlib,html,json,re,zipfile

args=argparse.ArgumentParser()
args.add_argument('--bis',type=int,default=50)
END=args.parse_args().bis
B=Path(__file__).resolve().parent
D=json.loads((B/'transkription.json').read_text(encoding='utf-8'))
P={int(k):v for k,v in D['pages'].items() if int(k)<=END}
EXPECTED=[n for n in range(1,END+1) if n!=2]
assert sorted(P)==EXPECTED, 'Die Etappe enthält Lücken.'
O=B/f'ausgabe_PDF{END:03}'
O.mkdir(exist_ok=True)
NAME=f'Siddur_HaRashash_Teil_2_HB21375_bis_PDF{END:03}.txt'

def heb(n):
    if n in (15,16): return {15:'טו',16:'טז'}[n]
    s=''
    for v,c in [(400,'ת'),(300,'ש'),(200,'ר'),(100,'ק'),(90,'צ'),(80,'פ'),(70,'ע'),(60,'ס'),(50,'נ'),(40,'מ'),(30,'ל'),(20,'כ'),(10,'י'),(9,'ט'),(8,'ח'),(7,'ז'),(6,'ו'),(5,'ה'),(4,'ד'),(3,'ג'),(2,'ב'),(1,'א')]:
        while n>=v:s+=c;n-=v
    return s

def folio(n):
    return 'שער — ללא מספור' if n==1 else f'דף {heb(n//2)} ע"'+('א' if n%2==0 else 'ב')

issues=[];checks={}
for n,s in sorted(P.items()):
    # *) ist ein gedruckter Fußnotenverweis, keine schließende Textklammer.
    check=re.sub(r'\*\)','*',s)
    stack=[];errors=[]
    for i,c in enumerate(check):
        if c in '[(':stack.append(c)
        elif c in '])':
            if not stack or stack.pop()!={']':'[',')':'('}[c]:errors.append(f'Klammer bei {i}')
    if stack:errors.append('Offene Klammer')
    if s.count('=== טבלה ===')!=s.count('=== סוף טבלה ==='):errors.append('Tabellenmarken')
    if s.count('■')%2:errors.append('Überschriftsmarken')
    if '@@' in s:errors.append('Interne Markierung')
    checks[str(n)]={'formatfehler':errors,'tabellen':s.count('=== טבלה ==='),'unsicherheiten':s.count('[?]')}
    for m in re.finditer(re.escape('[?]'),s):
        issues.append({'pdf':n,'folio':folio(n),'kontext':s[max(0,m.start()-85):m.end()+95].replace('\n',' '),'hinweis':D['notes'].get(str(n),'')})
assert not any(x['formatfehler'] for x in checks.values()),checks

header=f'''סידור תפלה להרש"ש — חלק שני
רבנו שלום שרעבי זצ"ל (הרש"ש)
מקור: hebrewbooks.org, מס' 21375; תצלומי העמודים שצורפו בידי המשתמש
הועתק מכתב רש"י לכתב מרובע ונערך לקריאה על פי התצלומים.

ETAPPE BIS PDF-SEITE {END} VON 323
Enthalten: PDF 1 sowie PDF 3–{END} ({len(P)} Inhaltsseiten).
PDF 2: Stempelseite, ausgelassen.
{len(issues)} mit [?] gekennzeichnete Unsicherheiten; siehe Prüfprotokoll.
Der restliche Band ab PDF {END+1} ist in dieser Datei nicht enthalten.

סימנים:
(אדני) = שם קטן הנדפס בתוך שם הוי"ה או על גביו
[ ... ] = כוונה, הערה קטנה או תיאור של פרט גרפי
( ... ) = הוראה או כותרת הוראה
■ ... ■ = כותרת
נוסח התפלה בלא ניקוד; בשמות הקודש שבכוונות נשמר הניקוד שנקרא בדפוס
=== טבלה === / === סוף טבלה === = תחילת טבלה וסופה
[טור ימין] / [טור אמצעי] / [טור שמאל] = סדר קריאה של עמודות
[אות זעירה: ...] = אות קטנה הנדפסת מעל מלה, בנפרד ממניין התיבות
[?] = קריאה מסופקת; אין להשלים על פי השערה
מספר הדף = כפי שנדפס בספר, ובסוגריים מספר העמוד בקובץ ה־PDF
כותרות־ריצה, קוסטוסים, חתימות־גליון וחותמות־סריקה מושמטים
דף א ע"ב ב־PDF 3 הוסק מן הדף הבא, ב ע"א; אינו ממוספר בדפוס
כוונה הנמשכת מעבר לעמוד הושלמה תחת העמוד שבו היא מתחילה
תוספות עריכה לתיאור הטבלאות והציורים נתונות בסוגריים מרובעים

'''
txt=header+'\n\n'.join(f'━━━━━━━━━━  {folio(n)}   (PDF {n})  ━━━━━━━━━━\n\n'+P[n].strip() for n in EXPECTED)+'\n'
(O/NAME).write_text(txt,encoding='utf-8')
assert len(re.findall(r'^━+.*\(PDF \d+\)',txt,re.M))==len(EXPECTED)
for filename,data in [('Offene_Stellen.json',issues),('Quellen.json',D['sources'])]:
    (O/filename).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with (O/'Offene_Stellen.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['pdf','folio','kontext','hinweis'],lineterminator='\n');w.writeheader();w.writerows(issues)
with (O/'Seitenstatus.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f,lineterminator='\n');w.writerow(['PDF','Folio','Status','Hinweis'])
    for n in range(1,END+1):
        w.writerow([n,folio(n) if n!=2 else '', 'Stempelseite ausgelassen' if n==2 else 'Am Scan übertragen; siehe markierte Unsicherheiten',D['notes'].get(str(n),'')])

diffs={}
for n in EXPECTED:
    a=(B/'ocr'/f'o{n:03}.txt').read_text(encoding='utf-8').split();b=P[n].split()
    diffs[str(n)]=[{'typ':tag,'ocr':' '.join(a[i:j]),'transkription':' '.join(b[k:l])} for tag,i,j,k,l in difflib.SequenceMatcher(None,a,b,autojunk=False).get_opcodes() if tag!='equal']
(O/'OCR_Wortvergleich.json').write_text(json.dumps(diffs,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
validation={'band':'Teil 2 / HB21375','etappe_bis_pdf':END,'scan_seiten_gesamt':323,'stempelseite':2,'erwartete_seitenkoepfe_etappe':len(EXPECTED),'vorhandene_seitenkoepfe_etappe':len(P),'fehlende_seiten_in_etappe':[],'band_vollstaendig':END==323,'naechste_pdf':END+1 if END<323 else None,'offene_markierungen':len(issues),'formale_pruefung':checks,'hinweis':'Formale Prüfungen belegen die Dateistruktur, nicht die Fehlerfreiheit jeder Lesung. Wortvergleich enthält auch Formatierungsänderungen.'}
(O/'Validierung.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
snapshot={**D,'status':f'Scanübertragung bis PDF {END}; {len(issues)} markierte Unsicherheiten; Band unvollständig.','pages':{str(n):P[n] for n in EXPECTED}}
(O/'transkription.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

report=f'''# Siddur HaRashash Teil 2, HB21375 — Etappe bis PDF {END}

Die TXT enthält PDF 1 und 3–{END}: {len(P)} Inhaltsseiten. PDF 2 ist die Stempelseite und ausgelassen. Grundlage sind die vom Nutzer gelieferten PNG-Scans; die hebRashi-OCR wurde nur als Lesehilfe verwendet. Der Band hat 323 PDF-Seiten. Die Seiten {END+1}–323 sind noch nicht in dieser Etappe enthalten.

Die Gebete stehen ohne Niqqud. Gedruckte Punktierungen der Namen in Kawwanot, Namenwiederholungen, Spalten, Randnotizen und Fußnoten sind gesondert wiedergegeben. Nicht linear darstellbare Umrissbuchstaben sind beschrieben. Die Datei ist eine Übertragung mit offengelegten Unsicherheiten, keine kritische Edition.

## Offene Lesungen

'''
for x in issues:report+=f'- PDF {x["pdf"]}, {x["folio"]}: {x["hinweis"]} Kontext: `{x["kontext"]}`\n'
report+='''
## Nachprüfung der zuvor offenen Stellen

- PDF 9: Die Scanlesung `אלי` bleibt erhalten. Der Zahlenbezug widerspricht dem erwartbaren Wert; deshalb weiterhin `[?]`.
- PDF 12: Sichtbares zusätzliches ו bei Wort טז ergänzt. Eine versehentliche Verdoppelung von העליון entfernt.
- PDF 13: Kleine Zusatzbuchstaben bei כה/כו/לב/לג/לט erfasst; die allgemeine Prüfmarkierung entfernt. Keine nicht sichtbaren Buchstaben ergänzt.
- PDF 20: 43 kleine Buchstaben über den Wörtern מה–פז einzeln zugeordnet und an den vergrößerten Zeilen geprüft; die allgemeine Prüfmarkierung entfernt.

## Stellen mit schwieriger OCR oder Gestaltung

- PDF 3–8: Namen, Vokalgruppen und Raschi-Anweisungen.
- PDF 9: Menora-Anordnung, gedrehte Schrift und Randnotizen.
- PDF 10–20: Kleine Namengruppen, Buchstabenzählung und überlagerte Kawwanot.
- PDF 21–24: Randbuchstaben und Attribute in den Gebeten; besonders dichter Kommentar auf PDF 24. Dort wurden unter anderem פא״י und סא״ל am Scan gegen die falsche OCR gelesen.
- PDF 25–30: Mehrspaltige Namen, Fußnote und über Seitenwechsel laufende Kawwanot.
- PDF 31–35: Akrostichzeichen, Attribute, Zehn-Tage-Tabelle und umfangreicher gedruckter Zusatz zum Kaddisch.
- PDF 36–44: Namen in zwei oder drei Spalten, zahlreiche Wiederholungen und Punktierungen. Die fünf markierten Vokalisierungen bleiben ausdrücklich unsicher.
- PDF 45–50: Grafische Umrissbuchstaben, Körpergrafik, gedrehte Nasenbeschriftung und kleine Tabellenzusätze. Bei PDF 45 wurden je Diagramm 10+5 Wiederholungen von הי gezählt.

## Seitenwechsel und redaktionelle Entscheidungen

Die Kawwanot über PDF 12/13, 26/27, 29/30, 31/32 und 41/42 wurden unter ihrer jeweiligen Anfangsseite vervollständigt. Bei PDF 36 wurde die im Druck fehlende öffnende runde Klammer vor שהם א״א ergänzt und im Seitenstatus dokumentiert. Sonstige Haupttexte bleiben auf ihrer Scan-Seite. Kustoden sind in der TXT ausgelassen; die Übergänge wurden beim Lesen der aufeinanderfolgenden Seiten verglichen. PDF 51 wurde für den Anschluss an PDF 50 eingesehen und gehört noch nicht zur Etappendatei.

## Formale Prüfung und Vergleich

UTF-8 geprüft; genau 49 Seitenköpfe in der Etappe; keine Seitenlücke außer der ausgewiesenen Stempelseite; geschlossene eckige und runde Textklammern; paarige Tabellen- und Überschriftsmarken; keine internen @@-Markierungen. Gedruckte Fußnotenverweise `*)` werden bei der Klammerprüfung als Verweise behandelt.

`Validierung.json` enthält die Ergebnisse je Seite. `Offene_Stellen.csv` und `.json` führen sämtliche `[?]` im Seitentext auf. `OCR_Wortvergleich.json` zeigt alle Wortabweichungen zwischen Roh-OCR und Übertragung einschließlich Formatänderungen; diese Liste ist kein Verzeichnis gesicherter Druckfehler.

Das ZIP enthält außerdem die Scans, zugehörige Roh-OCR, eine lokale Bild/Text-Vergleichsansicht sowie den reproduzierbaren Export. `Quellen.json` hält die SHA-256-Werte der Originalanhänge fest. Die Prüfung der gesamten 323 Seiten ist noch nicht abgeschlossen.
'''
(O/'Pruefprotokoll.md').write_text(report,encoding='utf-8')

# Lokale Ansicht im ZIP: jede Seite links im Original, rechts die Übertragung.
proof=O/'vergleich';proof.mkdir(exist_ok=True)
css='body{font:16px system-ui;margin:20px;background:#f7f6f2}.cols{display:grid;grid-template-columns:1fr 1fr;gap:20px}img{width:100%}pre{white-space:pre-wrap;direction:rtl;font:22px/1.6 serif;background:white;padding:16px}@media(max-width:850px){.cols{display:block}}'
for n in EXPECTED:
    s=f'<!doctype html><meta charset="utf-8"><title>HB21375 PDF {n}</title><style>{css}</style><a href="../Vergleich_Start.html">Übersicht</a><h1>PDF {n}</h1><div class="cols"><a href="../scans/p{n:03}.png"><img src="../scans/p{n:03}.png" alt="Originalscan PDF {n}"></a><pre lang="he">{html.escape(P[n])}</pre></div>'
    (proof/f'p{n:03}.html').write_text(s,encoding='utf-8')
(O/'Vergleich_Start.html').write_text('<!doctype html><meta charset="utf-8"><h1>Teil 2, HB21375 — PDF 1–50</h1><p>PDF 2: Stempelseite ausgelassen. Unsichere Lesungen: siehe Prüfprotokoll.</p><ul>'+''.join(f'<li><a href="vergleich/p{n:03}.html">PDF {n}</a></li>' for n in EXPECTED)+'</ul>',encoding='utf-8')

bundle=B/f'Siddur_HaRashash_Teil_2_HB21375_Etappe_PDF{END:03}.zip'
with zipfile.ZipFile(bundle,'w',zipfile.ZIP_DEFLATED) as z:
    for f in sorted(O.rglob('*')):
        if f.is_file() and f.name!='SHA256.json':z.write(f,str(f.relative_to(O)))
    for n in EXPECTED:
        z.write(B/'scans'/f'p{n:03}.png',f'scans/p{n:03}.png')
        z.write(B/'ocr'/f'o{n:03}.txt',f'ocr/o{n:03}.txt')
    z.write(Path(__file__),'etappe_exportieren.py')
with zipfile.ZipFile(bundle) as z:assert z.testzip() is None
hashes={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in [O/NAME,O/'Pruefprotokoll.md',bundle]}
(O/'SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'txt':str(O/NAME),'zip':str(bundle),'inhaltsseiten':len(P),'offen':len(issues),'zip_bytes':bundle.stat().st_size},ensure_ascii=False))
