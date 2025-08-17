<template>
  <div class="ds-chat-container">
    <!-- Enhanced Multimodal AI Chat Interface -->
    <ClientOnly>
      <DigiSetuEnhancedChat />
      <template #fallback>
        <div class="ds-loading-state">
          <div class="ds-loading-spinner"></div>
          <p>Loading Digi Setu AI with Multimodal Capabilities...</p>
        </div>
      </template>
    </ClientOnly>
  </div>
</template>

<script setup lang="ts">
import DigiSetuEnhancedChat from '~/components/Chat/DigiSetuEnhancedChat.vue'

// Page metadata
useHead({
  title: 'Digi Setu AI - Enhanced Multimodal Platform',
  meta: [
    { name: 'description', content: 'Advanced AI platform with multimodal capabilities: audio generation, reasoning, structured outputs, live search, and more!' }
  ]
})
</script>

<style scoped>
.ds-chat-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.ds-loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 1rem;
  color: var(--ds-text-secondary);
}

.ds-loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid var(--ds-border-primary);
  border-top: 2px solid var(--ds-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
</style>
