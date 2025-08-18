/**
 * Composable for AI-powered component analysis
 * 
 * Handles content analysis and dynamic component generation
 */

import type { Ref } from 'vue'

// Helper function to safely extract error messages
function getErrorMessage(err: unknown): string {
  if (err instanceof Error) {
    return err.message
  }
  
  if (typeof err === 'object' && err !== null) {
    const errorObj = err as Record<string, unknown>
    
    // Try to extract nested error message
    if (errorObj.data && typeof errorObj.data === 'object' && errorObj.data !== null) {
      const dataObj = errorObj.data as Record<string, unknown>
      if (dataObj.error && typeof dataObj.error === 'object' && dataObj.error !== null) {
        const errorNestedObj = dataObj.error as Record<string, unknown>
        if (typeof errorNestedObj.message === 'string') {
          return errorNestedObj.message
        }
      }
    }
    
    // Try to extract direct message
    if (typeof errorObj.message === 'string') {
      return errorObj.message
    }
  }
  
  return 'Analysis failed'
}

interface ComponentDecision {
  decision: 'GENERATE_NOW' | 'NO_COMPONENT'
  component_type?: 'pie-chart' | 'bar-chart' | 'line-chart' | 'data-table'
  confidence: number
  reasoning: string
  markdown?: string
  extracted_data?: Record<string, unknown>
}

interface ContentAnalysisRequest {
  content: string
  context?: string
  user_preferences?: Record<string, unknown>
}

interface SupportedComponent {
  type: string
  name: string
  description: string
  best_for: string[]
  markdown_syntax: string
}

interface UseComponentAnalysisReturn {
  // State
  isAnalyzing: Ref<boolean>
  lastDecision: Ref<ComponentDecision | null>
  supportedComponents: Ref<SupportedComponent[]>
  error: Ref<string | null>
  
  // Methods
  analyzeContent: (request: ContentAnalysisRequest) => Promise<ComponentDecision | null>
  batchAnalyze: (requests: ContentAnalysisRequest[]) => Promise<ComponentDecision[]>
  loadSupportedComponents: () => Promise<void>
  clearError: () => void
  reset: () => void
}

export const useComponentAnalysis = (): UseComponentAnalysisReturn => {
  const config = useRuntimeConfig()
  
  // Reactive state
  const isAnalyzing = ref(false)
  const lastDecision = ref<ComponentDecision | null>(null)
  const supportedComponents = ref<SupportedComponent[]>([])
  const error = ref<string | null>(null)

  /**
   * Analyze content for component generation
   */
  const analyzeContent = async (
    request: ContentAnalysisRequest
  ): Promise<ComponentDecision | null> => {
    if (isAnalyzing.value) {
      console.warn('Analysis already in progress')
      return null
    }

    try {
      isAnalyzing.value = true
      error.value = null

      const response = await $fetch<ComponentDecision>('/v1/components/analyze', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: request,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      lastDecision.value = response
      
      console.log('Component analysis completed:', {
        decision: response.decision,
        type: response.component_type,
        confidence: response.confidence
      })

      return response

    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err)
      error.value = errorMessage
      
      console.error('Component analysis error:', {
        error: errorMessage,
        content: request.content.substring(0, 100) + '...'
      })

      // Return safe fallback
      const fallback: ComponentDecision = {
        decision: 'NO_COMPONENT',
        confidence: 0.0,
        reasoning: `Analysis failed: ${errorMessage}`
      }
      
      lastDecision.value = fallback
      return fallback

    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * Analyze multiple content pieces in batch
   */
  const batchAnalyze = async (
    requests: ContentAnalysisRequest[]
  ): Promise<ComponentDecision[]> => {
    if (requests.length === 0) return []
    
    if (requests.length > 10) {
      throw new Error('Batch size cannot exceed 10 items')
    }

    try {
      isAnalyzing.value = true
      error.value = null

      const response = await $fetch<{
        total: number
        results: Array<{
          index: number
          success: boolean
          decision?: ComponentDecision
          error?: string
        }>
      }>('/v1/components/batch-analyze', {
        method: 'POST',
        baseURL: config.public.apiBase,
        body: requests,
        headers: {
          'Content-Type': 'application/json'
        }
      })

      // Extract decisions from results
      const decisions: ComponentDecision[] = []
      
      for (const result of response.results) {
        if (result.success && result.decision) {
          decisions.push(result.decision)
        } else {
          // Add fallback decision for failed analyses
          decisions.push({
            decision: 'NO_COMPONENT',
            confidence: 0.0,
            reasoning: result.error || 'Analysis failed'
          })
        }
      }

      console.log('Batch analysis completed:', {
        total: response.total,
        successful: response.results.filter(r => r.success).length,
        generated: decisions.filter(d => d.decision === 'GENERATE_NOW').length
      })

      return decisions

    } catch (err: unknown) {
      const errorMessage = getErrorMessage(err) || 'Batch analysis failed'
      error.value = errorMessage
      
      console.error('Batch analysis error:', errorMessage)
      
      // Return fallback decisions for all requests
      return requests.map(() => ({
        decision: 'NO_COMPONENT' as const,
        confidence: 0.0,
        reasoning: `Batch analysis failed: ${errorMessage}`
      }))

    } finally {
      isAnalyzing.value = false
    }
  }

  /**
   * Load supported component types
   */
  const loadSupportedComponents = async (): Promise<void> => {
    try {
      const response = await $fetch<{
        components: SupportedComponent[]
        total_components: number
        version: string
      }>('/v1/components/supported-components', {
        baseURL: config.public.apiBase
      })

      supportedComponents.value = response.components
      
      console.log('Loaded supported components:', {
        count: response.total_components,
        version: response.version
      })

    } catch (err: unknown) {
      console.error('Failed to load supported components:', err)
      // Set default components as fallback
      supportedComponents.value = [
        {
          type: 'pie-chart',
          name: 'Pie Chart',
          description: 'Display percentage-based data as circular segments',
          best_for: ['market share', 'demographics', 'survey results'],
          markdown_syntax: ':::pie-chart'
        },
        {
          type: 'bar-chart',
          name: 'Bar Chart',
          description: 'Compare quantities across different categories',
          best_for: ['performance metrics', 'comparisons', 'rankings'],
          markdown_syntax: ':::bar-chart'
        },
        {
          type: 'line-chart',
          name: 'Line Chart',
          description: 'Show trends and changes over time',
          best_for: ['time series data', 'growth trends', 'performance tracking'],
          markdown_syntax: ':::line-chart'
        },
        {
          type: 'data-table',
          name: 'Data Table',
          description: 'Present structured data with sorting and filtering',
          best_for: ['detailed datasets', 'comparison tables', 'structured lists'],
          markdown_syntax: ':::data-table'
        }
      ]
    }
  }

  /**
   * Clear error state
   */
  const clearError = (): void => {
    error.value = null
  }

  /**
   * Reset all state
   */
  const reset = (): void => {
    isAnalyzing.value = false
    lastDecision.value = null
    error.value = null
  }

  // Load supported components on initialization
  onMounted(() => {
    loadSupportedComponents()
  })

  return {
    // State
    isAnalyzing: readonly(isAnalyzing),
    lastDecision: readonly(lastDecision),
    supportedComponents: supportedComponents as Ref<SupportedComponent[]>,
    error: readonly(error),
    
    // Methods
    analyzeContent,
    batchAnalyze,
    loadSupportedComponents,
    clearError,
    reset
  }
}
