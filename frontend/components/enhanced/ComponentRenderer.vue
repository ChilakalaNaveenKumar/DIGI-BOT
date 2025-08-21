<template>
  <div class="component-renderer">
    <!-- Chart.js Charts -->
    <EnhancedChartJSRenderer
      v-if="(componentType === 'pie-chart' || componentType === 'bar-chart' || componentType === 'line-chart') && parsedData"
      :type="componentType.replace('-chart', '')"
      :data="parsedData"
      :title="componentTitle"
      :height="300"
    />
    
    <!-- Data Table -->
    <EnhancedDataTable
      v-else-if="componentType === 'data-table' && parsedData"
      :data="parsedData.data || parsedData.rows"
      :headers="parsedData.headers"
      :title="componentTitle"
      :page-size="5"
    />
    
    <!-- Fallback: Show raw markdown if parsing fails -->
    <div v-else class="fallback-display">
      <div class="bg-gray-100 dark:bg-gray-800 rounded-lg p-4">
        <h4 class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Component Render Error
        </h4>
        <pre class="text-xs text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ markdown }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import yaml from 'js-yaml'
interface Props {
  componentType: string
  markdown: string
  title?: string
}

const props = defineProps<Props>()

// Parse component data from markdown
const parsedData = computed(() => {
  try {
    if (!props.markdown) return null
    
    console.log('ComponentRenderer - Parsing markdown:', props.markdown)
    console.log('ComponentRenderer - Component type:', props.componentType)
    
    // Extract content between :::component-type and :::
    
    // Try multiple regex patterns to handle different markdown formats
    let contentMatch = props.markdown.match(/:::[^:\s]+\s*\n?([\s\S]*?)\n?:::/);
    
    if (!contentMatch) {
      // Try more flexible pattern
      contentMatch = props.markdown.match(/:::.*?\n([\s\S]*?):::/);
    }
    
    if (!contentMatch) {
      // Try pattern without requiring newlines
      contentMatch = props.markdown.match(/:::[^:]+\s*([\s\S]*?)\s*:::/);
    }
    
    if (!contentMatch) {
      console.warn('No regex match found for markdown:', props.markdown)
      return null
    }
    
    const content = contentMatch[1]?.trim() || ''
    console.log('ComponentRenderer - Extracted content:', content)
    
    // Try to parse as YAML first, but handle special case of long JSON arrays
    let data
    
    // Special handling for YAML with inline JSON arrays (common AI output)
    if (content.includes('data: [') && content.includes('}]')) {
      try {
        // Extract title and data separately
        const lines = content.split('\n')
        let title = ''
        let dataLine = ''
        
        for (const line of lines) {
          if (line.startsWith('title:')) {
            title = line.replace('title:', '').trim()
          } else if (line.startsWith('data:')) {
            dataLine = line.replace('data:', '').trim()
          }
        }
        
        if (dataLine) {
          const parsedData = JSON.parse(dataLine)
          data = { title, data: parsedData }
          console.log('ComponentRenderer - Parsed as manual YAML+JSON:', data)
        }
      } catch (manualError) {
        console.log('ComponentRenderer - Manual parsing failed, trying standard YAML:', manualError)
        // Fall back to standard YAML parsing
        try {
          data = yaml.load(content) as Record<string, unknown>
          console.log('ComponentRenderer - Parsed as YAML:', data)
        } catch (yamlError) {
          console.log('ComponentRenderer - YAML parsing failed, trying JSON:', yamlError)
          try {
            data = JSON.parse(content)
            console.log('ComponentRenderer - Parsed as JSON:', data)
          } catch {
            // Try to fix common JSON issues
            let fixedContent = content
            
            // If content starts with a property like "data": [...], wrap it in braces
            if (content.match(/^\s*"[^"]+"\s*:/)) {
              fixedContent = `{${content}}`
              
              try {
                data = JSON.parse(fixedContent)
                console.log('ComponentRenderer - Parsed as fixed JSON:', data)
              } catch {
                console.warn('Could not parse component data as JSON or YAML:', content)
                return null
              }
            } else {
              console.warn('Could not parse component data:', content)
              return null
            }
          }
        }
      }
    } else {
      // Standard YAML parsing for simple cases
      try {
        data = yaml.load(content) as Record<string, unknown>
        console.log('ComponentRenderer - Parsed as standard YAML:', data)
      } catch (yamlError) {
        console.log('ComponentRenderer - Standard YAML parsing failed:', yamlError)
        return null
      }
    }
    
    // Transform data based on component type
    switch (props.componentType) {
      case 'pie-chart':
        // AI can return either array directly or object with data property
        if (Array.isArray(data)) {
          console.log('ComponentRenderer - Returning direct array:', data)
          return data
        } else if (data.data && Array.isArray(data.data)) {
          console.log('ComponentRenderer - Returning data.data array:', data.data)
          return data.data
        }
        console.log('ComponentRenderer - No valid data found for pie-chart:', data)
        return null
        
      case 'bar-chart':
        // AI can return either array directly or object with data property
        if (Array.isArray(data)) {
          return data
        } else if (data.data && Array.isArray(data.data)) {
          return data.data
        }
        return null
        
      case 'line-chart':
        // AI returns object with series: {"data": [{"name": "Traffic", "data": [...]}]}
        if (data.data && Array.isArray(data.data)) {
          return data.data
        }
        // Fallback: if it's just an array, wrap it
        if (Array.isArray(data)) {
          return [{
            name: 'Series 1',
            data: data
          }]
        }
        return null
        
      case 'data-table':
        // AI returns object with headers and rows: {"headers": [...], "rows": [...]}
        if (data.headers && data.rows) {
          return {
            headers: data.headers.map((header: string, index: number) => ({
              key: `col_${index}`,
              label: header,
              type: 'text'
            })),
            data: data.rows.map((row: unknown[]) => {
              const rowObj: Record<string, unknown> = {}
              row.forEach((cell, index) => {
                rowObj[`col_${index}`] = cell
              })
              return rowObj
            })
          }
        }
        return null
        
      default:
        return data
    }
  } catch (error) {
    console.error('Error parsing component data:', error, 'for markdown:', props.markdown)
    return null
  }
})

// Extract title from markdown if present
const componentTitle = computed(() => {
  if (props.title) return props.title
  
  // Try to extract title from JSON in markdown
  try {
    const contentMatch = props.markdown.match(/:::[^:\s]+\s*\n?([\s\S]*?)\n?:::/);
    if (contentMatch) {
      const content = contentMatch[1]?.trim() || ''
      const data = JSON.parse(content)
      if (data.title) return data.title
    }
  } catch {
    // Fallback to regex pattern
    const titleMatch = props.markdown.match(/title:\s*"([^"]+)"/);
    if (titleMatch) return titleMatch[1]
  }
  
  // Default titles based on component type
  const defaultTitles = {
    'pie-chart': 'Data Distribution',
    'bar-chart': 'Comparison Chart',
    'line-chart': 'Trend Analysis',
    'data-table': 'Data Table'
  }
  
  return defaultTitles[props.componentType as keyof typeof defaultTitles] || 'Chart'
})
</script>

<style scoped>
@reference "tailwindcss";
.component-renderer {
  width: 100%;
}

.fallback-display {
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1rem;
  background-color: #fef2f2;
}
</style>
