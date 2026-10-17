import fs from 'node:fs/promises'
import path from 'node:path'
import crypto from 'node:crypto'
import { fileURLToPath } from 'node:url'

async function filesIn(folder) {
  let entries
  try {
    entries = await fs.readdir(folder, { withFileTypes: true })
  } catch (error) {
    if (error.code === 'ENOENT') return []
    throw error
  }
  const files = []
  for (const entry of entries) {
    const full = path.join(folder, entry.name)
    if (entry.isDirectory()) files.push(...(await filesIn(full)))
    else if (entry.isFile()) files.push(full)
  }
  return files
}

export async function frontendFingerprint(root) {
  const frontend = path.join(root, 'frontend')
  const files = [
    ...(await filesIn(path.join(frontend, 'src'))),
    ...(await filesIn(path.join(frontend, 'public'))),
  ]
  const names = ['index.html', 'package.json', 'package-lock.json', 'scripts/build-info.mjs']
  for (const name of await fs.readdir(frontend))
    if (/^tsconfig.*\.json$/.test(name) || /^vite\.config\./.test(name)) names.push(name)
  for (const name of names) {
    const full = path.join(frontend, name)
    try {
      if ((await fs.stat(full)).isFile()) files.push(full)
    } catch (error) {
      if (error.code !== 'ENOENT') throw error
    }
  }
  const relative = (file) => path.relative(root, file).split(path.sep).join('/')
  const ordered = [...new Set(files)].sort((a, b) =>
    Buffer.compare(Buffer.from(relative(a)), Buffer.from(relative(b))),
  )
  const digest = crypto.createHash('sha256')
  for (const file of ordered) {
    const content = crypto
      .createHash('sha256')
      .update(await fs.readFile(file))
      .digest('hex')
    digest.update(`${relative(file)}\0${content}\n`)
  }
  return digest.digest('hex')
}

async function main() {
  const root = path.resolve(
    process.argv[3] || path.join(path.dirname(fileURLToPath(import.meta.url)), '../..'),
  )
  const source = await frontendFingerprint(root)
  if (process.argv[2] === '--fingerprint') {
    console.log(source)
    return
  }
  const dist = path.join(root, 'frontend/dist')
  const output = path.join(dist, 'assets/build-info.json')
  const artifacts = []
  for (const file of (await filesIn(dist)).sort()) {
    if (file === output) continue
    const bytes = await fs.readFile(file)
    artifacts.push({
      path: path.relative(dist, file).split(path.sep).join('/'),
      bytes: bytes.length,
      sha256: crypto.createHash('sha256').update(bytes).digest('hex'),
    })
  }
  if (!artifacts.some((entry) => entry.path === 'index.html'))
    throw new Error('Built index.html is missing.')
  await fs.mkdir(path.dirname(output), { recursive: true })
  await fs.writeFile(
    output,
    JSON.stringify(
      {
        fingerprint_version: 1,
        frontend_source_sha256: source,
        built_at_utc: new Date().toISOString(),
        node_version: process.version,
        artifacts,
      },
      null,
      2,
    ) + '\n',
  )
  console.log(`Recorded offline build identity (${artifacts.length} artifacts).`)
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  await main()
