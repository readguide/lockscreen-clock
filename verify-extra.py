import asyncio,json
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
async def main():
 async with async_playwright() as p:
  b=await p.chromium.launch(channel='chrome',headless=True)
  page=await b.new_page()
  await page.clock.install(time=datetime(2026,11,14,23,59,58))
  await page.goto('http://127.0.0.1:8794/');await page.locator('[data-mode=prism]').click()
  await page.clock.fast_forward(3000)
  assert await page.locator('time').get_attribute('datetime')=='00:00'
  cdp=await page.context.new_cdp_session(page)
  await cdp.send('Emulation.setEmulatedMedia',{'features':[{'name':'display-mode','value':'standalone'}]})
  standalone=await page.evaluate("matchMedia('(display-mode: standalone)').matches")
  if standalone: assert not await page.locator('.styles').is_visible()
  result={'midnight_timer_rollover':'23:59 -> 00:00','standalone_media_emulated':standalone,'standalone_controls_hidden':standalone}
  Path('/Users/en/lockscreen-clock/qa/extra.json').write_text(json.dumps(result,indent=2));print(result)
  await b.close()
asyncio.run(main())
