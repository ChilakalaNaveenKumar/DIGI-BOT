import { ref, computed } from 'vue'
import { marked } from 'marked'

/**
 * Smart Content Router Plugin
 * Handles LIVE STREAMING with format transitions and half-baked content
 */
export const useContentRouter = () => {
  const activeStreams = ref(new Map())

  /**
   * Route content for LIVE STREAMING - shows half-baked content immediately
   */
  const routeContent = (chunk, streamId = 'default') => {
    // Get or create stream buffer
    const stream = activeStreams.value.get(streamId) || {
      buffer: '',
      segments: [], // Track different content segments
      currentType: 'text',
      currentComponent: 'DigiSetuText',
      metadata: {},
      isComplete: false,
      lastDetectionLength: 0
    }

    // Append new content
    const newContent = chunk.content || ''
    stream.buffer += newContent

    // Only re-detect if we have significant new content (optimization)
    const shouldRedetect = stream.buffer.length - stream.lastDetectionLength > 10 || 
                          newContent.includes('\n') || 
                          newContent.includes('```') ||
                          newContent.includes('|') ||
                          newContent.includes('{') ||
                          newContent.includes('[')

    if (shouldRedetect) {
      // Detect format changes for LIVE content
      const segments = detectLiveSegments(stream.buffer)
      stream.segments = segments
      stream.lastDetectionLength = stream.buffer.length

      // Get the dominant/current format for the stream
      const currentSegment = segments[segments.length - 1] || { type: 'text', component: 'DigiSetuText' }
      stream.currentType = currentSegment.type
      stream.currentComponent = currentSegment.component
      stream.metadata = currentSegment.metadata || {}
    }

    // Update stream
    activeStreams.value.set(streamId, stream)

    return {
      // Return the current/dominant component for rendering
      component: stream.currentComponent,
      content: stream.buffer,
      contentType: stream.currentType,
      metadata: stream.metadata,
      segments: stream.segments, // All detected segments
      isStreaming: !stream.isComplete,
      streamId,
      hasMultipleFormats: stream.segments.length > 1
    }
  }

  /**
   * Detect multiple content segments in LIVE streaming content
   * Handles format transitions and incomplete content
   */
  const detectLiveSegments = (content) => {
    if (!content || content.trim().length === 0) {
      return [{ type: 'text', component: 'DigiSetuText', content: '', metadata: {} }]
    }

    const segments = []
    const lines = content.split('\n')
    let currentSegment = { type: 'text', content: '', startLine: 0 }

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i]
      const remainingContent = lines.slice(i).join('\n')

      // Detect format boundaries
      if (line.startsWith('```')) {
        // Code block boundary
        if (currentSegment.content.trim()) {
          segments.push(finalizeSegment(currentSegment))
        }
        
        // Find end of code block (or treat as incomplete if not found)
        const codeMatch = remainingContent.match(/^```(\w*)\n([\s\S]*?)(?:\n```|$)/)
        if (codeMatch) {
          const language = codeMatch[1] || 'text'
          const codeContent = codeMatch[2]
          segments.push({
            type: 'code',
            component: 'DigiSetuCodeBlock',
            content: `\`\`\`${language}\n${codeContent}\n\`\`\``,
            metadata: { language, isComplete: codeContent.endsWith('\n```') },
            startLine: i,
            endLine: i + codeContent.split('\n').length + 1
          })
          i += codeContent.split('\n').length + 1 // Skip processed lines
        } else {
          // Incomplete code block - still show it
          const incompleteCode = lines.slice(i + 1).join('\n')
          segments.push({
            type: 'code',
            component: 'DigiSetuCodeBlock',
            content: `\`\`\`${line.slice(3)}\n${incompleteCode}`,
            metadata: { language: line.slice(3) || 'text', isComplete: false },
            startLine: i
          })
          break // Rest is part of this incomplete code block
        }
        currentSegment = { type: 'text', content: '', startLine: i + 1 }
      } else if (line.includes('|') && (line.match(/\|/g) || []).length >= 2) {
        // Potential table row
        const tableContent = detectTableSegment(lines, i)
        if (tableContent.isTable) {
          if (currentSegment.content.trim()) {
            segments.push(finalizeSegment(currentSegment))
          }
          segments.push({
            type: 'table',
            component: 'DigiSetuTable',
            content: tableContent.content,
            metadata: tableContent.metadata,
            startLine: i,
            endLine: i + tableContent.lineCount
          })
          i += tableContent.lineCount - 1
          currentSegment = { type: 'text', content: '', startLine: i + 1 }
        } else {
          currentSegment.content += line + '\n'
        }
      } else if (line.trim().startsWith('{') || line.trim().startsWith('[')) {
        // Potential JSON
        const jsonContent = detectJsonSegment(lines, i)
        if (jsonContent.isJson) {
          if (currentSegment.content.trim()) {
            segments.push(finalizeSegment(currentSegment))
          }
          segments.push({
            type: 'json',
            component: 'DigiSetuJsonViewer',
            content: jsonContent.content,
            metadata: jsonContent.metadata,
            startLine: i,
            endLine: i + jsonContent.lineCount
          })
          i += jsonContent.lineCount - 1
          currentSegment = { type: 'text', content: '', startLine: i + 1 }
        } else {
          currentSegment.content += line + '\n'
        }
      } else if (['graph', 'flowchart', 'sequenceDiagram', 'classDiagram'].some(keyword => 
                 line.toLowerCase().includes(keyword))) {
        // Mermaid diagram
        if (currentSegment.content.trim()) {
          segments.push(finalizeSegment(currentSegment))
        }
        const diagramContent = detectDiagramSegment(lines, i)
        segments.push({
          type: 'diagram',
          component: 'DigiSetuDiagram',
          content: diagramContent.content,
          metadata: diagramContent.metadata,
          startLine: i,
          endLine: i + diagramContent.lineCount
        })
        i += diagramContent.lineCount - 1
        currentSegment = { type: 'text', content: '', startLine: i + 1 }
      } else {
        // Regular text content
        currentSegment.content += line + '\n'
      }
    }

    // Add final segment
    if (currentSegment.content.trim()) {
      segments.push(finalizeSegment(currentSegment))
    }

    // If no segments detected, treat as text
    if (segments.length === 0) {
      segments.push({
        type: 'text',
        component: 'DigiSetuText',
        content: content,
        metadata: {},
        startLine: 0
      })
    }

    return segments
  }

  /**
   * Finalize a text segment with proper type detection
   */
  const finalizeSegment = (segment) => {
    const detectedType = detectContentType(segment.content)
    return {
      type: detectedType,
      component: getComponent(detectedType),
      content: segment.content,
      metadata: extractMetadata(segment.content, detectedType),
      startLine: segment.startLine
    }
  }

  /**
   * Detect table segment from lines starting at index
   */
  const detectTableSegment = (lines, startIndex) => {
    const potentialTable = []
    let i = startIndex
    
    // Look for table pattern
    while (i < lines.length && lines[i].includes('|')) {
      potentialTable.push(lines[i])
      i++
      if (i < lines.length && lines[i].includes('---')) {
        potentialTable.push(lines[i])
        i++
        break
      }
    }
    
    // Continue collecting table rows
    while (i < lines.length && lines[i].includes('|') && lines[i].trim() !== '') {
      potentialTable.push(lines[i])
      i++
    }

    const content = potentialTable.join('\n')
    const isTable = potentialTable.length >= 2 && potentialTable.some(line => line.includes('---'))

    return {
      isTable,
      content,
      lineCount: potentialTable.length,
      metadata: isTable ? extractTableMetadata(content) : {}
    }
  }

  /**
   * Detect JSON segment from lines starting at index
   */
  const detectJsonSegment = (lines, startIndex) => {
    let braceCount = 0
    let bracketCount = 0
    let jsonLines = []
    let i = startIndex

    for (const char of lines[i]) {
      if (char === '{') braceCount++
      if (char === '}') braceCount--
      if (char === '[') bracketCount++
      if (char === ']') bracketCount--
    }

    jsonLines.push(lines[i])
    i++

    // Continue until braces/brackets are balanced or we run out of lines
    while (i < lines.length && (braceCount > 0 || bracketCount > 0)) {
      const line = lines[i]
      for (const char of line) {
        if (char === '{') braceCount++
        if (char === '}') braceCount--
        if (char === '[') bracketCount++
        if (char === ']') bracketCount--
      }
      jsonLines.push(line)
      i++
    }

    const content = jsonLines.join('\n')
    let isJson = false
    let metadata = {}

    try {
      const parsed = JSON.parse(content)
      isJson = true
      metadata = {
        isArray: Array.isArray(parsed),
        keys: Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length,
        isComplete: braceCount === 0 && bracketCount === 0
      }
    } catch {
      // Might be incomplete JSON during streaming
      metadata = { isComplete: false, error: 'Incomplete JSON' }
    }

    return {
      isJson: isJson || braceCount === 0 || bracketCount === 0, // Show even incomplete JSON
      content,
      lineCount: jsonLines.length,
      metadata
    }
  }

  /**
   * Detect diagram segment from lines starting at index
   */
  const detectDiagramSegment = (lines, startIndex) => {
    const diagramLines = []
    let i = startIndex

    // Collect lines until we hit empty line or obvious end
    while (i < lines.length) {
      const line = lines[i]
      if (line.trim() === '' && diagramLines.length > 0) {
        break
      }
      diagramLines.push(line)
      i++
    }

    const content = diagramLines.join('\n')
    const firstLine = lines[startIndex].toLowerCase()
    
    let diagramType = 'flowchart'
    if (firstLine.includes('sequence')) diagramType = 'sequence'
    else if (firstLine.includes('class')) diagramType = 'class'
    else if (firstLine.includes('state')) diagramType = 'state'

    return {
      content,
      lineCount: diagramLines.length,
      metadata: { diagramType, isComplete: true }
    }
  }

  /**
   * Extract table metadata
   */
  const extractTableMetadata = (content) => {
    const lines = content.split('\n').filter(line => line.trim())
    if (lines.length < 2) return {}

    const headerLine = lines[0]
    const headers = headerLine.split('|').map(h => h.trim()).filter(h => h)
    
    return {
      headers,
      columns: headers.length,
      rows: lines.length - 2, // Exclude header and separator
      hasHeaders: true
    }
  }

  /**
   * Content type detection using proven libraries (for single segments)
   */
  const detectContentType = (content) => {
    if (!content || content.trim().length === 0) return 'text'

    const trimmed = content.trim()

    // JSON detection using built-in JSON parser
    if (isJSON(trimmed)) return 'json'

    // Code block detection using marked.js lexer
    if (isCodeBlock(trimmed)) return 'code'

    // Table detection using marked.js
    if (isTable(trimmed)) return 'table'

    // Diagram detection (mermaid patterns)
    if (isDiagram(trimmed)) return 'diagram'

    // Markdown detection using marked.js lexer
    if (isMarkdown(trimmed)) return 'markdown'

    // Default to text
    return 'text'
  }

  /**
   * JSON detection using native JSON parser
   */
  const isJSON = (content) => {
    if (!content.startsWith('{') && !content.startsWith('[')) return false
    
    try {
      JSON.parse(content)
      return true
    } catch {
      return false
    }
  }

  /**
   * Code block detection using marked.js
   */
  const isCodeBlock = (content) => {
    // Markdown code block
    if (content.startsWith('```') && content.includes('\n')) return true
    
    // Use highlight.js for auto-detection if available
    if (typeof window !== 'undefined' && window.hljs) {
      const result = window.hljs.highlightAuto(content)
      return result.relevance > 5 // High confidence threshold
    }
    
    return false
  }

  /**
   * Table detection using marked.js lexer
   */
  const isTable = (content) => {
    try {
      const tokens = marked.lexer(content)
      return tokens.some(token => token.type === 'table')
    } catch {
      return false
    }
  }

  /**
   * Diagram detection (mermaid keywords)
   */
  const isDiagram = (content) => {
    const diagramKeywords = [
      'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
      'stateDiagram', 'pie', 'gantt', 'gitgraph'
    ]
    
    const firstLine = content.split('\n')[0].toLowerCase()
    return diagramKeywords.some(keyword => firstLine.includes(keyword))
  }

  /**
   * Markdown detection using marked.js lexer
   */
  const isMarkdown = (content) => {
    try {
      const tokens = marked.lexer(content)
      
      // If we get more than just a paragraph, it's likely markdown
      if (tokens.length > 1) return true
      
      // Check if the single token has markdown features
      const firstToken = tokens[0]
      if (firstToken?.type !== 'paragraph') return true
      
      // Check for inline markdown in the text
      const inlineMarkdown = /(\*\*.*\*\*|\*.*\*|`.*`|!\[.*\]\(.*\)|\[.*\]\(.*\))/
      return inlineMarkdown.test(content)
    } catch {
      return false
    }
  }

  /**
   * Get component based on content type
   */
  const getComponent = (contentType) => {
    const componentMap = {
      text: 'DigiSetuText',
      markdown: 'DigiSetuMarkdown',
      code: 'DigiSetuCodeBlock',
      json: 'DigiSetuJsonViewer',
      table: 'DigiSetuTable',
      diagram: 'DigiSetuDiagram'
    }
    
    return componentMap[contentType] || 'DigiSetuText'
  }

  /**
   * Extract metadata using appropriate parsers
   */
  const extractMetadata = (content, contentType) => {
    const metadata = {}

    switch (contentType) {
      case 'code': {
        // Extract language from code block
        const codeMatch = content.match(/^```(\w+)/)
        if (codeMatch) {
          metadata.language = codeMatch[1]
        } else if (typeof window !== 'undefined' && window.hljs) {
          const result = window.hljs.highlightAuto(content)
          metadata.language = result.language || 'text'
          metadata.relevance = result.relevance
        }
        break
      }

      case 'table': {
        // Extract table structure using marked.js
        try {
          const tokens = marked.lexer(content)
          const tableToken = tokens.find(token => token.type === 'table')
          if (tableToken) {
            metadata.headers = tableToken.header
            metadata.rows = tableToken.rows
            metadata.align = tableToken.align
          }
        } catch (error) {
          console.warn('Failed to parse table metadata:', error)
        }
        break
      }

      case 'json': {
        // Extract JSON structure info
        try {
          const parsed = JSON.parse(content)
          metadata.isArray = Array.isArray(parsed)
          metadata.keys = Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length
        } catch {
          metadata.error = 'Invalid JSON'
        }
        break
      }

      case 'diagram': {
        // Extract diagram type
        const firstLine = content.split('\n')[0].toLowerCase()
        if (firstLine.includes('flowchart') || firstLine.includes('graph')) {
          metadata.diagramType = 'flowchart'
        } else if (firstLine.includes('sequence')) {
          metadata.diagramType = 'sequence'
        } else if (firstLine.includes('class')) {
          metadata.diagramType = 'class'
        } else {
          metadata.diagramType = 'flowchart'
        }
        break
      }

      case 'markdown': {
        // Extract markdown features using marked.js
        try {
          const tokens = marked.lexer(content)
          metadata.hasHeaders = tokens.some(token => token.type === 'heading')
          metadata.hasLists = tokens.some(token => token.type === 'list')
          metadata.hasCodeBlocks = tokens.some(token => token.type === 'code')
          metadata.hasTables = tokens.some(token => token.type === 'table')
          metadata.hasLinks = tokens.some(token => 
            token.type === 'paragraph' && token.tokens?.some(t => t.type === 'link')
          )
        } catch (error) {
          console.warn('Failed to parse markdown metadata:', error)
        }
        break
      }
    }

    return metadata
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
   * Clear stream buffer
   */
  const clearStream = (streamId) => {
    activeStreams.value.delete(streamId)
  }

  /**
   * Get all active streams
   */
  const getActiveStreams = computed(() => {
    return Array.from(activeStreams.value.entries()).map(([id, stream]) => ({
      id,
      ...stream
    }))
  })

  return {
    routeContent,
    completeStream,
    clearStream,
    getActiveStreams,
    detectContentType // Expose for testing
  }
}
