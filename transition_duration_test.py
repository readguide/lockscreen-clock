"""Real installed Chrome regression: a changed digit settles within 550 ms.

CLOCK_URL selects local or deployed Pages; CLOCK_VIDEO optionally records evidence.
"""
import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=False)
        options = dict(viewport={'width': 390, 'height': 844})
        if os.getenv('CLOCK_VIDEO'):
            options.update(record_video_dir=os.environ['CLOCK_VIDEO'], record_video_size=options['viewport'])
        context = await browser.new_context(**options)
        page = await context.new_page()
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        await page.add_init_script("localStorage.setItem('clock-style','prism');const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
        await page.goto(os.getenv('CLOCK_URL', 'http://127.0.0.1:8794/'))
        await page.evaluate('document.fonts.ready')
        await page.wait_for_timeout(500)
        rects = await page.locator('time>span').evaluate_all('(es)=>es.map(e=>e.getBoundingClientRect().toJSON())')
        # Poll in the browser, not Python: wall time includes the real glyph rebuild.
        results = await page.evaluate("""async () => {
          const durations=[];
          for (const text of ['10:39','10:38','10:39']) {
            const start=performance.now(); clockQA.render(text);
            await new Promise(resolve=>requestAnimationFrame(resolve));
            if (!glassQA.transition) throw Error('Expected animated transition');
            await new Promise(resolve=>{function poll(){if(!glassQA.transition)resolve();else requestAnimationFrame(poll)}requestAnimationFrame(poll)});
            durations.push(performance.now()-start);
          }
          return {durations, glError:glassQA.glError()};
        }""")
        assert await page.locator('time>span').evaluate_all('(es)=>es.map(e=>e.getBoundingClientRect().toJSON())') == rects
        idle = await page.evaluate('glassQA.draws')
        await page.wait_for_timeout(1100)
        results.update(idleDraws=await page.evaluate('glassQA.draws')-idle, errors=errors)
        if os.getenv('CLOCK_VIDEO'):
            await page.screenshot(path=str(Path(os.environ['CLOCK_VIDEO'])/'faster-settled.png'))
        video = page.video
        await context.close()
        if video:
            results['video'] = str(await video.path())
        await browser.close()
        print(json.dumps(results), flush=True)
        assert max(results['durations']) <= 550, f"Fade exceeds 550 ms: {results['durations']}"
        assert min(results['durations']) >= 400, results
        assert results['idleDraws'] == 0, results
        assert results['glError'] == 0 and not errors, results

if __name__ == '__main__':
    asyncio.run(main())
