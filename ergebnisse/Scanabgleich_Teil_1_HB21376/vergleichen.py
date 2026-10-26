#!/usr/bin/env python3
"""Compare tagged Siddur text with a page-delimited, fallible OCR witness.

No third-party modules required. No OCR reading is automatically accepted.
Usage: python vergleichen.py --text FILE --ocr FILE --scans DIR --out DIR
"""
import argparse,csv,difflib,hashlib,html,json,pathlib,re,shutil,unicodedata
import xml.etree.ElementTree as ET

POINTS=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]')
def normalize(s):
    s=unicodedata.normalize('NFKC',s)
    s=POINTS.sub('',s).replace('[?]','')
    s=s.translate(str.maketrans({'״':'"','׳':"'",'“':'"','”':'"','’':"'",'־':'-'}))
    return ' '.join(s.split())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser(description=__doc__)
    for name in ['text','ocr','scans','out']:ap.add_argument('--'+name,required=True,type=pathlib.Path)
    a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'seiten').mkdir(exist_ok=True);(a.out/'scans').mkdir(exist_ok=True)
    raw=a.ocr.read_text(encoding='utf-8-sig')
    parts=re.split(r'\[File: ([^\]\n]+)\]\s*',raw)
    witnesses={}
    for i in range(1,len(parts),2):
        m=re.search(r'Seite_(\d+)\.png$',parts[i])
        if not m:raise ValueError('Unrecognized page boundary: '+parts[i])
        n=int(m.group(1));assert n not in witnesses,'Duplicate OCR page'
        witnesses[n]=dict(filename=pathlib.PureWindowsPath(parts[i]).name,text=parts[i+1].strip())
    assert set(witnesses)==set(range(1,178)), 'OCR must contain exactly all 177 pages'
    root=ET.parse(a.text).getroot();pages={int(p.get('pdf')):p for p in root.findall('page')}
    assert set(pages)==set(range(1,178))-{2}
    all_pages=[];all_diffs=[]
    for n in range(1,178):
        image=a.scans/f'p-{n:03}.png'
        if not image.is_file():raise FileNotFoundError(image)
        shutil.copy2(image,a.out/'scans'/image.name)
        witness=witnesses[n]
        (a.out/'seiten'/f'ocr-{n:03}.txt').write_text(witness['text'])
        if n==2:
            all_pages.append(dict(pdf=n,status='stamp-page-excluded-from-text',ocr_chars=len(witness['text']),scan_sha256=sha(image)));continue
        page=pages[n];elements=[e for e in page.iter() if e.tag in {'p','row','heading'}]
        text='\n'.join(''.join(e.itertext()) for e in elements)
        (a.out/'seiten'/f'text-{n:03}.txt').write_text(text)
        left=[];owners=[]
        for e in elements:
            words=normalize(''.join(e.itertext())).split();left+=words;owners += [e.get('id')]*len(words)
        right=normalize(witness['text']).split()
        sm=difflib.SequenceMatcher(None,left,right,autojunk=False)
        diffs=[];left_html=[];right_html=[]
        for kind,i,j,k,l in sm.get_opcodes():
            x=' '.join(left[i:j]);y=' '.join(right[k:l])
            if kind=='equal':left_html.append(html.escape(x));right_html.append(html.escape(y));continue
            ident=f'D{n:03}-{len(diffs)+1:03}'
            rec=dict(difference_id=ident,pdf=n,folio=page.get('folio'),kind=kind,element_ids=list(dict.fromkeys(owners[i:j] or owners[max(0,i-1):i+1])),text_token_range=[i,j],ocr_token_range=[k,l],current=x,ocr=y,left_anchor=' '.join(left[max(0,i-6):i]),right_anchor=' '.join(left[j:j+6]),verdict='not-automatically-decided')
            diffs.append(rec);all_diffs.append(rec)
            left_html.append(f'<mark id="{ident}">{html.escape(x) or "∅"}<sup>{ident}</sup></mark>')
            right_html.append(f'<mark>{html.escape(y) or "∅"}<sup>{ident}</sup></mark>')
        info=dict(pdf=n,folio=page.get('folio'),text_tokens=len(left),ocr_tokens=len(right),token_similarity=round(sm.ratio(),4),differences=len(diffs),source_uncertainty_markers=text.count('[?]'),scan_sha256=sha(image),visual_review='pending',font_classification='requires-human-inspection',differences_data=diffs)
        all_pages.append(info)
        header=f'<h1>PDF {n} · {html.escape(page.get("folio") or "")}</h1><p>Token-Ähnlichkeit {sm.ratio():.1%}; {len(diffs)} Differenzblöcke. Ähnlichkeit ist kein Richtigkeitsnachweis. OCR-Wortfolge und Namens-/Vokaltabellen können falsch ausgerichtet sein.</p>'
        nav=f'<a href="../vergleich.html">Übersicht</a> · <a href="seite-{max(1,n-1):03}.html">Vorige</a> · <a href="seite-{min(177,n+1):03}.html">Nächste</a>'
        doc='<!doctype html><meta charset="utf-8"><title>Vergleich PDF '+str(n)+'</title>'+STYLE+nav+header
        doc+='<div class="columns"><section><h2>Scanbild</h2><a href="../scans/'+image.name+'"><img src="../scans/'+image.name+'"></a></section><section><h2>Prüffassung · Niqqud für Vergleich ausgeblendet</h2><div dir="rtl">'+' '.join(left_html)+'</div><h2>Neue OCR · unsicherer Vergleichstext</h2><div dir="rtl">'+' '.join(right_html)+'</div></section></div>'
        (a.out/'seiten'/f'seite-{n:03}.html').write_text(doc)
    payload=dict(source_xml=a.text.name,source_sha256=sha(a.text),ocr_filename=a.ocr.name,ocr_sha256=sha(a.ocr),method='Page identity from Seite_NNN filenames. Niqqud, quote shapes and whitespace normalized only for comparison. Exact source text remains separate. Word-level SequenceMatcher opcodes are candidate differences, never automatic corrections. No assertion of printed Rashi font from XML tags.',pages=all_pages,differences=all_diffs)
    (a.out/'Vergleich.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    with (a.out/'Unterschiede.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=list(all_diffs[0]));w.writeheader()
        for row in all_diffs:w.writerow({k:json.dumps(v,ensure_ascii=False) if isinstance(v,list) else v for k,v in row.items()})
    with (a.out/'Seitenstatus.csv').open('w',newline='',encoding='utf-8-sig') as f:
        keys=['pdf','folio','token_similarity','differences','source_uncertainty_markers','visual_review','font_classification']
        w=csv.DictWriter(f,fieldnames=keys,extrasaction='ignore');w.writeheader();w.writerows(all_pages)
    overview='<!doctype html><meta charset="utf-8"><title>Siddur-Scanvergleich</title>'+STYLE+'<h1>Siddur: Prüffassung ↔ neue OCR ↔ Scanbild</h1><p>177 Scan-/OCR-Seiten; 176 Textseiten. PDF 2 ist die Stempelseite. Jeder farbige Block ist ein Prüfhinweis, kein Fehlerbeweis. Roh-OCR kann stark beschädigt sein. Bildkontrolle wird separat protokolliert.</p><table><tr><th>PDF</th><th>Folio</th><th>Token-Ähnlichkeit</th><th>Differenzblöcke</th></tr>'
    for p in all_pages:
        if p['pdf']==2:overview+='<tr><td>2</td><td>Stempelseite, kein Textabgleich</td></tr>';continue
        overview+=f'<tr><td><a href="seiten/seite-{p["pdf"]:03}.html">{p["pdf"]}</a></td><td dir="rtl">{html.escape(p["folio"])}</td><td>{p["token_similarity"]:.1%}</td><td>{p["differences"]}</td></tr>'
    (a.out/'vergleich.html').write_text(overview+'</table>')
    shutil.copy2(a.ocr,a.out/'OCR_Anlage_original.txt')
    shutil.copy2(a.text,a.out/a.text.name)
    print(json.dumps(dict(ocr_pages=len(witnesses),text_pages=len(pages),difference_blocks=len(all_diffs),output=str(a.out)),ensure_ascii=False))
STYLE='<style>body{font:17px system-ui;margin:24px;color:#222}a{color:#1258a0}table{border-collapse:collapse}td,th{border:1px solid #aaa;padding:8px}mark{background:#ffe0b2;line-height:2}sup{font:10px system-ui;color:#8b2900}.columns{display:grid;grid-template-columns:1fr 1fr;gap:24px}img{width:100%;height:auto}section [dir=rtl]{font-size:23px;line-height:1.9}section{min-width:0}</style>'
if __name__=='__main__':main()
