import { spawn } from 'node:child_process'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import fs from 'node:fs/promises'
import { randomUUID } from 'node:crypto'
const frontend = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
const root = path.resolve(frontend, '..')
const stopFile = path.join(root, '.local/e2e-control', randomUUID() + '.stop')
await fs.mkdir(path.dirname(stopFile), { recursive: true })
const env = {
  ...process.env,
  NO_PROXY: '127.0.0.1,localhost,::1',
  no_proxy: '127.0.0.1,localhost,::1',
  PLAYWRIGHT_BROWSERS_PATH: path.join(root, '.local/ms-playwright'),
  YUANHANG_RUNTIME: path.join(root, '.local/e2e-runtime'),
  YUANHANG_API_URL: 'http://127.0.0.1:8011',
  YUANHANG_E2E_STOP_FILE: stopFile,
  YUANHANG_E2E_REPORT:
    process.env.YUANHANG_E2E_REPORT ||
    (process.argv.some((arg) => arg.startsWith('--grep'))
      ? '../evidence/browser/e2e-targeted-results.json'
      : '../evidence/browser/e2e-results.json'),
}
const python = path.join(
  root,
  process.platform === 'win32' ? '.venv/Scripts/python.exe' : '.venv/bin/python',
)
const processes = []
const start = (command, args, cwd) => {
  const child = spawn(command, args, {
    cwd,
    env,
    stdio: ['pipe', 'inherit', 'inherit'],
    windowsHide: true,
  })
  processes.push(child)
  return child
}
async function ready(url, child) {
  for (let i = 0; i < 120; i++) {
    if (child.exitCode !== null) throw new Error('Test service exited before readiness: ' + url)
    try {
      const response = await fetch(url, { signal: AbortSignal.timeout(1000) })
      if (response.ok) return
      if (i === 10) console.error('Readiness HTTP status', response.status, await response.text())
    } catch (error) {
      if (i === 10)
        console.error('Readiness still pending', url, error.cause?.code || error.message)
    }
    await new Promise((resolve) => setTimeout(resolve, 250))
  }
  throw new Error('Test service startup timed out: ' + url)
}
let code
try {
  for (const port of [8011, 5174]) {
    try {
      await fetch(`http://127.0.0.1:${port}`, { signal: AbortSignal.timeout(300) })
      throw new Error(`Test port ${port} is already occupied`)
    } catch (e) {
      if (e.message.includes('already occupied')) throw e
    }
  }
  const backend = start(python, ['-m', 'scripts.e2e_service'], root)
  await ready('http://127.0.0.1:8011/api/v1/health', backend)
  const vite = start(process.execPath, [path.join(frontend, 'scripts/e2e-vite.mjs')], frontend)
  await ready('http://127.0.0.1:5174', vite)
  const test = spawn(
    process.execPath,
    [path.join(frontend, 'node_modules/@playwright/test/cli.js'), 'test', ...process.argv.slice(2)],
    { cwd: frontend, env, stdio: 'inherit', windowsHide: true },
  )
  code = await new Promise((resolve, reject) => {
    test.once('exit', (c) => resolve(c ?? 1))
    test.once('error', reject)
  })
} catch (error) {
  console.error(error)
  code = 1
} finally {
  await fs.writeFile(stopFile, 'stop')
  await Promise.all(
    processes.map(async (child) => {
      if (child.exitCode !== null) return
      child.stdin.end('stop\n')
      await Promise.race([
        new Promise((resolve) => child.once('exit', resolve)),
        new Promise((resolve) => setTimeout(resolve, 5000)),
      ])
      if (child.exitCode === null) child.kill()
    }),
  )
  await fs.unlink(stopFile).catch(() => {})
}
process.exit(code)
