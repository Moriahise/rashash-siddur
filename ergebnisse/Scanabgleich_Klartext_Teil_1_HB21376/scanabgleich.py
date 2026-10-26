#!/usr/bin/env python3
"""Page-aware comparison of a plain Siddur transcription, fallible OCR and scan images.
Only explicit decisions.json entries change text. Python 3 standard library only.
"""
import argparse,collections,csv,difflib,hashlib,html,json,pathlib,re,shutil,zipfile
B=pathlib.Path(__file__).resolve().parent
POINTS=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]')
PAGE=re.compile(r'(?m)^(━+[^\n]*\(PDF (\d+)\)[^\n]*━+)[ \t]*\n')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def norm(s):return ' '.join(POINTS.sub('',s).replace('[?]','').translate(str.maketrans({'״':'"','׳':"'",'־':'-'})).split())
def pages(s):
 matches=list(PAGE.finditer(s));return {int(m[2]):dict(header=m[1],start=m.end(),end=matches[i+1].start() if i+1<len(matches) else len(s),text=s[m.end():matches[i+1].start() if i+1<len(matches) else len(s)]) for i,m in enumerate(matches)}
def tables(s):return re.findall(r'^=== טבלה ===[ \t]*\n.*?^=== סוף טבלה ===[ \t]*$',s,re.S|re.M)
def marks(s):return POINTS.findall(s)
def main():
 ap=argparse.ArgumentParser(description=__doc__)
 for n in ['text','ocr','scans','out']:ap.add_argument('--'+n,required=True,type=pathlib.Path)
 a=ap.parse_args();O=a.out;O.mkdir(parents=True,exist_ok=True)
 raw=a.text.read_text();ps=pages(raw);assert set(ps)==set(range(1,178))-{2}
 decisions=json.loads((B/'entscheidungen.json').read_text());notes=json.loads((B/'seitennotizen.json').read_text());records=[];corrected={n:p['text'] for n,p in ps.items()}
 for i,d in enumerate(decisions,1):
  n=d['pdf'];s=corrected[n];old=d['old'];new=d['new'];assert s.count(old)==1,(n,old,s.count(old))
  at=s.index(old);updated=s.replace(old,new,1)
  assert tables(s)==tables(updated),(n,'table change');assert marks(s)==marks(updated),(n,'vowel change')
  line=raw[:ps[n]['start']].count('\n')+ps[n]['text'][:ps[n]['text'].index(old)].count('\n')+1
  records.append(dict(number=i,**d,input_line=line,page_line=ps[n]['text'][:ps[n]['text'].index(old)].count('\n')+1,status='lokale_Korrektur',context_before=s[max(0,at-80):at+len(old)+80]))
  corrected[n]=updated
 result=raw
 for n,p in sorted(ps.items(),reverse=True):result=result[:p['start']]+corrected[n]+result[p['end']:]
 assert raw.count('[?]')==result.count('[?]');assert tables(raw)==tables(result);assert marks(raw)==marks(result)
 output=O/'Siddur_HaRashash_Teil_1_HB21376_Scanabgleich_Klartext.txt';output.write_text(result)
 shutil.copy2(a.text,O/'Eingabe_original.txt');shutil.copy2(a.ocr,O/'OCR_Vergleichszeuge_original.txt')
 for name in ['scanabgleich.py','entscheidungen.json','bereits_richtig.json','seitennotizen.json']:shutil.copy2(B/name,O/name) if (B/name).resolve()!=(O/name).resolve() else None
 (O/'Aenderungsprotokoll.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
 md=['# Scanabgleich der hochgeladenen Klartextdatei','',f'{len(records)} lokale Korrekturen. Die ältere Bildkollation wurde auf diese bytegleiche Ausgangstranskription neu zugeordnet. PDF 6/7/19/119 wurden für abweichende Ausgangslesarten erneut am Bild angesehen. Keine neue vollständige Bildkollation aller Seiten.','']
 for r in records:md.extend([f"## {r['number']}. PDF {r['pdf']} · Eingabezeile {r['input_line']}",'',f"Vorher: {r['old']}",'',f"Nachher: {r['new']}",'',r['reason'],''])
 (O/'Aenderungsprotokoll.md').write_text('\n'.join(md))
 with (O/'Aenderungsprotokoll.csv').open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(records[0]));w.writeheader();w.writerows(records)
 ocrraw=a.ocr.read_text(encoding='utf-8-sig');spl=re.split(r'\[File: ([^\]\n]+)\]\s*',ocrraw);ocr={int(re.search(r'Seite_(\d+)\.png$',spl[i])[1]):spl[i+1].strip() for i in range(1,len(spl),2)};assert set(ocr)==set(range(1,178))
 (O/'seiten').mkdir(exist_ok=True);(O/'scans').mkdir(exist_ok=True);diffs=[];status=[];openitems=[]
 style='<style>body{font:17px system-ui;margin:2em;line-height:1.6}pre{white-space:pre-wrap;font:20px serif}mark{background:#fff0b0}article{display:grid;grid-template-columns:1fr 1fr;gap:24px}img{max-width:100%;position:sticky;top:0}aside{padding:1em;background:#eff9f1}sup{font:10px monospace}@media(max-width:900px){article{display:block}}</style>'
 overview='<!doctype html><meta charset="utf-8"><title>Klartext-Scanabgleich</title>'+style+'<h1>Scanabgleich der Klartextdatei</h1><p>Original, lokale Korrekturen, OCR und Scanbilder. Farbige OCR-Differenzen sind Prüfhinweise, keine bestätigten Fehler. <a href="README.md">Methode und Grenzen</a> · <a href="Aenderungsprotokoll.md">Änderungsprotokoll</a> · <a href="'+output.name+'">Neue Textfassung</a></p><table><tr><th>PDF</th><th>Korrekturen</th><th>OCR-Differenzen</th><th>[?]</th></tr>'
 for n in range(1,178):
  scan=a.scans/f'p-{n:03}.png';assert scan.exists();shutil.copy2(scan,O/'scans'/scan.name)
  s=ps[n]['text'] if n in ps else '';new=corrected.get(n,'');left=norm(s).split();right=norm(ocr[n]).split();lh=[];rh=[];count=0
  for kind,i,j,k,l in difflib.SequenceMatcher(None,left,right,autojunk=False).get_opcodes():
   x=' '.join(left[i:j]);y=' '.join(right[k:l])
   if kind=='equal':lh.append(html.escape(x));rh.append(html.escape(y));continue
   count+=1;ident=f'K{n:03}-{count:03}';diffs.append(dict(difference_id=ident,pdf=n,kind=kind,input=x,ocr=y,input_token_start=i,input_token_end=j,ocr_token_start=k,ocr_token_end=l,status='Kandidat_nicht_automatisch_entschieden'))
   lh.append('<mark>'+html.escape(x or '∅')+'<sup>'+ident+'</sup></mark>');rh.append('<mark>'+html.escape(y or '∅')+'<sup>'+ident+'</sup></mark>')
  local=[r for r in records if r['pdf']==n];kind,note=notes[str(n)]
  status.append(dict(pdf=n,schrift=kind,korrekturen=len(local),ocr_differenzen=count,unsicherheitszeichen=new.count('[?]'),pruefgrundlage='frühere Bildsichtung übernommen; neue Zuordnung auf identische Ausgangsdatei',erneut_am_bild_angesehen=n in [6,7,19,119],beobachtung=note))
  for lineno,line in enumerate(new.splitlines(),1):
   if '[?]' in line:openitems.append(dict(pdf=n,page_line=lineno,markers=line.count('[?]'),text=line,status='offen'))
  panel='<aside><h2>Lokale Korrekturen</h2><p>'+html.escape(note)+'</p><p>Seitennotiz aus früherer Bildsichtung; keine neue Freigabe jedes Buchstabens.</p>'
  for r in local:panel+='<p><span dir="rtl">'+html.escape(r['old'])+'</span> → <strong dir="rtl">'+html.escape(r['new'])+'</strong><br>'+html.escape(r['reason'])+'</p>'
  panel+='</aside>'
  doc='<!doctype html><meta charset="utf-8"><title>PDF '+str(n)+'</title>'+style+'<a href="../START.html">Übersicht</a>'
  if n>1:doc+=f' · <a href="seite-{n-1:03}.html">Vorige</a>'
  if n<177:doc+=f' · <a href="seite-{n+1:03}.html">Nächste</a>'
  doc+=f'<h1>PDF {n}</h1>'+panel+f'<article><section><a href="../scans/p-{n:03}.png"><img src="../scans/p-{n:03}.png"></a></section><section><h2>Neue Klartextfassung</h2><pre dir="rtl">'+html.escape(new or 'Stempelseite; keine Transkription.')+'</pre><details><summary>Original gegen neue OCR · Niqqud für Vergleich ausgeblendet</summary><h3>Original</h3><div dir="rtl">'+' '.join(lh)+'</div><h3>OCR · fehlbar</h3><div dir="rtl">'+' '.join(rh)+'</div></details></section></article>'
  (O/'seiten'/f'seite-{n:03}.html').write_text(doc);overview+=f'<tr><td><a href="seiten/seite-{n:03}.html">{n}</a></td><td>{len(local)}</td><td>{count}</td><td>{new.count("[?]")}</td></tr>'
 (O/'START.html').write_text(overview+'</table>')
 for name,data in [('OCR_Differenzen',diffs),('Seitenstatus',status),('Offene_Stellen',openitems)]:
  (O/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2))
  with (O/(name+'.csv')).open('w',encoding='utf-8-sig',newline='') as f:
   w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
 stats=dict(input_sha256=sha(a.text),output_sha256=sha(output),corrections=len(records),changed_pages=len(set(r['pdf'] for r in records)),text_pages=len(ps),scans_linked=177,ocr_differences=len(diffs),markers_in_text_before=sum(p['text'].count('[?]') for p in ps.values()),markers_in_text_after=sum(s.count('[?]') for s in corrected.values()),tables_preserved=True,existing_niqqud_preserved=True,headers_preserved=True,unchanged_pages_preserved=all(corrected[n]==p['text'] for n,p in ps.items() if not any(r['pdf']==n for r in records)),comparison_scope='Frühere Bildkollation auf identische Klartext-Ausgangsfassung neu zugeordnet; PDF 6/7/19/119 erneut angesehen. Keine neue vollständige Zeichenkollation.')
 (O/'Validierung.json').write_text(json.dumps(stats,ensure_ascii=False,indent=2));print(json.dumps(stats,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
