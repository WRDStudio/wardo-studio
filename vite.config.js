import { defineConfig } from 'vite'
import { resolve } from 'path'
// Force Git Sync: {new Date().toISOString()}

export default defineConfig({
  build: {
    rollupOptions: {
      input: {
        main: resolve(process.cwd(), 'index.html'),
        tech: resolve(process.cwd(), 'tech.html'),
        media: resolve(process.cwd(), 'media.html'),
        music: resolve(process.cwd(), 'music.html'),
        hospitality: resolve(process.cwd(), 'hospitality.html')
      }
    }
  }
})
