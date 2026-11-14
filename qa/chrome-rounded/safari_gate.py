from playwright.sync_api import sync_playwright
import subprocess,hashlib,json
base=subprocess.check_output(['git','show','726c9b1:index.html'],cwd='/Users/en/lockscreen-clock').decode()
ua='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/27.2 Safari/605.1.15'
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=False)
 results=[]
 for old in [True,False]:
  c=b.new_context(user_agent=ua,viewport={'width':844,'height':390})
  page=c.new_page();page.clock.install(time=1794657325000)
  if old:page.route('http://127.0.0.1:8917/',lambda r:r.fulfill(body=base,content_type='text/html'))
  page.goto('http://127.0.0.1:8917/');page.wait_for_timeout(1000)
  for mode in ['classic','glass','frost','prism']:
   page.locator(f'[data-mode={mode}]').click();page.wait_for_timeout(500)
   state=page.evaluate('({font:clock.style.fontFamily,computed:getComputedStyle(clock).font,html:clock.outerHTML,loaded:[...document.fonts].map(f=>f.family)})')
   shot=page.screenshot(path=f'/tmp/clock-rounded-qa/safari-gate-{old}-{mode}.png')
   results.append({'baseline':old,'mode':mode,'sha256':hashlib.sha256(shot).hexdigest(),'state':state})
  c.close()
 for j in range(4):
  from PIL import Image,ImageChops
  diff=ImageChops.difference(Image.open(f'/tmp/clock-rounded-qa/safari-gate-True-{results[j]["mode"]}.png'),Image.open(f'/tmp/clock-rounded-qa/safari-gate-False-{results[j]["mode"]}.png'))
  changed=sum(any(pixel) for pixel in diff.getdata())
  assert changed<=1,changed  # Chrome text AA occasionally differs at one edge pixel.
  results[j+4]['changedPixels']=changed
  assert results[j]['state']==results[j+4]['state'],results
 print(json.dumps(results,indent=2));b.close()
