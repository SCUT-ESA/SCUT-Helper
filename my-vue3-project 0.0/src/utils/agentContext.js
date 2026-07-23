/**
 * Agent 设备上下文：按用户问题意图，只传需要的课表/签到数据（减负加速）
 *
 * scope:
 * - none：无关问题，几乎不传课表
 * - day：某一天的课（今天/明天/后天/前天/周几…）
 * - next：下一节课
 * - week：本教学周整体课表
 * - full：导入的完整课表条目（含周次）
 * - checkin：签到相关
 */
import {
  parsePeriodFromWeeksStr,
  checkIsCurrentWeek,
  getTeachingWeek,
  formatDateYMD,
  alignToMonday
} from '@/utils/timetableParse.js'
import { EMOJI_LIST } from '@/utils/artAssets.js'

const STORAGE_COURSES = 'local_course_data'
const STORAGE_SEMESTER = 'semester_start'
const STORAGE_TIME_MODE = 'time_mode'
const STORAGE_SIGN_DATE = 'daily_sign_last_date'
const STORAGE_SIGN_EMOJI = 'daily_sign_emoji_v1'
const STORAGE_SIGN_DAYS = 'daily_sign_total_days'

const WEEKDAY_CN = ['日', '一', '二', '三', '四', '五', '六']
const COURSE_DAY_CN = ['', '周一', '周二', '周三', '周四', '周五', '周六', '周日']

const TIME_MODES = {
  university: [
    { period: 1, start: '08:50', end: '09:35' },
    { period: 2, start: '09:40', end: '10:25' },
    { period: 3, start: '10:40', end: '11:25' },
    { period: 4, start: '11:30', end: '12:15' },
    { period: 5, start: '14:00', end: '14:45' },
    { period: 6, start: '14:50', end: '15:35' },
    { period: 7, start: '15:45', end: '16:30' },
    { period: 8, start: '16:35', end: '17:20' },
    { period: 9, start: '19:00', end: '19:45' },
    { period: 10, start: '19:55', end: '20:40' },
    { period: 11, start: '20:50', end: '21:35' },
    { period: 12, start: '21:45', end: '22:30' }
  ],
  wushan: [
    { period: 1, start: '08:00', end: '08:45' },
    { period: 2, start: '08:55', end: '09:40' },
    { period: 3, start: '10:00', end: '10:45' },
    { period: 4, start: '10:55', end: '11:40' },
    { period: 5, start: '14:30', end: '15:15' },
    { period: 6, start: '15:25', end: '16:10' },
    { period: 7, start: '16:20', end: '17:05' },
    { period: 8, start: '17:15', end: '18:00' },
    { period: 9, start: '19:00', end: '19:45' },
    { period: 10, start: '19:55', end: '20:40' },
    { period: 11, start: '20:50', end: '21:35' },
    { period: 12, start: '21:45', end: '22:30' }
  ]
}

function getTodayYMD(d = new Date()) {
  return formatDateYMD(d) || ''
}

function jsDayToCourseDay(jsDay) {
  return jsDay === 0 ? 7 : jsDay
}

function slotRange(timeMode, start, span) {
  const slots = TIME_MODES[timeMode] || TIME_MODES.university
  const s = Number(start) || 1
  const n = Number(span) || 1
  const first = slots.find((x) => x.period === s)
  const last = slots.find((x) => x.period === s + n - 1) || first
  return {
    section: n > 1 ? `${s}-${s + n - 1}` : String(s),
    time_start: (first && first.start) || '',
    time_end: (last && last.end) || ''
  }
}

function normalizeCourses(rawList, teachingWeek) {
  if (!Array.isArray(rawList)) return []
  return rawList
    .map((item, index) => {
      let start = Number(item.start) || 1
      let span = Number(item.span) || 1
      if (item.weeksStr) {
        const parsed = parsePeriodFromWeeksStr(item.weeksStr)
        if (parsed) {
          start = parsed.start
          span = parsed.span
        }
      }
      const name = (item.name || '').trim()
      if (!name) return null
      const weeksStr = item.weeksStr || ''
      return {
        id: item.id != null ? item.id : `${item.day}-${start}-${index}`,
        name,
        location: String(item.location || '').replace('大学城校区', '').trim(),
        teacher: item.teacher || '',
        day: Number(item.day) || 1,
        start,
        span,
        weeksStr,
        isCurrentWeek: checkIsCurrentWeek(weeksStr, teachingWeek)
      }
    })
    .filter(Boolean)
}

