<template>
  <header class="header">
    <div class="header-content">
      <div class="header-left">
        <h1 class="header-title">Digi Setu AI</h1>
        <div class="status-badge">
          <div class="status-dot" />
          <span>Ready</span>
        </div>
      </div>
      
      <div class="header-actions">
        <button class="settings-btn">
          <Icon name="lucide:settings" :size="16" />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
// Clean header - no demo/development toggles needed for live system
</script>

<style scoped>
.header {
  background: var(--bg-primary);
  border-bottom: 1px solid var(--border-primary);
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  flex-shrink: 0;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.header-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.status-badge {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 8px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 12px;
  font-size: 12px;
  color: var(--text-secondary);
}

.status-dot {
  width: 6px;
  height: 6px;
  background: #10b981;
  border-radius: 50%;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.settings-btn {
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

.settings-btn:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}
</style>