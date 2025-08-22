<template>
  <button 
    class="theme-toggle"
    @click="toggleTheme"
    :title="`Switch to ${currentTheme === 'light' ? 'dark' : 'light'} mode`"
  >
    <Icon 
      :name="currentTheme === 'light' ? 'lucide:moon' : 'lucide:sun'" 
      :size="16" 
    />
  </button>
</template>

<script setup lang="ts">
const { currentTheme, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  background: transparent;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.theme-toggle:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>
