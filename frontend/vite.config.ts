import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import viteTsconfigPaths from 'vite-tsconfig-paths'
import checker from 'vite-plugin-checker'

export default defineConfig({
  plugins: [
    react(),
    viteTsconfigPaths(),
    checker({
      typescript: true,
    }),
  ],
  server: {
    port: 3000,
    open: true,

  },
  build: {
    outDir: 'build',
  },
})