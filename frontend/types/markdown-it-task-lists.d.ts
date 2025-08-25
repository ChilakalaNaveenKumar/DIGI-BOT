declare module 'markdown-it-task-lists' {
  import type MarkdownIt from 'markdown-it'
  
  interface TaskListOptions {
    enabled?: boolean
    label?: boolean
    labelAfter?: boolean
  }
  
  const taskLists: (md: MarkdownIt, options?: TaskListOptions) => void
  export = taskLists
}

declare module 'markdown-it-katex' {
  import type MarkdownIt from 'markdown-it'
  const katex: (md: MarkdownIt, options?: any) => void
  export = katex
}

declare module 'markdown-it-container' {
  import type MarkdownIt from 'markdown-it'
  
  interface ContainerOptions {
    validate?: (params: string) => boolean | RegExpMatchArray | null
    render?: (tokens: any[], idx: number) => string
  }
  
  const container: (md: MarkdownIt, name: string, options?: ContainerOptions) => void
  export = container
}

declare module 'markdown-it-emoji' {
  import type MarkdownIt from 'markdown-it'
  const emoji: (md: MarkdownIt, options?: any) => void
  export = emoji
}

declare module 'markdown-it-footnote' {
  import type MarkdownIt from 'markdown-it'
  const footnote: (md: MarkdownIt) => void
  export = footnote
}

declare module 'markdown-it-mark' {
  import type MarkdownIt from 'markdown-it'
  const mark: (md: MarkdownIt) => void
  export = mark
}

declare module 'markdown-it-ins' {
  import type MarkdownIt from 'markdown-it'
  const ins: (md: MarkdownIt) => void
  export = ins
}

declare module 'markdown-it-sub' {
  import type MarkdownIt from 'markdown-it'
  const sub: (md: MarkdownIt) => void
  export = sub
}

declare module 'markdown-it-sup' {
  import type MarkdownIt from 'markdown-it'
  const sup: (md: MarkdownIt) => void
  export = sup
}

declare module 'markdown-it-deflist' {
  import type MarkdownIt from 'markdown-it'
  const deflist: (md: MarkdownIt) => void
  export = deflist
}

declare module 'markdown-it-abbr' {
  import type MarkdownIt from 'markdown-it'
  const abbr: (md: MarkdownIt) => void
  export = abbr
}
