<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
    <div class="bg-white rounded-2xl p-8 shadow-2xl max-w-md">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">
        🎯 Tailwind CSS Working!
      </h1>
      <p class="text-gray-600 mb-6">
        If you see this styled correctly, Tailwind is fixed.
      </p>
      <div class="flex space-x-2">
        <div class="w-4 h-4 bg-red-500 rounded-full animate-bounce"></div>
        <div class="w-4 h-4 bg-green-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
        <div class="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
      </div>
      <NuxtLink to="/" class="inline-block mt-4 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors">
        Back to Chat
      </NuxtLink>
    </div>
  </div>
</template>
