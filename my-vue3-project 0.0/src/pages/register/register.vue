<template>
  <view class="page login-bg">
    <view class="avatar-section">
      <view class="avatar-circle">
        <view class="avatar-icon">👤</view>
      </view>
    </view>

    <view class="login-card">
      <view class="success-content fade-in">
        <!-- 修改这里：显示从本地存储获取的用户名 -->
        <view class="user-name">{{ username }}</view>
        <view class="success-text">登录成功</view>
        
        <view class="firework-icon">
          🎆
        </view>
        
        <view class="sub-text">欢迎回来，开启美好的一天</view>
        
        <button class="login-btn btn-outline" @tap="switchToLogin">
          退出登录
        </button>
      </view>
    </view>

    <TabBar :current="1" />
  </view>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TabBar from '@/components/TabBar.vue'

// 创建响应式变量存储用户名
const username = ref('')

// 在页面加载时从本地存储获取用户名
onMounted(() => {
  try {
    // 从本地存储获取用户信息
    const userInfo = uni.getStorageSync('userInfo')
    if (userInfo && userInfo.username) {
      username.value = userInfo.username
    } else {
      username.value = '用户'
    }
  } catch (error) {
    console.error('获取用户信息失败', error)
    username.value = '用户'
  }
})

// 跳转到登录页面
const switchToLogin = () => {
  try {
    // 清除本地存储的用户信息
    uni.removeStorageSync('userInfo')
    uni.removeStorageSync('token')
    
    uni.reLaunch({
      url: '../login/login'
    })
  } catch (err) {
    console.error('跳转失败', err)
  }
}
</script>


<style lang="scss" scoped>
/* 页面整体背景 - 对应原型图的青色背景 */
.page {
  min-height: 100vh;
  padding: 32rpx;
  padding-bottom: 160rpx;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  /* 这里的颜色取自原型图背景色，稍微调整以适应APP风格 */
  background-color: #f5f5f5; 
}

/* 头像区域 */
.avatar-section {
  margin-top: 60rpx;
  margin-bottom: 40rpx;
  display: flex;
  justify-content: center;
}

.avatar-circle {
  width: 140rpx;
  height: 140rpx;
  border: 6rpx solid #000; /* 原型图中的黑色粗边框 */
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: transparent;
}

.avatar-icon {
  font-size: 80rpx;
  margin-bottom: 10rpx; /* 微调位置 */
}

/* 核心卡片 - 复用 DailyDraw 的紫色渐变风格 */
.login-card {
  width: 100%;
  /* 对应 dailyDraw.txt 的渐变 */
  background: linear-gradient(135deg, #b794f6 0%, #9f7aea 100%);
  border-radius: 32rpx;
  padding: 60rpx 40rpx;
  box-shadow: 0 8rpx 24rpx rgba(183, 148, 246, 0.3);
  box-sizing: border-box;
  min-height: 600rpx;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

/* 标题样式 */
.card-title {
  font-size: 56rpx;
  color: #333; /* 原型图中文字偏黑 */
  text-align: center;
  margin-bottom: 60rpx;
  font-weight: 500;
}

/* 输入框组 */
.input-group {
  margin-bottom: 40rpx;
}

.input-label {
  font-size: 30rpx;
  color: #333;
  margin-bottom: 16rpx;
  display: block;
  padding-left: 10rpx;
}

.input-wrapper {
  background-color: #fff;
  border-radius: 20rpx;
  height: 96rpx;
  display: flex;
  align-items: center;
  padding: 0 24rpx;
  box-shadow: 0 2rpx 8rpx rgba(0,0,0,0.05);
}

.input-icon {
  font-size: 40rpx;
  color: #666; /* 原型图中的灰色图标 */
  margin-right: 20rpx;
  width: 50rpx;
  text-align: center;
}

.input-field {
  flex: 1;
  height: 100%;
  font-size: 32rpx;
  color: #333;
}

/* 登录按钮 - 复用 User.txt 中 feedback-box.green 的颜色 */
.login-btn {
  margin-top: 60rpx;
  width: 60%;
  height: 96rpx;
  line-height: 96rpx;
  background: linear-gradient(135deg, #68d391 0%, #48bb78 100%); /* 对应原型图的绿色按钮 */
  color: #333; /* 原型图文字是深色 */
  border-radius: 24rpx;
  font-size: 36rpx;
  font-weight: 500;
  border: none;
  box-shadow: 0 4rpx 12rpx rgba(72, 187, 120, 0.3);
  
  &:active {
    transform: scale(0.98);
  }
}

/* 成功状态样式 */
.success-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #333;
}

.user-name {
  font-size: 48rpx;
  margin-bottom: 20rpx;
}

.success-text {
  font-size: 56rpx;
  margin-bottom: 60rpx;
}

.firework-icon {
  font-size: 120rpx;
  margin: 20rpx 0 60rpx 0;
  animation: scaleUp 0.5s ease infinite alternate;
}

.sub-text {
  font-size: 28rpx;
  color: rgba(0,0,0,0.6);
  margin-bottom: 40rpx;
}

.btn-outline {
  background: transparent;
  border: 2rpx solid rgba(0,0,0,0.2);
  color: #333;
  margin-top: 20rpx;
}

/* 简单的淡入动画 */
.fade-in {
  animation: fadeIn 0.5s ease;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20rpx); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes scaleUp {
  from { transform: scale(1); }
  to { transform: scale(1.1); }
}
</style>
