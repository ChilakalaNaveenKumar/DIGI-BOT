<template>
  <button 
    @click="handleLogout"
    class="logout-btn"
    :disabled="isLoading"
  >
    <Icon name="lucide:log-out" :size="16" />
    <span v-if="!isLoading">Logout</span>
    <span v-else>Logging out...</span>
  </button>
</template>

<script setup lang="ts">
const isLoading = ref(false)
const authStore = useAuthStore()

const handleLogout = async () => {
  isLoading.value = true
  
  try {
    // Call logout from auth store
    await authStore.logout()
    // Navigate to home page
    await navigateTo('/')
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.logout-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.logout-btn:hover:not(:disabled) {
  background: var(--bg-hover);
  color: var(--text-primary);
  border-color: var(--border-secondary);
}

.logout-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
