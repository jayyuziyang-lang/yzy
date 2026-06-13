import { chromium } from 'playwright';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const CHARTS_DIR = path.resolve(__dirname, '../ai-chain/mlcc-series/charts');

const CHARTS = [
  { file: 'ai_position_sankey.html', output: 'ai_position_sankey.png', width: 1200, height: 700 },
  { file: 'usage_per_device.html', output: 'usage_per_device.png', width: 800, height: 500 },
  { file: 'market_share.html', output: 'market_share.png', width: 1000, height: 600 },
  { file: 'supply_chain_d3.html', output: 'supply_chain.png', width: 1000, height: 700 },
  { file: 'market_size.html', output: 'market_size.png', width: 900, height: 550 },
  { file: 'price_cycle.html', output: 'price_cycle.png', width: 900, height: 600 },
  { file: 'tech_evolution.html', output: 'tech_evolution.png', width: 1000, height: 650 },
];

async function main() {
  console.log('='.repeat(60));
  console.log('  Playwright: Plotly/D3 HTML -> static PNG');
  console.log('='.repeat(60));

  const browser = await chromium.launch({ headless: true });

  try {
    const page = await browser.newPage();

    for (const { file, output, width, height } of CHARTS) {
      const filePath = path.join(CHARTS_DIR, file);
      const outputPath = path.join(CHARTS_DIR, output);

      if (!fs.existsSync(filePath)) {
        console.log(`\nSKIP: ${file} not found`);
        continue;
      }

      console.log(`\n>>> ${file} -> ${output}`);

      // Use file:// protocol to load local HTML
      const fileUrl = `file://${filePath.replace(/\\/g, '/')}`;
      await page.goto(fileUrl, { waitUntil: 'networkidle', timeout: 30000 });

      // Wait for plotly/d3 to render
      await page.waitForTimeout(3000);

      // Set viewport
      await page.setViewportSize({ width, height: height + 60 });

      // Wait a bit more for rendering
      await page.waitForTimeout(2000);

      // Take screenshot of the chart div or full page
      await page.screenshot({ path: outputPath, fullPage: true });

      const sizeKB = fs.statSync(outputPath).size / 1024;
      console.log(`  OK: ${output} (${sizeKB.toFixed(0)} KB)`);
    }
  } finally {
    await browser.close();
  }

  console.log('\n' + '='.repeat(60));
  console.log('  Done!');
  console.log('='.repeat(60));
}

main().catch(console.error);
