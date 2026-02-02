<template>
  <view class="custom-tab-bar">
    <view 
      class="tab-item" 
      :class="{ active: selected === 0, 'tab-home': true }"
      @tap="switchTab"
      :data-path="list[0].pagePath"
      :data-index="0"
    >
      <view class="tab-icon">🏠</view>
      <view class="tab-text">首页</view>
    </view>
    <view 
      class="tab-item" 
      :class="{ active: selected === 1, 'tab-feedback': true }"
      @tap="switchTab"
      :data-path="list[1].pagePath"
      :data-index="1"
    >
      <view class="tab-icon">👤</view>
      <view class="tab-text">反馈</view>
    </view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      selected: 0,
      color: '#333333',
      selectedColor: '#333333',
      list: [
        {
          pagePath: '/pages/index/index',
          text: '首页',
          iconPath: '',
          selectedIconPath: ''
        },
        {
          pagePath: '/pages/feedback/feedback',
          text: '反馈',
          iconPath: '',
          selectedIconPath: ''
        }
      ]
    }
  },
  methods: {
    switchTab(e) {
      const data = e.currentTarget.dataset
      const url = data.path
      const index = parseInt(data.index)
      this.selected = index
      uni.switchTab({ url })
    },
    updateSelected() {
      // 这个方法会被页面调用
      const pages = getCurrentPages()
      if (pages.length > 0) {
        const currentPage = pages[pages.length - 1]
        const route = currentPage.route || ''
        if (route.includes('index')) {
          this.selected = 0
        } else if (route.includes('feedback')) {
          this.selected = 1
        }
      }
    },
    setData(data) {
      // 兼容微信小程序的自定义tabBar接口
      if (data.selected !== undefined) {
        this.selected = data.selected
      }
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