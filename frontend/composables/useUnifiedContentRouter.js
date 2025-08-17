import { ref, computed } from 'vue'

/**
 * Unified Content Router
 * 
 * Combines the best of both routing systems:
 * - Simple keyword detection (reliable)
 * - Progressive rendering support (smooth UX)
 * - Fallback mechanisms (robust)
 */
export const useUnifiedContentRouter = () => {
  const activeStreams = ref(new Map())

  /**
   * Primary content detection keywords (highest priority)
   * These are injected by the AI system for reliable routing
   */
  const primaryKeywords = {
    thinking: [
      'DIGI_THINKING_START',
      'DIGI_ANALYSIS_START',
      '🔍 DIGI_THINKING_START',
      '🧠 DIGI_ANALYSIS_START',
      '⚡ DIGI_EXECUTION_START',
      '✅ DIGI_QUALITY_START',
      '🎯 DIGI_COMPLETION_START'
    ],
    code: [
      'DIGI_CODE_START',
      '💻 DIGI_CODE_START'
    ],
    diagram: [
      'DIGI_DIAGRAM_START',
      '📊 DIGI_DIAGRAM_START'
    ],
    json: [
      'DIGI_JSON_START',
      '📋 DIGI_JSON_START'
    ],
    table: [
      'DIGI_TABLE_START',
      '📈 DIGI_TABLE_START'
    ],
    search: [
      'DIGI_SEARCH_START',
      '🔍 DIGI_SEARCH_START'
    ],
    tool: [
      'DIGI_TOOL_START',
      '🔧 DIGI_TOOL_START'
    ],
    vision: [
      'DIGI_VISION_START',
      '👁️ DIGI_VISION_START',
      '📷 DIGI_IMAGE_ANALYSIS_START'
    ],
    audio: [
      'DIGI_AUDIO_START',
      '🎵 DIGI_AUDIO_START',
      '🎤 DIGI_TRANSCRIPTION_START'
    ]
  }

  /**
   * End keywords for content sections
   */
  const endKeywords = {
    code: [
      'DIGI_CODE_END',
      '💻 DIGI_CODE_END'
    ],
    diagram: [
      'DIGI_DIAGRAM_END',
      '📊 DIGI_DIAGRAM_END'
    ],
    json: [
      'DIGI_JSON_END',
      '📋 DIGI_JSON_END'
    ],
    table: [
      'DIGI_TABLE_END',
      '📈 DIGI_TABLE_END'
    ],
    search: [
      'DIGI_SEARCH_END',
      '🔍 DIGI_SEARCH_END'
    ],
    tool: [
      'DIGI_TOOL_END',
      '🔧 DIGI_TOOL_END'
    ],
    vision: [
      'DIGI_VISION_END',
      '👁️ DIGI_VISION_END',
      '📷 DIGI_IMAGE_ANALYSIS_END'
    ],
    audio: [
      'DIGI_AUDIO_END',
      '🎵 DIGI_AUDIO_END',
      '🎤 DIGI_TRANSCRIPTION_END'
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
    vision: 'DigiSetuVisionRenderer',
    audio: 'DigiSetuAudioRenderer',
    text: 'DigiSetuText' // Default fallback
  }

  /**
   * Route content with unified detection system
   */
  const routeContent = (chunk, streamId = 'default') => {
    // Get or create stream
    const stream = activeStreams.value.get(streamId) || {
      buffer: '',
      currentType: 'text',
      currentComponent: 'DigiSetuText',
      confidence: 0.0,
      isComplete: false,
      detectionHistory: [],
      progressiveData: {
        tableRows: [],
        codeBlocks: [],
        jsonObjects: [],
        diagramElements: []
      }
    }

    // Handle content properly - don't duplicate
    const newContent = chunk.content || ''
    
    // If this is the full content (not incremental), replace buffer
    if (!chunk.isStreaming || newContent.includes(stream.buffer)) {
      stream.buffer = newContent
    } else {
      // Only append if it's truly new content
      stream.buffer += newContent
    }

    // Primary detection: Look for AI-injected keywords first
    const primaryDetection = detectPrimaryKeywords(stream.buffer)
    
    // Secondary detection: Pattern-based fallback
    const secondaryDetection = detectContentPatterns(stream.buffer)
    
    // Choose the best detection result
    const finalDetection = chooseBestDetection(primaryDetection, secondaryDetection, stream)

    // Update stream with detection results
    if (finalDetection.confidence > stream.confidence) {
      stream.currentType = finalDetection.type
      stream.currentComponent = finalDetection.component
      stream.confidence = finalDetection.confidence
      
      // Track detection history for debugging
      stream.detectionHistory.push({
        type: finalDetection.type,
        confidence: finalDetection.confidence,
        method: finalDetection.method,
        timestamp: Date.now()
      })
    }

    // Progressive rendering: Extract incremental data
    updateProgressiveData(stream, newContent, finalDetection.type)

    // Update stream
    activeStreams.value.set(streamId, stream)

    return {
      // Core routing info
      component: stream.currentComponent,
      content: stream.buffer,
      contentType: stream.currentType,
      confidence: stream.confidence,
      
      // Progressive rendering data
      progressiveData: stream.progressiveData,
      
      // Stream management
      isStreaming: !stream.isComplete,
      streamId,
      
      // Debug info
      detectionHistory: stream.detectionHistory,
      cleanContent: cleanContentForDisplay(stream.buffer, stream.currentType)
    }
  }

  /**
   * Primary keyword detection (most reliable)
   */
  const detectPrimaryKeywords = (content) => {
    if (!content || typeof content !== 'string') {
      return { type: 'text', confidence: 0.0, method: 'fallback' }
    }

    const lowerContent = content.toLowerCase()

    // Check each content type for primary keywords
    for (const [type, keywords] of Object.entries(primaryKeywords)) {
      for (const keyword of keywords) {
        if (lowerContent.includes(keyword.toLowerCase())) {
          return {
            type,
            confidence: 1.0, // 100% confidence with primary keywords
            method: 'primary_keyword',
            keyword,
            component: componentMap[type]
          }
        }
      }
    }

    return { type: 'text', confidence: 0.0, method: 'no_primary_match' }
  }

  /**
   * Pattern-based detection (fallback)
   */
  const detectContentPatterns = (content) => {
    if (!content || typeof content !== 'string') {
      return { type: 'text', confidence: 0.0, method: 'fallback' }
    }

    // Code block detection (highest priority pattern)
    if (content.includes('```')) {
      const codeMatch = content.match(/```(\w*)\n([\s\S]*?)(?:\n```|$)/)
      if (codeMatch) {
        return {
          type: 'code',
          confidence: 0.9,
          method: 'pattern_code_complete',
          language: codeMatch[1] || 'text',
          component: componentMap.code
        }
      } else if (content.includes('```')) {
        // Incomplete code block
        return {
          type: 'code',
          confidence: 0.7,
          method: 'pattern_code_incomplete',
          component: componentMap.code
        }
      }
    }

    // Mermaid diagram detection
    const diagramKeywords = ['graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram']
    const firstLine = content.split('\n')[0].toLowerCase()
    if (diagramKeywords.some(keyword => firstLine.includes(keyword))) {
      return {
        type: 'diagram',
        confidence: 0.8,
        method: 'pattern_diagram',
        component: componentMap.diagram
      }
    }

    // JSON detection
    const trimmed = content.trim()
    if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
      try {
        // Try to parse a reasonable portion
        const testContent = trimmed.length > 1000 ? trimmed.substring(0, 1000) + '}' : trimmed
        JSON.parse(testContent)
        return {
          type: 'json',
          confidence: 0.8,
          method: 'pattern_json_valid',
          component: componentMap.json
        }
      } catch (e) {
        // Might be incomplete JSON during streaming
        if (trimmed.length > 10) {
          return {
            type: 'json',
            confidence: 0.4,
            method: 'pattern_json_incomplete',
            component: componentMap.json
          }
        }
      }
    }

    // Table detection (markdown tables)
    if (content.includes('|') && content.includes('---')) {
      const lines = content.split('\n')
      const tableLines = lines.filter(line => line.includes('|'))
      if (tableLines.length >= 2) {
        return {
          type: 'table',
          confidence: 0.7,
          method: 'pattern_table',
          component: componentMap.table
        }
      }
    }

    // Default to text
    return {
      type: 'text',
      confidence: 0.5,
      method: 'pattern_default',
      component: componentMap.text
    }
  }

  /**
   * Choose the best detection result from multiple methods
   */
  const chooseBestDetection = (primary, secondary, stream) => {
    // Primary keywords always win (AI-injected, most reliable)
    if (primary.confidence >= 1.0) {
      return primary
    }

    // If we have a strong pattern match and no primary match
    if (secondary.confidence >= 0.8 && primary.confidence === 0.0) {
      return secondary
    }

    // If we already have a confident detection, don't change unless new detection is much better
    if (stream.confidence >= 0.7 && secondary.confidence < stream.confidence + 0.2) {
      return {
        type: stream.currentType,
        confidence: stream.confidence,
        method: 'stability_preference',
        component: stream.currentComponent
      }
    }

    // Choose the higher confidence option
    return primary.confidence >= secondary.confidence ? primary : secondary
  }

  /**
   * Update progressive rendering data as content streams in
   */
  const updateProgressiveData = (stream, newContent, contentType) => {
    if (!newContent) return

    switch (contentType) {
      case 'table':
        updateProgressiveTable(stream, newContent)
        break
      case 'code':
        updateProgressiveCode(stream, newContent)
        break
      case 'json':
        updateProgressiveJson(stream, newContent)
        break
      case 'diagram':
        updateProgressiveDiagram(stream, newContent)
        break
    }
  }

  /**
   * Update progressive table data
   */
  const updateProgressiveTable = (stream, newContent) => {
    const lines = stream.buffer.split('\n')
    const tableLines = lines.filter(line => line.includes('|') && line.trim() !== '')
    
    // Extract headers (first table line)
    if (tableLines.length > 0 && !stream.progressiveData.tableHeaders) {
      const headerLine = tableLines[0]
      stream.progressiveData.tableHeaders = headerLine
        .split('|')
        .map(h => h.trim())
        .filter(h => h)
    }

    // Extract rows (skip header and separator)
    const dataLines = tableLines.slice(2) // Skip header and separator
    stream.progressiveData.tableRows = dataLines.map(line => 
      line.split('|').map(cell => cell.trim()).filter(cell => cell)
    )
  }

  /**
   * Update progressive code data
   */
  const updateProgressiveCode = (stream, newContent) => {
    const codeMatch = stream.buffer.match(/```(\w*)\n([\s\S]*?)(?:\n```|$)/)
    if (codeMatch) {
      stream.progressiveData.codeLanguage = codeMatch[1] || 'text'
      stream.progressiveData.codeContent = codeMatch[2]
      stream.progressiveData.codeComplete = stream.buffer.includes('\n```')
    }
  }

  /**
   * Update progressive JSON data
   */
  const updateProgressiveJson = (stream, newContent) => {
    try {
      const parsed = JSON.parse(stream.buffer.trim())
      stream.progressiveData.jsonValid = true
      stream.progressiveData.jsonData = parsed
      stream.progressiveData.jsonComplete = true
    } catch (e) {
      stream.progressiveData.jsonValid = false
      stream.progressiveData.jsonComplete = false
      // Try to extract partial structure
      stream.progressiveData.jsonPreview = stream.buffer.trim().substring(0, 200)
    }
  }

  /**
   * Update progressive diagram data
   */
  const updateProgressiveDiagram = (stream, newContent) => {
    const lines = stream.buffer.split('\n')
    const firstLine = lines[0].toLowerCase()
    
    if (firstLine.includes('graph')) {
      stream.progressiveData.diagramType = 'flowchart'
    } else if (firstLine.includes('sequence')) {
      stream.progressiveData.diagramType = 'sequence'
    } else if (firstLine.includes('class')) {
      stream.progressiveData.diagramType = 'class'
    } else {
      stream.progressiveData.diagramType = 'flowchart'
    }
    
    stream.progressiveData.diagramContent = stream.buffer
  }

  /**
   * Clean content for display by removing detection keywords
   */
  const cleanContentForDisplay = (content, contentType) => {
    if (!content) return content

    let cleaned = content

    // Remove all DIGI_*_START and DIGI_*_END keywords and their emoji variants
    const keywordPatterns = [
      // START keywords
      /🔍 DIGI_THINKING_START\n?/g,
      /🧠 DIGI_ANALYSIS_START\n?/g,
      /⚡ DIGI_EXECUTION_START\n?/g,
      /✅ DIGI_QUALITY_START\n?/g,
      /🎯 DIGI_COMPLETION_START\n?/g,
      /💻 DIGI_CODE_START\n?/g,
      /📊 DIGI_DIAGRAM_START\n?/g,
      /📋 DIGI_JSON_START\n?/g,
      /📈 DIGI_TABLE_START\n?/g,
      /🔍 DIGI_SEARCH_START\n?/g,
      /🔧 DIGI_TOOL_START\n?/g,
      /DIGI_\w+_START\n?/g,
      // END keywords
      /💻 DIGI_CODE_END\n?/g,
      /📊 DIGI_DIAGRAM_END\n?/g,
      /📋 DIGI_JSON_END\n?/g,
      /📈 DIGI_TABLE_END\n?/g,
      /🔍 DIGI_SEARCH_END\n?/g,
      /🔧 DIGI_TOOL_END\n?/g,
      /👁️ DIGI_VISION_END\n?/g,
      /📷 DIGI_IMAGE_ANALYSIS_END\n?/g,
      /🎵 DIGI_AUDIO_END\n?/g,
      /🎤 DIGI_TRANSCRIPTION_END\n?/g,
      /DIGI_\w+_END\n?/g
    ]

    keywordPatterns.forEach(pattern => {
      cleaned = cleaned.replace(pattern, '')
    })

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

  /**
   * Get debug information for a stream
   */
  const getStreamDebugInfo = (streamId) => {
    const stream = activeStreams.value.get(streamId)
    if (!stream) return null

    return {
      streamId,
      currentType: stream.currentType,
      confidence: stream.confidence,
      bufferLength: stream.buffer.length,
      detectionHistory: stream.detectionHistory,
      progressiveDataKeys: Object.keys(stream.progressiveData),
      isComplete: stream.isComplete
    }
  }

  /**
   * Force detection re-evaluation (for testing/debugging)
   */
  const redetectContent = (streamId) => {
    const stream = activeStreams.value.get(streamId)
    if (!stream) return null

    // Reset confidence to force re-detection
    stream.confidence = 0.0
    stream.detectionHistory = []

    // Re-run detection
    const primary = detectPrimaryKeywords(stream.buffer)
    const secondary = detectContentPatterns(stream.buffer)
    const final = chooseBestDetection(primary, secondary, stream)

    // Update stream
    stream.currentType = final.type
    stream.currentComponent = final.component
    stream.confidence = final.confidence

    activeStreams.value.set(streamId, stream)

    return {
      primary,
      secondary,
      final,
      stream: getStreamDebugInfo(streamId)
    }
  }

  /**
   * Get all active streams (for debugging)
   */
  const getActiveStreams = computed(() => {
    return Array.from(activeStreams.value.entries()).map(([id, stream]) => ({
      id,
      type: stream.currentType,
      confidence: stream.confidence,
      bufferLength: stream.buffer.length,
      isComplete: stream.isComplete
    }))
  })

  return {
    // Core functionality
    routeContent,
    completeStream,
    clearStream,
    
    // Progressive rendering support
    updateProgressiveData,
    cleanContentForDisplay,
    
    // Debug and testing
    getStreamDebugInfo,
    redetectContent,
    getActiveStreams,
    
    // Utilities
    detectPrimaryKeywords,
    detectContentPatterns,
    
    // Configuration
    primaryKeywords,
    componentMap
  }
}
