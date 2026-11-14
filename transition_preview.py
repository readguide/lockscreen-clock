"""Record actual Chrome compositor frames; use system ffmpeg, no installs."""
import asyncio,base64,json,subprocess
from pathlib import Path
from playwright.async_api import async_playwright
OUT=Path(__file__).parent/'qa/digit-transition'; FRAMES=OUT/'preview-frames';FRAMES.mkdir(exist_ok=True)
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(channel='chrome',headless=True)
  page=await b.new_page(viewport={'width':1440,'height':900})
  await page.add_init_script("localStorage.setItem('clock-style','prism');const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
  await page.goto('http://127.0.0.1:8794/');await page.evaluate('document.fonts.ready');await page.wait_for_timeout(500)
  c=await page.context.new_cdp_session(page);frames=[]
  async def frame(e):
   target=FRAMES/f'{len(frames):04}.jpg';target.write_bytes(base64.b64decode(e['data']));frames.append((target,e['metadata']['timestamp']))
   await c.send('Page.screencastFrameAck',{'sessionId':e['sessionId']})
  c.on('Page.screencastFrame',frame)
  await c.send('Page.startScreencast',{'format':'jpeg','quality':95,'everyNthFrame':1})
  await page.wait_for_timeout(800);await page.evaluate("clockQA.render('10:39')");await page.wait_for_timeout(1800)
  await c.send('Page.stopScreencast');await b.close()
  lines=[]
  for i,(path,t) in enumerate(frames):
   lines.extend([f"file '{path}'",f"duration {(frames[i+1][1]-t) if i+1<len(frames) else 1:.6f}"])
  lines.append(f"file '{frames[-1][0]}'")
  (OUT/'preview.concat').write_text('\n'.join(lines));(OUT/'preview-timestamps.json').write_text(json.dumps([t for _,t in frames]))
  subprocess.run(['ffmpeg','-y','-f','concat','-safe','0','-i',str(OUT/'preview.concat'),'-vf','fps=30','-c:v','libx264','-pix_fmt','yuv420p','-movflags','+faststart',str(OUT/'prism-1038-1039.mp4')],check=True,capture_output=True)
  print(f'{len(frames)} real compositor frames; {OUT}/prism-1038-1039.mp4')
asyncio.run(main())
