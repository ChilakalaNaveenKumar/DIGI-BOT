import { ref, computed } from 'vue'

export interface ComponentBlock {
  id: string
  type: string
  title: string
  position: number
  action: 'insert' | 'update'
  data: any
  startPosition?: number
  endPosition?: number
  rawContent: string
}

export interface ContentBlock {
  id: string
  type: 'text' | 'component'
  content: string
  position: number
  component?: ComponentBlock
}

export interface StreamingContent {
  rawText: string
  blocks: ContentBlock[]
  components: ComponentBlock[]
  totalLength: number
}

export const useEnhancedStreaming = () => {
  const streamingContent = ref<StreamingContent>({
    rawText: '',
    blocks: [],
    components: [],
    totalLength: 0
  })

  const isStreaming = ref(false)
  const pendingComponents = ref<ComponentBlock[]>([])

  /**
   * Parse component matcher response format
   * Expected format: :::component-type\ntitle: xyz\nposition: 10\naction: insert\ndata: [...]\n:::
   */
  const parseComponentBlock = (componentText: string): ComponentBlock | null => {
    try {
      const lines = componentText.trim().split('\n')
      const componentType = lines[0].replace(':::', '').trim()
      
      const component: Partial<ComponentBlock> = {
        id: `component-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: componentType,
        rawContent: componentText
      }

      // Parse component properties
      for (let i = 1; i < lines.length; i++) {
        const line = lines[i].trim()
        if (line === ':::') break

        if (line.startsWith('title:')) {
          component.title = line.replace('title:', '').trim()
        } else if (line.startsWith('position:')) {
          component.position = parseInt(line.replace('position:', '').trim())
        } else if (line.startsWith('action:')) {
          component.action = line.replace('action:', '').trim() as 'insert' | 'update'
        } else if (line.startsWith('data:')) {
          // Handle multi-line data
          const dataStart = i
          let dataEnd = i
          let bracketCount = 0
          let inData = false

          for (let j = i; j < lines.length; j++) {
            const dataLine = lines[j]
            if (dataLine.includes('[') || dataLine.includes('{')) {
              inData = true
              bracketCount += (dataLine.match(/[\[\{]/g) || []).length
            }
            if (inData) {
              bracketCount -= (dataLine.match(/[\]\}]/g) || []).length
              if (bracketCount === 0) {
                dataEnd = j
                break
              }
            }
          }

          const dataText = lines.slice(dataStart, dataEnd + 1)
            .join('\n')
            .replace('data:', '')
            .trim()

          try {
            component.data = JSON.parse(dataText)
          } catch (e) {
            console.warn('Failed to parse component data:', e)
            component.data = null
          }
          
          i = dataEnd // Skip processed lines
        }
      }

      // Validate required fields
      if (!component.type || component.position === undefined || !component.action) {
        console.warn('Invalid component block - missing required fields:', component)
        return null
      }

      return component as ComponentBlock
    } catch (error) {
      console.error('Error parsing component block:', error)
      return null
    }
  }

  /**
   * Extract component blocks from text
   */
  const extractComponents = (text: string): ComponentBlock[] => {
    const components: ComponentBlock[] = []
    const componentRegex = /:::([\w-]+)(?:\n)([\s\S]*?)(?:\n):::/g
    let match

    while ((match = componentRegex.exec(text)) !== null) {
      const fullMatch = match[0]
      const component = parseComponentBlock(fullMatch)
      if (component) {
        components.push(component)
      }
    }

    return components.sort((a, b) => a.position - b.position)
  }

  /**
   * Remove component blocks from text, leaving clean text
   */
  const removeComponentBlocks = (text: string): string => {
    return text.replace(/:::([\w-]+)(?:\n)([\s\S]*?)(?:\n):::/g, '').trim()
  }

  /**
   * Insert components at their specified positions
   */
  const insertComponentsAtPositions = (text: string, components: ComponentBlock[]): ContentBlock[] => {
    const blocks: ContentBlock[] = []
    let currentPosition = 0
    let textOffset = 0

    // Sort components by position
    const sortedComponents = [...components].sort((a, b) => a.position - b.position)

    for (const component of sortedComponents) {
      const insertPosition = component.position - textOffset

      // Add text before component
      if (insertPosition > currentPosition) {
        const textContent = text.slice(currentPosition, insertPosition)
        if (textContent.trim()) {
          blocks.push({
            id: `text-${blocks.length}`,
            type: 'text',
            content: textContent,
            position: currentPosition
          })
        }
      }

      // Add component block
      blocks.push({
        id: component.id,
        type: 'component',
        content: '', // Component content is in the component object
        position: insertPosition,
        component
      })

      currentPosition = Math.max(insertPosition, currentPosition)
      
      // Account for the component block length in text offset
      textOffset += component.rawContent.length
    }

    // Add remaining text
    if (currentPosition < text.length) {
      const remainingText = text.slice(currentPosition)
      if (remainingText.trim()) {
        blocks.push({
          id: `text-${blocks.length}`,
          type: 'text',
          content: remainingText,
          position: currentPosition
        })
      }
    }

    return blocks
  }

  /**
   * Process streaming text and extract components
   */
  const processStreamingText = (newText: string) => {
    // Update raw text
    streamingContent.value.rawText = newText
    streamingContent.value.totalLength = newText.length

    // Extract components from the text
    const extractedComponents = extractComponents(newText)
    
    // Remove component blocks from text to get clean text
    const cleanText = removeComponentBlocks(newText)

    // Insert components at their positions
    const blocks = insertComponentsAtPositions(cleanText, extractedComponents)

    // Update streaming content
    streamingContent.value.components = extractedComponents
    streamingContent.value.blocks = blocks
  }

  /**
   * Add component from component matcher response
   */
  const addComponentFromMatcher = (componentResponse: string) => {
    const component = parseComponentBlock(componentResponse)
    if (component) {
      pendingComponents.value.push(component)
      
      // If we have current text, reprocess with new component
      if (streamingContent.value.rawText) {
        const updatedText = streamingContent.value.rawText + '\n' + componentResponse
        processStreamingText(updatedText)
      }
    }
  }

  /**
   * Update component (for action: update)
   */
  const updateComponent = (componentId: string, newData: any) => {
    const component = streamingContent.value.components.find(c => c.id === componentId)
    if (component) {
      component.data = newData
      
      // Update the corresponding block
      const block = streamingContent.value.blocks.find(b => b.component?.id === componentId)
      if (block && block.component) {
        block.component.data = newData
      }
    }
  }

  /**
   * Get rendered content blocks for display
   */
  const getRenderedBlocks = computed(() => {
    return streamingContent.value.blocks.map(block => {
      if (block.type === 'component' && block.component) {
        return {
          ...block,
          renderable: true,
          componentType: block.component.type,
          componentData: block.component.data,
          componentTitle: block.component.title
        }
      }
      return {
        ...block,
        renderable: true
      }
    })
  })

  /**
   * Clear streaming content
   */
  const clearContent = () => {
    streamingContent.value = {
      rawText: '',
      blocks: [],
      components: [],
      totalLength: 0
    }
    pendingComponents.value = []
  }

  /**
   * Start streaming
   */
  const startStreaming = () => {
    isStreaming.value = true
    clearContent()
  }

  /**
   * Stop streaming
   */
  const stopStreaming = () => {
    isStreaming.value = false
  }

  return {
    // State
    streamingContent: computed(() => streamingContent.value),
    isStreaming: computed(() => isStreaming.value),
    pendingComponents: computed(() => pendingComponents.value),
    renderedBlocks: getRenderedBlocks,

    // Methods
    processStreamingText,
    addComponentFromMatcher,
    updateComponent,
    parseComponentBlock,
    extractComponents,
    startStreaming,
    stopStreaming,
    clearContent
  }
}
