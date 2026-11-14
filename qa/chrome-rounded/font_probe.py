from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=False)
 page=b.new_page(); page.goto('file:///Users/en/lockscreen-clock/index.html');page.wait_for_timeout(1500)
 s=page.context.new_cdp_session(page);s.send('DOM.enable');s.send('CSS.enable')
 out={}
 for font in ['ui-rounded','"SF Pro Rounded"','".AppleSystemUIFontRounded"','"SF Rounded"','"SFCompactRounded"','"SF Compact Rounded"','"Arial Rounded MT Bold"','-apple-system','BlinkMacSystemFont']:
  page.evaluate('(font)=>{document.body.innerHTML="<span id=probe>0123456789</span>";probe.style.cssText=`font:600 100px ${font}`}',font)
  page.wait_for_timeout(100)
  node=s.send('DOM.querySelector',{'nodeId':s.send('DOM.getDocument')['root']['nodeId'],'selector':'#probe'})['nodeId']
  out[font]=s.send('CSS.getPlatformFontsForNode',{'nodeId':node})
 for name in ['.SF NS Rounded','.SFNSRounded-Regular','.SFNSRounded','SFNSRounded','SF Pro Rounded','Arial Rounded MT Bold']:
  out['local:'+name]=page.evaluate('async name=>{try{const f=new FontFace("probeLocal",`local("${name}")`);await f.load();return f.status}catch(e){return String(e)}}',name)
 print(json.dumps(out,indent=2));b.close()
