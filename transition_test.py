"""Real Chrome pixel regression for sequential, per-digit glass fades."""
import asyncio, io, json, os
from pathlib import Path
from PIL import Image, ImageStat
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent
OUT=ROOT/'qa/digit-transition'; OUT.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome',headless=True)
  page=await browser.new_page(viewport={'width':1440,'height':900})
  await page.add_init_script("localStorage.setItem('clock-style','prism');const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
  await page.goto(os.getenv('CLOCK_URL','http://127.0.0.1:8794/'));await page.evaluate('document.fonts.ready');await page.wait_for_timeout(200)
  rects=await page.locator('time>span').evaluate_all('(es)=>es.map(e=>{let b=e.getBoundingClientRect();return [b.x,b.y,b.right,b.bottom]})')
  async def sample(name):
   shot=await page.screenshot(path=str(OUT/f'{name}.png'));im=Image.open(io.BytesIO(shot)).convert('L')
   return [ImageStat.Stat(im.crop(tuple(map(round,b)))).mean[0] for b in rects]
  before=await sample('before');await page.evaluate("clockQA.render('10:39')");await page.wait_for_timeout(250);mid=await sample('outgoing')
  assert mid[4]<before[4]*.65,dict(before=before,mid=mid)
  assert all(abs(mid[i]-before[i])<.1 for i in range(4))
  await page.wait_for_timeout(600);after=await sample('after');assert after[4]>mid[4]*1.5
  print(json.dumps(dict(before=before,mid=mid,after=after)))
  await browser.close()
asyncio.run(main())
