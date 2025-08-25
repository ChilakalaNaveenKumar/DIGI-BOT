<template>
  <header class="header">
    <div class="header-content">
      <div class="header-left">
        <h1 class="header-title">Claude</h1>
        <UiBadge variant="success" size="sm">Ready</UiBadge>
      </div>
      
      <div class="header-actions">
        <div class="system-toggle">
          <UiToggle
            v-model="useDigiSetuSystem"
            size="sm"
            :on-label="'Digi Setu'"
            :off-label="'Mock'"
            :on-icon="'lucide:zap'"
            :off-icon="'lucide:flask'"
            @update:model-value="handleSystemToggle"
          />
        </div>
        
        <div class="model-selector">
          <UiIcon name="lucide:cpu" :size="14" />
          <span class="model-label">{{ useDigiSetuSystem ? 'Digi Setu Orchestrator' : 'Sonnet 4' }}</span>
        </div>
        
        <UiButton variant="ghost" size="sm">
          <UiIcon name="lucide:settings" :size="16" />
        </UiButton>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
// Use Nuxt global state
const { useDigiSetuSystem, toggleSystem } = useSystemState()

const handleSystemToggle = (value: boolean) => {
  toggleSystem(value)
}
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.system-toggle {
  display: flex;
  align-items: center;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  transition: all 0.2s ease;
}

.model-selector:hover {
  background: var(--bg-tertiary);
}

.model-label {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}
</style>
