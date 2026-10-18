import { createServer } from 'vite'
const server = await createServer({ server: { host: '127.0.0.1', port: 5174, strictPort: true } })
await server.listen()
process.stdin.once('data', async () => {
  await server.close()
  process.exit(0)
})
process.stdin.once('end', async () => {
  await server.close()
  process.exit(0)
})