function toSummary(course, timeMode) {
  const t = slotRange(timeMode, course.start, course.span)
  return {
    name: course.name,
    section: t.section,
    time_start: t.time_start,
    time_end: t.time_end,
    room: course.location || '',
    teacher: course.teacher || '',
    day: course.day,
    day_cn: COURSE_DAY_CN[course.day] || ''
  }
}

function coursesOnDay(all, day, timeMode) {
  return all
    .filter((c) => c.isCurrentWeek && c.day === day)
    .sort((a, b) => a.start - b.start)
    .map((c) => toSummary(c, timeMode))
}

function findNextCourse(todayList, now = new Date()) {
  const hm = now.getHours() * 60 + now.getMinutes()
  for (const c of todayList) {
    if (!c.time_start) continue
    const parts = String(c.time_start).split(':')
    const startMin = Number(parts[0]) * 60 + Number(parts[1] || 0)
    if (startMin >= hm) return c
  }
  return null
}

/** 相对今天 offset 天 → 教学周 + 课表 day */
function resolveDayOffset(now, semesterStart, teachingWeek, offset) {
  const target = new Date(now)
  target.setHours(0, 0, 0, 0)
  target.setDate(target.getDate() + offset)
  const jsDay = target.getDay()
  const courseDay = jsDayToCourseDay(jsDay)
  let week = teachingWeek > 0 ? teachingWeek : 1
  if (semesterStart) {
    const w = getTeachingWeek(semesterStart, target)
    if (w > 0) week = w
  }
  return {
    date: getTodayYMD(target),
    weekday: jsDay,
    weekday_cn: `周${WEEKDAY_CN[jsDay]}`,
    course_day: courseDay,
    teaching_week: week,
    day_offset: offset
  }
}

/**
 * 从用户话术识别课表/签到意图
 */
export function detectContextIntent(message = '') {
  const t = String(message || '').trim()
  const wantCheckin = /签到|抽签|运势|配语|今天.*(表情|emoji)/i.test(t)

  // 纯跳转指令：不塞课表，加快响应
  if (
    /(打开|跳转|进入|去看|帮我开)/.test(t) &&
    !/(什么课|有没有课|有什么课|几节|上课吗|课表里|今天|明天|后天|昨天|前天)/.test(t)
  ) {
    return {
      scope: wantCheckin ? 'checkin' : 'none',
      dayOffset: null,
      weekdayHint: null,
      wantCheckin,
      aboutCourse: false
    }
  }

  const wantFull =
    /整体课表|完整课表|全部课表|所有课|整个课表|课表全|全部课程|所有课程|导入的课表/.test(t)
  const wantWeek =
    /本周课|这周课|这一周|本周有什么课|这周有什么课|一周的课|周课表/.test(t) ||
    (/课表/.test(t) && /(整体|全部|完整|所有|本周|这周)/.test(t))

  const wantNext = /下一节|下节课|接下来.*课|马上.*课|现在下一/.test(t)

  // 相对日
  let dayOffset = null
  if (/大前天/.test(t)) dayOffset = -3
  else if (/前天/.test(t)) dayOffset = -2
  else if (/昨天|昨日/.test(t)) dayOffset = -1
  else if (/大后天/.test(t)) dayOffset = 3
  else if (/后天/.test(t)) dayOffset = 2
  else if (/明天|明日/.test(t)) dayOffset = 1
  else if (/今天|今日|今儿/.test(t)) dayOffset = 0

  // 周几（本教学周内）
  let weekdayHint = null
  const wd = t.match(/周([一二三四五六日天])/)
  if (wd) {
    const map = { 一: 1, 二: 2, 三: 3, 四: 4, 五: 5, 六: 6, 日: 7, 天: 7 }
    weekdayHint = map[wd[1]] || null
  }

  const aboutCourse =
    wantFull ||
    wantWeek ||
    wantNext ||
    dayOffset !== null ||
    weekdayHint != null ||
    /有什么课|什么课|有没有课|几节课|上课|教室|哪节/.test(t)

  let scope = 'none'
  if (wantFull) scope = 'full'
  else if (wantWeek) scope = 'week'
  else if (wantNext) scope = 'next'
  else if (dayOffset !== null || weekdayHint != null) scope = 'day'
  else if (aboutCourse) scope = 'day'
  else if (wantCheckin) scope = 'checkin'

  if (scope === 'day' && dayOffset === null && weekdayHint == null) {
    dayOffset = 0
  }

  return {
    scope,
    dayOffset,
    weekdayHint,
    wantCheckin: wantCheckin || scope === 'checkin',
    aboutCourse
  }
}

