"""Run with existing /tmp/clock-qa-venv; no installed dependencies required."""
from playwright.sync_api import sync_playwright
import json, os, sys
URL=sys.argv[1] if len(sys.argv)>1 else 'http://127.0.0.1:8917/'
out='/tmp/clock-rounded-qa';os.makedirs(out,exist_ok=True)
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=False)
 page=b.new_page(viewport={'width':1440,'height':900});errors=[]
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
 page.clock.install(time=1794657325000)
 page.goto(URL);page.wait_for_timeout(1600)
 s=page.context.new_cdp_session(page);s.send('DOM.enable');s.send('CSS.enable')
 node=s.send('DOM.querySelector',{'nodeId':s.send('DOM.getDocument')['root']['nodeId'],'selector':'.digit .glyph'})['nodeId']
 fonts=s.send('CSS.getPlatformFontsForNode',{'nodeId':node})
 print(json.dumps(fonts))
 assert any('Nunito' in x['familyName'] for x in fonts['fonts']), 'Chrome still renders square system fallback instead of rounded digits'
 rows=[]
 for w,h in [(390,844),(844,390),(1440,900),(1920,1080)]:
  page.set_viewport_size({'width':w,'height':h})
  for fmt in ['hm','hms']:
   page.locator(f'[data-format={fmt}]').click()
   for mode in ['classic','glass','frost','prism']:
    page.locator(f'[data-mode={mode}]').click();page.evaluate("clockQA.render('19:55:25'.slice(0,document.querySelectorAll('.digit').length===4?5:8))");page.wait_for_timeout(500)
    box=page.locator('#clock').bounding_box()
    assert box['x']>=0 and box['y']>=0 and box['x']+box['width']<=w+1 and box['y']+box['height']<=h+1
    assert abs(box['x']+box['width']/2-w/2)<1 and abs(box['y']+box['height']/2-h/2)<1
    assert page.evaluate('glassQA.glError()')==0
    page.screenshot(path=f'{out}/{w}-{fmt}-{mode}.png')
    before=page.locator('#clock').get_attribute('datetime');page.evaluate("clockQA.render('19:56:26'.slice(0,document.querySelectorAll('.digit').length===4?5:8))");page.wait_for_timeout(450)
    assert before!=page.locator('#clock').get_attribute('datetime')
    rows.append([w,h,fmt,mode,box])
 assert not errors,errors
 json.dump({'fonts':fonts,'cases':rows,'errors':errors},open(out+'/results.json','w'),indent=2)
 b.close()
 print('PASS',len(rows),'cases',out)
