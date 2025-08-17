<template>
  <div class="chat-page">
    <ChatContainer />
  </div>
</template>

<script setup lang="ts">
// All chat logic is now handled in ChatContainer
</script>

<style scoped>
.chat-page {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
</style>
