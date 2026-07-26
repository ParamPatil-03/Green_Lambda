const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.error('PAGE ERROR:', err));

  console.log('Navigating to connect.html...');
  await page.goto('http://localhost:8000/connect.html');
  
  console.log('Filling form...');
  await page.fill('#awsAccessKey', 'TEST-KEY-123');
  await page.fill('#awsSecretKey', 'test');
  
  console.log('Clicking Connect...');
  await page.click('#connectAwsBtn');
  
  console.log('Waiting for network idle...');
  await page.waitForTimeout(3000);
  
  console.log('Taking screenshot...');
  await page.screenshot({ path: 'screenshot.png' });
  
  console.log('Checking visibility of wrap...');
  const wrapHidden = await page.evaluate(() => document.getElementById('connectedFunctionsWrap').hidden);
  console.log('Wrap hidden?', wrapHidden);
  
  console.log('Clicking Analyze link...');
  await page.click('#gotoAnalyzeBtn');
  
  await page.waitForTimeout(3000);
  console.log('Taking screenshot of Analyze...');
  await page.screenshot({ path: 'screenshot_analyze.png' });

  await browser.close();
})();
