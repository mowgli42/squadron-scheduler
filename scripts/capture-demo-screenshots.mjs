/**
 * Capture demo build-up screenshots by clicking each Demo stage button.
 * Usage: node scripts/capture-demo-screenshots.mjs [uiUrl]
 */
import { chromium } from 'playwright'
import { mkdir } from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const root = path.resolve(__dirname, '..')
const outDir = path.join(root, 'docs/images/demo')
const ui = process.argv[2] || 'http://127.0.0.1:5200'

const stages = [
  '01-empty-board',
  '02-tails-assigned',
  '03-loadouts-applied',
  '04-crew-filled',
  '05-crew-ready',
  '06-launched',
]

await mkdir(outDir, { recursive: true })
const browser = await chromium.launch()
const page = await browser.newPage({ viewport: { width: 1280, height: 720 } })
await page.goto(ui, { waitUntil: 'networkidle' })

for (const id of stages) {
  const btn = id.slice(0, 2)
  await page.getByRole('button', { name: btn, exact: true }).click()
  await page.waitForTimeout(500)
  const dest = path.join(outDir, `${id}.png`)
  await page.screenshot({ path: dest, fullPage: true })
  console.log('wrote', path.relative(root, dest))
}

await browser.close()
