import { resolve } from 'node:path'
import { existsSync } from 'node:fs'
import { spawn } from 'node:child_process'
import react from '@vitejs/plugin-react'
import { type Connect, type Plugin } from 'vite'
import { defineConfig } from 'vitest/config'

const repositoryRoot = resolve(import.meta.dirname, '..')
const bridgePath = resolve(repositoryRoot, 'scripts/arca_mechanica_bridge.py')
const virtualEnvironmentPython = resolve(repositoryRoot, '.venv/bin/python')

function readBody(request: Connect.IncomingMessage): Promise<string> {
  return new Promise((resolveBody, reject) => {
    const chunks: Buffer[] = []
    request.on('data', (chunk) => chunks.push(Buffer.from(chunk)))
    request.on('end', () => resolveBody(Buffer.concat(chunks).toString('utf8')))
    request.on('error', reject)
  })
}

function invokeHistoricalKernel(command: 'manifest' | 'execute', input = ''): Promise<string> {
  const executable = existsSync(virtualEnvironmentPython) ? virtualEnvironmentPython : 'python3'
  return new Promise((resolveOutput, reject) => {
    const child = spawn(executable, [bridgePath, command], {
      cwd: repositoryRoot,
      stdio: ['pipe', 'pipe', 'pipe'],
    })
    const stdout: Buffer[] = []
    const stderr: Buffer[] = []
    child.stdout.on('data', (chunk) => stdout.push(Buffer.from(chunk)))
    child.stderr.on('data', (chunk) => stderr.push(Buffer.from(chunk)))
    child.on('error', reject)
    child.on('close', (code) => {
      const output = Buffer.concat(stdout).toString('utf8')
      if (code === 0) {
        resolveOutput(output)
      } else {
        reject(new Error(Buffer.concat(stderr).toString('utf8') || `kernel bridge exited ${code}`))
      }
    })
    child.stdin.end(input)
  })
}

function historicalKernelMiddleware(): Connect.NextHandleFunction {
  return async (request, response, next) => {
    const url = request.url?.split('?')[0]
    const isManifest = request.method === 'GET' && url === '/api/historica/manifest'
    const isExecution = request.method === 'POST' && url === '/api/historica/execute'
    if (!isManifest && !isExecution) {
      next()
      return
    }

    try {
      const input = isExecution ? await readBody(request) : ''
      const payload = await invokeHistoricalKernel(isManifest ? 'manifest' : 'execute', input)
      response.statusCode = 200
      response.setHeader('Content-Type', 'application/json; charset=utf-8')
      response.setHeader('Cache-Control', 'no-store')
      response.end(payload)
    } catch (error) {
      response.statusCode = 422
      response.setHeader('Content-Type', 'application/json; charset=utf-8')
      response.end(JSON.stringify({
        error: 'historical_alignment_rejected',
        message: error instanceof Error ? error.message : 'The historical bridge rejected the request.',
      }))
    }
  }
}

function historicalKernelBridge(): Plugin {
  return {
    name: 'arca-historica-kernel-bridge',
    configureServer(server) {
      server.middlewares.use(historicalKernelMiddleware())
    },
    configurePreviewServer(server) {
      server.middlewares.use(historicalKernelMiddleware())
    },
  }
}

export default defineConfig({
  plugins: [react(), historicalKernelBridge()],
  server: { host: '0.0.0.0', port: 4173, allowedHosts: ['terminal.local'] },
  preview: { host: '0.0.0.0', port: 4173 },
  test: {
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    css: true,
  },
})