function readCheckin(detail) {
  const today = getTodayYMD()
  let totalDays = 0
  try {
    totalDays = Number(uni.getStorageSync(STORAGE_SIGN_DAYS) || 0) || 0
  } catch (_) {}

  let lastDate = ''
  let saved = null
  try {
    lastDate = uni.getStorageSync(STORAGE_SIGN_DATE) || ''
    saved = uni.getStorageSync(STORAGE_SIGN_EMOJI)
  } catch (_) {}

  const signed = lastDate === today && saved && typeof saved.index === 'number'

  if (!detail) {
    return {
      signed_today: !!signed,
      total_days: totalDays
    }
  }

  if (!signed) {
    return {
      signed_today: false,
      total_days: totalDays,
      emoji_index: null,
      caption: '',
      label: ''
    }
  }

  const fromList = EMOJI_LIST[saved.index]
  return {
    signed_today: true,
    total_days: totalDays,
    emoji_index: saved.index,
    caption: (fromList && fromList.caption) || saved.caption || '',
    label: (fromList && fromList.label) || `表情 ${String(saved.index).padStart(2, '0')}`
  }
}

function loadStorageMeta() {
  let semesterStart = ''
  let timeMode = 'university'
  let rawCourses = []
  try {
    semesterStart = uni.getStorageSync(STORAGE_SEMESTER) || ''
    const mode = uni.getStorageSync(STORAGE_TIME_MODE)
    if (mode === 'university' || mode === 'wushan') timeMode = mode
    const data = uni.getStorageSync(STORAGE_COURSES)
    if (Array.isArray(data)) rawCourses = data
  } catch (_) {}
  return { semesterStart, timeMode, rawCourses }
}

function weekOverview(rawCourses, teachingWeek, timeMode) {
  const normalized = normalizeCourses(rawCourses, teachingWeek > 0 ? teachingWeek : 1)
  const byDay = {}
  for (let d = 1; d <= 7; d++) {
    const list = coursesOnDay(normalized, d, timeMode)
    if (list.length) byDay[String(d)] = list
  }
  return byDay
}

function fullCatalog(rawCourses, timeMode) {
  return (rawCourses || [])
    .map((item, index) => {
      let start = Number(item.start) || 1
      let span = Number(item.span) || 1
      if (item.weeksStr) {
        const parsed = parsePeriodFromWeeksStr(item.weeksStr)
        if (parsed) {
          start = parsed.start
          span = parsed.span
        }
      }
      const name = (item.name || '').trim()
      if (!name) return null
      const t = slotRange(timeMode, start, span)
      const day = Number(item.day) || 1
      return {
        name,
        day,
        day_cn: COURSE_DAY_CN[day] || '',
        section: t.section,
        time_start: t.time_start,
        time_end: t.time_end,
        room: String(item.location || '').replace('大学城校区', '').trim(),
        teacher: item.teacher || '',
        weeks: item.weeksStr || ''
      }
    })
    .filter(Boolean)
}

/**
 * @param {string} [userMessage] 用户本轮原话，用于意图裁剪
 */
