<template>
  <div class="simple-chat">
    <h1>Simple Chat Page</h1>
    <p>This is a test to see if the route works</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({
  layout: false,
  ssr: false
})
</script>

<style scoped>
.simple-chat {
  padding: 20px;
  background: #f0f0f0;
  min-height: 100vh;
}
</style>
