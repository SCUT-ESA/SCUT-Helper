<template>
  <view class="content">
    <!-- App 端直接使用 web-view 组件 -->
    <web-view 
      :src="url" 
      @load="onLoadSuccess" 
      @error="onLoadError"
      v-if="url"
    ></web-view>
    
    <!-- 链接无效时的提示 -->
    <view v-else class="error-message">无效的链接</view>
    
    <!-- 加载状态提示（可选） -->
    <view v-if="loading" class="loading">加载中…</view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      url: '',          // 要加载的网页地址
      loading: true     // 是否正在加载
    }
  },
  
  onLoad(options) {
    // 从页面参数中获取 URL（已由上一页 encodeURIComponent 编码）
    if (options.url) {
      this.url = decodeURIComponent(options.url)
    } else {
      this.url = ''
      this.loading = false
    }
  },
  
  methods: {
    // 加载成功
    onLoadSuccess() {
      this.loading = false
      console.log('webview 加载成功')
    },
    
    // 加载失败
    onLoadError(e) {
      this.loading = false
      console.error('webview 加载失败', e)
      uni.showToast({
        title: '页面加载失败',
        icon: 'none',
        duration: 2000
      })
    }
  }
}
</script>

<style scoped>
.content {
  width: 100%;
  height: 100vh;          /* 撑满全屏 */
  position: relative;
  background-color: #f5f5f5;
}

.loading {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 28rpx;
  color: #999;
}

.error-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 32rpx;
  color: #ff5500;
}
</style>