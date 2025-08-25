<template>
  <div class="toolbar">
    <div class="toolbar-left">
      <UiButton 
        variant="ghost" 
        size="sm"
        @click="$emit('add')"
        class="toolbar-button"
      >
        <UiIcon name="lucide:plus" :size="16" />
      </UiButton>
      
      <UiButton 
        variant="ghost" 
        size="sm"
        @click="$emit('options')"
        class="toolbar-button"
      >
        <UiIcon name="lucide:more-horizontal" :size="16" />
      </UiButton>
      
      <UiButton 
        variant="ghost" 
        size="sm"
        @click="$emit('research')"
        class="toolbar-button toolbar-button--research"
      >
        <UiIcon name="lucide:search" :size="14" />
        <span>Research</span>
      </UiButton>
    </div>
    
    <div class="toolbar-right">
      <div class="model-selector">
        <UiIcon name="lucide:cpu" :size="14" />
        <span>{{ modelName }}</span>
        <UiIcon name="lucide:chevron-down" :size="14" />
      </div>
      
      <UiButton 
        variant="ghost" 
        size="sm"
        @click="$emit('upload')"
        class="toolbar-button"
      >
        <UiIcon name="lucide:arrow-up" :size="16" />
      </UiButton>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelName?: string
}

interface Emits {
  (e: 'add'): void
  (e: 'options'): void
  (e: 'research'): void
  (e: 'upload'): void
  (e: 'model-change'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelName: 'Claude Sonnet 4'
})

defineEmits<Emits>()
</script>

<style scoped>
.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 8px 12px;
  background: transparent;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-button {
  color: var(--text-secondary);
  border-radius: 8px;
  padding: 6px 8px;
  min-height: 32px;
}

.toolbar-button:hover {
  color: var(--text-primary);
  background: var(--bg-hover);
}

.toolbar-button--research {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.model-selector:hover {
  background: var(--bg-hover);
  border-color: var(--border-secondary);
  color: var(--text-primary);
}
</style>
