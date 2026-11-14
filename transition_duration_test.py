"""Real Chrome regression: 110 ms out, 220 ms in, no post-rebuild pause.

Use a controlled RAF clock; glyph rebuild, WebGL and renderer remain real.
CLOCK_URL selects local or deployed Pages. No screenshots or video required.
"""
import asyncio
import json
import os
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(channel='chrome', headless=True)
        page = await browser.new_page(viewport={'width': 390, 'height': 844}, reduced_motion='no-preference')
        errors = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        await page.add_init_script("localStorage.setItem('clock-style','prism');const D=Date;window.Date=class extends D{constructor(...a){super(...(a.length?a:[2026,0,1,10,38,10]))}static now(){return new D(2026,0,1,10,38,10).getTime()}}")
        await page.goto(os.getenv('CLOCK_URL', 'http://127.0.0.1:8794/'))
        await page.evaluate('document.fonts.ready')
        await page.wait_for_function('window.glassQA && window.clockQA && glassQA.draws > 0')
        await page.wait_for_timeout(200)
        results = await page.evaluate("""async () => {
          let now=1000, next=0; const pending=new Map(), samples=[];
          performance.now=()=>now;
          window.requestAnimationFrame=cb=>{pending.set(++next,cb);return next};
          window.cancelAnimationFrame=id=>pending.delete(id);
          const proto=WebGL2RenderingContext.prototype;
          const uniform=proto.uniform1fv, upload=proto.texImage2D;
          let fades=[];
          proto.uniform1fv=function(loc, values){
            if(values.length===5)fades=Array.from(values);
            return uniform.call(this,loc,values);
          };
          // Real geometry upload consumes time: incoming fade must start afterwards.
          proto.texImage2D=function(...args){now+=37;return upload.apply(this,args)};
          const rects=()=>Array.from(document.querySelectorAll('time>span'),e=>e.getBoundingClientRect().toJSON());
          const before=JSON.stringify(rects());
          clockQA.render('10:39');
          await Promise.resolve();
          // Flush the observer's scheduled renderer update without advancing time.
          {const callbacks=[...pending.values()];pending.clear();callbacks.forEach(cb=>cb(now));}
          if(!glassQA.transition)throw Error('Expected animated transition');
          function step(dt){now+=dt;const callbacks=[...pending.values()];pending.clear();callbacks.forEach(cb=>cb(now));samples.push({fades:[...fades],active:!!glassQA.transition});}
          step(55);step(55);step(110);step(110);
          const idle=glassQA.draws;step(1000);
          return {samples,unchangedLayout:before===JSON.stringify(rects()),idleDraws:glassQA.draws-idle,glError:glassQA.glError()};
        }""")
        await browser.close()
        print(json.dumps(dict(results, errors=errors)), flush=True)
        expected = [(0.5, True), (0, True), (0.5, True), (1, False)]
        for sample, (opacity, active) in zip(results['samples'], expected):
            assert abs(sample['fades'][4]-opacity) < 0.00001, (sample, opacity)
            assert sample['active'] == active, sample
            assert sample['fades'][:4] == [1, 1, 1, 1], sample
        assert results['unchangedLayout'] and results['idleDraws'] == 0, results
        assert results['glError'] == 0 and not errors, results


if __name__ == '__main__':
    asyncio.run(main())
