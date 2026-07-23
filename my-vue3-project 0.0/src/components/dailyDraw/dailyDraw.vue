<template>
  <view class="sign-card" @tap="handleSign">
    <!-- 未签到 -->
    <view v-if="!hasSigned" class="sign-initial">
      <view class="sign-icon">🎡</view>
      <text class="sign-title">每日签到</text>
      <view class="sign-icon">🎡</view>
    </view>

    <!-- 已签到：形象 emoji + 配语 -->
    <view v-else class="sign-result">
      <view class="emoji-stage">
        <image
          class="emoji-img"
          :src="todayEmoji.src"
          mode="aspectFit"
          :lazy-load="false"
        />
      </view>
      <text class="emoji-caption">{{ todayEmoji.caption }}</text>
      <view class="sign-meta">
        <text class="meta-days">签到累计 {{ totalDays }} 天</text>
        <text class="meta-slogan">我的华工 · 签到的总是最好的</text>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import { EMOJI_LIST } from '@/utils/artAssets.js'

const STORAGE_LAST_DATE = 'daily_sign_last_date'
const STORAGE_EMOJI = 'daily_sign_emoji_v1'
const STORAGE_TOTAL_DAYS = 'daily_sign_total_days'

const hasSigned = ref(false)
const totalDays = ref(0)
const todayEmoji = ref({
  index: 0,
  src: '/static/00.emoji/00.jpg',
  caption: ''
})

const getTodayDate = () => {
  const d = new Date()
  const year = d.getFullYear()
  const month = (d.getMonth() + 1).toString().padStart(2, '0')
  const day = d.getDate().toString().padStart(2, '0')
  return `${year}-${month}-${day}`
}

const pickRandomEmoji = () => {
  const list = EMOJI_LIST || []
  if (!list.length) {
    return { index: 0, src: '/static/00.emoji/00.jpg', caption: '' }
  }
  const item = list[Math.floor(Math.random() * list.length)]
  return {
    index: item.index,
    src: item.src,
    caption: item.caption || ''
  }
}

const applyEmoji = (data) => {
  if (!data || typeof data.index !== 'number') return false
  const fromList = EMOJI_LIST[data.index]
  todayEmoji.value = {
    index: data.index,
    src: (fromList && fromList.src) || data.src || '/static/00.emoji/00.jpg',
    caption: (fromList && fromList.caption) || data.caption || ''
  }
  return true
}

/** 真正「今日已签到」= 日期是今天 且 已有新版 emoji 结果 */
const isTodaySignedComplete = () => {
  try {
    const lastDate = uni.getStorageSync(STORAGE_LAST_DATE) || ''
    if (lastDate !== getTodayDate()) return false
    const saved = uni.getStorageSync(STORAGE_EMOJI)
    return !!(saved && typeof saved.index === 'number')
  } catch (_) {
    return false
  }
}

try {
  totalDays.value = uni.getStorageSync(STORAGE_TOTAL_DAYS) || 0
  if (isTodaySignedComplete()) {
    const saved = uni.getStorageSync(STORAGE_EMOJI)
    if (applyEmoji(saved)) hasSigned.value = true
  }
} catch (e) {
  console.error('读取签到状态失败', e)
}

const handleSign = () => {
  if (hasSigned.value) return

  // 完整签到才拦截；仅有旧版日期、没有 emoji 时允许补签
  if (isTodaySignedComplete()) {
    const saved = uni.getStorageSync(STORAGE_EMOJI)
    if (applyEmoji(saved)) hasSigned.value = true
    uni.showToast({ title: '今天已经签到过了', icon: 'none' })
    return
  }

  const today = getTodayDate()
  // 旧运势今天已写过日期：补签时不再重复累加天数
  const hadLegacyDateToday = (uni.getStorageSync(STORAGE_LAST_DATE) || '') === today

  uni.showLoading({ title: '签到中', mask: true })

  setTimeout(() => {
    const picked = pickRandomEmoji()
    todayEmoji.value = picked

    try {
      uni.setStorageSync(STORAGE_LAST_DATE, today)
      uni.setStorageSync(STORAGE_EMOJI, picked)
      if (!hadLegacyDateToday) {
        totalDays.value += 1
        uni.setStorageSync(STORAGE_TOTAL_DAYS, totalDays.value)
      }
    } catch (e) {
      console.error('保存签到状态失败', e)
    }

    hasSigned.value = true
    uni.hideLoading()
  }, 800)
}
</script>

<style lang="scss" scoped>
/* 白底卡片，天蓝边框贴最外侧 */
.sign-card {
  position: relative;
  background: #ffffff;
  border-radius: 28rpx;
  margin-bottom: 48rpx;
  min-height: 200rpx;
  overflow: hidden;
  box-sizing: border-box;
  /* 左右外侧天蓝竖边，上下保持细浅线 */
  border-style: solid;
  border-color: #e8eef3 #7ec8e8;
  border-width: 1px 10rpx;
  box-shadow: 0 6rpx 20rpx rgba(126, 200, 232, 0.12);
}

/* 未签到 */
.sign-initial {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 36rpx;
  padding: 52rpx 40rpx;
  min-height: 200rpx;
  box-sizing: border-box;
}

.sign-icon {
  width: 80rpx;
  height: 80rpx;
  background: rgba(126, 200, 232, 0.12);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 48rpx;
  flex-shrink: 0;
}

.sign-title {
  color: #1e293b;
  font-size: 48rpx;
  font-weight: 600;
  letter-spacing: 4rpx;
  line-height: 1.2;
}

/* 已签到 */
.sign-result {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 36rpx 40rpx 32rpx;
  box-sizing: border-box;
}

.emoji-stage {
  width: 378rpx;
  height: 378rpx;
  border-radius: 28rpx;
  background: #f7fafc;
  border: 1px solid #e8eef3;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  margin-bottom: 28rpx;
}

.emoji-img {
  width: 92%;
  height: 92%;
  display: block;
}

.emoji-caption {
  display: block;
  width: 100%;
  font-size: 38rpx;
  font-weight: 600;
  line-height: 1.6;
  color: #334155;
  text-align: center;
  margin-bottom: 28rpx;
  padding: 0 8rpx;
  box-sizing: border-box;
}

.sign-meta {
  width: 100%;
  padding-top: 20rpx;
  border-top: 1px solid #e8eef3;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10rpx;
}

.meta-days {
  font-size: 32rpx;
  color: #529bcc;
  font-weight: 600;
}

.meta-slogan {
  font-size: 30rpx;
  color: #94a3b8;
  text-align: center;
}
</style>
