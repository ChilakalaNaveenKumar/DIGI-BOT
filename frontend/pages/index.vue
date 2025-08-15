<template>
  <div>
    <!-- AI SDK Chat Interface -->
    <AiChatContainer />
  </div>
</template>

<script setup lang="ts">
import AiChatContainer from '~/components/Chat/AiChatContainer.vue'

// Page metadata
useHead({
  title: 'Digi Setu AI - Interactive Learning Platform',
  meta: [
    { name: 'description', content: 'Transform static content into interactive learning experiences with AI' }
  ]
})
</script>
