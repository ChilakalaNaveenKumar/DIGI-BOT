import { ref } from 'vue'

/**
 * Simple Keyword-Based Content Router
 * No complex parsing - just look for keywords that AI models return
 */
export const useSimpleContentRouter = () => {
  const activeStreams = ref(new Map())

  /**
   * Content type keywords that AI models return
   */
  const contentKeywords = {
    // Thinking/Reasoning
    thinking: [
      'DIGI_THINKING_START',
      'DIGI_ANALYSIS_START', 
      '🔍 DIGI_THINKING_START',
      '🧠 DIGI_ANALYSIS_START',
      'Let me think',
      'Analysis:',
      'Step by step:'
    ],
    
    // Code blocks
    code: [
      'DIGI_CODE_START',
      '💻 DIGI_CODE_START',
      '```',
      'Here\'s the code:',
      'Code solution:'
    ],
    
    // Diagrams
    diagram: [
      'DIGI_DIAGRAM_START',
      '📊 DIGI_DIAGRAM_START',
      'Here\'s the diagram:',
      'Mermaid diagram:',
      'Flowchart:',
      'Venn diagram:',
      'graph TD',
      'graph LR',
      'sequenceDiagram',
      '```mermaid'
    ],
    
    // JSON data
    json: [
      'DIGI_JSON_START',
      '📋 DIGI_JSON_START',
      'JSON response:',
      'Data structure:',
      'API response:'
    ],
    
    // Tables
    table: [
      'DIGI_TABLE_START',
      '📈 DIGI_TABLE_START',
      'Here\'s the table:',
      'Data table:',
      'Comparison table:'
    ],
    
    // Search results
    search: [
      'DIGI_SEARCH_START',
      '🔍 DIGI_SEARCH_START',
      'Search results:',
      'Current information:',
      'Live data:',
      'According to recent'
    ],
    
    // Tool results
    tool: [
      'DIGI_TOOL_START',
      '🔧 DIGI_TOOL_START',
      'Tool result:',
      'Calculation result:',
      'Analysis complete:'
    ]
  }

  /**
   * Component mapping for each content type
   */
  const componentMap = {
    thinking: 'DigiSetuThoughtProcess',
    code: 'DigiSetuCodeBlock',
    diagram: 'DigiSetuDiagram',
    json: 'DigiSetuJsonViewer', 
    table: 'DigiSetuTable',
    search: 'DigiSetuSearchResults',
    tool: 'DigiSetuToolResult',
    text: 'DigiSetuText' // Default
  }

  /**
   * Simple keyword detection - no complex parsing!
   */
  const detectContentType = (content) => {
    if (!content || typeof content !== 'string') {
      return { type: 'text', confidence: 0.5, keyword: null }
    }

    const lowerContent = content.toLowerCase()

    // Check each content type for keywords
    for (const [type, keywords] of Object.entries(contentKeywords)) {
      for (const keyword of keywords) {
        if (lowerContent.includes(keyword.toLowerCase())) {
          return {
            type,
            confidence: 1.0, // 100% confidence with keywords
            keyword,
            component: componentMap[type]
          }
        }
      }
    }

    // Special cases for common patterns
    
    // Code block detection (highest priority)
    if (content.includes('```') || /```[\w]*\n/.test(content)) {
      return { type: 'code', confidence: 0.9, keyword: 'code_block', component: componentMap.code }
    }
    
    // JSON detection
    if (content.trim().startsWith('{') || content.trim().startsWith('[')) {
      try {
        // Try to parse a reasonable portion to validate
        const trimmed = content.trim()
        const testContent = trimmed.length > 1000 ? trimmed.substring(0, 1000) + '}' : trimmed
        JSON.parse(testContent)
        return { type: 'json', confidence: 0.8, keyword: 'json_start', component: componentMap.json }
      } catch (e) {
        // Not valid JSON, continue
      }
    }

    // Table detection (markdown tables)
    if (content.includes('|') && content.includes('---')) {
      return { type: 'table', confidence: 0.7, keyword: 'table_pattern', component: componentMap.table }
    }

    // Default to text
    return { type: 'text', confidence: 0.5, keyword: null, component: componentMap.text }
  }

  /**
   * Route content using simple keyword detection
   */
  const routeContent = (chunk, streamId = 'default') => {
    // Get or create stream
    const stream = activeStreams.value.get(streamId) || {
      buffer: '',
      currentType: 'text',
      currentComponent: 'DigiSetuText',
      confidence: 0.5,
      isComplete: false
    }

    // Append new content
    const newContent = chunk.content || ''
    stream.buffer += newContent

    // Detect content type using keywords
    const detection = detectContentType(stream.buffer)

    // Update stream if we found a better match
    if (detection.confidence > stream.confidence) {
      stream.currentType = detection.type
      stream.currentComponent = detection.component
      stream.confidence = detection.confidence
    }

    // Update stream
    activeStreams.value.set(streamId, stream)

    return {
      component: stream.currentComponent,
      content: stream.buffer,
      contentType: stream.currentType,
      confidence: stream.confidence,
      keyword: detection.keyword,
      isStreaming: !stream.isComplete,
      streamId
    }
  }

  /**
   * Clean content by removing keywords
   */
  const cleanContent = (content) => {
    if (!content) return content

    // Remove our detection keywords from display
    let cleaned = content

    // Remove all DIGI_*_START keywords
    cleaned = cleaned.replace(/🔍 DIGI_THINKING_START\n?/g, '')
    cleaned = cleaned.replace(/🧠 DIGI_ANALYSIS_START\n?/g, '')
    cleaned = cleaned.replace(/💻 DIGI_CODE_START\n?/g, '')
    cleaned = cleaned.replace(/📊 DIGI_DIAGRAM_START\n?/g, '')
    cleaned = cleaned.replace(/📋 DIGI_JSON_START\n?/g, '')
    cleaned = cleaned.replace(/📈 DIGI_TABLE_START\n?/g, '')
    cleaned = cleaned.replace(/🔍 DIGI_SEARCH_START\n?/g, '')
    cleaned = cleaned.replace(/🔧 DIGI_TOOL_START\n?/g, '')

    // Remove plain DIGI keywords
    cleaned = cleaned.replace(/DIGI_\w+_START\n?/g, '')

    return cleaned.trim()
  }

  /**
   * Mark stream as complete
   */
  const completeStream = (streamId) => {
    const stream = activeStreams.value.get(streamId)
    if (stream) {
      stream.isComplete = true
      activeStreams.value.set(streamId, stream)
    }
  }

  /**
   * Clear stream
   */
  const clearStream = (streamId) => {
    activeStreams.value.delete(streamId)
  }

  return {
    routeContent,
    detectContentType,
    cleanContent,
    completeStream,
    clearStream,
    contentKeywords,
    componentMap
  }
}
