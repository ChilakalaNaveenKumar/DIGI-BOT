// Digi Setu Orchestrator Integration - Preserves existing UI/UX
import type { Message, ReasoningStep, GeneratedComponent } from '~/types'

interface DigiSetuStreamResponse {
  type: 'conversation_id' | 'thinking' | 'reasoning' | 'activity' | 'tool_output' | 'content' | 'error' | 'placeholder' | 'component_replacement' | 'placeholder_removal' | 'complete'
  content: string
  metadata?: {
    step?: string
    tool?: string
    tools?: string[]
    confidence?: number
    orchestrator?: string
    tools_used?: string[]
    reasoning?: string
  }
  final?: boolean
  // New fields for streaming analysis
  placeholder_id?: string
  component?: {
    type: string
    markdown: string
    confidence: number
    reasoning: string
    extracted_data?: any
  }
  reasoning?: string
}

export const useDigiSetuChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
  // Get runtime config for API base URL
  const config = useRuntimeConfig()
  
  // Component analysis composables (reuse existing)
  const { analyzeContent, isAnalyzing } = useComponentAnalysis()

  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) {
      return
    }
    
    // Add user message (same as existing)
    const userMessage: Message = {
      id: Date.now(),
      content,
      role: 'user' as const,
      timestamp: new Date()
    }
    messages.value.push(userMessage)
    
    input.value = ''
    isLoading.value = false
    isStreaming.value = true
    
    // Prepare assistant message for streaming (same structure as existing)
    const assistantMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: false,
      isStreaming: true,
      reasoning: '',
      reasoningSteps: [],
      components: []
    }
    messages.value.push(assistantMessage)
    
    try {
      await streamDigiSetuResponse(assistantMessage.id, content)
    } catch (error) {
      console.error('Digi Setu streaming error:', error)
      
      const index = messages.value.findIndex(m => m.id === assistantMessage.id)
      if (index !== -1) {
        messages.value[index] = {
          ...assistantMessage,
          content: 'Sorry, I encountered an error. Please try again.',
          isLoading: false,
          isStreaming: false,
          error: error instanceof Error ? error.message : String(error)
        }
      }
      
      isLoading.value = false
      isStreaming.value = false
    }
  }

  /**
   * Stream Digi Setu orchestrator response
   */
  const streamDigiSetuResponse = async (messageId: number, userContent: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) {
      console.log('❌ Message not found for streaming:', messageId)
      return
    }

    // Starting Digi Setu orchestrator streaming

    try {
      // Call Digi Setu streaming endpoint
      const response = await fetch(`${config.public.apiBase}/v1/api/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/event-stream',
        },
        body: JSON.stringify({
          message: userContent,
          user_preferences: {},
        })
      })

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body reader available')
      }

      let conversationId = ''
      let accumulatedContent = ''
      let currentReasoning = ''
      let reasoningSteps: ReasoningStep[] = []
      let toolsUsed: string[] = []
      let lastAnalyzedLength = 0  // Track what we've already analyzed
      let pendingAnalysis: Map<string, { position: number, content: string }> = new Map() // Track analysis placeholders

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value, { stream: true })
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: Claude4StreamResponse = JSON.parse(line.slice(6))
              
              // Handle different stream types
              switch (data.type) {
                case 'conversation_id':
                  conversationId = data.content
                  break

                case 'thinking':
                  // Handle thinking blocks properly based on metadata
                  if (data.metadata?.block_start) {
                    // Start new thinking step
                    reasoningSteps.push({
                      type: 'thinking',
                      content: '',
                      result: '', // Will accumulate content
                      status: 'active'
                    })
                  } else if (data.metadata?.thinking_delta && data.content) {
                    // Add content to current thinking step
                    const currentStep = reasoningSteps[reasoningSteps.length - 1]
                    if (currentStep && currentStep.type === 'thinking' && currentStep.status === 'active') {
                      currentStep.content += data.content
                      currentStep.result += data.content
                    } else {
                      // Fallback: create new step if no active thinking step exists
                      reasoningSteps.push({
                        type: 'thinking',
                        content: data.content,
                        result: data.content,
                        status: 'active'
                      })
                    }
                  }
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'reasoning':
                  // Handle reasoning conclusion based on metadata
                  if (data.metadata?.block_end) {
                    // Mark current thinking step as completed
                    const lastStep = reasoningSteps[reasoningSteps.length - 1]
                    if (lastStep && lastStep.type === 'thinking' && lastStep.status === 'active') {
                      lastStep.status = 'completed'
                    }
                    // Set the accumulated reasoning content
                    currentReasoning = lastStep?.content || ''
                    updateMessage(messageIndex, { 
                      reasoning: currentReasoning,
                      reasoningSteps: [...reasoningSteps]
                    })
                  } else if (data.content) {
                    // Fallback: handle as conclusion step
                    currentReasoning = data.content
                    reasoningSteps.push({
                      type: 'conclusion',
                      content: data.content,
                      result: data.content,
                      status: 'active'
                    })
                    updateMessage(messageIndex, { 
                      reasoning: currentReasoning,
                      reasoningSteps: [...reasoningSteps]
                    })
                  }
                  break

                case 'activity':
                  // Add activity step
                  reasoningSteps.push({
                    type: 'tool_call',
                    content: data.content,
                    status: 'active',
                    tool_name: data.metadata?.tool
                  })
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'tool_output':
                  // Update tool output
                  const toolStep = reasoningSteps.find(s => s.type === 'tool_call' && s.status === 'active')
                  if (toolStep) {
                    toolStep.result = data.content
                    if (data.final) {
                      toolStep.status = 'completed'
                    }
                  }
                  updateMessage(messageIndex, { reasoningSteps: [...reasoningSteps] })
                  break

                case 'content':
                  // Accumulate final content
                  accumulatedContent += data.content
                  
                  // Mark all reasoning steps as completed
                  reasoningSteps.forEach(step => {
                    if (step.status === 'active') step.status = 'completed'
                  })

                  updateMessage(messageIndex, {
                    content: accumulatedContent,
                    reasoningSteps: [...reasoningSteps],
                    isStreaming: data.final ? false : true
                  })

                  // Backend handles all analysis - no need for frontend analysis
                  break

                case 'complete':
                  console.log('✅ Stream complete:', {
                    messageIndex,
                    accumulatedContentLength: accumulatedContent?.length || 0
                  })
                  
                  // Mark streaming as complete
                  updateMessage(messageIndex, {
                    isStreaming: false,
                    isLoading: false
                  })
                  
                  // No need for additional analysis - backend has already handled it
                  break

                case 'placeholder':
                  // Handle analysis placeholder injection
                  console.log('🔄 Analysis placeholder injected:', data.placeholder_id)
                  
                  // Use a markdown-compatible placeholder that won't break rendering
                  const placeholderText = `\n\n> 🔄 **${data.content}** *(Placeholder: ${data.placeholder_id})*\n\n`
                  
                  accumulatedContent += placeholderText
                  updateMessage(messageIndex, { content: accumulatedContent })
                  break

                case 'component_replacement':
                  // Replace placeholder with actual component
                  console.log('✅ Component ready for placeholder:', data.placeholder_id)
                  
                  const componentMarkdown = data.component?.markdown || ''
                  
                  // Replace markdown placeholder with component
                  const placeholderPattern = `> 🔄 \\*\\*.*?\\*\\* \\*\\(Placeholder: ${data.placeholder_id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\)\\*`
                  accumulatedContent = accumulatedContent.replace(
                    new RegExp(placeholderPattern, 's'),
                    `\n\n${componentMarkdown}\n\n`
                  )
                  
                  // Also add to components array for proper rendering
                  const currentMessage = messages.value[messageIndex]
                  if (currentMessage && data.component) {
                    const existingComponents = currentMessage.components || []
                    existingComponents.push({
                      id: data.placeholder_id,
                      type: data.component.type,
                      title: `Generated ${data.component.type}`,
                      content: data.component.extracted_data || {},
                      reasoning: data.component.reasoning,
                      markdown: data.component.markdown,
                      confidence: data.component.confidence
                    })
                    
                    updateMessage(messageIndex, { 
                      content: accumulatedContent,
                      components: existingComponents 
                    })
                  } else {
                    updateMessage(messageIndex, { content: accumulatedContent })
                  }
                  break

                case 'placeholder_removal':
                  // Remove placeholder that didn't generate a component
                  console.log('⏭️ Removing placeholder (no component):', data.placeholder_id)
                  
                  // Remove markdown placeholder completely
                  const removalPattern = `> 🔄 \\*\\*.*?\\*\\* \\*\\(Placeholder: ${data.placeholder_id.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')}\\)\\*\\n\\n`
                  accumulatedContent = accumulatedContent.replace(
                    new RegExp(removalPattern, 's'),
                    '' // Remove completely
                  )
                  
                  updateMessage(messageIndex, { content: accumulatedContent })
                  break

                case 'error':
                  console.error('❌ Digi Setu error:', data.content)
                  updateMessage(messageIndex, {
                    error: data.content,
                    isStreaming: false,
                    isLoading: false
                  })
                  break
              }

            } catch (parseError) {
              console.warn('Failed to parse SSE data:', line, parseError)
            }
          }
        }
      }

    } catch (error) {
      console.error('Streaming error:', error)
      throw error
    } finally {
      isLoading.value = false
      isStreaming.value = false
    }
  }

  /**
   * Update message by index (preserves existing pattern)
   */
  const updateMessage = (index: number, updates: Partial<Message>) => {
    if (index >= 0 && index < messages.value.length) {
      messages.value[index] = { ...messages.value[index], ...updates }
    }
  }

  /**
   * Check for semantic boundaries and insert placeholders during streaming
   */
  const checkForSemanticBoundaryWithPlaceholder = async (
    messageIndex: number, 
    content: string, 
    lastAnalyzedLength: number,
    pendingAnalysis: Map<string, { position: number, content: string }>
  ) => {
    try {
      // Only analyze if we have new content
      if (content.length <= lastAnalyzedLength) return
      
      const newContent = content.slice(lastAnalyzedLength)
      
      // Detect semantic boundaries (paragraph breaks, list items, table rows)
      const semanticBoundaries = [
        /\n\n/,           // Paragraph break
        /\n\s*[-*+]\s/,   // List item
        /\n\s*\d+\.\s/,   // Numbered list
        /\|\s*\n/,        // Table row end
        /```\n/,          // Code block end
        /\n#{1,6}\s/      // Header
      ]
      
      let foundBoundary = false
      for (const boundary of semanticBoundaries) {
        if (boundary.test(newContent)) {
          foundBoundary = true
          break
        }
      }
      
      // If we found a semantic boundary and have enough content, create placeholder
      if (foundBoundary && content.length > 50) {
        const analysisId = `analysis_${Date.now()}_${Math.random()}`
        const boundaryPosition = content.length
        
        console.log('🔍 Semantic boundary detected - inserting placeholder:', {
          analysisId,
          position: boundaryPosition,
          contentLength: content.length
        })
        
        // Store analysis info
        pendingAnalysis.set(analysisId, {
          position: boundaryPosition,
          content: content
        })
        
        // Insert placeholder component immediately
        const currentMessage = messages.value[messageIndex]
        if (currentMessage) {
          const placeholderComponent = {
            id: analysisId,
            type: 'analysis-placeholder',
            title: 'Analyzing content...',
            content: { analysisId, position: boundaryPosition },
            reasoning: 'Analysis in progress',
            markdown: `<!-- PLACEHOLDER:${analysisId} -->`
          }
          
          const existingComponents = currentMessage.components || []
          currentMessage.components = [...existingComponents, placeholderComponent]
        }
        
        // Start analysis in background (will replace placeholder when done)
        analyzeAndReplacePlaceholder(messageIndex, content, analysisId, pendingAnalysis)
      }
      
    } catch (error) {
      console.error('Semantic boundary placeholder error:', error)
    }
  }

  /**
   * Analyze content and replace placeholder when ready
   */
  const analyzeAndReplacePlaceholder = async (
    messageIndex: number, 
    content: string, 
    analysisId: string,
    pendingAnalysis: Map<string, { position: number, content: string }>
  ) => {
    try {
      console.log(`🔍 Starting analysis for placeholder: ${analysisId}`)
      
      // Perform the actual analysis
      const decision = await analyzeContent({ content })
      
      // Get current message
      const currentMessage = messages.value[messageIndex]
      if (!currentMessage || !currentMessage.components) return
      
      // Find and replace the placeholder
      const componentIndex = currentMessage.components.findIndex(c => c.id === analysisId)
      
      if (componentIndex !== -1) {
        if (decision && decision.decision === 'GENERATE_NOW') {
          // Replace placeholder with actual component
          const realComponent = {
            id: Date.now() + Math.random(),
            type: decision.component_type || 'unknown',
            title: `Generated ${decision.component_type || 'Component'}`,
            content: decision.extracted_data || {},
            reasoning: decision.reasoning || 'Auto-generated from content analysis',
            markdown: decision.markdown
          }
          
          currentMessage.components[componentIndex] = realComponent
          console.log(`✅ Replaced placeholder ${analysisId} with component: ${decision.component_type}`)
        } else {
          // Remove placeholder if no component needed
          currentMessage.components.splice(componentIndex, 1)
          console.log(`❌ Removed placeholder ${analysisId} - no component generated`)
        }
      }
      
      // Clean up pending analysis
      pendingAnalysis.delete(analysisId)
      
    } catch (error) {
      console.error(`Analysis error for placeholder ${analysisId}:`, error)
      
      // Remove placeholder on error
      const currentMessage = messages.value[messageIndex]
      if (currentMessage?.components) {
        const componentIndex = currentMessage.components.findIndex(c => c.id === analysisId)
        if (componentIndex !== -1) {
          currentMessage.components.splice(componentIndex, 1)
        }
      }
      
      pendingAnalysis.delete(analysisId)
    }
  }

  /**
   * Original semantic boundary function (keeping for compatibility)
   */
  const checkForSemanticBoundaryAndAnalyze = async (
    messageIndex: number, 
    content: string, 
    lastAnalyzedLength: number
  ) => {
    try {
      // Only analyze if we have new content
      if (content.length <= lastAnalyzedLength) return
      
      const newContent = content.slice(lastAnalyzedLength)
      
      // Detect semantic boundaries (paragraph breaks, list items, table rows)
      const semanticBoundaries = [
        /\n\n/,           // Paragraph break
        /\n\s*[-*+]\s/,   // List item
        /\n\s*\d+\.\s/,   // Numbered list
        /\|\s*\n/,        // Table row end
        /```\n/,          // Code block end
        /\n#{1,6}\s/      // Header
      ]
      
      let foundBoundary = false
      for (const boundary of semanticBoundaries) {
        if (boundary.test(newContent)) {
          foundBoundary = true
          break
        }
      }
      
      // If we found a semantic boundary and have enough content, analyze
      if (foundBoundary && content.length > 50) {
        console.log('🔍 Semantic boundary detected - analyzing chunk:', {
          totalLength: content.length,
          newContentLength: newContent.length,
          boundary: 'detected'
        })
        
        // Show analysis indicator immediately
        const currentMessage = messages.value[messageIndex]
        if (currentMessage) {
          currentMessage.isAnalyzing = true
        }
        
        // Analyze the accumulated content up to this point (non-blocking)
        analyzeAndInjectComponents(messageIndex, content, true).finally(() => {
          // Hide analysis indicator when done
          const message = messages.value[messageIndex]
          if (message) {
            message.isAnalyzing = false
          }
        })
      }
      
    } catch (error) {
      console.error('Semantic boundary analysis error:', error)
    }
  }

  /**
   * Analyze content and inject components (reuses existing component analysis)
   */
  const analyzeAndInjectComponents = async (messageIndex: number, content: string, isChunk: boolean = false) => {
    try {
      console.log(`🔍 analyzeAndInjectComponents called (${isChunk ? 'CHUNK' : 'FINAL'}):`, {
        messageIndex,
        contentLength: content?.length || 0,
        contentPreview: content?.substring(0, 100) + '...',
        isChunk
      })
      
      // Skip analysis if content is empty or too short
      if (!content || content.trim().length < 10) {
        console.log('⏭️ Skipping analysis: content too short or empty')
        return
      }
      
      console.log('📊 Starting component analysis...')
      // Use existing component analysis system
      const decision = await analyzeContent({ content })
      
      if (decision && decision.decision === 'GENERATE_NOW') {
        // Create component based on the decision
        const component = {
          id: Date.now() + Math.random(),
          type: decision.component_type || 'unknown',
          title: `Generated ${decision.component_type || 'Component'}`,
          content: decision.extracted_data || {},
          reasoning: decision.reasoning || 'Auto-generated from content analysis',
          markdown: decision.markdown
        }
        
        // For chunk analysis, append to existing components; for final, replace
        const currentMessage = messages.value[messageIndex]
        const existingComponents = currentMessage?.components || []
        
        updateMessage(messageIndex, {
          components: isChunk ? [...existingComponents, component] : [component]
        })
        
        console.log(`✅ Generated component (${isChunk ? 'CHUNK' : 'FINAL'}): ${decision.component_type} (confidence: ${decision.confidence})`)
      }

    } catch (error) {
      console.error('Component analysis error:', error)
    }
  }

  return {
    messages,
    isLoading,
    isStreaming,
    input,
    sendMessage
  }
}
