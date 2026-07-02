import type MarkdownIt from 'markdown-it'

// === 空行注入 ===

export function blankLineInject(md: MarkdownIt) {
  md.core.ruler.after('block', 'blank-line', (state) => {
    const newTokens = []

    for (let i = 0; i < state.tokens.length; i++) {
      const token = state.tokens[i]
      newTokens.push(token)

      if (!token.type.endsWith('_close') || !token.map) continue
      if (i >= state.tokens.length - 1) continue

      const nextToken = state.tokens[i + 1]
      if (!nextToken.map) continue

      const gapLines = nextToken.map[0] - token.map[1]
      const extraLines = gapLines - 1

      for (let j = 0; j < extraLines; j++) {
        const open = new state.Token('paragraph_open', 'p', 1)
        open.attrSet('class', 'blank-line')
        const inline = new state.Token('inline', '', 0)
        inline.content = ' '
        inline.children = []
        newTokens.push(open, inline)
        newTokens.push(new state.Token('paragraph_close', 'p', -1))
      }
    }

    state.tokens = newTokens
  })
}
