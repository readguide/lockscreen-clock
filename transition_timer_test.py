"""Exercise production minute timer -> sync(true), not the QA render hook."""
import asyncio,datetime,json,os
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(channel='chrome',headless=True)
  page=await b.new_page(viewport={'width':390,'height':844},timezone_id='UTC')
  await page.clock.install(time=datetime.datetime(2026,1,1,10,38,59,tzinfo=datetime.timezone.utc))
  await page.clock.pause_at(datetime.datetime(2026,1,1,10,38,59,tzinfo=datetime.timezone.utc))
  await page.add_init_script("localStorage.setItem('clock-style','prism')")
  await page.goto(os.getenv('CLOCK_URL','http://127.0.0.1:8794/'));await page.evaluate('document.fonts.ready')
  assert await page.locator('time').get_attribute('datetime')=='10:38'
  await page.clock.run_for(1100)
  state=await page.evaluate('({text:clock.getAttribute("datetime"),motion:clock.dataset.motion,transition:glassQA.transition})')
  assert state['text']=='10:39' and state['motion']=='true' and state['transition']=={'from':'10:38','to':'10:39'},state
  await page.clock.run_for(900)
  assert await page.evaluate('glassQA.geometryUpdates.at(-1).chars')=='10:39'
  assert await page.evaluate('glassQA.transition') is None
  out=Path(__file__).parent/'qa/digit-transition/minute-timer.json';out.write_text(json.dumps(state,indent=2));print(state)
  await b.close()
asyncio.run(main())
