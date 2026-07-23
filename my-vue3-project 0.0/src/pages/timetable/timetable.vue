<template>
  <view class="page">
    <view class="header-section">
      <view class="header-top">
        <view class="date-info">
          <text class="date-main">{{ displayDate }}</text>
          <text class="week-info">第{{ displayWeek }}周 {{ currentDay }}</text>
        </view>
        <view class="action-icons">
          <text class="icon" @tap="prevWeek">←</text>
          <text class="icon" @tap="nextWeek">→</text>
          <text class="icon" @tap="onTapSemester">📅</text>
          <text class="icon" @tap="toggleTimeMode">
            {{ timeMode === 'university' ? '🏫' : '⛰️' }}
          </text>
          <text class="icon" @tap="switchToImport">📥</text>
        </view>
      </view>

      <view class="week-bar">
        <view class="month-col">
          <text class="month-text">{{ currentMonth }}</text>
          <text class="month-text">月</text>
        </view>
        <view class="day-col" v-for="(day, index) in displayWeekDays" :key="index">
          <text class="day-name" :class="{ active: day.isToday }">{{ day.name }}</text>
          <text class="day-date" :class="{ active: day.isToday }">{{ day.date }}</text>
        </view>
      </view>
    </view>

    <scroll-view scroll-y class="timetable-scroll">
      <view class="timetable-container" :style="{ minHeight: gridMinHeight }">
        <view class="time-column">
          <view class="time-item" v-for="time in timeSlots" :key="time.period">
            <text class="period-num">{{ time.period }}</text>
            <text class="time-text">{{ time.start }}</text>
            <text class="time-text">{{ time.end }}</text>
          </view>
        </view>

        <view class="course-grid">
          <view class="grid-row" v-for="i in gridRowCount" :key="i"></view>

          <view
            class="course-card"
            v-for="course in visibleCourses"
            :key="course.id"
            :style="getCourseStyle(course)"
            :class="[course.color, { conflict: course.conflictCount > 1 }]"
            @tap="handleCourseTap(course)"
          >
            <view class="course-content">
              <text v-if="course.conflictCount > 1" class="conflict-badge">
                冲突×{{ course.conflictCount }}
              </text>
              <text class="course-name">{{ course.name }}</text>
              <text class="course-location" v-if="course.location">
                {{ course.location }}
              </text>
              <text class="course-teacher" v-if="course.teacher">
                {{ course.teacher }}
              </text>
            </view>
          </view>
        </view>
      </view>
    </scroll-view>
  </view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import {
  parsePeriodFromWeeksStr,
  checkIsCurrentWeek,
  alignToMonday,
  formatDateYMD,
  getTeachingWeek,
  layoutConflictColumns
} from '@/utils/timetableParse.js'

const PERIOD_HEIGHT = 120
/** 网格节数（含预留第 12 节，避免晚课溢出） */
const GRID_PERIODS = 12

const switchToImport = () => {
  try {
    uni.navigateTo({ url: '../import/import' })
  } catch (err) {
    console.error('跳转失败', err)
  }
}

const currentDay = ref('')
const currentWeek = ref(1)
const currentMonth = ref(0)
const displayWeek = ref(1)
const displayDate = ref('')
const displayWeekDays = ref([])
const hasPromptedSemester = ref(false)

