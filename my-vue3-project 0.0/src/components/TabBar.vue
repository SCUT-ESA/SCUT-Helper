<template>
  <view class="custom-tab-bar">
    <view 
      class="tab-item" 
      :class="{ active: current === 0, 'tab-home': true }"
      @tap="switchToIndex"
    >
      <view class="tab-icon">🏠</view>
      <view class="tab-text">首页</view>
    </view>
    <view 
      class="tab-item" 
      :class="{ active: current === 1, 'tab-feedback': true }"
      @tap="switchToFeedback"
    >
      <view class="tab-icon">👤</view>
      <view class="tab-text">用户</view>
    </view>
  </view>
</template>

<script setup>
const props = defineProps({
  current: {
    type: Number,
    default: 0
  }
})

const switchToIndex = () => {
  if (props.current !== 0) {
    try {
      uni.reLaunch({
        url: '/pages/index/index'
      })
    } catch (err) {
      console.error('跳转失败', err)
    }
  }
}

const switchToFeedback = () => {
  if (props.current !== 1) {
    try {
      uni.reLaunch({
        url: '/pages/user/user'
      })
    } catch (err) {
      console.error('跳转失败', err)
    }
  }
}
</script>

<style lang="scss" scoped>
.custom-tab-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 128rpx;
  background: #fff;
  display: flex;
  justify-content: space-around;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  z-index: 999;
  padding-bottom: env(safe-area-inset-bottom);
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  flex: 1;
  padding: 16rpx;
  color: #333;
  transition: color 0.3s;
}

/* 首页激活时使用红棕色 */
.tab-item.tab-home.active {
  color: #8B4513;
}

/* 反馈页激活时使用紫色 */
.tab-item.tab-feedback.active {
  color: #9f7aea;
}

.tab-icon {
  width: 48rpx;
  height: 48rpx;
  margin-bottom: 8rpx;
  font-size: 48rpx;
  display: flex;
  align-items: center;
  justify-content: center;
}

.tab-text {
  font-size: 24rpx;
}
</style>