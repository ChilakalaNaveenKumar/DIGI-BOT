<template>
  <Toggle
    :model-value="isDark"
    @update:model-value="toggleTheme"
    label="Theme"
    on-label="Dark"
    off-label="Light"
    on-icon="moon"
    off-icon="sun"
    size="md"
  />
</template>

<script setup>
const { theme, toggleTheme, isDark } = useTheme()
</script>

<style scoped>
/* Theme toggle styles handled by Toggle component */
</style>
