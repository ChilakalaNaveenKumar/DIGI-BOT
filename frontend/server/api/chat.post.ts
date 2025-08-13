import { streamText } from 'ai'
import { openai } from '@ai-sdk/openai'
import { anthropic } from '@ai-sdk/anthropic'

export default defineEventHandler(async (event) => {
  try {
    const { messages, provider = 'openai', streamMode = 'text' } = await readBody(event)
    
    // Get runtime config for API keys
    const config = useRuntimeConfig()

    // Select the appropriate model based on provider
    let model
    switch (provider) {
      case 'openai':
        if (!config.openaiApiKey) {
          throw new Error('OpenAI API key not configured')
        }
        model = openai('gpt-5', {
          apiKey: config.openaiApiKey
        })
        break
      case 'anthropic':
        if (!config.anthropicApiKey) {
          throw new Error('Anthropic API key not configured')
        }
        model = anthropic('claude-4-opus', {
          apiKey: config.anthropicApiKey
        })
        break
      case 'grok':
        // For now, fallback to OpenAI since Grok isn't directly supported in AI SDK
        if (!config.openaiApiKey) {
          throw new Error('OpenAI API key not configured (fallback for Grok)')
        }
        model = openai('gpt-5', {
          apiKey: config.openaiApiKey
        })
        break
      default:
        model = openai('gpt-5', {
          apiKey: config.openaiApiKey
        })
    }

    // Stream the response using AI SDK
    const result = await streamText({
      model,
      messages,
      system: `You are Digi Setu AI, an intelligent assistant that helps transform static content into interactive learning experiences. You specialize in:

1. Creating educational content from documents and text
2. Building interactive quizzes and assessments  
3. Generating timelines and visual explanations
4. Designing flowcharts and diagrams
5. Converting complex topics into engaging formats

Always provide helpful, accurate, and educational responses. When showing code, use proper syntax highlighting with language specification. Be concise but thorough in your explanations.

Format your responses using proper markdown with:
- Code blocks with language specification: \`\`\`python, \`\`\`javascript, etc.
- Proper headings and structure
- Lists and emphasis where appropriate`,
      temperature: 0.7,
      maxTokens: 1000000,  // Maximum tokens for latest models
    })

    // Return the AI SDK stream response
    return result.toDataStreamResponse()
  } catch (error) {
    console.error('Chat API error:', error)
    
    // Return error response
    return new Response(
      JSON.stringify({ 
        error: 'An error occurred while processing your request.',
        details: error.message 
      }),
      { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      }
    )
  }
})
