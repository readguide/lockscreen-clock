import asyncio,json
from PIL import Image
from pathlib import Path
from playwright.async_api import async_playwright
root=Path(__file__).parent
async def main():
 (root/'qa').mkdir(exist_ok=True)
 results=[]; measurements=[]
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
    shot=root/f'qa/{name}-{mode}.png'
    await page.screenshot(path=str(shot))
    image=Image.open(shot).convert('RGB')
    points=[(8,8),(w//2,8),(w-9,8),(8,h//2),(w-9,h//2),(8,h-9),(w-9,h-9)]
    samples=[image.getpixel(q) for q in points]
    assert all(rgb==(0,0,0) for rgb in samples),(name,mode,samples)
    assert all(r==g==b for r,g,b in image.getdata()),(name,mode,'non-neutral pixel')
    nav=await page.locator('.styles').bounding_box()
    for y in range(h):
     for x in range(w):
      near_clock=box['x']-4<=x<=box['x']+box['width']+4 and box['y']-4<=y<=box['y']+box['height']+4
      near_nav=nav['x']-4<=x<=nav['x']+nav['width']+4 and nav['y']-4<=y<=nav['y']+nav['height']+4
      if not near_clock and not near_nav:assert image.getpixel((x,y))==(0,0,0),(name,mode,x,y)
    # Visible ink union and horizontal air measured independently of DOM line boxes.
    pixels=image.load(); ink=[]
    for x in range(w):
     ys=[y for y in range(max(0,int(box['y'])-2),min(h,int(box['y']+box['height'])+3)) if max(pixels[x,y])>32]
     if ys: ink.append((x,min(ys),max(ys)))
    assert ink
    inkbox=[ink[0][0],min(q[1] for q in ink),ink[-1][0]+1,max(q[2] for q in ink)+1]
    assert abs((inkbox[0]+inkbox[2])/2-w/2)<=1.5,(name,mode,inkbox)
    assert abs((inkbox[1]+inkbox[3])/2-h/2)<=2.5,(name,mode,inkbox)
    runs=[]
    for q in ink:
     if not runs or q[0]>runs[-1][1]+1:runs.append([q[0],q[0]])
     else:runs[-1][1]=q[0]
    gaps=[runs[j+1][0]-runs[j][1]-1 for j in range(len(runs)-1)]
    measurements.append({'size':name,'mode':mode,'font_px':await page.locator('time').evaluate('(e)=>parseFloat(getComputedStyle(e).fontSize)'),'ink_box':inkbox,'ink_center_error':[(inkbox[0]+inkbox[2])/2-w/2,(inkbox[1]+inkbox[3])/2-h/2],'visible_gaps_px':gaps,'background_samples':samples})
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
  assert await page.locator('time').evaluate('(e)=>getComputedStyle(e).color')=='rgb(238, 238, 238)'
  await page.screenshot(path=str(root/'qa/css-fallback.png'))
  results.append({'fallback':'CSS white glass','verified':True})
  await browser.close()
 (root/'qa/measurements.json').write_text(json.dumps(measurements,indent=2))
 (root/'qa/verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
asyncio.run(main())