const timeModes = {
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
const timeMode = ref('university')
const timeSlots = ref([])

const courses = ref([])
const semesterStart = ref('')

const gridRowCount = computed(() => Math.max(GRID_PERIODS, timeSlots.value.length || GRID_PERIODS))
const gridMinHeight = computed(() => `${gridRowCount.value * PERIOD_HEIGHT}rpx`)

const visibleCourses = computed(() => {
  const weekCourses = courses.value.filter((c) => c.isCurrentWeek)
  return layoutConflictColumns(weekCourses)
})

const colorTheme = ['pink', 'blue', 'purple', 'green', 'orange', 'rose']
const getCourseColor = (name) => {
  let hash = 0
  const s = name || ''
  for (let i = 0; i < s.length; i++) {
    hash = s.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colorTheme[Math.abs(hash) % colorTheme.length]
}

const applySemesterStart = (rawInput, { silent } = {}) => {
  const monday = alignToMonday(rawInput)
  if (!monday) return false
  const normalized = formatDateYMD(monday)
  uni.setStorageSync('semester_start', normalized)
  semesterStart.value = normalized
  updateActualDateInfo()
  displayWeek.value = currentWeek.value
  updateDisplayForWeek(displayWeek.value)
  refreshCoursesWeekStatus()
  if (!silent) {
    const tip =
      normalized === rawInput.trim().replace(/\./g, '-')
        ? '开学日期已设置'
        : `已对齐到当周周一 ${normalized}`
    uni.showToast({ title: tip, icon: 'success' })
  }
  return true
}

const updateActualDateInfo = () => {
  const now = new Date()
  const weekIndex = now.getDay()
  const weekMap = ['日', '一', '二', '三', '四', '五', '六']
  currentDay.value = `周${weekMap[weekIndex]}`

  if (semesterStart.value) {
    const teachingWeek = getTeachingWeek(semesterStart.value, now)
    currentWeek.value = teachingWeek > 0 ? teachingWeek : 1
  } else {
    // 禁止 ISO 周回退：未设置开学日时固定为第 1 周，并引导设置
    currentWeek.value = 1
  }
}

const updateDisplayForWeek = (week) => {
  const weekMap = ['一', '二', '三', '四', '五', '六', '日']
  const today = new Date()
  const todayYear = today.getFullYear()
  const todayMonth = today.getMonth()
  const todayDate = today.getDate()

  let monday
  if (semesterStart.value) {
    const startMonday = alignToMonday(semesterStart.value)
    monday = new Date(startMonday)
    monday.setDate(startMonday.getDate() + (week - 1) * 7)
  } else {
    // 未设置开学日：按「相对本周」偏移，避免日期条僵死在本周
    const now = new Date()
    const weekIndex = now.getDay()
    const mondayOffset = weekIndex === 0 ? -6 : 1 - weekIndex
    monday = new Date(now.getFullYear(), now.getMonth(), now.getDate() + mondayOffset)
    monday.setDate(monday.getDate() + (week - 1) * 7)
  }

  const days = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(monday)
    date.setDate(monday.getDate() + i)
    const isToday =
      date.getFullYear() === todayYear &&
      date.getMonth() === todayMonth &&
      date.getDate() === todayDate
    days.push({
      name: weekMap[i],
      date: date.getDate(),
      isToday
    })
  }
  displayWeekDays.value = days
  currentMonth.value = monday.getMonth() + 1
}

const refreshCoursesWeekStatus = () => {
  courses.value = courses.value.map((course) => ({
    ...course,
    isCurrentWeek: checkIsCurrentWeek(course.weeksStr, displayWeek.value)
  }))
}

const loadCourses = () => {
  const localData = uni.getStorageSync('local_course_data')
  if (localData && Array.isArray(localData)) {
    courses.value = localData
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
        return {
          id: item.id != null ? item.id : `${item.day}-${start}-${index}`,
          name,
          location: String(item.location || '').replace('大学城校区', '').trim(),
          teacher: item.teacher || '',
          day: Number(item.day) || 1,
          start,
          span,
          weeksStr: item.weeksStr || '',
          color: getCourseColor(name),
          isCurrentWeek: checkIsCurrentWeek(item.weeksStr || '', displayWeek.value)
        }
      })
      .filter((c) => c.name)
  } else {
    courses.value = []
  }
}

const prevWeek = () => {
  if (!semesterStart.value) {
    openSemesterStartDialog(true)
    return
  }
  if (displayWeek.value > 1) {
    displayWeek.value -= 1
    updateDisplayForWeek(displayWeek.value)
    refreshCoursesWeekStatus()
  } else {
    uni.showToast({ title: '已是最小周', icon: 'none' })
  }
}

const nextWeek = () => {
  if (!semesterStart.value) {
    openSemesterStartDialog(true)
    return
  }
  displayWeek.value += 1
  updateDisplayForWeek(displayWeek.value)
  refreshCoursesWeekStatus()
}

const openSemesterStartDialog = (required = false) => {
  uni.showModal({
    title: required ? '请先设置开学日期' : '设置开学日期',
    content: '请输入开学日期（YYYY-MM-DD）。若不是周一，将自动对齐到当周周一。',
    editable: true,
    placeholderText: '例如：2026-02-23',
    success: (res) => {
      if (res.confirm) {
        const input = (res.content || '').trim()
        const dateRegex = /^\d{4}-\d{1,2}-\d{1,2}$/
        if (!dateRegex.test(input)) {
          uni.showToast({ title: '日期格式不正确', icon: 'none' })
          if (required) {
            setTimeout(() => openSemesterStartDialog(true), 400)
          }
          return
        }
        if (!applySemesterStart(input)) {
          uni.showToast({ title: '日期无效', icon: 'none' })
          if (required) {
            setTimeout(() => openSemesterStartDialog(true), 400)
          }
        }
      } else if (required && !semesterStart.value) {
        uni.showToast({ title: '需设置开学日后才能正确显示课表', icon: 'none' })
      }
    }
  })
}

const onTapSemester = () => openSemesterStartDialog(false)

const initTimeMode = () => {
  const savedMode = uni.getStorageSync('time_mode')
  if (savedMode === 'university' || savedMode === 'wushan') {
    timeMode.value = savedMode
  } else {
    timeMode.value = 'university'
  }
  timeSlots.value = timeModes[timeMode.value]
}

const toggleTimeMode = () => {
  const newMode = timeMode.value === 'university' ? 'wushan' : 'university'
  timeMode.value = newMode
  uni.setStorageSync('time_mode', newMode)
  timeSlots.value = timeModes[newMode]
  uni.showToast({
    title: newMode === 'university' ? '切换到国际/大学城时间' : '切换到五山时间',
    icon: 'none'
  })
}

