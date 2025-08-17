<template>
  <div class="ds-progressive-table-container" :style="cssVariables">
    <!-- Table Controls -->
    <div v-if="customSettings.showControls && showControls" class="ds-table-controls">
      <div class="ds-control-group">
        <button 
          @click="toggleAnimation" 
          class="ds-control-btn"
          :class="{ 'active': animationsEnabled }"
        >
          <Zap class="w-4 h-4" />
          {{ animationsEnabled ? 'Disable' : 'Enable' }} Animation
        </button>
        
        <button 
          @click="completeRendering" 
          class="ds-control-btn"
          v-if="isRendering"
        >
          <FastForward class="w-4 h-4" />
          Complete Now
        </button>
      </div>
      
      <div class="ds-progress-indicator" v-if="isRendering">
        <div class="ds-progress-bar">
          <div 
            class="ds-progress-fill" 
            :style="{ width: `${progressPercentage}%` }"
          ></div>
        </div>
        <span class="ds-progress-text">
          {{ itemsRendered }}/{{ totalItems }} rows
        </span>
      </div>
    </div>

    <!-- Search -->
    <div v-if="searchable && hasContent" class="ds-table-search">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Search table..."
        class="ds-search-input"
      />
    </div>

    <!-- Main Table -->
    <div class="ds-table-wrapper">
      <!-- Loading State -->
      <div v-if="!hasContent" class="ds-table-loading">
        <div class="ds-loading-skeleton">
          <div class="ds-skeleton-header"></div>
          <div class="ds-skeleton-row" v-for="n in 3" :key="n"></div>
        </div>
      </div>

      <!-- Progressive Table -->
      <table v-else class="ds-table" :class="tableClasses">
        <!-- Headers (always visible once detected) -->
        <thead v-if="tableHeaders.length > 0">
          <tr class="ds-header-row">
            <th
              v-for="(header, index) in tableHeaders"
              :key="`header-${index}`"
              :class="{ 'ds-sortable': sortable }"
              @click="sortable ? sortBy(index) : null"
              class="ds-table-header"
            >
              {{ header }}
              <ChevronUp v-if="sortable && sortColumn === index && sortDirection === 'asc'" class="w-4 h-4 inline ml-1" />
              <ChevronDown v-if="sortable && sortColumn === index && sortDirection === 'desc'" class="w-4 h-4 inline ml-1" />
            </th>
          </tr>
        </thead>

        <!-- Progressive Body -->
        <tbody>
          <!-- Rendered Rows -->
          <tr
            v-for="(row, rowIndex) in filteredVisibleRows"
            :key="row.id || `row-${rowIndex}`"
            class="ds-table-row"
            :class="getRowClasses(row, rowIndex)"
            :style="getRowAnimationStyle(rowIndex)"
          >
            <td
              v-for="(cell, cellIndex) in row.cells || []"
              :key="`${row.id}-cell-${cellIndex}`"
              class="ds-table-cell"
              :class="getCellClasses(cell, cellIndex, rowIndex)"
            >
              {{ cell }}
            </td>
            
            <!-- Fill empty cells if row is incomplete -->
            <td
              v-for="n in Math.max(0, tableHeaders.length - (row.cells?.length || 0))"
              :key="`${row.id}-empty-${n}`"
              class="ds-table-cell ds-empty-cell"
            >
              <div class="ds-cell-placeholder" v-if="isStreaming">...</div>
            </td>
          </tr>

          <!-- Painting Row (current row being streamed) -->
          <tr v-if="isStreaming && currentPaintingRow" class="ds-table-row ds-painting-row">
            <td
              v-for="(cell, cellIndex) in currentPaintingRow.cells || []"
              :key="`painting-cell-${cellIndex}`"
              class="ds-table-cell ds-painting-cell"
            >
              <span class="ds-painting-content">{{ cell }}</span>
              <span class="ds-painting-cursor">█</span>
            </td>
            
            <!-- Placeholder cells for incomplete painting row -->
            <td
              v-for="n in Math.max(0, tableHeaders.length - (currentPaintingRow.cells?.length || 0))"
              :key="`painting-placeholder-${n}`"
              class="ds-table-cell ds-placeholder-cell"
            >
              <div class="ds-painting-indicator">
                <div class="ds-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </td>
          </tr>

          <!-- Empty State -->
          <tr v-if="!isStreaming && visibleItems.length === 0" class="ds-empty-row">
            <td :colspan="tableHeaders.length || 1" class="ds-empty-cell">
              <div class="ds-empty-state">
                <Table class="w-8 h-8 text-gray-400" />
                <p>No table data available</p>
              </div>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Raw Content Fallback -->
      <div v-if="renderingError && !canRender" class="ds-fallback-content">
        <div class="ds-fallback-header">
          <AlertTriangle class="w-4 h-4" />
          <span>Displaying raw content</span>
        </div>
        <pre class="ds-raw-content">{{ rawContent }}</pre>
      </div>
    </div>

    <!-- Table Stats -->
    <div v-if="hasContent && customSettings.showStats && showStats" class="ds-table-stats">
      <span>{{ totalItems }} rows</span>
      <span v-if="tableHeaders.length">{{ tableHeaders.length }} columns</span>
      <span v-if="searchQuery">{{ filteredVisibleRows.length }} filtered</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { 
  ChevronUp, 
  ChevronDown, 
  Table, 
  AlertTriangle, 
  Zap, 
  FastForward 
} from 'lucide-vue-next'
import { useProgressiveRenderer } from '@/composables/useProgressiveRenderer'
import { useComponentCustomization } from '@/composables/useComponentCustomization'

