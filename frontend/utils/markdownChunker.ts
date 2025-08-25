/**
 * Markdown Chunker - Groups markdown tokens into semantic blocks
 * Uses existing markdown-it parser to create meaningful content chunks for AI analysis
 */

import type { Token } from 'markdown-it'

export interface SemanticBlock {
  type: 'section' | 'paragraph' | 'list' | 'table' | 'code' | 'other'
  content: string
  rawContent: string // Original markdown
  tokens: Token[]
  hasData: boolean // Quick flag for data patterns
  startIndex: number // Character position in original text
  endIndex: number
}

export interface ChunkingResult {
  blocks: SemanticBlock[]
  totalBlocks: number
  dataBlocks: number // Blocks that likely contain data
}

/**
 * Parse markdown content into semantic blocks using existing markdown-it
 */
export function parseMarkdownIntoSemanticBlocks(
  content: string,
  md: any // MarkdownIt instance from useMarkdown
): ChunkingResult {
  try {
    const tokens = md.parse(content, {})
    const blocks: SemanticBlock[] = []
    let charPosition = 0

    let i = 0
    while (i < tokens.length) {
      const token = tokens[i]
      
      if (token.type === 'heading_open') {
        // Process section (header + content until next header)
        const headerLevel = parseInt(token.tag.substring(1))
        let sectionContent = ''
        let sectionTokens = [token]
        let startPos = charPosition
        i++
        
        // Get header text
        if (tokens[i]?.type === 'inline') {
          sectionContent = tokens[i].content
          sectionTokens.push(tokens[i])
          i++
        }
        
        // Skip header_close
        if (tokens[i]?.type === 'heading_close') {
          sectionTokens.push(tokens[i])
          i++
        }
        
        sectionContent += '\n\n'
        
        // Collect content until next header (any level)
        while (i < tokens.length) {
          const nextToken = tokens[i]
          
          // Stop at any header
          if (nextToken.type === 'heading_open') {
            break
          }
          
          // Add content
          if (nextToken.content) {
            sectionContent += nextToken.content
            if (nextToken.type === 'inline') {
              sectionContent += '\n'
            }
          }
          
          sectionTokens.push(nextToken)
          i++
        }
        
        const endPos = startPos + sectionContent.length
        charPosition = endPos
        
        blocks.push({
          type: 'section',
          content: sectionContent.trim(),
          rawContent: sectionContent.trim(),
          tokens: sectionTokens,
          hasData: hasDataPatterns(sectionContent),
          startIndex: startPos,
          endIndex: endPos
        })
        
      } else if (token.type === 'paragraph_open') {
        // Process standalone paragraph
        let paragraphContent = ''
        let paragraphTokens = [token]
        let startPos = charPosition
        i++
        
        // Get paragraph text
        if (tokens[i]?.type === 'inline') {
          paragraphContent = tokens[i].content
          paragraphTokens.push(tokens[i])
          i++
        }
        
        // Skip paragraph_close
        if (tokens[i]?.type === 'paragraph_close') {
          paragraphTokens.push(tokens[i])
          i++
        }
        
        const endPos = startPos + paragraphContent.length
        charPosition = endPos
        
        blocks.push({
          type: 'paragraph',
          content: paragraphContent.trim(),
          rawContent: paragraphContent.trim(),
          tokens: paragraphTokens,
          hasData: hasDataPatterns(paragraphContent),
          startIndex: startPos,
          endIndex: endPos
        })
        
      } else {
        // Skip other tokens
        i++
      }
    }

    const dataBlocks = blocks.filter(block => block.hasData).length

    return {
      blocks,
      totalBlocks: blocks.length,
      dataBlocks
    }
  } catch (error) {
    console.error('Markdown chunking failed:', error)
    return {
      blocks: [{
        type: 'other',
        content: content,
        rawContent: content,
        tokens: [],
        hasData: hasDataPatterns(content),
        startIndex: 0,
        endIndex: content.length
      }],
      totalBlocks: 1,
      dataBlocks: hasDataPatterns(content) ? 1 : 0
    }
  }
}

/**
 * Process a group of tokens into a semantic block
 */
