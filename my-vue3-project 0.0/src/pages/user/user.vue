<template>
  <view class="page">
	<!-- 登录系统 -->
	<view class="feedback-section">
		<view class="feedback-box text-center-blue" @tap="switchToLogin">
		  用户登录
		</view>
	</view>
	
    <!-- 联系我们 -->
    <view class="feedback-section">
      <view class="feedback-title">联系我们</view>
      <view class="feedback-box">
        如果你对这个小程序有什么想法<text class="br"></text>
        可以联系我们
      </view>
    </view>

    <!-- 我的博客 -->
    <view class="feedback-section">
      <view class="feedback-title">我的博客</view>
      <view class="feedback-box blue" @tap="openBlog">
        moon-explorer.top
      </view>
    </view>

    <!-- 一键反馈 -->
    <view class="feedback-section">
      <view class="feedback-title">一键反馈</view>
      <view class="feedback-box blue" @tap="handleFeedback">
        点此处直接评论即可
      </view>
    </view>

    <!-- 鸣谢 -->
    <view class="feedback-section">
      <view class="feedback-title">鸣谢</view>
      <view class="feedback-box green">
        感谢各位的支持<text class="br"></text>
        更多功能敬请期待
      </view>
    </view>
    
    <!-- 底部导航栏 -->
    <TabBar :current="1" />
  </view>
</template>

<script setup>
import { onMounted } from 'vue'
import TabBar from '@/components/TabBar.vue'

// 跳转到登录页面
const switchToLogin = () => {
    try {
      uni.reLaunch({
        url: '../login/login'
      })} catch (err) {
      console.error('跳转失败', err)
    }
  }



// 复制博客地址
const openBlog = () => {
  const blogUrl = 'https://moon-explorer.top'
  uni.setClipboardData({
    data: blogUrl,
    success: () => {
      uni.showToast({
        title: '博客地址已复制',
        icon: 'success',
        duration: 2000
      })
    },
    fail: () => {
      uni.showToast({
        title: '复制失败',
        icon: 'none',
        duration: 2000
      })
    }
  })
}

// 复制反馈网址
const handleFeedback = () => {
  const feedbackUrl = 'https://dcnmcid6v0ct.feishu.cn/wiki/RFEbw4pV8iP6IUkiAzMcmBwKn7c'
  uni.setClipboardData({
    data: feedbackUrl,
    success: () => {
      uni.showToast({
        title: '反馈链接已复制',
        icon: 'success',
        duration: 2000
      })
    },
    fail: () => {
      uni.showToast({
        title: '复制失败',
        icon: 'none',
        duration: 2000
      })
    }
  })
}
</script>


<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 32rpx;
  padding-bottom: 160rpx; // 为底部导航栏留出空间
}

.feedback-section {
  background: #fff;
  border-radius: 24rpx;
  padding: 40rpx;
  margin-bottom: 32rpx;
  box-shadow: 0 4rpx 16rpx rgba(0, 0, 0, 0.05);
}

.feedback-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
}

.feedback-box {
  background: linear-gradient(135deg, #b794f6 0%, #9f7aea 100%);
  border-radius: 24rpx;
  padding: 32rpx;
  color: #fff;
  line-height: 1.6;
  font-size: 28rpx;
}

.feedback-box.blue {
  background: linear-gradient(135deg, #90cdf4 0%, #63b3ed 100%);
}

.feedback-box.green {
  background: linear-gradient(135deg, #68d391 0%, #48bb78 100%);
}


.feedback-box.text-center-blue {
  text-align: center;
  background: linear-gradient(135deg, #90cdf4 0%, #63b3ed 100%);
}

.br {
  display: block;
}
</style>