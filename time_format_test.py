"""Installed Chrome acceptance for both persistent formats, all finishes and sizes."""
import asyncio, datetime, io, json, os
from PIL import Image
from playwright.async_api import async_playwright
URL=os.getenv('CLOCK_URL','http://127.0.0.1:8794/')
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(channel='chrome',headless=True)
  results=[]
  for w,h in [(1440,900),(1920,1080),(390,844),(844,390)]:
   page=await b.new_page(viewport={'width':w,'height':h},timezone_id='UTC');errors=[]
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   await page.clock.install(time=datetime.datetime(2026,1,1,10,38,58,tzinfo=datetime.timezone.utc))
   await page.clock.pause_at(datetime.datetime(2026,1,1,10,38,58,tzinfo=datetime.timezone.utc))
   await page.goto(URL);await page.evaluate('document.fonts.ready')
   assert await page.locator('time').get_attribute('datetime')=='10:38'
   assert await page.locator('[data-format="hms"]').count()==1,'missing seconds format setting'
   for fmt,n in [('hm',5),('hms',8)]:
    await page.locator('[data-format="'+fmt+'"]').click()
    base=None; ink=None
    for mode in ['classic','glass','frost','prism']:
     await page.locator('[data-mode="'+mode+'"]').click()
     state=await page.evaluate('''() => {const t=document.querySelector('time'),r=t.getBoundingClientRect();return {n:t.children.length,font:getComputedStyle(t).fontSize,rect:[r.x,r.y,r.width,r.height],cells:[...t.children].map(e=>{const b=e.getBoundingClientRect();return [b.x,b.y,b.width,b.height]}),gl:glassQA.glError()}}''')
     assert state['n']==n and state['gl']==0,state
     x,y,cw,ch=state['rect'];assert x>=0 and y>=0 and x+cw<=w+.1 and y+ch<=h+.1,state
     assert abs(x+cw/2-w/2)<.1 and abs(y+ch/2-h/2)<.1,state
     if base:assert state==base,(state,base)
     base=state
     image=Image.open(io.BytesIO(await page.screenshot())).convert('L')
     bounds=[image.crop((round(x),round(y),round(x+cw),round(y+ch))).point(lambda v:255 if v>100 else 0).getbbox() for x,y,cw,ch in state['cells']]
     assert all(bounds),(w,h,fmt,mode,bounds)
     if ink:
      assert all(max(abs(a-b) for a,b in zip(old,new))<=3 for old,new in zip(ink,bounds)),(fmt,mode,ink,bounds)
     ink=bounds
    await page.reload();await page.evaluate('document.fonts.ready')
    assert await page.evaluate('document.querySelector("time").children.length')==n
    await page.clock.run_for(1100)
    assert await page.locator('time').get_attribute('datetime')==('10:38:59' if fmt=='hms' else '10:38')
    if fmt=='hms':
     assert await page.evaluate('glassQA.transition.to')=='10:38:59'
     await page.clock.run_for(400)
     before=await page.evaluate('({draws:glassQA.draws,builds:glassQA.sdfBuilds,uploads:glassQA.textureUploads})')
     await page.clock.run_for(200)
     assert await page.evaluate('({draws:glassQA.draws,builds:glassQA.sdfBuilds,uploads:glassQA.textureUploads})')==before
     await page.clock.run_for(500)
     assert await page.locator('time').get_attribute('datetime')=='10:39:00'
     await page.clock.run_for(400)
    assert await page.evaluate('({font:getComputedStyle(clock).fontSize,cells:[...clock.children].map(e=>{const b=e.getBoundingClientRect();return [b.x,b.y,b.width,b.height]})})')=={'font':base['font'],'cells':base['cells']}
    # Switching formats during a live fade must discard both old layouts.
    await page.evaluate("clockQA.render(clock.children.length===8?'23:59:59':'23:59')")
    await page.locator('[data-format="'+('hm' if fmt=='hms' else 'hms')+'"]').click()
    await page.locator('[data-format="'+fmt+'"]').click()
    assert await page.evaluate('glassQA.transition') is None
    assert await page.evaluate('[...clock.children].every(c=>c.children.length===1)')
    await page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))")
    before=await page.evaluate('glassQA.draws')
    await page.clock.run_for(2200)
    assert await page.evaluate('glassQA.draws')==before
    await page.evaluate("Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))")
    await page.set_viewport_size({'width':w+10,'height':h+10});await page.set_viewport_size({'width':w,'height':h})
    assert await page.evaluate('glassQA.transition') is None
    await page.keyboard.press('f');await page.wait_for_function('!!document.fullscreenElement')
    assert not await page.locator('.styles').is_visible()
    await page.evaluate('document.exitFullscreen()')
    results.append({'size':[w,h],'format':fmt,'styles':4,'errors':list(errors)})
    assert not errors,errors
    # Reset the controlled wall clock before the next format.
    await page.clock.set_system_time(datetime.datetime(2026,1,1,10,38,58,tzinfo=datetime.timezone.utc))
   await page.close()
  await b.close();print(json.dumps(results))
asyncio.run(main())
