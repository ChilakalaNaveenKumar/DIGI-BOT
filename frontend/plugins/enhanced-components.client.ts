// plugins/enhanced-components.client.ts
// Plugin to register enhanced chart and interactive components

import VueApexCharts from 'vue3-apexcharts'

export default defineNuxtPlugin((nuxtApp) => {
  // Only run on client side
  if (process.client) {
    console.log('📊 Enhanced Components Plugin loaded')
    
    // Register ApexCharts globally
    nuxtApp.vueApp.component('apexchart', VueApexCharts)
    
    return {
      provide: {
        enhancedComponentsReady: true,
        chartLibrary: 'apexcharts'
      }
    }
  }
})
