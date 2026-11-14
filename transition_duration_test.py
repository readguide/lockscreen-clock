"""Real Chrome/WebGL regression for 160ms out, 130ms delay, 220ms in."""
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
        seconds = os.getenv('CLOCK_FORMAT') == 'hms'
        if seconds:
            await page.locator('[data-format=hms]').click()
        results = await page.evaluate("""async seconds => {
          let now=1000, next=0; const pending=new Map(), samples=[];
          performance.now=()=>now;
          window.requestAnimationFrame=cb=>{pending.set(++next,cb);return next};
          window.cancelAnimationFrame=id=>pending.delete(id);
          const canvas=document.querySelector('canvas'), gl=canvas.getContext('webgl2');
          const uniform=gl.uniform1fv.bind(gl);let passes=[];
          gl.uniform1fv=(loc,values)=>{if(values.length===8)passes.push(Array.from(values));return uniform(loc,values)};
          const pixels=()=>{const a=new Uint8Array(canvas.width*canvas.height*4);gl.readPixels(0,0,canvas.width,canvas.height,gl.RGBA,gl.UNSIGNED_BYTE,a);return a};
          const rects=()=>Array.from(document.querySelectorAll('time>span'),e=>e.getBoundingClientRect().toJSON());
          const bounds=rects(), before=JSON.stringify(bounds), old=pixels();
          clockQA.render(seconds?'10:38:11':'10:39');await Promise.resolve();
          const flush=()=>{const callbacks=[...pending.values()];pending.clear();callbacks.forEach(cb=>cb(now))};
          flush();if(!glassQA.transition)throw Error('Expected animated transition');
          const builds=glassQA.sdfBuilds, uploads=glassQA.textureUploads, start=now;
          let overlap;
          for(const elapsed of [80,130,145,160,240,349,350]){
            now=start+elapsed;passes=[];flush();
            samples.push({elapsed,active:!!glassQA.transition,passes});
            if(elapsed===145)overlap=pixels();
          }
          const final=pixels();let oldOnly=0,newOnly=0,unchangedDiff=0;
          for(let y=0;y<canvas.height;y++)for(let x=0;x<canvas.width;x++){
            const i=(y*canvas.width+x)*4, cssX=x*390/canvas.width;
            if(cssX<bounds[seconds?6:3].right){if(old[i]!==overlap[i])unchangedDiff++;}
            if(cssX<bounds[seconds?7:4].left)continue;
            if(old[i]>80 && final[i]<2 && overlap[i]>1)oldOnly++;
            if(final[i]>80 && old[i]<2 && overlap[i]>1)newOnly++;
          }
          const idle=glassQA.draws;now+=1000;flush();
          return {samples,oldOnly,newOnly,unchangedDiff,unchangedLayout:before===JSON.stringify(rects()),idleDraws:glassQA.draws-idle,pendingFrames:pending.size,frameBuilds:glassQA.sdfBuilds-builds,frameUploads:glassQA.textureUploads-uploads,glError:glassQA.glError()};
        }""", seconds)
        await browser.close()
        print(json.dumps(dict(results, errors=errors)), flush=True)
        assert results['oldOnly'] > 10 and results['newOnly'] > 10, '145ms must show BOTH glyph silhouettes: '+str(results)
        for sample in results['samples']:
            t = sample['elapsed']
            def ease(x):
                x = max(0, min(1, x))
                return x*x*(3-2*x)
            outgoing, incoming = sample['passes']
            digit = 7 if seconds else 4
            assert abs(outgoing[digit] - (1-ease(t/160))) < 1e-6, sample
            assert abs(incoming[digit] - ease((t-130)/220)) < 1e-6, sample
            assert all(v == 0 for j,v in enumerate(outgoing) if j != digit), sample
            assert all(v == 1 for j,v in enumerate(incoming) if j != digit), sample
        assert [s['active'] for s in results['samples']] == [True]*6+[False], results
        assert results['unchangedDiff'] == 0 and results['unchangedLayout'], results
        assert results['idleDraws'] == results['pendingFrames'] == results['frameBuilds'] == results['frameUploads'] == 0, results
        assert results['glError'] == 0 and not errors, results


if __name__ == '__main__':
    asyncio.run(main())
