import { nextTick } from 'vue'
// Note: These would need to be installed via npm
// import html2canvas from 'html2canvas'
// import jsPDF from 'jspdf'

/**
 * Component Export System
 * 
 * Provides comprehensive export functionality for all progressive components
 * supporting multiple formats: SVG, PNG, PDF, HTML, and more.
 */
export const useComponentExport = () => {
  
  // Export formats
  const exportFormats = {
    SVG: 'svg',
    PNG: 'png',
    JPEG: 'jpeg',
    PDF: 'pdf',
    HTML: 'html',
    JSON: 'json',
    CSV: 'csv',
    MARKDOWN: 'markdown'
  }
  
  // Quality settings
  const qualitySettings = {
    low: { scale: 1, quality: 0.7 },
    medium: { scale: 2, quality: 0.85 },
    high: { scale: 3, quality: 1.0 }
  }
  
  /**
   * Export component as SVG
   */
  const exportAsSVG = async (element, options = {}) => {
    try {
      const {
        filename = 'component',
        includeStyles = true,
        includeMetadata = true
      } = options
      
      // Clone the element to avoid modifying the original
      const clonedElement = element.cloneNode(true)
      
      // Get computed styles
      const computedStyles = window.getComputedStyle(element)
      const styles = includeStyles ? extractStyles(element) : ''
      
      // Create SVG wrapper
      const svg = createSVGWrapper(clonedElement, computedStyles, styles)
      
      // Add metadata if requested
      if (includeMetadata) {
        addSVGMetadata(svg, {
          title: filename,
          description: 'Exported from Digi Setu',
          created: new Date().toISOString()
        })
      }
      
      // Convert to string and download
      const svgString = new XMLSerializer().serializeToString(svg)
      downloadFile(svgString, `${filename}.svg`, 'image/svg+xml')
      
      return { success: true, format: 'svg', size: svgString.length }
      
    } catch (error) {
      console.error('SVG export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export component as PNG/JPEG
   */
  const exportAsImage = async (element, options = {}) => {
    try {
      const {
        filename = 'component',
        format = 'png',
        quality = 'high',
        backgroundColor = '#ffffff',
        includeMetadata = true
      } = options
      
      const qualityConfig = qualitySettings[quality] || qualitySettings.high
      
      // Wait for any pending renders
      await nextTick()
      
      // Check if html2canvas is available
      if (typeof window.html2canvas === 'undefined') {
        throw new Error('html2canvas library not installed. Run: npm install html2canvas')
      }
      
      // Generate canvas
      const canvas = await window.html2canvas(element, {
        scale: qualityConfig.scale,
        backgroundColor,
        useCORS: true,
        allowTaint: true,
        logging: false,
        width: element.offsetWidth,
        height: element.offsetHeight
      })
      
      // Convert to blob
      const blob = await new Promise(resolve => {
        canvas.toBlob(resolve, `image/${format}`, qualityConfig.quality)
      })
      
      // Add metadata to PNG if supported
      if (format === 'png' && includeMetadata) {
        // PNG metadata would require additional library
        // For now, we'll skip metadata for images
      }
      
      // Download
      const url = URL.createObjectURL(blob)
      downloadFromURL(url, `${filename}.${format}`)
      URL.revokeObjectURL(url)
      
      return {
        success: true,
        format,
        size: blob.size,
        dimensions: {
          width: canvas.width,
          height: canvas.height
        }
      }
      
    } catch (error) {
      console.error('Image export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export component as PDF
   */
  const exportAsPDF = async (element, options = {}) => {
    try {
      const {
        filename = 'component',
        orientation = 'portrait',
        format = 'a4',
        quality = 'high',
        includeMetadata = true
      } = options
      
      // Check if jsPDF is available
      if (typeof window.jsPDF === 'undefined') {
        throw new Error('jsPDF library not installed. Run: npm install jspdf')
      }
      
      // Create PDF document
      const pdf = new window.jsPDF({
        orientation,
        unit: 'mm',
        format
      })
      
      // Add metadata
      if (includeMetadata) {
        pdf.setProperties({
          title: filename,
          subject: 'Component Export',
          author: 'Digi Setu',
          creator: 'Digi Setu Export System',
          creationDate: new Date()
        })
      }
      
      // Convert element to canvas first
      const canvas = await window.html2canvas(element, {
        scale: qualitySettings[quality].scale,
        useCORS: true,
        allowTaint: true
      })
      
      // Calculate dimensions to fit page
      const imgData = canvas.toDataURL('image/png')
      const imgWidth = pdf.internal.pageSize.getWidth() - 20 // 10mm margin on each side
      const imgHeight = (canvas.height * imgWidth) / canvas.width
      
      // Add image to PDF
      pdf.addImage(imgData, 'PNG', 10, 10, imgWidth, imgHeight)
      
      // Save PDF
      pdf.save(`${filename}.pdf`)
      
      return {
        success: true,
        format: 'pdf',
        pages: 1,
        size: pdf.output('blob').size
      }
      
    } catch (error) {
      console.error('PDF export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export component as HTML
   */
  const exportAsHTML = async (element, options = {}) => {
    try {
      const {
        filename = 'component',
        includeStyles = true,
        includeMetadata = true,
        standalone = true
      } = options
      
      // Clone element
      const clonedElement = element.cloneNode(true)
      
      // Extract styles
      const styles = includeStyles ? extractAllStyles(element) : ''
      
      // Create HTML document
      let html = ''
      
      if (standalone) {
        html = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${filename}</title>
    ${includeMetadata ? `
    <meta name="generator" content="Digi Setu Export System">
    <meta name="created" content="${new Date().toISOString()}">
    ` : ''}
    <style>
        body { margin: 0; padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        ${styles}
    </style>
</head>
<body>
    ${clonedElement.outerHTML}
</body>
</html>`
      } else {
        html = clonedElement.outerHTML
      }
      
      // Download
      downloadFile(html, `${filename}.html`, 'text/html')
      
      return {
        success: true,
        format: 'html',
        size: html.length,
        standalone
      }
      
    } catch (error) {
      console.error('HTML export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export table data as CSV
   */
  const exportTableAsCSV = async (tableData, options = {}) => {
    try {
      const {
        filename = 'table-data',
        delimiter = ',',
        includeHeaders = true,
        includeMetadata = false
      } = options
      
      if (!tableData || !tableData.headers || !tableData.rows) {
        throw new Error('Invalid table data format')
      }
      
      let csv = ''
      
      // Add metadata as comments
      if (includeMetadata) {
        csv += `# Exported from Digi Setu\n`
        csv += `# Created: ${new Date().toISOString()}\n`
        csv += `# Rows: ${tableData.rows.length}\n`
        csv += `# Columns: ${tableData.headers.length}\n`
        csv += `\n`
      }
      
      // Add headers
      if (includeHeaders && tableData.headers.length > 0) {
        csv += tableData.headers
          .map(header => escapeCSVField(header, delimiter))
          .join(delimiter) + '\n'
      }
      
      // Add data rows
      tableData.rows.forEach(row => {
        const csvRow = row
          .map(cell => escapeCSVField(String(cell || ''), delimiter))
          .join(delimiter)
        csv += csvRow + '\n'
      })
      
      // Download
      downloadFile(csv, `${filename}.csv`, 'text/csv')
      
      return {
        success: true,
        format: 'csv',
        size: csv.length,
        rows: tableData.rows.length,
        columns: tableData.headers.length
      }
      
    } catch (error) {
      console.error('CSV export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export data as JSON
   */
  const exportAsJSON = async (data, options = {}) => {
    try {
      const {
        filename = 'data',
        pretty = true,
        includeMetadata = true
      } = options
      
      let exportData = data
      
      // Add metadata wrapper
      if (includeMetadata) {
        exportData = {
          metadata: {
            exported_from: 'Digi Setu',
            created: new Date().toISOString(),
            version: '1.0'
          },
          data: data
        }
      }
      
      // Stringify
      const jsonString = pretty 
        ? JSON.stringify(exportData, null, 2)
        : JSON.stringify(exportData)
      
      // Download
      downloadFile(jsonString, `${filename}.json`, 'application/json')
      
      return {
        success: true,
        format: 'json',
        size: jsonString.length,
        pretty
      }
      
    } catch (error) {
      console.error('JSON export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  /**
   * Export as Markdown
   */
  const exportAsMarkdown = async (data, options = {}) => {
    try {
      const {
        filename = 'content',
        includeMetadata = true
      } = options
      
      let markdown = ''
      
      // Add metadata header
      if (includeMetadata) {
        markdown += `---\n`
        markdown += `title: ${filename}\n`
        markdown += `exported_from: Digi Setu\n`
        markdown += `created: ${new Date().toISOString()}\n`
        markdown += `---\n\n`
      }
      
      // Convert data to markdown based on type
      if (data.type === 'table' && data.headers && data.rows) {
        markdown += convertTableToMarkdown(data)
      } else if (data.type === 'code') {
        markdown += convertCodeToMarkdown(data)
      } else if (typeof data === 'string') {
        markdown += data
      } else {
        markdown += '```json\n' + JSON.stringify(data, null, 2) + '\n```'
      }
      
      // Download
      downloadFile(markdown, `${filename}.md`, 'text/markdown')
      
      return {
        success: true,
        format: 'markdown',
        size: markdown.length
      }
      
    } catch (error) {
      console.error('Markdown export failed:', error)
      return { success: false, error: error.message }
    }
  }
  
  // Helper functions
  const createSVGWrapper = (element, computedStyles, styles) => {
    const rect = element.getBoundingClientRect()
    
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg')
    svg.setAttribute('width', rect.width)
    svg.setAttribute('height', rect.height)
    svg.setAttribute('viewBox', `0 0 ${rect.width} ${rect.height}`)
    
    // Add styles
    if (styles) {
      const styleElement = document.createElementNS('http://www.w3.org/2000/svg', 'style')
      styleElement.textContent = styles
      svg.appendChild(styleElement)
    }
    
    // Convert HTML to foreignObject
    const foreignObject = document.createElementNS('http://www.w3.org/2000/svg', 'foreignObject')
    foreignObject.setAttribute('width', '100%')
    foreignObject.setAttribute('height', '100%')
    foreignObject.appendChild(element)
    
    svg.appendChild(foreignObject)
    return svg
  }
  
  const addSVGMetadata = (svg, metadata) => {
    const titleElement = document.createElementNS('http://www.w3.org/2000/svg', 'title')
    titleElement.textContent = metadata.title
    svg.insertBefore(titleElement, svg.firstChild)
    
    const descElement = document.createElementNS('http://www.w3.org/2000/svg', 'desc')
    descElement.textContent = metadata.description
    svg.insertBefore(descElement, titleElement.nextSibling)
  }
  
  const extractStyles = (element) => {
    const styles = []
    const sheets = document.styleSheets
    
    for (let i = 0; i < sheets.length; i++) {
      try {
        const rules = sheets[i].cssRules || sheets[i].rules
        for (let j = 0; j < rules.length; j++) {
          if (rules[j].style && element.matches && element.matches(rules[j].selectorText)) {
            styles.push(rules[j].cssText)
          }
        }
      } catch (e) {
        // Cross-origin stylesheet, skip
      }
    }
    
    return styles.join('\n')
  }
  
  const extractAllStyles = (element) => {
    // Get all stylesheets and extract relevant rules
    let allStyles = ''
    
    try {
      for (const sheet of document.styleSheets) {
        try {
          for (const rule of sheet.cssRules) {
            if (rule.cssText) {
              allStyles += rule.cssText + '\n'
            }
          }
        } catch (e) {
          // Cross-origin or other access issues
        }
      }
    } catch (e) {
      console.warn('Could not extract all styles:', e)
    }
    
    return allStyles
  }
  
  const escapeCSVField = (field, delimiter) => {
    if (field.includes(delimiter) || field.includes('"') || field.includes('\n')) {
      return '"' + field.replace(/"/g, '""') + '"'
    }
    return field
  }
  
  const convertTableToMarkdown = (tableData) => {
    let md = ''
    
    // Headers
    if (tableData.headers && tableData.headers.length > 0) {
      md += '| ' + tableData.headers.join(' | ') + ' |\n'
      md += '|' + tableData.headers.map(() => '---').join('|') + '|\n'
    }
    
    // Rows
    if (tableData.rows && tableData.rows.length > 0) {
      tableData.rows.forEach(row => {
        md += '| ' + row.join(' | ') + ' |\n'
      })
    }
    
    return md
  }
  
  const convertCodeToMarkdown = (codeData) => {
    const language = codeData.language || ''
    const code = codeData.content || codeData.code || ''
    
    return '```' + language + '\n' + code + '\n```\n'
  }
  
  const downloadFile = (content, filename, mimeType) => {
    const blob = new Blob([content], { type: mimeType })
    const url = URL.createObjectURL(blob)
    downloadFromURL(url, filename)
    URL.revokeObjectURL(url)
  }
  
  const downloadFromURL = (url, filename) => {
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }
  
  // Component-specific export functions
  const exportTable = async (element, tableData, format, options = {}) => {
    switch (format) {
      case exportFormats.CSV:
        return await exportTableAsCSV(tableData, options)
      case exportFormats.JSON:
        return await exportAsJSON(tableData, options)
      case exportFormats.MARKDOWN:
        return await exportAsMarkdown({ type: 'table', ...tableData }, options)
      case exportFormats.HTML:
        return await exportAsHTML(element, options)
      case exportFormats.SVG:
        return await exportAsSVG(element, options)
      case exportFormats.PNG:
        return await exportAsImage(element, { ...options, format: 'png' })
      case exportFormats.PDF:
        return await exportAsPDF(element, options)
      default:
        throw new Error(`Unsupported export format: ${format}`)
    }
  }
  
  const exportCode = async (element, codeData, format, options = {}) => {
    switch (format) {
      case exportFormats.MARKDOWN:
        return await exportAsMarkdown({ type: 'code', ...codeData }, options)
      case exportFormats.JSON:
        return await exportAsJSON(codeData, options)
      case exportFormats.HTML:
        return await exportAsHTML(element, options)
      case exportFormats.SVG:
        return await exportAsSVG(element, options)
      case exportFormats.PNG:
        return await exportAsImage(element, { ...options, format: 'png' })
      case exportFormats.PDF:
        return await exportAsPDF(element, options)
      default:
        throw new Error(`Unsupported export format: ${format}`)
    }
  }
  
  const exportDiagram = async (element, diagramData, format, options = {}) => {
    switch (format) {
      case exportFormats.SVG:
        return await exportAsSVG(element, options)
      case exportFormats.PNG:
        return await exportAsImage(element, { ...options, format: 'png' })
      case exportFormats.PDF:
        return await exportAsPDF(element, options)
      case exportFormats.HTML:
        return await exportAsHTML(element, options)
      case exportFormats.JSON:
        return await exportAsJSON(diagramData, options)
      default:
        throw new Error(`Unsupported export format: ${format}`)
    }
  }
  
  return {
    // Export formats
    exportFormats,
    qualitySettings,
    
    // Generic export functions
    exportAsSVG,
    exportAsImage,
    exportAsPDF,
    exportAsHTML,
    exportAsJSON,
    exportAsMarkdown,
    exportTableAsCSV,
    
    // Component-specific exports
    exportTable,
    exportCode,
    exportDiagram,
    
    // Utility functions
    downloadFile,
    downloadFromURL
  }
}
