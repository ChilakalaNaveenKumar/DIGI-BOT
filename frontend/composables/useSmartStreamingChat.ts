// Smart Streaming Chat with Real-time Component Analysis
import type { Message } from '~/types'
import { mockMarkdownContent } from '~/utils/mockMarkdownContent'
import { getRandomMockResponse, getMockResponseById } from '~/utils/complexMockData'
import { parseMarkdownIntoSemanticBlocks, type SemanticBlock } from '~/utils/markdownChunker'

interface AnalysisState {
  waitingBlocks: SemanticBlock[]
  currentBlockIndex: number
  isAnalyzing: boolean
}

export const useSmartStreamingChat = () => {
  const messages = ref<Message[]>([])
  const isLoading = ref(false)
  const input = ref('')
  const isStreaming = ref(false)
  
  // Component analysis composables
  const { analyzeContent, isAnalyzing } = useComponentAnalysis()
  const { md } = useMarkdown()
  
  const sendMessage = async (content: string) => {
    if (!content.trim() || isLoading.value || isStreaming.value) return
    
    // Add user message
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
    
    // Prepare assistant message for streaming
    const assistantMessage: Message = {
      id: Date.now() + 1,
      content: '',
      role: 'assistant' as const,
      timestamp: new Date(),
      isLoading: false,
      isStreaming: true,
      reasoning: '',
      components: []
    }
    messages.value.push(assistantMessage)
    
    try {
      const isHiMessage = content.toLowerCase().trim() === 'hi'
      
      if (isHiMessage) {
        // Original markdown demo with smart streaming
        await smartStreamWithAnalysis(assistantMessage.id, mockMarkdownContent)
      } else if (content.toLowerCase().includes('test')) {
        // Use comprehensive business analysis for 'test'
        const mockResponse = getMockResponseById('comprehensive-business-analysis')
        console.log(`🎯 Using comprehensive test data: ${mockResponse.id} (expects: ${mockResponse.expectedComponents.join(', ')})`)
        await smartStreamWithAnalysis(assistantMessage.id, mockResponse.content)
      } else if (content.toLowerCase().includes('demo')) {
        // Use random mock data for 'demo'
        const mockResponse = getRandomMockResponse()
        console.log(`🎯 Using random mock data: ${mockResponse.id} (expects: ${mockResponse.expectedComponents.join(', ')})`)
        await smartStreamWithAnalysis(assistantMessage.id, mockResponse.content)
      } else {
        // Regular message with smart analysis
        await handleRegularMessage(assistantMessage, content)
      }
      
    } catch (error) {
      console.error('Smart streaming chat error:', error)
      
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
   * Smart streaming with real-time component analysis
   */
  const smartStreamWithAnalysis = async (messageId: number, content: string) => {
    const messageIndex = messages.value.findIndex(m => m.id === messageId)
    if (messageIndex === -1) return

    console.log('🧠 Starting smart streaming with semantic analysis...')
    
    // Parse content into semantic blocks
    const { blocks } = parseMarkdownIntoSemanticBlocks(content, md)
    console.log(`📝 Parsed ${blocks.length} semantic blocks:`, blocks.map(b => `${b.type}(${b.hasData ? 'DATA' : 'text'})`))
    
    const message = messages.value[messageIndex]
    if (!message) return
    
    message.isLoading = false
    message.isStreaming = true
    message.content = ''
    message.components = []
    message.reasoning = `Smart streaming with real-time analysis of ${blocks.length} semantic blocks...`

    // Analysis state
    const analysisState: AnalysisState = {
      waitingBlocks: [],
      currentBlockIndex: 0,
      isAnalyzing: false
    }

    // Stream each block with analysis
    for (let i = 0; i < blocks.length; i++) {
      const block = blocks[i]
      if (!block) continue
      
      console.log(`\n🔍 Processing block ${i + 1}/${blocks.length}: ${block.type}`)
      
      // Stream the block content
      await streamBlock(message, block)
      
      // Analyze the block
      await analyzeBlock(message, block, analysisState, i)
      
      // Small pause between blocks for better UX
      await new Promise(resolve => setTimeout(resolve, 100))
    }

    // Final analysis of any remaining waiting blocks
    if (analysisState.waitingBlocks.length > 0) {
      await generateComponentFromWaitingBlocks(message, analysisState)
    }

    // Streaming complete
    message.isStreaming = false
    isLoading.value = false
    isStreaming.value = false
    
    console.log('✅ Smart streaming completed!')
  }

  /**
   * Stream a single semantic block
   */
  const streamBlock = async (message: Message, block: SemanticBlock): Promise<void> => {
    return new Promise((resolve) => {
      const blockContent = block.content
      let charIndex = 0
      
      const streamInterval = setInterval(() => {
        if (charIndex >= blockContent.length) {
          clearInterval(streamInterval)
          message.content += '\n\n' // Add spacing between blocks
          resolve()
          return
        }

        // Stream in chunks for smooth experience
        const chunkSize = Math.random() > 0.8 ? Math.floor(Math.random() * 3) + 1 : Math.floor(Math.random() * 2) + 1
        const nextIndex = Math.min(charIndex + chunkSize, blockContent.length)
        const chunk = blockContent.substring(charIndex, nextIndex)
        
        message.content += chunk
        charIndex = nextIndex

      }, 30 + Math.random() * 20) // Comfortable reading speed
    })
  }

  /**
   * Analyze a block and decide: IGNORE, WAIT, or GENERATE
   */
  const analyzeBlock = async (
    message: Message, 
    block: SemanticBlock, 
    state: AnalysisState,
    blockIndex: number
  ) => {
    // Skip analysis for non-data blocks
    if (!block.hasData) {
      console.log(`⏭️  Block ${blockIndex + 1}: IGNORE (no data patterns)`)
      return
    }

    state.isAnalyzing = true
    console.log(`🔍 Block ${blockIndex + 1}: Analyzing for components...`)

    try {
      // Create analysis context from waiting blocks + current block
      const contextBlocks = [...state.waitingBlocks, block]
      const contextContent = contextBlocks.map(b => b.content).join('\n\n')
      
      const decision = await analyzeContent({
        content: contextContent,
        context: `Semantic block analysis - Block ${blockIndex + 1} of type ${block.type}`
      })

      if (!decision) {
        console.log(`❌ Block ${blockIndex + 1}: Analysis failed`)
        return
      }

      console.log(`📊 Block ${blockIndex + 1}: ${decision.decision} (${(decision.confidence * 100).toFixed(1)}% confidence)`)
      console.log(`💭 Reasoning: ${decision.reasoning}`)

      // Handle AI decision
      switch (decision.decision) {
        case 'NO_COMPONENT':
          // IGNORE - clear waiting blocks and continue
          state.waitingBlocks = []
          break
          
        case 'GENERATE_NOW':
          // GENERATE - create component from waiting blocks + current
          state.waitingBlocks.push(block)
          await generateComponentFromWaitingBlocks(message, state, decision)
          state.waitingBlocks = []
          break
          
        default:
          // WAIT - add to waiting blocks (this would be a new decision type we'd add)
          state.waitingBlocks.push(block)
          break
      }

    } catch (error) {
      console.error(`❌ Block ${blockIndex + 1} analysis error:`, error)
    } finally {
      state.isAnalyzing = false
    }
  }

  /**
   * Generate component from accumulated waiting blocks
   */
  const generateComponentFromWaitingBlocks = async (
    message: Message,
    state: AnalysisState,
    decision?: { decision: string; component_type?: string; markdown?: string; confidence?: number }
  ) => {
    if (state.waitingBlocks.length === 0) return

    console.log(`🎨 Generating component from ${state.waitingBlocks.length} waiting blocks...`)

    // If no decision provided, analyze the accumulated content
    if (!decision) {
      const contextContent = state.waitingBlocks.map(b => b.content).join('\n\n')
      const result = await analyzeContent({
        content: contextContent,
        context: 'Accumulated waiting blocks analysis'
      })
      
      if (!result) return
      
      decision = {
        decision: result.decision,
        component_type: result.component_type,
        markdown: result.markdown,
        confidence: result.confidence
      }
    }

    if (decision?.decision === 'GENERATE_NOW' && decision.markdown) {
      // Inject component markdown directly into the content stream
      const componentMarkdown = `\n\n${decision.markdown}\n\n`
      message.content += componentMarkdown

      console.log(`✅ Component injected inline: ${decision.component_type}`)
    }
  }

  /**
   * Handle regular messages with smart analysis
   */
  const handleRegularMessage = async (assistantMessage: Message, userContent: string) => {
    const response = `I understand you're asking about: "${userContent}". Let me help you with that!`
    
    // Stream response and then analyze
    await smartStreamWithAnalysis(assistantMessage.id, response + '\n\n' + userContent)
  }

  const clearMessages = () => {
    messages.value = []
  }

  return {
    messages,
    isLoading: readonly(isLoading),
    isStreaming: readonly(isStreaming),
    isAnalyzing: readonly(isAnalyzing),
    input,
    sendMessage,
    clearMessages
  }
}
