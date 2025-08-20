<template>
  <div class="enhanced-content-renderer" :data-message-id="messageId">
    <!-- Enhanced Content Display -->
    <div v-if="enhancedContent" class="enhanced-content">
      <UiStreamingMarkdown
        :content="enhancedContent"
        :is-streaming="false"
        :show-cursor="false"
        mode="static"
      />
    </div>
    
    <!-- Component Overlays -->
    <div v-if="overlayComponents.length > 0" class="component-overlays">
      <div
        v-for="component in overlayComponents"
        :key="component.id"
        class="component-overlay"
        :style="{ top: `${component.position * 0.1}px` }"
      >
        <div class="overlay-header">
          <UiBadge variant="primary" size="sm">
            {{ component.component_type }}
          </UiBadge>
          <UiButton
            variant="ghost"
            size="xs"
            @click="$emit('component-interaction', component.id, 'scroll_to')"
          >
            <UiIcon name="lucide:arrow-up" :size="12" />
            Jump to content
          </UiButton>
        </div>
        
        <div class="overlay-content">
          <EnhancedComponentRenderer
            :component-type="component.component_type"
            :markdown="component.markdown"
            :component-spec="component.component_spec"
          />
        </div>
        
        <div class="overlay-footer">
          <span class="component-reasoning">{{ component.reasoning }}</span>
        </div>
      </div>
    </div>
    
    <!-- Replacement Components Info -->
    <div v-if="replacementComponents.length > 0" class="replacement-info">
      <div class="info-header">
        <UiIcon name="lucide:replace" :size="14" />
        <span>Content Enhanced ({{ replacementComponents.length }} sections)</span>
      </div>
      <div class="replacement-list">
        <div
          v-for="component in replacementComponents"
          :key="component.id"
          class="replacement-item"
        >
          <UiBadge variant="secondary" size="sm">
            {{ component.component_type }}
          </UiBadge>
          <span class="replacement-description">
            Replaced {{ component.original_content.length }} chars with enhanced {{ component.component_type }}
          </span>
        </div>
      </div>
    </div>
    
    <!-- Hybrid Components Info -->
    <div v-if="hybridComponents.length > 0" class="hybrid-info">
      <div class="info-header">
        <UiIcon name="lucide:layers" :size="14" />
        <span>Content Modified ({{ hybridComponents.length }} sections)</span>
      </div>
      <div class="hybrid-list">
        <div
          v-for="component in hybridComponents"
          :key="component.id"
          class="hybrid-item"
        >
          <UiBadge variant="outline" size="sm">
            {{ component.component_type }}
          </UiBadge>
          <span class="hybrid-description">
            Enhanced with interactive {{ component.component_type }} elements
          </span>
        </div>
      </div>
    </div>
    
    <!-- Enhancement Statistics -->
    <div v-if="components.length > 0" class="enhancement-stats">
      <div class="stats-header">
        <UiIcon name="lucide:activity" :size="12" />
        <span>Enhancement Summary</span>
      </div>
      <div class="stats-content">
        <div class="stat-item">
          <span class="stat-label">Components:</span>
          <span class="stat-value">{{ components.length }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Types:</span>
          <span class="stat-value">{{ uniqueComponentTypes.join(', ') }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">Enhancements:</span>
          <span class="stat-value">{{ uniqueEnhancementTypes.join(', ') }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EnhancedComponent } from '~/composables/useEnhancedContent'

interface Props {
  messageId: number
  enhancedContent: string
  components: EnhancedComponent[]
}

interface Emits {
  (e: 'component-interaction', componentId: string, interaction: string, data?: any): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Computed properties for different component types
const overlayComponents = computed(() => 
  props.components.filter(c => c.enhancement_type === 'overlay')
)

const replacementComponents = computed(() => 
  props.components.filter(c => c.enhancement_type === 'replace')
)

const hybridComponents = computed(() => 
  props.components.filter(c => c.enhancement_type === 'hybrid')
)

const uniqueComponentTypes = computed(() => 
  [...new Set(props.components.map(c => c.component_type))]
)

const uniqueEnhancementTypes = computed(() => 
  [...new Set(props.components.map(c => c.enhancement_type))]
)
</script>

<style scoped>
.enhanced-content-renderer {
  margin-top: 16px;
  border: 1px solid var(--border-secondary);
  border-radius: 8px;
  background: var(--bg-tertiary);
  overflow: hidden;
}

.enhanced-content {
  padding: 16px;
  background: var(--bg-primary);
}

/* Component Overlays */
.component-overlays {
  position: relative;
  padding: 12px;
  background: var(--bg-secondary);
}

.component-overlay {
  margin-bottom: 16px;
  padding: 12px;
  border: 1px solid var(--border-primary);
  border-radius: 6px;
  background: var(--bg-primary);
}

.overlay-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}

.overlay-content {
  margin-bottom: 8px;
}

.overlay-footer {
  font-size: 12px;
  color: var(--text-secondary);
  font-style: italic;
}

/* Replacement Info */
.replacement-info,
.hybrid-info {
  padding: 12px;
  border-top: 1px solid var(--border-secondary);
  background: var(--bg-secondary);
}

.info-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.replacement-list,
.hybrid-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.replacement-item,
.hybrid-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: var(--text-secondary);
}

.replacement-description,
.hybrid-description {
  flex: 1;
}

/* Enhancement Statistics */
.enhancement-stats {
  padding: 12px;
  border-top: 1px solid var(--border-secondary);
  background: var(--bg-tertiary);
}

.stats-header {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
}

.stats-content {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 11px;
}

.stat-item {
  display: flex;
  gap: 4px;
}

.stat-label {
  color: var(--text-tertiary);
}

.stat-value {
  color: var(--text-secondary);
  font-weight: 500;
}

/* Component reasoning */
.component-reasoning {
  font-size: 11px;
  color: var(--text-tertiary);
  line-height: 1.4;
}
</style>
