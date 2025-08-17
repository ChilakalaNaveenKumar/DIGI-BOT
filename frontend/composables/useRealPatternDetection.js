/**
 * Real Pattern Detection - Based on ACTUAL AI Testing Results
 * 
 * This detection is based on comprehensive testing of OpenAI responses.
 * See: /comprehensive_ai_format_tests.md for test results
 */

export const useRealPatternDetection = () => {
  
  /**
   * Detect content type based on REAL AI output patterns
   * Priority order based on specificity of patterns
   */
  const detectContentType = (content) => {
    if (!content || typeof content !== 'string') return 'text'
    
    const trimmed = content.trim()
    
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
  const extractContent = (content, type) => {
    if (!content) return ''
    
    switch (type) {
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
  const getContentMetadata = (content, type) => {
    const metadata = { type }
    
    if (type === 'code') {
      metadata.language = extractCodeLanguage(content)
    }
    
    return metadata
  }
  
  return {
    detectContentType,
    extractContent,
    extractCodeContent,
    extractCodeLanguage,
    extractJsonContent,
    cleanContent,
    getContentMetadata
  }
}
