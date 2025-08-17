/**
 * Simple Markdown Content Detection
 * Based on REAL AI output patterns (tested with OpenAI)
 * 
 * All AI models return standard markdown - no complex parsing needed!
 */

export const useSimpleMarkdownDetection = () => {
  
  /**
   * Detect content type based on actual AI markdown patterns
   */
  const detectContentType = (content) => {
    if (!content || typeof content !== 'string') return 'text'
    
    const trimmed = content.trim()
    
    // Code detection: ```{language} (but not ```json)
    if (trimmed.includes('```') && !trimmed.includes('```json')) {
      return 'code'
    }
    
    // JSON detection: ```json specifically
    if (trimmed.includes('```json')) {
      return 'json'
    }
    
    // Table detection: | column | with --- separators (markdown table)
    if (trimmed.includes('|') && trimmed.includes('---')) {
      return 'table'
    }
    
    // Default: plain text/markdown
    return 'text'
  }
  
  /**
   * Extract language from code block
   */
  const extractCodeLanguage = (content) => {
    const match = content.match(/```(\w+)/)
    return match ? match[1] : 'text'
  }
  
  /**
   * Extract code content (remove ``` wrappers)
   */
  const extractCodeContent = (content) => {
    const match = content.match(/```\w*\n?([\s\S]*?)```/)
    return match ? match[1].trim() : content
  }
  
  /**
   * Extract JSON content (remove ```json wrappers)
   */
  const extractJsonContent = (content) => {
    const match = content.match(/```json\n?([\s\S]*?)```/)
    return match ? match[1].trim() : content
  }
  
  /**
   * Clean content for display (no complex processing)
   */
  const cleanContent = (content) => {
    if (!content) return ''
    return content.trim()
  }
  
  return {
    detectContentType,
    extractCodeLanguage,
    extractCodeContent,
    extractJsonContent,
    cleanContent
  }
}
