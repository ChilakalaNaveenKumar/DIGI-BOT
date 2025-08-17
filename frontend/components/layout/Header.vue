<template>
  <header class="header">
    <div class="header-content">
      <h1 class="header-title">Coffee and Claude time?</h1>
      <div class="header-actions">
        <!-- Additional header actions can go here -->
      </div>
    </div>
  </header>
</template>

<script setup>
// Header logic
</script>

<style scoped>
.header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  padding: 16px 24px;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