const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isStreaming: {
    type: Boolean,
    default: false
  },
  sortable: {
    type: Boolean,
    default: true
  },
  searchable: {
    type: Boolean,
    default: true
  },
  showControls: {
    type: Boolean,
    default: true
  },
  showStats: {
    type: Boolean,
    default: true
  },
  animationDelay: {
    type: Number,
    default: 100
  },
  chunkSize: {
    type: Number,
    default: 3
  }
})

// Component customization
const { getTableSettings, cssVariables, initialize: initCustomization } = useComponentCustomization()
initCustomization()

// Get customized settings
const customSettings = computed(() => getTableSettings('progressive-table'))

// Progressive renderer
const { createProgressiveRenderer } = useProgressiveRenderer()
const renderer = createProgressiveRenderer('table', {
  chunkSize: customSettings.value.chunkSize || props.chunkSize,
  renderDelay: customSettings.value.renderDelay || props.animationDelay,
  enableAnimations: customSettings.value.animationsEnabled && true,
  fallbackMode: 'graceful'
})

// Destructure renderer state and methods
const {
  rawContent,
  parsedContent,
  visibleItems,
  renderProgress,
  isRendering,
  renderingError,
  hasContent,
  canRender,
  progressPercentage,
  itemsRendered,
  totalItems,
  updateContent,
  completeRendering: rendererCompleteRendering,
  stopRendering
} = renderer

// Local state
const searchQuery = ref('')
const sortColumn = ref(null)
const sortDirection = ref('asc')
const animationsEnabled = ref(true)

// Computed properties
const tableHeaders = computed(() => {
  return parsedContent.value?.headers || []
})

const tableClasses = computed(() => {
  return {
    'ds-table-streaming': props.isStreaming,
    'ds-table-animated': animationsEnabled.value,
    'ds-table-sorting': sortColumn.value !== null
  }
})

const currentPaintingRow = computed(() => {
  if (!props.isStreaming || !parsedContent.value) return null
  
  // Get the row that's currently being painted (last incomplete row)
  const allRows = parsedContent.value.rows || []
  const lastRow = allRows[allRows.length - 1]
  
  if (lastRow && (!lastRow.cells || lastRow.cells.length < tableHeaders.value.length)) {
    return lastRow
  }
  
  return null
})

