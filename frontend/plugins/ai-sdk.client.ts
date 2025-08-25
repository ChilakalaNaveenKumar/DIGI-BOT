// plugins/ai-sdk.client.ts
// This plugin ensures AI SDK is only loaded on the client side

export default defineNuxtPlugin(() => {
  // Only run on client side
  if (process.client) {
    console.log('🤖 AI SDK client plugin loaded')
    
    // Pre-load AI SDK modules for better performance
    return {
      provide: {
        aiSdkReady: true
      }
    }
  }
})

