/**
 * 课表周次/节次解析工具
 */

/** 全角括号等归一化 */
function normalizeWeeksStr(weeksStr = '') {
  return String(weeksStr)
    .replace(/（/g, '(')
    .replace(/）/g, ')')
    .replace(/，/g, ',')
    .trim()
}

/** 去掉节次前缀，如 "(5-6节)1周" → "1周" */
function stripPeriodPrefix(weeksStr = '') {
  return normalizeWeeksStr(weeksStr)
    .replace(/\(\d+(?:\s*-\s*\d+)?节\)/g, '')
    .trim()
}

/** 从 "(9-11节)..." 解析 start/span；支持 (11-11节)、(9节) */
function parsePeriodFromWeeksStr(weeksStr = '') {
  const s = normalizeWeeksStr(weeksStr)
  const match = s.match(/\((\d+)\s*-\s*(\d+)节\)/)
  if (match) {
    const start = parseInt(match[1], 10)
    const end = parseInt(match[2], 10)
    if (!Number.isNaN(start) && !Number.isNaN(end) && end >= start) {
      return { start, span: end - start + 1 }
    }
  }
  const single = s.match(/\((\d+)节\)/)
  if (single) {
    const start = parseInt(single[1], 10)
    return { start, span: 1 }
  }
  return null
}

/**
 * 将「1,3,5周」规范为「1周,3周,5周」，便于按逗号分段
 */
function expandDiscreteWeeks(rest = '') {
  let s = rest
  // 反复把「数字,数字」补成「数字周,数字」
  let prev = ''
  while (prev !== s) {
    prev = s
    s = s.replace(/(\d+)\s*,\s*(?=\d)/g, '$1周,')
  }
  return s
}

/**
 * 判断某教学周是否命中 weeksStr
 * 支持：1周 | 1周,4周 | 1,3,5周 | 4-10周,12-16周 | 2-16周(双) | 5-7周(单)
 */
function checkIsCurrentWeek(weeksStr, currentWk) {
  if (!weeksStr) return true
  const wk = Number(currentWk)
  if (!wk || wk < 1) return false

  const rest = expandDiscreteWeeks(stripPeriodPrefix(weeksStr))
  // 仅有节次、无周次信息：不臆测为每周都有
  if (!rest) return false

  const segments = rest.split(/[,，]/).map((s) => s.trim()).filter(Boolean)
  for (const segment of segments) {
    const rangeMatch = segment.match(/(\d+)\s*-\s*(\d+)\s*周/)
    if (rangeMatch) {
      const startWk = parseInt(rangeMatch[1], 10)
      const endWk = parseInt(rangeMatch[2], 10)
      const isDouble = segment.includes('双')
      const isSingle = segment.includes('单')
      if (wk >= startWk && wk <= endWk) {
        if (isDouble && wk % 2 !== 0) continue
        if (isSingle && wk % 2 === 0) continue
        return true
      }
      continue
    }
    const singleMatch = segment.match(/(\d+)\s*周/)
    if (singleMatch) {
      if (parseInt(singleMatch[1], 10) === wk) return true
      continue
    }
    // 纯数字段（规范后仍可能残留）
    if (/^\d+$/.test(segment) && parseInt(segment, 10) === wk) return true
  }
  return false
}

/** 将任意日期对齐到当周周一（周日算上周） */
function alignToMonday(dateInput) {
  const d = dateInput instanceof Date ? new Date(dateInput) : new Date(String(dateInput).replace(/\./g, '-'))
  if (Number.isNaN(d.getTime())) return null
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  const offset = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + offset)
  return d
}

function formatDateYMD(d) {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${day}`
}

/**
 * 基于「第1周周一」计算教学周；开学日若非周一会先对齐到当周周一
 */
function getTeachingWeek(startDateStr, today) {
  const startMonday = alignToMonday(startDateStr)
  if (!startMonday) return 0
  const now = today instanceof Date ? new Date(today) : new Date(today)
  now.setHours(0, 0, 0, 0)
  const diffDays = Math.floor((now - startMonday) / (1000 * 60 * 60 * 24))
  if (diffDays < 0) return 0
  return Math.floor(diffDays / 7) + 1
}

/**
 * 为本周可见课程分配分栏（处理同格/时段重叠冲突）
 */
function layoutConflictColumns(courseList) {
  const byDay = {}
  courseList.forEach((c, idx) => {
    const day = c.day
    if (!byDay[day]) byDay[day] = []
    byDay[day].push({ ...c, _idx: idx })
  })

  const laid = new Array(courseList.length)
  Object.keys(byDay).forEach((day) => {
    const list = byDay[day].sort((a, b) => a.start - b.start || b.span - a.span || String(a.name).localeCompare(String(b.name)))
    const colEnds = []
    list.forEach((c) => {
      let col = colEnds.findIndex((end) => end < c.start)
      if (col === -1) {
        col = colEnds.length
        colEnds.push(0)
      }
      colEnds[col] = c.start + c.span - 1
      c.colIndex = col
    })
    const maxCol = Math.max(colEnds.length, 1)
    list.forEach((c) => {
      // 与该课时段相交的数量
      const cEnd = c.start + c.span - 1
      const overlapN = list.filter((o) => {
        const oEnd = o.start + o.span - 1
        return o.start <= cEnd && c.start <= oEnd
      }).length
      laid[c._idx] = {
        ...courseList[c._idx],
        colIndex: c.colIndex,
        colCount: maxCol,
        conflictCount: overlapN
      }
    })
  })
  return laid.map((c, i) => c || { ...courseList[i], colIndex: 0, colCount: 1, conflictCount: 1 })
}

export {
  normalizeWeeksStr,
  stripPeriodPrefix,
  parsePeriodFromWeeksStr,
  expandDiscreteWeeks,
  checkIsCurrentWeek,
  alignToMonday,
  formatDateYMD,
  getTeachingWeek,
  layoutConflictColumns
}