const filteredVisibleRows = computed(() => {
  let rows = [...visibleItems.value]
  
  // Apply search filter
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    rows = rows.filter(row => 
      row.cells?.some(cell => 
        String(cell).toLowerCase().includes(query)
      )
    )
  }
  
  // Apply sorting
  if (sortColumn.value !== null && tableHeaders.value.length > 0) {
    rows.sort((a, b) => {
      const aVal = String(a.cells?.[sortColumn.value] || '')
      const bVal = String(b.cells?.[sortColumn.value] || '')
      
      const comparison = aVal.localeCompare(bVal, undefined, { numeric: true })
      return sortDirection.value === 'asc' ? comparison : -comparison
    })
  }
  
  return rows
})

// Methods
const sortBy = (columnIndex) => {
  if (sortColumn.value === columnIndex) {
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortColumn.value = columnIndex
    sortDirection.value = 'asc'
  }
}

const toggleAnimation = () => {
  animationsEnabled.value = !animationsEnabled.value
}

const completeRendering = () => {
  rendererCompleteRendering()
}

const getRowClasses = (row, index) => {
  return {
    'ds-row-even': index % 2 === 0,
    'ds-row-odd': index % 2 === 1,
    'ds-row-new': animationsEnabled.value && isRendering.value
  }
}

const getCellClasses = (cell, cellIndex, rowIndex) => {
  return {
    'ds-cell-empty': !cell || cell === '',
    'ds-cell-numeric': !isNaN(cell) && cell !== '',
    'ds-cell-header': cellIndex === 0
  }
}

const getRowAnimationStyle = (index) => {
  if (!animationsEnabled.value || !isRendering.value) return {}
  
  return {
    animationDelay: `${index * 50}ms`,
    animationDuration: '0.3s'
  }
}

// Watch for content changes
watch(() => props.content, (newContent) => {
  updateContent(newContent, props.isStreaming)
}, { immediate: true })

watch(() => props.isStreaming, (streaming) => {
  if (streaming) {
    updateContent(props.content, true)
  } else {
    // Complete rendering when streaming stops
    setTimeout(() => {
      completeRendering()
    }, 500)
  }
})

// Lifecycle
onMounted(() => {
  updateContent(props.content, props.isStreaming)
})
</script>

<style scoped>
.ds-progressive-table-container {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-lg);
  overflow: hidden;
}

/* === CONTROLS === */
.ds-table-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-bottom: 1px solid var(--ds-border-primary);
}

.ds-control-group {
  display: flex;
  gap: var(--ds-space-2);
}

.ds-control-btn {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-2) var(--ds-space-3);
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
  cursor: pointer;
  transition: all var(--ds-transition-fast);
}

.ds-control-btn:hover {
  background: var(--ds-surface-hover);
}

.ds-control-btn.active {
  background: var(--ds-primary);
  color: white;
  border-color: var(--ds-primary);
}

.ds-progress-indicator {
  display: flex;
  align-items: center;
  gap: var(--ds-space-3);
}

.ds-progress-bar {
  width: 120px;
  height: 4px;
  background: var(--ds-border-primary);
  border-radius: var(--ds-radius-full);
  overflow: hidden;
}

.ds-progress-fill {
  height: 100%;
  background: var(--ds-primary);
  transition: width var(--ds-transition-fast);
}

.ds-progress-text {
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
  min-width: 80px;
}

/* === SEARCH === */
.ds-table-search {
  padding: var(--ds-space-3);
  border-bottom: 1px solid var(--ds-border-primary);
  background: var(--ds-surface-secondary);
}

.ds-search-input {
  width: 100%;
  padding: var(--ds-space-2) var(--ds-space-3);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  background: var(--ds-surface-primary);
  color: var(--ds-text-primary);
  font-size: var(--ds-text-sm);
}

.ds-search-input:focus {
  outline: none;
  border-color: var(--ds-primary);
  box-shadow: 0 0 0 3px color-mix(in srgb, var(--ds-primary) 10%, transparent);
}

/* === TABLE === */
.ds-table-wrapper {
  overflow-x: auto;
  max-height: 500px;
  overflow-y: auto;
}

.ds-table {
  width: 100%;
  border-collapse: collapse;
}

.ds-table-header {
  background: var(--ds-surface-secondary);
  color: var(--ds-text-primary);
  font-weight: var(--ds-font-medium);
  padding: var(--ds-space-3);
  text-align: left;
  border-bottom: 1px solid var(--ds-border-primary);
  position: sticky;
  top: 0;
  z-index: 1;
}