export function buildDeviceContext(userMessage = '') {
  const intent = detectContextIntent(userMessage)
  const now = new Date()
  const today = getTodayYMD(now)
  const weekday = now.getDay()
  const { semesterStart, timeMode, rawCourses } = loadStorageMeta()
  const hasTimetable = rawCourses.length > 0
  let teachingWeek = 0
  if (semesterStart) teachingWeek = getTeachingWeek(semesterStart, now)

  const base = {
    scope: intent.scope,
    today,
    weekday,
    weekday_cn: `周${WEEKDAY_CN[weekday]}`,
    semester_start: semesterStart || '',
    teaching_week: teachingWeek,
    time_mode: timeMode,
    has_timetable: hasTimetable,
    semester_set: !!semesterStart
  }

  // 非课表/签到问题：极简上下文，加快响应
  if (intent.scope === 'none') {
    return {
      ...base,
      checkin: readCheckin(false)
    }
  }

  if (intent.wantCheckin || intent.scope === 'checkin') {
    base.checkin = readCheckin(true)
  } else {
    base.checkin = readCheckin(false)
  }

  if (!hasTimetable && intent.aboutCourse) {
    return base
  }

  if (intent.scope === 'checkin') {
    return base
  }

  // —— 某一天 ——
  if (intent.scope === 'day' || intent.scope === 'next') {
    let meta
    if (intent.weekdayHint != null) {
      const hint = intent.weekdayHint
      const week = teachingWeek > 0 ? teachingWeek : 1
      let monday
      if (semesterStart) {
        monday = alignToMonday(semesterStart)
        if (monday) {
          monday = new Date(monday)
          monday.setDate(monday.getDate() + (week - 1) * 7)
        }
      }
      if (!monday) {
        const js = now.getDay()
        const off = js === 0 ? -6 : 1 - js
        monday = new Date(now.getFullYear(), now.getMonth(), now.getDate() + off)
      }
      const target = new Date(monday)
      target.setDate(monday.getDate() + (hint - 1))
      meta = {
        date: getTodayYMD(target),
        weekday: target.getDay(),
        weekday_cn: COURSE_DAY_CN[hint],
        course_day: hint,
        teaching_week: week,
        day_offset: Math.round((target - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000)
      }
    } else {
      const offset = intent.dayOffset != null ? intent.dayOffset : 0
      meta = resolveDayOffset(now, semesterStart, teachingWeek, offset)
    }

    const normalized = normalizeCourses(
      rawCourses,
      meta.teaching_week > 0 ? meta.teaching_week : 1
    )
    const dayCourses = coursesOnDay(normalized, meta.course_day, timeMode)

    const out = {
      ...base,
      query_date: meta.date,
      query_weekday_cn: meta.weekday_cn,
      query_day_offset: meta.day_offset,
      query_teaching_week: meta.teaching_week,
      day_courses: dayCourses
    }

    if (intent.scope === 'next' || (intent.dayOffset === 0 && /下一节|下节课/.test(userMessage))) {
      const todayList =
        meta.day_offset === 0
          ? dayCourses
          : coursesOnDay(
              normalizeCourses(rawCourses, teachingWeek > 0 ? teachingWeek : 1),
              jsDayToCourseDay(weekday),
              timeMode
            )
      out.next_course = findNextCourse(todayList, now)
      if (intent.scope === 'next') {
        out.day_courses = todayList
        out.query_date = today
        out.query_weekday_cn = `周${WEEKDAY_CN[weekday]}`
        out.query_day_offset = 0
      }
    }

    return out
  }

  // —— 本周 ——
  if (intent.scope === 'week') {
    return {
      ...base,
      week_courses: weekOverview(rawCourses, teachingWeek, timeMode)
    }
  }

  // —— 完整导入课表 ——
  if (intent.scope === 'full') {
    return {
      ...base,
      all_courses: fullCatalog(rawCourses, timeMode),
      week_courses: weekOverview(rawCourses, teachingWeek, timeMode)
    }
  }

  return base
}
