import asyncio,json
from pathlib import Path
from playwright.async_api import async_playwright
root=Path(__file__).parent
async def main():
 (root/'qa').mkdir(exist_ok=True)
 results=[]
 async with async_playwright() as p:
  browser=await p.chromium.launch(channel='chrome',headless=True)
  for name,w,h in [('desktop',1440,900),('wide',1920,1080),('mobile',390,844),('landscape',844,390)]:
   page=await browser.new_page(viewport={'width':w,'height':h})
   errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   await page.goto('http://127.0.0.1:8794/');await page.evaluate('document.fonts.ready')
   for mode in ['classic','glass','frost','prism']:
    await page.locator('[data-mode='+mode+']').click()
    await page.evaluate("clockQA.render('10:38')");await page.wait_for_timeout(850)
    box=await page.locator('time').bounding_box()
    assert abs(box['x']+box['width']/2-w/2)<1
    assert abs(box['y']+box['height']/2-h/2)<1
    assert box['x']>=0 and box['y']>=0
    await page.screenshot(path=str(root/f'qa/{name}-{mode}.png'))
    before=await page.evaluate('glassQA.draws');await page.wait_for_timeout(1200)
    assert await page.evaluate('glassQA.draws')==before
    await page.evaluate("clockQA.render('10:39')");await page.wait_for_timeout(800)
    assert await page.locator('time').bounding_box()==box
    assert await page.evaluate('glassQA.glError()')==0
   await page.reload();await page.wait_for_timeout(500)
   assert await page.evaluate('document.documentElement.dataset.style')=='prism'
   await page.keyboard.press('f');await page.wait_for_timeout(300)
   assert await page.evaluate('!!document.fullscreenElement')
   assert not await page.locator('.styles').is_visible()
   await page.evaluate('document.exitFullscreen()');await page.wait_for_timeout(300)
   assert await page.locator('.styles').is_visible()
   assert not errors,errors
   results.append({'size':name,'width':w,'height':h,'styles':4,'centered':True,'idle_draw_delta':0,'minute_bounds_unchanged':True,'persistence':True,'fullscreen':True,'console_errors':errors})
   await page.close()
  page=await browser.new_page()
  await page.add_init_script("const orig=HTMLCanvasElement.prototype.getContext; HTMLCanvasElement.prototype.getContext=function(type,...args){return type==='webgl2'?null:orig.call(this,type,...args)}")
  await page.goto('http://127.0.0.1:8794/');await page.locator('[data-mode=glass]').click();await page.wait_for_timeout(200)
  assert await page.evaluate('document.documentElement.dataset.renderer')=='css'
  assert await page.locator('time').evaluate('(e)=>getComputedStyle(e).color')=='rgb(237, 244, 247)'
  await page.screenshot(path=str(root/'qa/css-fallback.png'))
  results.append({'fallback':'CSS white glass','verified':True})
  await browser.close()
 (root/'qa/verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
asyncio.run(main())