.ds-table-header.ds-sortable {
  cursor: pointer;
  user-select: none;
  transition: background-color var(--ds-transition-fast);
}

.ds-table-header.ds-sortable:hover {
  background: var(--ds-surface-tertiary);
}

.ds-table-cell {
  padding: var(--ds-space-3);
  border-bottom: 1px solid var(--ds-border-secondary);
  color: var(--ds-text-primary);
  vertical-align: top;
}

.ds-table-row:hover {
  background: var(--ds-surface-secondary);
}

/* === PROGRESSIVE RENDERING === */
.ds-table-animated .ds-table-row {
  animation: fadeInUp 0.3s ease-out forwards;
  opacity: 0;
  transform: translateY(10px);
}

@keyframes fadeInUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.ds-painting-row {
  background: color-mix(in srgb, var(--ds-primary) 5%, var(--ds-surface-primary));
}

.ds-painting-cell {
  position: relative;
}

.ds-painting-content {
  display: inline;
}

.ds-painting-cursor {
  display: inline;
  color: var(--ds-primary);
  animation: blink 1s infinite;
  margin-left: 2px;
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.ds-placeholder-cell {
  opacity: 0.5;
}

.ds-painting-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 20px;
}

.ds-dots {
  display: flex;
  gap: 4px;
}

.ds-dots span {
  width: 4px;
  height: 4px;
  border-radius: 50%;
  background: var(--ds-primary);
  animation: dotPulse 1.4s infinite ease-in-out;
}

.ds-dots span:nth-child(1) { animation-delay: -0.32s; }
.ds-dots span:nth-child(2) { animation-delay: -0.16s; }

@keyframes dotPulse {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

.ds-empty-cell {
  color: var(--ds-text-muted);
  font-style: italic;
}

.ds-cell-placeholder {
  color: var(--ds-text-muted);
  animation: pulse 2s infinite;
}

/* === LOADING === */
.ds-table-loading {
  padding: var(--ds-space-4);
}

.ds-loading-skeleton {
  animation: pulse 2s infinite;
}

.ds-skeleton-header {
  height: 40px;
  background: var(--ds-surface-secondary);
  border-radius: var(--ds-radius-md);
  margin-bottom: var(--ds-space-2);
}

.ds-skeleton-row {
  height: 32px;
  background: var(--ds-surface-tertiary);
  border-radius: var(--ds-radius-sm);
  margin-bottom: var(--ds-space-1);
}

/* === EMPTY STATE === */
.ds-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--ds-space-2);
  padding: var(--ds-space-6);
  color: var(--ds-text-muted);
}

/* === FALLBACK === */
.ds-fallback-content {
  padding: var(--ds-space-4);
  background: var(--ds-surface-secondary);
}

.ds-fallback-header {
  display: flex;
  align-items: center;
  gap: var(--ds-space-2);
  margin-bottom: var(--ds-space-3);
  color: var(--ds-warning);
  font-weight: var(--ds-font-medium);
}

.ds-raw-content {
  background: var(--ds-surface-primary);
  border: 1px solid var(--ds-border-primary);
  border-radius: var(--ds-radius-md);
  padding: var(--ds-space-3);
  font-family: var(--ds-font-mono);
  font-size: var(--ds-text-sm);
  white-space: pre-wrap;
  overflow-x: auto;
}

/* === STATS === */
.ds-table-stats {
  display: flex;
  gap: var(--ds-space-4);
  padding: var(--ds-space-3);
  background: var(--ds-surface-secondary);
  border-top: 1px solid var(--ds-border-primary);
  font-size: var(--ds-text-sm);
  color: var(--ds-text-muted);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
  .ds-table-controls {
    flex-direction: column;
    gap: var(--ds-space-3);
    align-items: stretch;
  }
  
  .ds-progress-indicator {
    justify-content: space-between;
  }
  
  .ds-table-header,
  .ds-table-cell {
    padding: var(--ds-space-2);
    font-size: var(--ds-text-sm);
  }
  
  .ds-table-wrapper {
    max-height: 400px;
  }
}
</style>
