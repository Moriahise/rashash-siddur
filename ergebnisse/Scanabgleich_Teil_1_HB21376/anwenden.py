"""Apply only image-supported editorial decisions; never adopt OCR automatically."""
import argparse,collections,copy,csv,difflib,hashlib,json,pathlib,re,xml.etree.ElementTree as ET
from bildentscheidungen import EDITS,PAGE_NOTES
BASE=pathlib.Path(__file__).resolve().parent
ap=argparse.ArgumentParser(description=__doc__)
ap.add_argument('--text',type=pathlib.Path,default=BASE/'vergleich'/'Siddur_HaRashash_Teil_1_HB21376_Niqqud_Tags_Kontextgeprueft.txt')
ap.add_argument('--out',type=pathlib.Path,default=BASE/'ausgabe')
args=ap.parse_args();SOURCE=args.text;OUT=args.out;OUT.mkdir(parents=True,exist_ok=True)
MARK=re.compile('[\u0591-\u05bd\u05bf\u05c1\u05c2\u05c4\u05c5\u05c7]')
def bare(s):return MARK.sub('',s)
def clusters(s):
 a=[]
 for c in s:
  if MARK.fullmatch(c) and a:a[-1]+=c
  else:a.append(c)
 return a
def slots(e):
 out=[]
 def visit(n):
  if n.text:out.append((n,'text'))
  for c in n:
   visit(c)
   if c.tail:out.append((c,'tail'))
 visit(e);return out
# Editorial vocalization of newly read ordinary words. Technical acronyms and
# uncertain Aramaic in the existing [?] passages retain no invented reading.
VOC={bare(w):w for w in '''אִימָא אֵלָיו אֶצְבְּעוֹת אֶת בִּבְרִיאָה בְּהוֹד בְּחִינָתָהּ בִּינָה בְּעֶשֶׂר בְּרֹאשָׁהּ בִּרְצֵה דְּאִימָא הָאָבוֹת הַבִּינָה הַדִּינִין הוּא הַזָּכָר הָרִאשׁוֹנָה הִתְעוֹרְרוּת וְאָז וּבָזֶה וְדַעַת וּלְעֵילָא וּמְדַלֶּגֶת וּמִשְׁתַּוֵּית זִיוּוּג חֶסֶד יוֹצְאָה יֵשׁ יְשַׁפְשֵׁף כְּלָלוּת לַחוּץ מִיסוֹד מְצִיאוּת מֵרֹאשׁ נְהוֹרִין נֶצַח נְתוּנִים נִתְקַן עֲטֶרֶת עַצְמָהּ עַרְבִית רֹאשׁ שֶׁבָּהּ שֶׁהוּא שֶׁיַּעֲקֹב שֶׁיֵּשׁ תּוֹסֶפֶת'''.split()}
tree=ET.parse(SOURCE);root=tree.getroot();original=copy.deepcopy(root)
byid={e.get('id'):e for e in root.iter() if e.get('id')};records=[]
for num,(eid,old,new,reason) in enumerate(EDITS,1):
 e=byid[eid];owners=slots(e);cur=[]
 for i,(n,a) in enumerate(owners):cur.extend((c,i) for c in clusters(getattr(n,a)))
 flat=''.join(c for c,_ in cur);plain=bare(flat)
 assert plain.count(old)==1,(eid,old)
 start=plain.index(old);stop=start+len(old);part=cur[start:stop]
 oldwords={}
 for w in re.findall(r'[א-ת][א-ת\u0591-\u05c7\"\'׳״]*',flat):
  if bare(w) not in oldwords or len(w)-len(bare(w))>len(oldwords[bare(w)])-len(bare(w)):oldwords[bare(w)]=w
 newpoint=[];unpointed=[]
 for w in new.split(' '):
  if w in VOC:pw=VOC[w]
  elif w in oldwords:pw=oldwords[w]
  else:pw=w;unpointed.append(w)
  newpoint.append(pw)
 pointed=' '.join(newpoint);assert bare(pointed)==new
 nc=clusters(pointed);mapping={}
 for block in difflib.SequenceMatcher(None,old,new,autojunk=False).get_matching_blocks():
  for k in range(block.size):mapping[block.b+k]=block.a+k
 replacement=[]
 for j,c in enumerate(nc):
  k=mapping.get(j)
  if k is None:
   before=[(b,a) for b,a in mapping.items() if b<j];after=[(b,a) for b,a in mapping.items() if b>j]
   k=max(before)[1] if before else min(after)[1] if after else 0
  oc,owner=part[k];n,a=owners[owner]
  if n.tag=='shem' and a=='text' and bare(oc)==bare(c):c=oc
  replacement.append((c,owner))
 before=''.join(c for c,_ in part);after=''.join(c for c,_ in replacement)
 cur[start:stop]=replacement;rebuilt=['']*len(owners)
 for c,i in cur:rebuilt[i]+=c
 for (n,a),s in zip(owners,rebuilt):setattr(n,a,s)
 assert bare(''.join(e.itertext()))==plain.replace(old,new,1)
 records.append(dict(number=num,pdf=int(eid.split('-P')[1][:3]),element_id=eid,before=before,after=after,before_unpointed=old,after_unpointed=new,reason=reason,niqqud='Redaktionell für neu gelesene gewöhnliche Wörter; bestehende Punkte unveränderter Wörter übernommen. Keine vollständige Niqqud-Fachprüfung.',new_unpointed_tokens=unpointed,uncertainty_retained='[?]' in ''.join(e.itertext())))
