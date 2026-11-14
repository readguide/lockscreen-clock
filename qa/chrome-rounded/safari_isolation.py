from playwright.sync_api import sync_playwright
with sync_playwright() as p:
 b=p.chromium.launch(channel='chrome',headless=False)
 page=b.new_page(user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 Version/27.2 Safari/605.1.15')
 page.route('**/chrome-rounded.js',lambda r:r.abort())
 page.goto('http://127.0.0.1:8917/');page.wait_for_timeout(800)
 assert page.evaluate('!!window.clockQA'), 'Safari initialization is coupled to a Chrome-only module request'
 print('PASS Safari exclusion survives unavailable Chrome module');b.close()
