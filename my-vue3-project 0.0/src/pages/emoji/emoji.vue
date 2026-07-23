<template>
  <view class="page">
    <view class="hint-bar">
      <text class="hint-text">左右滑动 · {{ current + 1 }} / {{ list.length }}</text>
    </view>

    <view
      class="stage"
      :style="{ height: stageH + 'px' }"
      @touchstart="onTouchStart"
      @touchmove.stop="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
    >
      <view class="track" :style="trackStyle">
        <view
          v-for="(item, i) in list"
          :key="item.index"
          class="slide"
          :style="slideStyle"
        >
          <view class="card">
            <text class="card-tag">Emoji</text>
            <text class="card-title">{{ item.label }}</text>
            <view class="image-wrap" :style="{ height: imageH + 'px' }">
              <image
                v-if="shouldMount(i)"
                class="emoji-img"
                :src="item.src"
                mode="aspectFit"
                :lazy-load="false"
                @error="onImgError(item)"
              />
            </view>
            <view class="caption-wrap">
              <text class="card-caption">{{ item.caption }}</text>
            </view>
          </view>
        </view>
      </view>
    </view>

    <view class="dots">
      <view
        v-for="n in list.length"
        :key="n"
        class="dot"
        :class="{ active: current === n - 1 }"
      />
    </view>
  </view>
</template>

<script setup>
import { EMOJI_LIST } from '@/utils/artAssets.js'
import { useCardGallery } from '@/utils/useCardGallery.js'

const list = EMOJI_LIST

const {
  current,
  stageH,
  imageH,
  trackStyle,
  slideStyle,
  shouldMount,
  onTouchStart,
  onTouchMove,
  onTouchEnd
} = useCardGallery({
  length: () => list.length,
  getSrcAt: (i) => (list[i] && list[i].src) || '',
  // 标签 + 标题 + 配语区（约 3 行）+ 内边距，给配语留足空间、图略收一点
  imageHeadRpx: 400,
  animMs: 400,
  keepRadius: 2
})

const onImgError = (item) => {
  console.error('表情包加载失败', item && item.src)
}
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: linear-gradient(165deg, #ebf2f7 0%, #e8eef3 100%);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  overflow: hidden;
}

.hint-bar {
  padding: 16rpx 32rpx 4rpx;
  flex-shrink: 0;
}

.hint-text {
  font-size: 24rpx;
  color: #76a9cc;
  text-align: center;
  display: block;
}

.stage {
  width: 100%;
  overflow: hidden;
  position: relative;
  flex-shrink: 0;
}

.track {
  display: flex;
  flex-direction: row;
  will-change: transform;
  backface-visibility: hidden;
}

.slide {
  flex-shrink: 0;
  box-sizing: border-box;
}

.card {
  height: calc(100% - 44rpx);
  margin: 12rpx 28rpx 32rpx;
  padding: 24rpx 28rpx 28rpx;
  background: #fff;
  border-radius: 28rpx;
  border: 1px solid #e2eaf0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.card-tag {
  display: inline-block;
  align-self: flex-start;
  font-size: 22rpx;
  color: #529bcc;
  background: #e3f2fd;
  padding: 6rpx 18rpx;
  border-radius: 999rpx;
  margin-bottom: 16rpx;
}

.card-title {
  font-size: 36rpx;
  font-weight: 600;
  color: #334155;
  margin-bottom: 16rpx;
}

.image-wrap {
  width: 100%;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 20rpx;
  border: 1px solid #e2eaf0;
  margin-bottom: 20rpx;
  overflow: hidden;
  box-sizing: border-box;
}

.emoji-img {
  width: 100%;
  height: 100%;
  display: block;
}

.caption-wrap {
  flex-shrink: 0;
  min-height: 148rpx;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 0 8rpx 8rpx;
  box-sizing: border-box;
}

.card-caption {
  font-size: 30rpx;
  font-weight: 600;
  line-height: 1.55;
  color: #64748b;
  text-align: center;
  width: 100%;
}

.dots {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10rpx;
  padding: 8rpx 24rpx 24rpx;
  flex-shrink: 0;
  flex-wrap: wrap;
}

.dot {
  width: 10rpx;
  height: 10rpx;
  border-radius: 50%;
  background: rgba(148, 193, 224, 0.45);
}

.dot.active {
  width: 20rpx;
  border-radius: 8rpx;
  background: #529bcc;
}
</style>
