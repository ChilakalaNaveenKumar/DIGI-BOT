/**
 * Enhanced Content Detection - Includes Multimodal Formats
 * 
 * Extends the existing pattern detection to include:
 * - Vision/Image analysis results
 * - Audio transcription results  
 * - Tool execution results
 * - Search results
 * - All existing formats (math, code, json, tables, reasoning, diagrams, text)
 */

export const useEnhancedContentDetection = () => {
  
  /**
   * Detect content type based on content and metadata
   * Priority order based on specificity of patterns
   */
  const detectContentType = (content, metadata = {}) => {
    if (!content || typeof content !== 'string') return 'text'
    
    const trimmed = content.trim()
    
    // Check metadata first (from API responses)
    if (metadata.type) {
      switch (metadata.type) {
        case 'image_analysis': return 'vision'
        case 'audio_transcription': return 'audio_transcription'
        case 'audio_analysis': return 'audio_analysis'
        case 'tool_result': return 'tool'
        case 'batch_tool_results': return 'batch_tools'
        case 'search_result': return 'search'
        case 'news_search_result': return 'news'
      }
    }
    
    // Vision/Image analysis detection
    if (trimmed.includes('image analysis') || 
        trimmed.includes('visual content') ||
        trimmed.includes('I can see') ||
        trimmed.includes('The image shows') ||
        trimmed.includes('In this image')) {
      return 'vision'
    }
    
    // Audio/Speech detection
    if (trimmed.includes('transcription:') || 
        trimmed.includes('audio analysis') ||
        trimmed.includes('Transcribed text:') ||
        trimmed.includes('Audio content:')) {
      return 'audio_transcription'
    }
    
    // Tool result detection
    if (trimmed.includes('function result') || 
        trimmed.includes('tool output') ||
        trimmed.includes('Tool execution:') ||
        trimmed.includes('Function call:')) {
      return 'tool'
    }
    
    // Search result detection
    if (trimmed.includes('search results') || 
        trimmed.includes('web search') ||
        trimmed.includes('Found the following') ||
        trimmed.includes('Search query:')) {
      return 'search'
    }
    
    // Existing detection logic (from useRealPatternDetection)
    
    // 1. Math detection (highest priority - very specific LaTeX patterns)
    if (trimmed.includes('\\(') || trimmed.includes('\\[')) {
      return 'math'
    }
    
    // 2. JSON detection (specific ```json pattern)
    if (trimmed.includes('```json')) {
      return 'json'
    }
    
    // 3. Code detection (```{language} but NOT ```json)
    if (trimmed.includes('```') && !trimmed.includes('```json')) {
      return 'code'
    }
    
    // 4. Table detection (markdown table pattern)
    if (trimmed.includes('|') && trimmed.includes('---')) {
      return 'table'
    }
    
    // 5. Reasoning detection (numbered steps with bold headers)
    if (trimmed.includes('1. **') && (trimmed.includes('2. **') || trimmed.includes('**Step'))) {
      return 'reasoning'
    }
    
    // 6. Diagram detection (numbered steps with "Decision:" pattern)
    if (trimmed.includes('1. **') && trimmed.includes('Decision:')) {
      return 'diagram'
    }
    
    // 7. Default: plain text/markdown
    return 'text'
  }
  
  /**
   * Extract content based on detected type
   */
  const extractContent = (content, type, metadata = {}) => {
    if (!content) return ''
    
    switch (type) {
      case 'vision':
        return extractVisionContent(content, metadata)
      case 'audio_transcription':
        return extractAudioTranscriptionContent(content, metadata)
      case 'audio_analysis':
        return extractAudioAnalysisContent(content, metadata)
      case 'tool':
        return extractToolContent(content, metadata)
      case 'batch_tools':
        return extractBatchToolsContent(content, metadata)
      case 'search':
        return extractSearchContent(content, metadata)
      case 'news':
        return extractNewsContent(content, metadata)
      case 'code':
        return extractCodeContent(content)
      case 'json':
        return extractJsonContent(content)
      case 'math':
        return content // Keep LaTeX as-is
      case 'table':
        return content // Keep markdown table as-is
      case 'reasoning':
        return content // Keep numbered steps as-is
      case 'diagram':
        return content // Keep text flowchart as-is
      default:
        return content // Plain text/markdown
    }
  }
  
  /**
   * Extract vision analysis content
   */
  const extractVisionContent = (content, metadata) => {
    return {
      analysis: content,
      image: metadata.image || null,
      model: metadata.model || 'Unknown',
      prompt: metadata.prompt || 'Image analysis'
    }
  }
  
  /**
   * Extract audio transcription content
   */
  const extractAudioTranscriptionContent = (content, metadata) => {
    return {
      transcription: content,
      language: metadata.language || 'en',
      model: metadata.model || 'whisper-1',
      filename: metadata.filename || 'audio.wav'
    }
  }
  
  /**
   * Extract audio analysis content
   */
  const extractAudioAnalysisContent = (content, metadata) => {
    // Content should be an object with analysis results
    if (typeof content === 'object') {
      return content
    }
    
    // Fallback for string content
    return {
      analysis: content,
      analysis_type: metadata.analysis_type || 'general'
    }
  }
  
  /**
   * Extract tool execution content
   */
  const extractToolContent = (content, metadata) => {
    return {
      result: content,
      tool_name: metadata.tool_name || 'Unknown Tool',
      parameters: metadata.parameters || {},
      execution_time: metadata.execution_time || 0
    }
  }
  
  /**
   * Extract batch tools content
   */
  const extractBatchToolsContent = (content, metadata) => {
    return {
      results: Array.isArray(content) ? content : [content],
      executed_tools: metadata.executed_tools || [],
      total_count: metadata.count || 1
    }
  }
  
  /**
   * Extract search results content
   */
  const extractSearchContent = (content, metadata) => {
    return {
      results: Array.isArray(content) ? content : [],
      query: metadata.query || '',
      search_type: metadata.search_type || 'web',
      total_results: metadata.total_results || 0
    }
  }
  
  /**
   * Extract news search content
   */
  const extractNewsContent = (content, metadata) => {
    return {
      results: Array.isArray(content) ? content : [],
      query: metadata.query || '',
      time_range: metadata.time_range || 'week',
      total_results: metadata.total_results || 0
    }
  }
  
  // Existing extraction methods from useRealPatternDetection
  
  /**
   * Extract code content (remove ``` wrappers)
   */
  const extractCodeContent = (content) => {
    const match = content.match(/```\w*\n?([\s\S]*?)```/)
    return match ? match[1].trim() : content
  }
  
  /**
   * Extract language from code block
   */
  const extractCodeLanguage = (content) => {
    const match = content.match(/```(\w+)/)
    return match ? match[1] : 'text'
  }
  
  /**
   * Extract JSON content (remove ```json wrappers)
   */
  const extractJsonContent = (content) => {
    const match = content.match(/```json\n?([\s\S]*?)```/)
    return match ? match[1].trim() : content
  }
  
  /**
   * Clean content for display (minimal processing)
   */
  const cleanContent = (content) => {
    if (!content) return ''
    return content.trim()
  }
  
  /**
   * Get metadata for content type
   */
  const getContentMetadata = (content, type, originalMetadata = {}) => {
    const metadata = { type, ...originalMetadata }
    
    if (type === 'code') {
      metadata.language = extractCodeLanguage(content)
    }
    
    return metadata
  }
  
  /**
   * Check if content type is multimodal
   */
  const isMultimodalContent = (type) => {
    return ['vision', 'audio_transcription', 'audio_analysis', 'tool', 'batch_tools', 'search', 'news'].includes(type)
  }
  
  /**
   * Get display name for content type
   */
  const getContentTypeDisplayName = (type) => {
    const displayNames = {
      'vision': 'Image Analysis',
      'audio_transcription': 'Audio Transcription',
      'audio_analysis': 'Audio Analysis',
      'tool': 'Tool Result',
      'batch_tools': 'Batch Tool Results',
      'search': 'Web Search',
      'news': 'News Search',
      'math': 'Mathematical Expression',
      'code': 'Code Block',
      'json': 'JSON Data',
      'table': 'Data Table',
      'reasoning': 'Step-by-Step Reasoning',
      'diagram': 'Text Diagram',
      'text': 'Text Content'
    }
    
    return displayNames[type] || 'Unknown Content'
  }
  
  /**
   * Get icon for content type
   */
  const getContentTypeIcon = (type) => {
    const icons = {
      'vision': 'mdi:image-search',
      'audio_transcription': 'mdi:text-to-speech',
      'audio_analysis': 'mdi:waveform',
      'tool': 'mdi:tools',
      'batch_tools': 'mdi:format-list-bulleted',
      'search': 'mdi:web',
      'news': 'mdi:newspaper',
      'math': 'mdi:function-variant',
      'code': 'mdi:code-braces',
      'json': 'mdi:code-json',
      'table': 'mdi:table',
      'reasoning': 'mdi:format-list-numbered',
      'diagram': 'mdi:chart-tree',
      'text': 'mdi:text'
    }
    
    return icons[type] || 'mdi:file-document'
  }
  
  return {
    detectContentType,
    extractContent,
    extractVisionContent,
    extractAudioTranscriptionContent,
    extractAudioAnalysisContent,
    extractToolContent,
    extractBatchToolsContent,
    extractSearchContent,
    extractNewsContent,
    extractCodeContent,
    extractCodeLanguage,
    extractJsonContent,
    cleanContent,
    getContentMetadata,
    isMultimodalContent,
    getContentTypeDisplayName,
    getContentTypeIcon
  }
}

