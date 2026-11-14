"""Capture every compositor frame around real clicks, not DOM-only snapshots."""
import asyncio,base64,io,json,sys,subprocess,os
from pathlib import Path
from PIL import Image,ImageChops
from playwright.async_api import async_playwright
ROOT=Path(__file__).parent
async def main():
 out=ROOT/'qa'/('visual-'+(sys.argv[1] if len(sys.argv)>1 else 'before'));out.mkdir(exist_ok=True)
 results=[]
 async with async_playwright() as p:
  b=await p.chromium.launch(channel='chrome',headless='--headed' not in sys.argv)
  for w,h,dpr in [(1440,900,1),(1920,1080,2),(390,844,3),(844,390,3)]:
   page=await b.new_page(viewport=dict(width=w,height=h),device_scale_factor=dpr)
   errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('console',lambda m:errors.append(m.text) if m.type=='error' else None)
   if '--old' in sys.argv:
    for filename in ['digit-glass.js','vendor/shaders.js']:
     body=subprocess.check_output(['git','show','df01c4b:'+filename],cwd=ROOT).decode()
     await page.route('**/'+filename,lambda route,request,body=body:route.fulfill(body=body,content_type='application/javascript'))
   await page.add_init_script("const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
   await page.goto(os.environ.get('CLOCK_URL','http://127.0.0.1:8794/'));await page.evaluate('document.fonts.ready');await page.wait_for_timeout(1000)
   cells=await page.evaluate("[...document.querySelector('time').children].map(e=>{let r=e.getBoundingClientRect();return {x:r.x,y:r.y,width:r.width,height:r.height}})")
   # Force compositor activity: screencast otherwise omits unchanged intermediate frames.
   await page.evaluate("""()=>{let marker=document.createElement('div');marker.style='position:fixed;left:0;bottom:0;width:2px;height:2px;background:white';document.body.append(marker);marker.animate([{opacity:.01},{opacity:.02}],{duration:32,iterations:Infinity})}""")
   c=await page.context.new_cdp_session(page);await c.send('Emulation.setCPUThrottlingRate',{'rate':6})
   frames=[]
   async def frame(e):
    frames.append((e['metadata']['timestamp'],e['data']))
    await c.send('Page.screencastFrameAck',{'sessionId':e['sessionId']})
   c.on('Page.screencastFrame',frame)
   for src,dst in [(s,t) for s in ['classic','glass','frost','prism'] for t in ['classic','glass','frost','prism'] if s!=t]:
    await page.locator(f'[data-mode={src}]').click();await page.wait_for_timeout(250)
    frames.clear();await c.send('Page.startScreencast',{'format':'png','everyNthFrame':1,'maxWidth':w,'maxHeight':h})
    await page.wait_for_timeout(100)
    await page.locator(f'[data-mode={dst}]').click();await page.wait_for_timeout(850)
    await c.send('Page.stopScreencast');await page.wait_for_timeout(50)
    # Explicit snapshots supplement screencast (which emits only changed frames).
    frames.append((0,base64.b64encode(await page.screenshot(scale='css')).decode()))
    boxes=[];glyph_boxes=[]
    state=await page.evaluate("""()=>{const canvas=document.querySelector('#glass-scene'),gl=canvas.getContext('webgl2'),p=gl.getParameter(gl.CURRENT_PROGRAM),box=canvas.getBoundingClientRect();return {css:[box.width,box.height],backing:[canvas.width,canvas.height],buffer:[gl.drawingBufferWidth,gl.drawingBufferHeight],viewport:Array.from(gl.getParameter(gl.VIEWPORT)),uRes:Array.from(gl.getUniform(p,gl.getUniformLocation(p,'uRes'))),error:gl.getError()}}""")
    expected=[round(w*min(dpr,2)),round(h*min(dpr,2))]
    assert state['backing']==state['buffer']==expected and state['viewport']==[0,0,*expected] and state['uRes']==[w,h] and state['error']==0,state
    if dst!='classic':assert state['css']==[w,h],state
    nav=await page.locator('.styles').bounding_box()
    for n,(ts,data) in enumerate(frames):
     im=Image.open(io.BytesIO(base64.b64decode(data))).convert('RGB');im=im.resize((w,h))
     gray=im.convert('L');gray.paste(0,(0,h-3,w,h))
     gray.paste(0,(round(nav['x'])-3,round(nav['y'])-3,round(nav['x']+nav['width'])+3,round(nav['y']+nav['height'])+3))
     binary=gray.point(lambda v:255 if v>100 else 0);boxes.append(binary.getbbox())
     glyph_boxes.append([binary.crop((round(cell['x'])-3,round(cell['y'])-3,round(cell['x']+cell['width'])+3,round(cell['y']+cell['height'])+3)).getbbox() for cell in cells])
     im.save(out/f'{w}-{src}-{dst}-{n:02}.png')
    stamps=[ts for ts,_ in frames if ts]
    gaps=[(b-a)*1000 for a,b in zip(stamps,stamps[1:])]
    results.append(dict(size=[w,h,dpr],src=src,dst=dst,frames=len(frames),timestamps=stamps,maxGapMs=max(gaps,default=0),boxes=boxes,glyphBoxes=glyph_boxes,state=state,errors=errors.copy()))
   await page.close()
  await b.close()
 (out/'results.json').write_text(json.dumps(results,indent=2))
 bad=[r for r in results if r['errors'] or any(not q or max(abs(a-b) for a,b in zip(q,r['boxes'][-1]))>4 for q in r['boxes']) or any(not q or max(abs(a-b) for a,b in zip(q,base))>4 for frame in r['glyphBoxes'] for q,base in zip(frame,r['glyphBoxes'][-1]))]
 print(json.dumps(dict(transitions=len(results),frames=sum(r['frames'] for r in results),bad=bad),indent=2))
 assert not bad,'Visible glyph bounds change during style switch'
asyncio.run(main())
