<template>
  <view class="page">
	<!-- 立绘鉴赏 -->
	<view class="feedback-section">
		<view
			class="feedback-box text-center-blue art-entry"
			hover-class="art-entry-hover"
			:hover-stay-time="100"
			@tap.stop="goArtGallery"
			@click.stop="goArtGallery"
		>
			<text class="art-entry-text">关于立绘</text>
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

    <!-- 使用说明 -->
    <view class="feedback-section">
      <view class="feedback-title">使用说明</view>
      <view class="feedback-box blue" @tap="openBlog">
        使用说明链接
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
  </view>
</template>

<script setup>
import { ref } from 'vue'

// 双击检测所需的状态
const lastTap = ref(null)          // 记录上一次点击的 { url, time }
let tapTimeout = null               // 单击延迟跳转的定时器

// 统一处理网址的双击复制/单击跳转
const handleUrlClick = (url, name = '链接') => {
  if (!url) return

  const now = Date.now()

  // 双击检测：同一网址且在 300ms 内再次点击
  if (lastTap.value && lastTap.value.url === url && now - lastTap.value.time < 300) {
    if (tapTimeout) {
      clearTimeout(tapTimeout)
      tapTimeout = null
    }
    // 双击：复制链接
    uni.setClipboardData({
      data: url,
      success: () => {
        uni.showToast({ title: `${name}已复制`, icon: 'success', duration: 2000 })
      },
      fail: () => {
        uni.showToast({ title: '复制失败', icon: 'none', duration: 2000 })
      }
    })
    lastTap.value = null
    return
  }

  // 单击：延迟执行跳转，等待可能出现的双击
  if (tapTimeout) {
    clearTimeout(tapTimeout)
  }

  tapTimeout = setTimeout(() => {
    uni.navigateTo({
      url: `/pages/webview/webview?url=${encodeURIComponent(url)}`
    })
    lastTap.value = null
    tapTimeout = null
  }, 300)

  lastTap.value = { url, time: now }
}

// 立绘鉴赏（Tab 页 → 普通页用 navigateTo；失败必须提示，否则像「点不动」）
let artNavigating = false
const goArtGallery = () => {
  if (artNavigating) return
  artNavigating = true
  uni.navigateTo({
    url: '/pages/art/art',
    complete: () => {
      artNavigating = false
    },
    fail: (err) => {
      console.error('跳转立绘页失败', err)
      uni.showModal({
        title: '无法打开立绘页',
        content:
          ((err && err.errMsg) || '未知错误') +
          '\n\n请先停止运行，再重新「运行到手机」一次（改 pages.json 后热更新常不生效）。',
        showCancel: false
      })
    }
  })
}

// 我的博客：单击跳转 Webview，双击复制
const openBlog = () => {
  handleUrlClick('https://dcnmcid6v0ct.feishu.cn/wiki/Yvxzwo85hieZTBkbKdhcvyy2nMe?from=from_copylink', '说明')
}

// 一键反馈：单击跳转 Webview，双击复制
const handleFeedback = () => {
  handleUrlClick('https://dcnmcid6v0ct.feishu.cn/wiki/RFEbw4pV8iP6IUkiAzMcmBwKn7c', '反馈链接')
}
</script>


<style lang="scss" scoped>
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 32rpx;
  padding-bottom: 32rpx;
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

.art-entry {
  /* 扩大可点区域，避免 App 上点到文字节点无响应 */
  min-height: 88rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  z-index: 2;
}

.art-entry-hover {
  opacity: 0.85;
}

.art-entry-text {
  font-size: 28rpx;
  font-weight: normal;
  color: #fff;
  pointer-events: none;
  line-height: 1.6;
}

.br {
  display: block;
}
</style>