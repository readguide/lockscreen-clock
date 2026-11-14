"""Photographed liquid rim depth; --old is expected to FAIL on flat old material."""
import asyncio,io,json,sys,statistics,subprocess
from pathlib import Path
from PIL import Image,ImageFilter,ImageChops
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent
async def main():
 results=[];label='before' if '--old' in sys.argv else 'after'
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome',headless=True)
  page=await browser.new_page(viewport=dict(width=1440,height=900))
  await page.add_init_script("const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
  if '--old' in sys.argv:
   for filename in ['digit-glass.js','vendor/shaders.js']:
    body=subprocess.check_output(['git','show','df01c4b:'+filename],cwd=ROOT).decode()
    await page.route('**/'+filename,lambda route,request,body=body:route.fulfill(body=body,content_type='application/javascript'))
  await page.goto('http://127.0.0.1:8794/');await page.evaluate('document.fonts.ready');await page.evaluate("clockQA.render('10:38')");await page.wait_for_timeout(800)
  classic=Image.open(io.BytesIO(await page.screenshot())).convert('L');classic.paste(0,(0,810,1440,900))
  mask=classic.point(lambda v:255 if v>100 else 0)
  band=ImageChops.subtract(mask.filter(ImageFilter.MinFilter(5)),mask.filter(ImageFilter.MinFilter(21)))
  coords=[i for i,v in enumerate(band.get_flattened_data()) if v]
  for mode in ['glass','frost','prism']:
   await page.locator(f'[data-mode={mode}]').click();await page.wait_for_timeout(100)
   shot=await page.screenshot(path=str(ROOT/'qa'/f'material-{label}-{mode}.png'))
   data=list(Image.open(io.BytesIO(shot)).convert('L').get_flattened_data());vals=sorted(data[i] for i in coords)
   results.append(dict(mode=mode,rimP05=vals[len(vals)//20],rimP95=vals[len(vals)*19//20],rimStd=statistics.pstdev(vals)))
  await browser.close()
 print(json.dumps(results,indent=2));(ROOT/'qa'/f'material-{label}.json').write_text(json.dumps(results,indent=2))
 for r in results[1:]:assert r['rimP95']-r['rimP05']>=20 and r['rimStd']>=7,(r,'flat rim, missing liquid depth')
asyncio.run(main())
