<template>
  <div class="tool-section" v-if="tools && tools.length > 0">
    <div class="tool-header" @click="toggleExpanded">
      <div class="tool-info">
        <Icon name="cpu" :size="16" class="tool-icon" />
        <span class="tool-title">Tools Used</span>
        <span class="tool-count">({{ tools.length }})</span>
      </div>
      <Icon 
        name="chevron-down" 
        :size="16" 
        class="expand-icon"
        :class="{ 'expand-icon--rotated': isExpanded }"
      />
    </div>
    
    <div v-if="isExpanded" class="tool-content">
      <div v-for="tool in tools" :key="tool.id" class="tool-item">
        <div class="tool-item-header">
          <Icon :name="tool.icon || 'cpu'" :size="14" />
          <span class="tool-name">{{ tool.name }}</span>
          <Badge 
            :variant="tool.status === 'completed' ? 'success' : tool.status === 'error' ? 'error' : 'warning'"
            size="sm"
          >
            {{ tool.status }}
          </Badge>
        </div>
        <div v-if="tool.description" class="tool-description">
          {{ tool.description }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
interface Tool {
  id: string
  name: string
  status: 'running' | 'completed' | 'error'
  description?: string
  icon?: string
}

interface Props {
  tools?: Tool[]
}

const props = withDefaults(defineProps<Props>(), {
  tools: () => []
})

const isExpanded = ref(false)

const toggleExpanded = () => {
  isExpanded.value = !isExpanded.value
}
</script>

<style scoped>
.tool-section {
  background: var(--bg-secondary);
  border: 1px solid var(--border-primary);
  border-radius: 8px;
  margin: 8px 0;
  overflow: hidden;
}

.tool-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tool-header:hover {
  background: var(--bg-hover);
}

.tool-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.tool-icon {
  color: var(--accent-primary);
}

.tool-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.tool-count {
  font-size: 12px;
  color: var(--text-tertiary);
}

.expand-icon {
  color: var(--text-secondary);
  transition: transform 0.2s ease;
}

.expand-icon--rotated {
  transform: rotate(180deg);
}

.tool-content {
  border-top: 1px solid var(--border-primary);
  padding: 12px 16px;
  background: var(--bg-primary);
}

.tool-item {
  padding: 8px 0;
}

.tool-item:not(:last-child) {
  border-bottom: 1px solid var(--border-secondary);
  padding-bottom: 12px;
  margin-bottom: 12px;
}

.tool-item-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}

.tool-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

/* Tool status styles handled by Badge component */

.tool-description {
  font-size: 12px;
  color: var(--text-secondary);
  line-height: 1.4;
  margin-left: 22px;
}
</style>
