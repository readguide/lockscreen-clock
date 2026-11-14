"""Summarize preserved compositor evidence without overstating baseline results."""
import json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).parent
summaries=[]
for name in ['before-highfreq','after-highfreq','before-headed','after-headed','deployed']:
 folder=ROOT/'qa'/('visual-'+name)
 if not (folder/'results.json').exists():continue
 rows=json.loads((folder/'results.json').read_text())
 glyph_delta=max((max(abs(x-y) for x,y in zip(box,base)) for r in rows if 'glyphBoxes' in r for frame in r['glyphBoxes'] for box,base in zip(frame,r['glyphBoxes'][-1]) if box and base),default=None)
 gaps=[r['maxGapMs'] for r in rows if 'maxGapMs' in r]
 summaries.append(dict(run=name,transitions=len(rows),frames=sum(r['frames'] for r in rows),maxGlyphBoundDeltaCssPx=glyph_delta,maxCaptureGapMs=max(gaps,default=None),errors=[e for r in rows for e in r['errors']],baselineReproduced=False if name.startswith('before') else None))
 if name in ['before-headed','after-headed']:
  selected=[r for r in rows if r['size'][0]==1440 and (r['src'],r['dst']) in [('classic','glass'),('glass','frost'),('frost','prism'),('prism','classic')]]
  contact=Image.new('RGB',(1000,len(selected)*185),'#151515');draw=ImageDraw.Draw(contact)
  for y,r in enumerate(selected):
   for x,n in enumerate(sorted(set([0,r['frames']//3,r['frames']*2//3,r['frames']-1]))):
    im=Image.open(folder/f"1440-{r['src']}-{r['dst']}-{n:02}.png");im=im.crop((70,220,1400,680));im.thumbnail((245,140))
    contact.paste(im,(x*250,y*185+28));draw.text((x*250+4,y*185+5),f"{r['src']} > {r['dst']} / frame {n}",fill='white')
  contact.save(ROOT/'qa'/f'contact-{name}.png')
(ROOT/'qa'/'visual-summary.json').write_text(json.dumps(summaries,indent=2))
print(json.dumps(summaries,indent=2))
