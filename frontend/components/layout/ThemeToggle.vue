<template>
  <UiToggle
    :model-value="isDark"
    @update:model-value="toggleTheme"
    label="Theme"
    :on-label="'Dark'"
    :off-label="'Light'"
    :on-icon="'lucide:moon'"
    :off-icon="'lucide:sun'"
    size="md"
  />
</template>

<script setup lang="ts">
const { theme, toggleTheme, isDark } = useTheme()
</script>

<style scoped>
/* Theme toggle styles handled by Toggle component */
</style>
