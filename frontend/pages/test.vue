<template>
  <div class="min-h-screen bg-background text-foreground p-8">
    <div class="max-w-md mx-auto">
      <div class="bg-card border border-border rounded-lg p-6 shadow-lg">
        <h1 class="text-2xl font-bold text-primary mb-4">
          🎯 CSS Variables Fixed!
        </h1>
        <p class="text-muted-foreground mb-4">
          If you see this properly styled, the border-border issue is resolved.
        </p>
        <div class="p-3 bg-muted rounded border border-border mb-4">
          <span class="text-accent-foreground">Border variables are working!</span>
        </div>
        <div class="flex space-x-2 mb-4">
          <div class="w-4 h-4 bg-blue-500 rounded-full animate-bounce"></div>
          <div class="w-4 h-4 bg-green-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
          <div class="w-4 h-4 bg-purple-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
        </div>
        <NuxtLink to="/" class="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity">
          Back to Chat
        </NuxtLink>
      </div>
    </div>
  </div>
</template>
