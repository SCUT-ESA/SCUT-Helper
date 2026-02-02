<template>
  <view class="webview-container">
    <!-- #ifdef H5 -->
    <iframe :src="url" frameborder="0" class="webview-frame"></iframe>
    <!-- #endif -->
    
    <!-- #ifdef MP-WEIXIN -->
    <web-view :src="url" v-if="url"></web-view>
    <!-- #endif -->
  </view>
</template>

<script>
export default {
  data() {
    return {
      url: ''
    }
  },
  onLoad(options) {
    if (options.url) {
      this.url = decodeURIComponent(options.url)
    }
  }
}
</script>

<style lang="scss" scoped>
.webview-container {
  width: 100%;
  height: 100vh;
}

.webview-frame {
  width: 100%;
  height: 100%;
  border: none;
}
</style>