changed={r['element_id'] for r in records}
a=list(original.iter());b=list(root.iter());assert len(a)==len(b)
assert [(x.tag,x.attrib) for x in a]==[(x.tag,x.attrib) for x in b]
for x,y in zip(a,b):
 if x.get('id') and x.tag in {'p','row','heading'} and x.get('id') not in changed:assert ET.tostring(x)==ET.tostring(y),x.get('id')
shemchanges=[dict(before=x.text,after=y.text) for x,y in zip(original.iter('shem'),root.iter('shem')) if x.text!=y.text]
assert not shemchanges,shemchanges
markers_before=sum(''.join(p.itertext()).count('[?]') for p in original.findall('page'))
markers_after=sum(''.join(p.itertext()).count('[?]') for p in root.findall('page'))
assert markers_before==markers_after
output=OUT/'Siddur_HaRashash_Teil_1_HB21376_Niqqud_Tags_Scanabgleich.txt'
tree.write(output,encoding='utf-8',xml_declaration=True)
ET.parse(output)
(OUT/'Aenderungsprotokoll.json').write_text(json.dumps(records,ensure_ascii=False,indent=2))
lines=['# Änderungsprotokoll des Scanabgleichs','',f'{len(records)} lokale Eingriffe in {len(changed)} Textelementen. Datum: 2026-10-26.','', 'Die Konsonantenkorrekturen beruhen auf der Bildsichtung. Niqqud neuer gewöhnlicher Wörter ist redaktionell; der weitgehend unpunktierte Druck bestätigt diese Vokalisierung nicht. Alle bisherigen [?] bleiben erhalten.','']
for r in records:lines.extend([f"## {r['number']}. PDF {r['pdf']} · {r['element_id']}",'',f"Vorher: {r['before']}",'',f"Nachher: {r['after']}",'',r['reason'],''])
(OUT/'Aenderungsprotokoll.md').write_text('\n'.join(lines))
with (OUT/'Seitensichtung.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.writer(f);w.writerow(['pdf','schrift','umfang','beobachtung'])
 for n,(kind,note) in sorted(PAGE_NOTES.items()):w.writerow([n,kind,'Bildsichtung und punktuelle Kollation; keine vollständige Zeichenfreigabe',note])
openitems=[]
for p in root.findall('page'):
 for e in p.iter():
  if e.tag in {'p','row','heading'} and '[?]' in ''.join(e.itertext()):openitems.append(dict(pdf=int(p.get('pdf')),element_id=e.get('id'),markers=''.join(e.itertext()).count('[?]'),text=''.join(e.itertext()),status='offen; Quelle nicht hinreichend sicher aufgelöst'))
(OUT/'Offene_Stellen.json').write_text(json.dumps(openitems,ensure_ascii=False,indent=2))
with (OUT/'Offene_Stellen.csv').open('w',newline='',encoding='utf-8-sig') as f:
 w=csv.DictWriter(f,fieldnames=['pdf','element_id','markers','status','text']);w.writeheader();w.writerows(openitems)
validation=dict(date='2026-10-26',corrections=len(records),changed_elements=len(changed),text_pages=len(root.findall('page')),scans_viewed=len(PAGE_NOTES),rashi_pages=sum(k=='raschi' for k,_ in PAGE_NOTES.values()),markers_before=markers_before,markers_after=markers_after,shem_text_changes=len(shemchanges),tags_ids_attributes_preserved=True,unmodified_elements_unchanged=True,xml_parse=True,source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),output_sha256=hashlib.sha256(output.read_bytes()).hexdigest())
(OUT/'Validierung.json').write_text(json.dumps(validation,ensure_ascii=False,indent=2));print(json.dumps(validation,ensure_ascii=False,indent=2))
print('unpointed new tokens', sorted(set(w for r in records for w in r['new_unpointed_tokens'])))
