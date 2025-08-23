// https://nuxt.com/docs/api/configuration/nuxt-config
import tailwindcss from '@tailwindcss/vite'

export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: false },

  modules: [
    '@nuxt/content',
    '@nuxt/eslint',
    '@nuxt/image',
    '@nuxt/scripts',
    '@nuxt/test-utils',
    // '@nuxt/ui',        // Removed - using manual Tailwind v4 setup instead
    '@nuxt/icon',
    '@pinia/nuxt'
  ],

  css: [
    '~/assets/css/main.css',
    'katex/dist/katex.min.css',
    'highlight.js/styles/github-dark.css'
  ],

  // Component auto-import configuration with prefixes
  components: [
    {
      path: '~/components/ui',
      prefix: 'Ui'
    },
    {
      path: '~/components/enhanced',
      prefix: 'Enhanced'
    },
    {
      path: '~/components/layout',
      prefix: 'Layout'
    },
    {
      path: '~/components/chat',
      prefix: ''
    },
    {
      path: '~/components/auth',
      prefix: ''
    },
    {
      path: '~/components',
      prefix: ''
    }
  ],

  vite: {
    plugins: [tailwindcss()],
    build: {
      sourcemap: false
    },
    server: {
      hmr: {
        port: 24678
      }
    }
  },

  // Add dev server configuration
  devServer: {
    host: '0.0.0.0',
    port: 3000
  },

  // Add nitro configuration for development
  nitro: {
    devServer: {
      watch: []
    },
    experimental: {
      wasm: true
    }
  },

  // SSR configuration for AI SDK compatibility
  ssr: true,
  
  // Ensure proper client-side hydration
  experimental: {
    payloadExtraction: false
  },

  // Route rules for specific pages
  routeRules: {
    '/chat': { ssr: false, prerender: false }
  },

  runtimeConfig: {
    // Private keys (only available on server-side)
    openaiApiKey: process.env.OPENAI_API_KEY,
    anthropicApiKey: process.env.ANTHROPIC_API_KEY,
    grokApiKey: process.env.GROK_API_KEY,
    
    // Public keys (exposed to client-side)
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api',
      appName: 'Digi Setu AI',
      appDescription: 'Transform static content into interactive learning experiences with AI'
    }
  }
})
