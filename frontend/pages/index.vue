<template>
  <div class="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
    <div class="max-w-4xl mx-auto">
      <!-- Simple Header -->
      <div class="text-center mb-6">
        <h1 class="text-2xl sm:text-3xl font-bold text-gray-900 mb-2">
          Digi Setu AI
        </h1>
        <p class="text-gray-600 text-sm sm:text-base">
          Chat with multiple AI providers
        </p>
      </div>

      <!-- Chat Interface -->
      <ChatInterface />
    </div>
  </div>
</template>

<script setup>
// Page metadata
useHead({
  title: 'Digi Setu AI - Interactive Learning Platform',
  meta: [
    { name: 'description', content: 'Transform static content into interactive learning experiences with AI' }
  ]
})
</script>
