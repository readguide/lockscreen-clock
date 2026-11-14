"""Installed Chrome acceptance, interruption and real canvas pixel evidence."""
import asyncio,io,json,os
from pathlib import Path
from PIL import Image,ImageStat
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent; OUT=ROOT/'qa/digit-transition';OUT.mkdir(exist_ok=True)
URL=os.getenv('CLOCK_URL','http://127.0.0.1:8794/')
async def main():
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome',headless=True)
  for w,h in [(1440,900),(1920,1080),(390,844),(844,390)]:
   context=await browser.new_context(viewport={'width':w,'height':h})
   page=await context.new_page();errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   await page.add_init_script("localStorage.setItem('clock-style','prism');const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
   await page.goto(URL);await page.evaluate('document.fonts.ready');await page.wait_for_timeout(500)
   rects=await page.locator('time>span').evaluate_all('(es)=>es.map(e=>{let b=e.getBoundingClientRect();return [b.x,b.y,b.right,b.bottom]})')
   async def sample(label):
    data=await page.screenshot(path=str(OUT/f'{w}-{label}.png'));im=Image.open(io.BytesIO(data)).convert('L')
    return [ImageStat.Stat(im.crop(tuple(map(round,b)))).mean[0] for b in rects]
   before=await sample('before');counts=await page.evaluate('({builds:glassQA.sdfBuilds,uploads:glassQA.textureUploads})')
   await page.evaluate("clockQA.render('10:39')");await page.wait_for_timeout(230);mid=await sample('fade-out')
   assert mid[4]<before[4]*.7,(w,before,mid)
   assert all(abs(mid[i]-before[i])<.1 for i in range(4))
   await page.wait_for_timeout(180);incoming=await sample('fade-in')
   await page.wait_for_timeout(500);after=await sample('after')
   assert after[4]>mid[4]*1.3
   assert await page.evaluate('glassQA.textureUploads')-counts['uploads']==2
   assert await page.evaluate('glassQA.sdfBuilds')-counts['builds']==1
   assert await page.locator('time>span').evaluate_all('(es)=>es.map(e=>{let b=e.getBoundingClientRect();return [b.x,b.y,b.right,b.bottom]})')==rects
   for text in ['10:59','11:00','23:59','00:00']:
    await page.evaluate('(t)=>clockQA.render(t)',text);await page.wait_for_timeout(850)
    assert await page.evaluate('glassQA.geometryUpdates.at(-1).chars')==text
   for text in ['10:38','10:39','10:40']:
    await page.evaluate('(t)=>clockQA.render(t)',text);await page.wait_for_timeout(80)
   await page.wait_for_timeout(850);assert await page.evaluate('glassQA.geometryUpdates.at(-1).chars')=='10:40'
   await page.evaluate("clockQA.render('10:41')");await page.wait_for_timeout(100)
   await page.locator('[data-mode=frost]').click();await page.wait_for_timeout(800)
   assert await page.evaluate('glassQA.transition') is None
   await page.locator('[data-mode=prism]').click()
   await page.evaluate("clockQA.render('10:42')");await page.wait_for_timeout(80)
   await page.set_viewport_size({'width':w+4,'height':h+4});await page.wait_for_timeout(200)
   await page.set_viewport_size({'width':w,'height':h});await page.wait_for_timeout(200)
   assert await page.evaluate('glassQA.transition') is None
   await page.evaluate("clockQA.render('10:43')");await page.wait_for_timeout(80)
   await page.emulate_media(reduced_motion='reduce');await page.wait_for_timeout(150)
   assert await page.evaluate('glassQA.transition') is None
   await page.evaluate("clockQA.render('10:44')");await page.wait_for_timeout(100)
   assert await page.evaluate('glassQA.geometryUpdates.at(-1).chars')=='10:44'
   await page.emulate_media(reduced_motion='no-preference')
   hiddenDraws=await page.evaluate('glassQA.draws')
   await page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:true});document.dispatchEvent(new Event('visibilitychange'));clockQA.render('10:46')")
   await page.wait_for_timeout(100);assert await page.evaluate('glassQA.transition') is None
   assert await page.evaluate('glassQA.draws')==hiddenDraws,'hidden page must not draw'
   await page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,value:false});document.dispatchEvent(new Event('visibilitychange'));clockQA.render('10:47')")
   await page.wait_for_timeout(850)
   assert await page.evaluate('glassQA.geometryUpdates.at(-1).chars')=='10:47'
   resumed=await page.evaluate('document.querySelector("#glass-scene").toDataURL()')
   await page.locator('[data-mode=frost]').click();await page.locator('[data-mode=prism]').click()
   assert await page.evaluate('document.querySelector("#glass-scene").toDataURL()')==resumed,'resumed canvas must equal fully opaque fresh draw'
   await page.keyboard.press('f');await page.wait_for_timeout(250)
   assert await page.evaluate('!!document.fullscreenElement')
   assert not await page.locator('.styles').is_visible()
   await page.evaluate('document.exitFullscreen()');await page.wait_for_timeout(250)
   idle=await page.evaluate('glassQA.draws');await page.wait_for_timeout(1100)
   assert await page.evaluate('glassQA.draws')==idle
   assert await page.evaluate('glassQA.glError()')==0
   assert not errors,errors
   results.append(dict(size=[w,h],before=before,fadeOut=mid,fadeIn=incoming,after=after,uploadsPerChange=2,newGlyphBuilds=1,idleDraws=0,rollovers=True,interruptions=True,fullscreen=True,reducedMotion=True,hidden=True,errors=errors))
   video=page.video
   await context.close()
   if video: (OUT/'preview-source.txt').write_text(await video.path())
  await browser.close()
 (OUT/('online.json' if URL.startswith('https') else 'acceptance.json')).write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
asyncio.run(main())
