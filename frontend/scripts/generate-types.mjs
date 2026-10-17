import fs from 'node:fs/promises'
import path from 'node:path'
import { fileURLToPath } from 'node:url'
import openapiTS, { astToString } from 'openapi-typescript'
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..')
await fs.mkdir(path.join(root, 'src/api/generated'), { recursive: true })
// Feed an object to avoid percent-encoded Windows Unicode filenames in external-ref resolution.
const schema = JSON.parse(
  await fs.readFile(path.join(root, '../contracts/http/openapi.generated.json'), 'utf8'),
)
const ast = await openapiTS(schema)
await fs.writeFile(path.join(root, 'src/api/generated/http.d.ts'), astToString(ast))
console.log('Generated frontend HTTP/domain types from actual OpenAPI.')
