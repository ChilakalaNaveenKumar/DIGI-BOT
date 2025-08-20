/**
 * Enhanced Content Composable
 * 
 * Handles enhanced content packets from the new batch analysis system.
 * Replaces the old placeholder-based system with direct content enhancement.
 */

import { ref, computed } from 'vue'

export interface EnhancedComponent {
  id: string
  position: number
  original_position: number
  enhancement_type: 'overlay' | 'replace' | 'hybrid'
  component_type: string
  reasoning: string
  enhanced_content?: string
  component_spec: {
    title?: string
    data?: any
    interactions?: any[]
    styling?: any
  }
  markdown?: string
  original_content: string
  block_type: string
}

export interface EnhancedContentPacket {
  enhanced_content: string
  components: EnhancedComponent[]
  metadata: {
    processed: boolean
    segmentation_time?: number
    analysis_time?: number
    blocks_found?: number
    components_generated?: number
    original_length?: number
    enhanced_length?: number
    error?: string
  }
}

export interface ProcessedMessage {
  id: number
  content: string
  enhanced_content?: string
  components: EnhancedComponent[]
  is_enhanced: boolean
  enhancement_metadata?: any
}

export const useEnhancedContent = () => {
  const processedMessages = ref<Map<number, ProcessedMessage>>(new Map())
  const isProcessingEnhancements = ref(false)

  /**
   * Process enhanced content packet from backend
   */
  const processEnhancedPacket = (
    messageId: number,
    packet: EnhancedContentPacket,
    originalContent: string
  ) => {
    try {
      isProcessingEnhancements.value = true

      const processedMessage: ProcessedMessage = {
        id: messageId,
        content: originalContent,
        enhanced_content: packet.enhanced_content,
        components: packet.components.map((comp, index) => ({
          ...comp,
          id: comp.id || `comp_${messageId}_${index}`,
        })),
        is_enhanced: packet.metadata.processed && packet.components.length > 0,
        enhancement_metadata: packet.metadata
      }

      processedMessages.value.set(messageId, processedMessage)

      console.log(`✅ Enhanced content processed for message ${messageId}:`, {
        components_count: processedMessage.components.length,
        is_enhanced: processedMessage.is_enhanced,
        enhancement_types: processedMessage.components.map(c => c.enhancement_type),
        component_types: processedMessage.components.map(c => c.component_type)
      })

    } catch (error) {
      console.error('Failed to process enhanced content packet:', error)
    } finally {
      isProcessingEnhancements.value = false
    }
  }

  /**
   * Get processed message by ID
   */
  const getProcessedMessage = (messageId: number): ProcessedMessage | undefined => {
    return processedMessages.value.get(messageId)
  }

  /**
   * Get enhanced content for display
   */
  const getEnhancedContent = (messageId: number): string => {
    const processed = processedMessages.value.get(messageId)
    return processed?.enhanced_content || processed?.content || ''
  }

  /**
   * Get components for a message
   */
  const getMessageComponents = (messageId: number): EnhancedComponent[] => {
    const processed = processedMessages.value.get(messageId)
    return processed?.components || []
  }

  /**
   * Check if message has enhancements
   */
  const isMessageEnhanced = (messageId: number): boolean => {
    const processed = processedMessages.value.get(messageId)
    return processed?.is_enhanced || false
  }

  /**
   * Get components by enhancement type
   */
  const getComponentsByType = (messageId: number, enhancementType: 'overlay' | 'replace' | 'hybrid'): EnhancedComponent[] => {
    const components = getMessageComponents(messageId)
    return components.filter(comp => comp.enhancement_type === enhancementType)
  }

  /**
   * Get overlay components (positioned over original content)
   */
  const getOverlayComponents = (messageId: number): EnhancedComponent[] => {
    return getComponentsByType(messageId, 'overlay')
  }

  /**
   * Get replacement components (content was replaced)
   */
  const getReplacementComponents = (messageId: number): EnhancedComponent[] => {
    return getComponentsByType(messageId, 'replace')
  }

  /**
   * Get hybrid components (content was modified + enhanced)
   */
  const getHybridComponents = (messageId: number): EnhancedComponent[] => {
    return getComponentsByType(messageId, 'hybrid')
  }

  /**
   * Get component by position
   */
  const getComponentAtPosition = (messageId: number, position: number): EnhancedComponent | undefined => {
    const components = getMessageComponents(messageId)
    return components.find(comp => 
      position >= comp.original_position && 
      position <= comp.original_position + comp.original_content.length
    )
  }

  /**
   * Get enhancement statistics
   */
  const getEnhancementStats = computed(() => {
    let totalMessages = 0
    let enhancedMessages = 0
    let totalComponents = 0
    const componentTypes: Record<string, number> = {}
    const enhancementTypes: Record<string, number> = {}

    processedMessages.value.forEach(message => {
      totalMessages++
      if (message.is_enhanced) {
        enhancedMessages++
      }
      
      message.components.forEach(component => {
        totalComponents++
        componentTypes[component.component_type] = (componentTypes[component.component_type] || 0) + 1
        enhancementTypes[component.enhancement_type] = (enhancementTypes[component.enhancement_type] || 0) + 1
      })
    })

    return {
      totalMessages,
      enhancedMessages,
      totalComponents,
      enhancementRate: totalMessages > 0 ? (enhancedMessages / totalMessages) * 100 : 0,
      componentTypes,
      enhancementTypes
    }
  })

  /**
   * Clear processed message
   */
  const clearProcessedMessage = (messageId: number) => {
    processedMessages.value.delete(messageId)
  }

  /**
   * Clear all processed messages
   */
  const clearAllProcessedMessages = () => {
    processedMessages.value.clear()
  }

  /**
   * Handle component interaction (click, hover, etc.)
   */
  const handleComponentInteraction = (
    messageId: number, 
    componentId: string, 
    interaction: string, 
    data?: any
  ) => {
    const component = getMessageComponents(messageId).find(c => c.id === componentId)
    
    if (!component) {
      console.warn(`Component ${componentId} not found in message ${messageId}`)
      return
    }

    console.log(`Component interaction: ${interaction}`, {
      messageId,
      componentId,
      componentType: component.component_type,
      enhancementType: component.enhancement_type,
      data
    })

    // Handle specific interactions
    switch (interaction) {
      case 'scroll_to':
        // Scroll to original position in content
        const element = document.querySelector(`[data-message-id="${messageId}"]`)
        if (element) {
          element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        }
        break
      
      case 'expand':
        // Handle component expansion
        break
      
      case 'collapse':
        // Handle component collapse
        break
      
      default:
        // Handle custom interactions based on component spec
        if (component.component_spec.interactions) {
          const customInteraction = component.component_spec.interactions.find(
            (inter: any) => inter.type === interaction
          )
          if (customInteraction && customInteraction.handler) {
            customInteraction.handler(data)
          }
        }
    }
  }

  return {
    // State
    processedMessages: processedMessages.value,
    isProcessingEnhancements,

    // Actions
    processEnhancedPacket,
    getProcessedMessage,
    getEnhancedContent,
    getMessageComponents,
    isMessageEnhanced,
    getComponentsByType,
    getOverlayComponents,
    getReplacementComponents,
    getHybridComponents,
    getComponentAtPosition,
    clearProcessedMessage,
    clearAllProcessedMessages,
    handleComponentInteraction,

    // Computed
    enhancementStats: getEnhancementStats
  }
}
