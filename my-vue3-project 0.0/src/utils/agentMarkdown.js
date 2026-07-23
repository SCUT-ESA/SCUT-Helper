/**
 * App 兼容 Markdown → HTML（不依赖 marked）
 * 原因：marked 使用 /[\p{L}\p{N}]/u，uni-app App JS 引擎不支持，会白屏
 */

/**
 * 拆分 <think> 区块
 * @returns {{ phase: 'plain'|'thinking'|'done', prefix: string, think: string, main: string }}
 */
export function splitThinkContent(fullText) {
  const raw = fullText || ''
  if (!raw.includes('<think>')) {
    return { phase: 'plain', prefix: '', think: '', main: raw }
  }
  const parts = raw.split('<think>')
  const prefix = parts[0] || ''
  const rest = parts[1] || ''
  if (rest.includes('</think>')) {
    const sub = rest.split('</think>')
    return {
      phase: 'done',
      prefix,
      think: sub[0] || '',
      main: sub.slice(1).join('</think>')
    }
  }
  return {
    phase: 'thinking',
    prefix,
    think: rest,
    main: ''
  }
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

function inlineMd(text) {
  let s = escapeHtml(text || '')

  // 行内代码
  s = s.replace(/`([^`]+)`/g, '<code style="background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:13px;">$1</code>')

  // 链接 [text](url)
  s = s.replace(
    /\[([^\]]+)\]\((https?:\/\/[^)\s]+)\)/g,
    '<a href="$2" style="color:#529bcc;text-decoration:underline;">$1</a>'
  )

  // 粗体 **text** 或 __text__
  s = s.replace(/\*\*([^*]+)\*\*/g, '<strong style="font-weight:700;color:#1e293b;">$1</strong>')
  s = s.replace(/__([^_]+)__/g, '<strong style="font-weight:700;color:#1e293b;">$1</strong>')

  // 斜体 *text* 或 _text_（简单处理，避免吃掉已有标签）
  s = s.replace(/(^|[^*])\*([^*\n]+)\*([^*]|$)/g, '$1<em>$2</em>$3')

  // 自动链接 http(s)
  s = s.replace(
    /(^|[\s>])(https?:\/\/[^\s<]+)/g,
    '$1<a href="$2" style="color:#529bcc;text-decoration:underline;">$2</a>'
  )

  return s
}

function isTableSep(line) {
  return /^\s*\|?[\s:|-]+\|[\s:|-|]*\|?\s*$/.test(line)
}

function parseTable(lines, start) {
  const headerLine = lines[start]
  const sepLine = lines[start + 1]
  if (!headerLine || !sepLine || !isTableSep(sepLine)) return null

  const splitRow = (line) => {
    let t = line.trim()
    if (t.charAt(0) === '|') t = t.slice(1)
    if (t.charAt(t.length - 1) === '|') t = t.slice(0, -1)
    return t.split('|').map((c) => c.trim())
  }

  const headers = splitRow(headerLine)
  const rows = []
  let i = start + 2
  while (i < lines.length) {
    const line = lines[i]
    if (!line.trim() || line.indexOf('|') < 0) break
    rows.push(splitRow(line))
    i++
  }

  let html = '<table style="border-collapse:collapse;width:100%;margin:10px 0;font-size:14px;"><thead><tr>'
  for (let h = 0; h < headers.length; h++) {
    html +=
      '<th style="border:1px solid #d0d9e0;background:#e9eef3;padding:6px 8px;text-align:left;">' +
      inlineMd(headers[h]) +
      '</th>'
  }
  html += '</tr></thead><tbody>'
  for (let r = 0; r < rows.length; r++) {
    html += '<tr>'
    for (let c = 0; c < headers.length; c++) {
      html +=
        '<td style="border:1px solid #d0d9e0;padding:6px 8px;">' +
        inlineMd(rows[r][c] || '') +
        '</td>'
    }
    html += '</tr>'
  }
  html += '</tbody></table>'
  return { html, next: i }
}

/**
 * 轻量 Markdown → HTML（App JS 引擎安全）
 */
export function mdToHtml(text) {
  const src = String(text || '').replace(/\r\n/g, '\n')
  if (!src.trim()) return ''

  const lines = src.split('\n')
  const out = []
  let i = 0
  let inCode = false
  let codeBuf = []
  let listType = null
  let listBuf = []

  const flushList = () => {
    if (!listType || !listBuf.length) {
      listType = null
      listBuf = []
      return
    }
    const tag = listType
    let html = '<' + tag + ' style="padding-left:1.4em;margin:6px 0 10px;">'
    for (let k = 0; k < listBuf.length; k++) {
      html +=
        '<li style="margin:4px 0;line-height:1.55;color:#334155;font-size:15px;">' +
        inlineMd(listBuf[k]) +
        '</li>'
    }
    html += '</' + tag + '>'
    out.push(html)
    listType = null
    listBuf = []
  }

  const flushCode = () => {
    const code = escapeHtml(codeBuf.join('\n'))
    out.push(
      '<pre style="background:#f8fafc;border:1px solid #e2eaf0;border-radius:8px;padding:10px;overflow:auto;font-size:13px;line-height:1.5;"><code style="background:transparent;padding:0;">' +
        code +
        '</code></pre>'
    )
    codeBuf = []
    inCode = false
  }

  while (i < lines.length) {
    const line = lines[i]

    if (line.trim().indexOf('```') === 0) {
      flushList()
      if (inCode) {
        flushCode()
      } else {
        inCode = true
        codeBuf = []
      }
      i++
      continue
    }

    if (inCode) {
      codeBuf.push(line)
      i++
      continue
    }

    // 表格
    if (line.indexOf('|') >= 0 && i + 1 < lines.length && isTableSep(lines[i + 1])) {
      flushList()
      const table = parseTable(lines, i)
      if (table) {
        out.push(table.html)
        i = table.next
        continue
      }
    }

    // 标题
    const heading = /^(#{1,4})\s+(.+)$/.exec(line)
    if (heading) {
      flushList()
      const level = heading[1].length
      const sizes = { 1: 22, 2: 19, 3: 17, 4: 16 }
      const size = sizes[level] || 16
      out.push(
        '<h' +
          level +
          ' style="font-size:' +
          size +
          'px;font-weight:700;margin:10px 0 8px;line-height:1.35;color:#1e293b;">' +
          inlineMd(heading[2]) +
          '</h' +
          level +
          '>'
      )
      i++
      continue
    }

    // 引用
    if (/^>\s?/.test(line)) {
      flushList()
      out.push(
        '<blockquote style="margin:8px 0;padding:6px 12px;border-left:3px solid #94c1e0;background:#f8fafc;color:#64748b;">' +
          inlineMd(line.replace(/^>\s?/, '')) +
          '</blockquote>'
      )
      i++
      continue
    }

    // 分隔线
    if (/^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      flushList()
      out.push('<hr style="border:none;border-top:1px solid #e2eaf0;margin:12px 0;"/>')
      i++
      continue
    }

    // 无序/有序列表
    const ul = /^\s*[-*+]\s+(.+)$/.exec(line)
    const ol = /^\s*\d+\.\s+(.+)$/.exec(line)
    if (ul || ol) {
      const type = ul ? 'ul' : 'ol'
      const item = ul ? ul[1] : ol[1]
      if (listType && listType !== type) flushList()
      listType = type
      listBuf.push(item)
      i++
      continue
    }

    // 空行
    if (!line.trim()) {
      flushList()
      i++
      continue
    }

    // 普通段落
    flushList()
    out.push(
      '<p style="margin:0 0 10px;line-height:1.65;color:#334155;font-size:15px;">' +
        inlineMd(line) +
        '</p>'
    )
    i++
  }

  flushList()
  if (inCode) flushCode()

  return out.join('')
}

