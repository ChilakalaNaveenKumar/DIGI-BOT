import { ref, computed, watch, nextTick } from 'vue'

/**
 * Progressive Rendering Framework
 * 
 * Provides utilities for components to render content progressively
 * as it streams in, creating a "painting" effect like ChatGPT.
 */
export const useProgressiveRenderer = () => {
  
  /**
   * Create a progressive renderer for a specific content type
   */
  const createProgressiveRenderer = (contentType, options = {}) => {
    const {
      chunkSize = 10,           // How many items to render at once
      renderDelay = 50,         // Delay between render chunks (ms)
      enableAnimations = true,  // Whether to show painting animations
      fallbackMode = 'immediate' // 'immediate', 'graceful', 'skeleton'
    } = options

    // State
    const rawContent = ref('')
    const parsedContent = ref(null)
    const renderProgress = ref(0)
    const isStreaming = ref(true)
    const isRendering = ref(false)
    const renderQueue = ref([])
    const visibleItems = ref([])
    const renderingError = ref(null)

    // Parse content based on type
    const parseContent = (content) => {
      try {
        switch (contentType) {
          case 'table':
            return parseTableContent(content)
          case 'code':
            return parseCodeContent(content)
          case 'json':
            return parseJsonContent(content)
          case 'diagram':
            return parseDiagramContent(content)
          case 'list':
            return parseListContent(content)
          default:
            return parseTextContent(content)
        }
      } catch (error) {
        console.warn(`Failed to parse ${contentType} content:`, error)
        renderingError.value = error
        return null
      }
    }

    // Progressive rendering engine
    const startProgressiveRender = async () => {
      if (isRendering.value || !parsedContent.value) return

      isRendering.value = true
      visibleItems.value = []
      renderProgress.value = 0

      const items = getItemsForRendering(parsedContent.value)
      renderQueue.value = [...items]

      // Render items progressively
      while (renderQueue.value.length > 0 && isRendering.value) {
        const chunk = renderQueue.value.splice(0, chunkSize)
        visibleItems.value.push(...chunk)
        
        renderProgress.value = (items.length - renderQueue.value.length) / items.length

        // Allow Vue to update DOM
        await nextTick()

        // Add delay for painting effect (skip if not streaming)
        if (isStreaming.value && enableAnimations) {
          await new Promise(resolve => setTimeout(resolve, renderDelay))
        }
      }

      isRendering.value = false
      renderProgress.value = 1.0
    }

    // Update content and trigger re-render
    const updateContent = (newContent, streaming = true) => {
      rawContent.value = newContent
      isStreaming.value = streaming

      const parsed = parseContent(newContent)
      
      if (parsed) {
        parsedContent.value = parsed
        
        // If content is complete or we're not streaming, render immediately
        if (!streaming || fallbackMode === 'immediate') {
          const items = getItemsForRendering(parsed)
          visibleItems.value = items
          renderProgress.value = 1.0
          isRendering.value = false
        } else {
          // Start progressive rendering
          startProgressiveRender()
        }
      } else if (fallbackMode === 'graceful') {
        // Show raw content if parsing fails
        visibleItems.value = [{ type: 'raw', content: newContent }]
        renderProgress.value = 1.0
      }
    }

    // Force complete rendering (skip animation)
    const completeRendering = () => {
      if (parsedContent.value) {
        const items = getItemsForRendering(parsedContent.value)
        visibleItems.value = items
        renderQueue.value = []
        renderProgress.value = 1.0
        isRendering.value = false
        isStreaming.value = false
      }
    }

    // Stop progressive rendering
    const stopRendering = () => {
      isRendering.value = false
      renderQueue.value = []
    }

    return {
      // State
      rawContent: readonly(rawContent),
      parsedContent: readonly(parsedContent),
      visibleItems: readonly(visibleItems),
      renderProgress: readonly(renderProgress),
      isStreaming: readonly(isStreaming),
      isRendering: readonly(isRendering),
      renderingError: readonly(renderingError),

      // Methods
      updateContent,
      completeRendering,
      stopRendering,
      
      // Computed
      hasContent: computed(() => rawContent.value.length > 0),
      isEmpty: computed(() => visibleItems.value.length === 0),
      isComplete: computed(() => !isStreaming.value && !isRendering.value),
      canRender: computed(() => parsedContent.value !== null),
      
      // Progress
      progressPercentage: computed(() => Math.round(renderProgress.value * 100)),
      itemsRendered: computed(() => visibleItems.value.length),
      totalItems: computed(() => {
        if (!parsedContent.value) return 0
        return getItemsForRendering(parsedContent.value).length
      })
    }
  }

  /**
   * Parse table content into renderable items
   */
  const parseTableContent = (content) => {
    const lines = content.split('\n').filter(line => line.trim())
    const tableLines = lines.filter(line => line.includes('|'))
    
    if (tableLines.length < 2) return null

    const headers = tableLines[0]
      .split('|')
      .map(h => h.trim())
      .filter(h => h)

    // Skip separator line
    const dataLines = tableLines.slice(2)
    const rows = dataLines.map((line, index) => ({
      id: `row-${index}`,
      cells: line.split('|').map(cell => cell.trim()).filter(cell => cell),
      type: 'table-row'
    }))

    return {
      type: 'table',
      headers,
      rows,
      metadata: {
        columnCount: headers.length,
        rowCount: rows.length,
        hasHeaders: true
      }
    }
  }

  /**
   * Parse code content into renderable items
   */
  const parseCodeContent = (content) => {
    // Handle code blocks
    const codeMatch = content.match(/```(\w*)\n([\s\S]*?)(?:\n```|$)/)
    
    if (codeMatch) {
      const language = codeMatch[1] || 'text'
      const code = codeMatch[2]
      const lines = code.split('\n')
      
      return {
        type: 'code',
        language,
        lines: lines.map((line, index) => ({
          id: `line-${index + 1}`,
          number: index + 1,
          content: line,
          type: 'code-line'
        })),
        metadata: {
          language,
          lineCount: lines.length,
          isComplete: content.includes('\n```')
        }
      }
    }

    // Handle plain code (no code block markers)
    const lines = content.split('\n')
    return {
      type: 'code',
      language: 'text',
      lines: lines.map((line, index) => ({
        id: `line-${index + 1}`,
        number: index + 1,
        content: line,
        type: 'code-line'
      })),
      metadata: {
        language: 'text',
        lineCount: lines.length,
        isComplete: true
      }
    }
  }

  /**
   * Parse JSON content into renderable items
   */
  const parseJsonContent = (content) => {
    try {
      const parsed = JSON.parse(content.trim())
      
      if (Array.isArray(parsed)) {
        return {
          type: 'json-array',
          items: parsed.map((item, index) => ({
            id: `item-${index}`,
            index,
            value: item,
            type: 'json-array-item'
          })),
          metadata: {
            isArray: true,
            length: parsed.length,
            isComplete: true
          }
        }
      } else {
        const entries = Object.entries(parsed)
        return {
          type: 'json-object',
          entries: entries.map(([key, value], index) => ({
            id: `entry-${index}`,
            key,
            value,
            type: 'json-object-entry'
          })),
          metadata: {
            isArray: false,
            keyCount: entries.length,
            isComplete: true
          }
        }
      }
    } catch (error) {
      // Try to parse partial JSON for streaming
      const trimmed = content.trim()
      if (trimmed.startsWith('{') || trimmed.startsWith('[')) {
        return {
          type: 'json-partial',
          content: trimmed,
          lines: trimmed.split('\n').map((line, index) => ({
            id: `line-${index}`,
            content: line,
            type: 'json-line'
          })),
          metadata: {
            isPartial: true,
            isComplete: false,
            error: error.message
          }
        }
      }
      throw error
    }
  }

  /**
   * Parse diagram content into renderable items
   */
  const parseDiagramContent = (content) => {
    const lines = content.split('\n').filter(line => line.trim())
    const firstLine = lines[0]?.toLowerCase() || ''
    
    let diagramType = 'flowchart'
    if (firstLine.includes('sequence')) diagramType = 'sequence'
    else if (firstLine.includes('class')) diagramType = 'class'
    else if (firstLine.includes('state')) diagramType = 'state'
    
    return {
      type: 'diagram',
      diagramType,
      lines: lines.map((line, index) => ({
        id: `line-${index}`,
        content: line,
        type: 'diagram-line'
      })),
      metadata: {
        diagramType,
        lineCount: lines.length,
        isComplete: true
      }
    }
  }

  /**
   * Parse list content into renderable items
   */
  const parseListContent = (content) => {
    const lines = content.split('\n').filter(line => line.trim())
    const listItems = lines.filter(line => 
      line.match(/^\s*[-*+]\s/) || line.match(/^\s*\d+\.\s/)
    )
    
    if (listItems.length === 0) return null
    
    return {
      type: 'list',
      items: listItems.map((line, index) => {
        const isOrdered = line.match(/^\s*\d+\.\s/)
        const content = line.replace(/^\s*(?:[-*+]|\d+\.)\s/, '')
        
        return {
          id: `item-${index}`,
          content,
          isOrdered,
          type: 'list-item'
        }
      }),
      metadata: {
        itemCount: listItems.length,
        hasOrdered: listItems.some(line => line.match(/^\s*\d+\.\s/)),
        hasUnordered: listItems.some(line => line.match(/^\s*[-*+]\s/))
      }
    }
  }

  /**
   * Parse text content into renderable items
   */
  const parseTextContent = (content) => {
    const paragraphs = content.split('\n\n').filter(p => p.trim())
    
    return {
      type: 'text',
      paragraphs: paragraphs.map((paragraph, index) => ({
        id: `paragraph-${index}`,
        content: paragraph.trim(),
        type: 'text-paragraph'
      })),
      metadata: {
        paragraphCount: paragraphs.length,
        wordCount: content.split(/\s+/).length,
        characterCount: content.length
      }
    }
  }

  /**
   * Extract items for progressive rendering based on content type
   */
  const getItemsForRendering = (parsedContent) => {
    if (!parsedContent) return []
    
    switch (parsedContent.type) {
      case 'table':
        return parsedContent.rows
      case 'code':
        return parsedContent.lines
      case 'json-array':
        return parsedContent.items
      case 'json-object':
        return parsedContent.entries
      case 'json-partial':
        return parsedContent.lines
      case 'diagram':
        return parsedContent.lines
      case 'list':
        return parsedContent.items
      case 'text':
        return parsedContent.paragraphs
      default:
        return []
    }
  }

  /**
   * Create a skeleton loader for progressive rendering
   */
  const createSkeleton = (contentType, itemCount = 3) => {
    const skeletonItems = []
    
    for (let i = 0; i < itemCount; i++) {
      skeletonItems.push({
        id: `skeleton-${i}`,
        type: `${contentType}-skeleton`,
        isSkeleton: true
      })
    }
    
    return skeletonItems
  }

  /**
   * Animation utilities for progressive rendering
   */
  const animations = {
    fadeIn: 'transition-opacity duration-300 ease-in-out',
    slideIn: 'transition-transform duration-300 ease-in-out transform',
    typewriter: 'animate-pulse',
    painting: 'animate-fade-in-up'
  }

  return {
    createProgressiveRenderer,
    parseTableContent,
    parseCodeContent,
    parseJsonContent,
    parseDiagramContent,
    parseListContent,
    parseTextContent,
    createSkeleton,
    animations
  }
}