onShow(() => {
  const today = new Date()
  displayDate.value = `${today.getFullYear()}/${today.getMonth() + 1}/${today.getDate()}`

  const storedStart = uni.getStorageSync('semester_start')
  if (storedStart) {
    const monday = alignToMonday(storedStart)
    if (monday) {
      const normalized = formatDateYMD(monday)
      semesterStart.value = normalized
      if (normalized !== storedStart) {
        uni.setStorageSync('semester_start', normalized)
      }
    } else {
      semesterStart.value = ''
    }
  } else {
    semesterStart.value = ''
  }

  updateActualDateInfo()
  displayWeek.value = currentWeek.value
  updateDisplayForWeek(displayWeek.value)
  initTimeMode()
  loadCourses()

  if (!semesterStart.value && !hasPromptedSemester.value) {
    hasPromptedSemester.value = true
    setTimeout(() => openSemesterStartDialog(true), 300)
  }
})

const getCourseStyle = (course) => {
  const top = (course.start - 1) * PERIOD_HEIGHT
  const height = course.span * PERIOD_HEIGHT - 6
  const dayWidth = 100 / 7
  const colCount = Math.max(course.colCount || 1, 1)
  const colIndex = course.colIndex || 0
  const width = dayWidth / colCount
  const left = (course.day - 1) * dayWidth + colIndex * width
  return {
    top: `${top}rpx`,
    left: `${left}%`,
    height: `${height}rpx`,
    width: `calc(${width}% - 4rpx)`,
    zIndex: 20 + colIndex
  }
}

const handleCourseTap = (course) => {
  const conflictTip =
    course.conflictCount > 1 ? `【冲突×${course.conflictCount}】` : ''
  const detail = [conflictTip + course.name, course.weeksStr, course.location, course.teacher]
    .filter(Boolean)
    .join(' · ')
  uni.showToast({
    title: detail || course.name,
    icon: 'none',
    duration: 2800
  })
}
</script>

<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: #eaf0f7;
  display: flex;
  flex-direction: column;
}

.header-section {
  background: #f1f4f9;
  padding: 40rpx 32rpx 16rpx;
}

.header-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32rpx;
}

.date-info {
  display: flex;
  align-items: baseline;
  gap: 16rpx;

  .date-main {
    font-size: 40rpx;
    font-weight: bold;
    color: #1a1a1a;
  }

  .week-info {
    font-size: 24rpx;
    color: #666;
  }
}

.action-icons {
  display: flex;
  gap: 24rpx;

  .icon {
    font-size: 36rpx;
    color: #333;
  }
}

.week-bar {
  display: flex;
  width: 100%;
  margin-bottom: 16rpx;
}

.month-col {
  width: 70rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .month-text {
    font-size: 24rpx;
    color: #333;
    font-weight: bold;
  }
}

.day-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4rpx;

  .day-name {
    font-size: 24rpx;
    color: #999;
  }

  .day-date {
    font-size: 24rpx;
    color: #999;
  }

  .active {
    color: #333;
    font-weight: bold;
  }
}

.timetable-scroll {
  flex: 1;
  height: 0;
  padding-bottom: 24rpx;
}

.timetable-container {
  display: flex;
  width: 100%;
  position: relative;
}

.time-column {
  width: 70rpx;
  display: flex;
  flex-direction: column;
  background: transparent;
}

.time-item {
  height: 120rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;

  .period-num {
    font-size: 28rpx;
    font-weight: bold;
    color: #333;
  }

  .time-text {
    font-size: 20rpx;
    color: #999;
    transform: scale(0.9);
  }
}

.course-grid {
  flex: 1;
  position: relative;
  margin-right: 12rpx;
}

.grid-row {
  height: 120rpx;
  border-bottom: 1px dashed rgba(200, 200, 200, 0.3);
  box-sizing: border-box;
}

.course-card {
  position: absolute;
  border-radius: 12rpx;
  padding: 6rpx;
  box-sizing: border-box;
  overflow: hidden;
  box-shadow: 0 4rpx 12rpx rgba(0, 0, 0, 0.08);

  &.conflict {
    border: 2rpx solid rgba(255, 255, 255, 0.85);
  }

  .course-content {
    display: flex;
    flex-direction: column;
    height: 100%;

    text {
      display: block;
      font-size: 22rpx;
      color: #fff;
      line-height: 1.4;
      word-break: break-all;
      font-weight: bold;
    }

    .conflict-badge {
      font-size: 20rpx;
      opacity: 0.95;
      margin-bottom: 2rpx;
    }

    .course-name {
      font-size: 24rpx;
      margin-bottom: 4rpx;
    }
  }
}

.blue,
.orange {
  background-color: #70a4f8;
}
.green,
.rose {
  background-color: #6ee3ad;
}
.purple,
.pink {
  background-color: #ba95f9;
}
</style>