export function buildErrorHtml(text) {
  const safe = escapeHtml(text || '请求失败').replace(/\n/g, '<br/>')
  return '<div style="color:#ef4444;font-weight:600;font-size:14px;line-height:1.55;">' + safe + '</div>'
}

export function parseStreamParts(fullText) {
  const { phase, prefix, think, main } = splitThinkContent(fullText || '')
  const mainText = [prefix, main].filter((s) => (s || '').trim()).join('\n\n')
  return {
    phase,
    thinkText: think || '',
    mainText,
    thinkHtml: think ? mdToHtml(think) : '',
    mainHtml: mainText.trim() ? mdToHtml(mainText) : '',
    thinking: phase === 'thinking'
  }
}

/** 从 HTML 粗略还原纯文本（兼容旧缓存消息无 plainText） */
export function htmlToPlain(html) {
  if (!html) return ''
  return String(html)
    .replace(/<br\s*\/?>/gi, '\n')
    .replace(/<\/p>/gi, '\n')
    .replace(/<\/div>/gi, '\n')
    .replace(/<\/li>/gi, '\n')
    .replace(/<\/h[1-6]>/gi, '\n')
    .replace(/<\/tr>/gi, '\n')
    .replace(/<\/th>/gi, '\t')
    .replace(/<\/td>/gi, '\t')
    .replace(/<[^>]+>/g, '')
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&quot;/g, '"')
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, '&')
    .replace(/[ \t]+\n/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .trim()
}