function processTokenGroup(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock | null {
  const token = tokens[startIndex]
  if (!token) return null

  // Handle different token types
  switch (token.type) {
    case 'heading_open':
      return processSection(tokens, startIndex, originalContent, charIndex)
    
    case 'paragraph_open':
      return processParagraph(tokens, startIndex, originalContent, charIndex)
    
    case 'bullet_list_open':
    case 'ordered_list_open':
      return processList(tokens, startIndex, originalContent, charIndex)
    
    case 'table_open':
      return processTable(tokens, startIndex, originalContent, charIndex)
    
    case 'code_block':
    case 'fence':
      return processCodeBlock(tokens, startIndex, originalContent, charIndex)
    
    default:
      return null
  }
}

/**
 * Process a complete section (header + content until next header)
 */
function processSection(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock {
  const headerToken = tokens[startIndex]
  const headerLevel = parseInt(headerToken.tag.substring(1)) // h1 -> 1, h2 -> 2
  
  let endIndex = startIndex + 1
  let content = ''
  let rawContent = ''
  const blockTokens: Token[] = [headerToken]

  // Get header content
  if (tokens[startIndex + 1]?.type === 'inline') {
    content += tokens[startIndex + 1].content
    blockTokens.push(tokens[startIndex + 1])
    endIndex++
  }

  // Skip header_close
  if (tokens[endIndex]?.type === 'heading_close') {
    blockTokens.push(tokens[endIndex])
    endIndex++
  }

  content += '\n\n'

  // Collect content until next header of same or higher level
  while (endIndex < tokens.length) {
    const token = tokens[endIndex]
    
    // Stop at same or higher level header
    if (token.type === 'heading_open') {
      const nextHeaderLevel = parseInt(token.tag.substring(1))
      if (nextHeaderLevel <= headerLevel) {
        break
      }
    }

    // Add content
    if (token.content) {
      content += token.content
      if (token.type === 'inline') {
        content += '\n'
      }
    }

    blockTokens.push(token)
    endIndex++
  }

  // Estimate character positions (approximate)
  const estimatedStart = charIndex
  const estimatedEnd = estimatedStart + content.length

  return {
    type: 'section',
    content: content.trim(),
    rawContent: content.trim(),
    tokens: blockTokens,
    hasData: hasDataPatterns(content),
    startIndex: estimatedStart,
    endIndex: estimatedEnd
  }
}

/**
 * Process a standalone paragraph
 */
function processParagraph(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock {
  const blockTokens: Token[] = []
  let content = ''
  let endIndex = startIndex

  // paragraph_open
  blockTokens.push(tokens[endIndex])
  endIndex++

  // inline content
  if (tokens[endIndex]?.type === 'inline') {
    content = tokens[endIndex].content
    blockTokens.push(tokens[endIndex])
    endIndex++
  }

  // paragraph_close
  if (tokens[endIndex]?.type === 'paragraph_close') {
    blockTokens.push(tokens[endIndex])
  }

  const estimatedStart = charIndex
  const estimatedEnd = estimatedStart + content.length

  return {
    type: 'paragraph',
    content: content.trim(),
    rawContent: content.trim(),
    tokens: blockTokens,
    hasData: hasDataPatterns(content),
    startIndex: estimatedStart,
    endIndex: estimatedEnd
  }
}

/**
 * Process a complete list
 */
function processList(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock {
  const blockTokens: Token[] = []
  let content = ''
  let endIndex = startIndex
  const isOrdered = tokens[startIndex].type === 'ordered_list_open'

  // Find matching list_close
  let listDepth = 1
  blockTokens.push(tokens[endIndex])
  endIndex++

  while (endIndex < tokens.length && listDepth > 0) {
    const token = tokens[endIndex]
    blockTokens.push(token)

    if (token.type === 'bullet_list_open' || token.type === 'ordered_list_open') {
      listDepth++
    } else if (token.type === 'bullet_list_close' || token.type === 'ordered_list_close') {
      listDepth--
    } else if (token.type === 'inline' && token.content) {
      content += token.content + '\n'
    }

    endIndex++
  }

  const estimatedStart = charIndex
  const estimatedEnd = estimatedStart + content.length

  return {
    type: 'list',
    content: content.trim(),
    rawContent: content.trim(),
    tokens: blockTokens,
    hasData: hasDataPatterns(content),
    startIndex: estimatedStart,
    endIndex: estimatedEnd
  }
}

/**
 * Process a table
 */
function processTable(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock {
  const blockTokens: Token[] = []
  let content = ''
  let endIndex = startIndex

  // Find matching table_close
  let tableDepth = 1
  blockTokens.push(tokens[endIndex])
  endIndex++

  while (endIndex < tokens.length && tableDepth > 0) {
    const token = tokens[endIndex]
    blockTokens.push(token)

    if (token.type === 'table_open') {
      tableDepth++
    } else if (token.type === 'table_close') {
      tableDepth--
    } else if (token.type === 'inline' && token.content) {
      content += token.content + ' | '
    }

    endIndex++
  }

  const estimatedStart = charIndex
  const estimatedEnd = estimatedStart + content.length

  return {
    type: 'table',
    content: content.trim(),
    rawContent: content.trim(),
    tokens: blockTokens,
    hasData: true, // Tables almost always contain data
    startIndex: estimatedStart,
    endIndex: estimatedEnd
  }
}

/**
 * Process a code block
 */
function processCodeBlock(
  tokens: Token[],
  startIndex: number,
  originalContent: string,
  charIndex: number
): SemanticBlock {
  const token = tokens[startIndex]
  const content = token.content || ''

  const estimatedStart = charIndex
  const estimatedEnd = estimatedStart + content.length

  return {
    type: 'code',
    content: content.trim(),
    rawContent: content.trim(),
    tokens: [token],
    hasData: hasDataPatterns(content),
    startIndex: estimatedStart,
    endIndex: estimatedEnd
  }
}

/**
 * Quick check if content contains data patterns
 */
function hasDataPatterns(content: string): boolean {
  const dataPatterns = [
    /\d+%/,                          // Percentages: 45%
    /\$[\d,]+/,                      // Money: $1,000
    /\d{1,3}(,\d{3})*/,             // Large numbers: 1,000
    /\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/i, // Months
    /\b(Q[1-4]|Quarter [1-4])\b/i,  // Quarters
    /\d+:\s*\d+/,                   // Ratios: 3:1
    /\d+\s*(vs|versus)\s*\d+/i,     // Comparisons: 100 vs 200
    /\d+\.\d+/,                     // Decimals: 3.14
    /\b\d+\s*(hours?|days?|months?|years?)\b/i, // Time units
  ]

  return dataPatterns.some(pattern => pattern.test(content))
}

/**
 * Get blocks that likely contain data for prioritized analysis
 */
export function getDataBlocks(blocks: SemanticBlock[]): SemanticBlock[] {
  return blocks.filter(block => block.hasData)
}

/**
 * Get blocks by type
 */
export function getBlocksByType(blocks: SemanticBlock[], type: SemanticBlock['type']): SemanticBlock[] {
  return blocks.filter(block => block.type === type)
}
