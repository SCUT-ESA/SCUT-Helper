<template>
  <view class="page">
    <view class="hint-bar">
      <text class="hint-text">左右滑动浏览 · {{ current + 1 }} / {{ pages.length }}</text>
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
          v-for="(page, i) in pages"
          :key="page.key"
          class="slide"
          :style="slideStyle"
        >
          <view class="card">
            <!-- 独立入口：Emoji 表情包（画廊第一张） -->
            <template v-if="page.type === 'emoji'">
              <text class="card-tag">表情包</text>
              <text class="card-title">Emoji 表情包</text>
              <view class="emoji-panel" :style="{ height: imageH + 'px' }">
                <!-- 网格 + 按钮成组垂直居中，避免全堆在上方 -->
                <view class="emoji-block">
                  <view class="emoji-stage">
                    <view class="emoji-grid">
                      <image
                        v-for="em in emojiAll"
                        :key="em.index"
                        class="emoji-thumb"
                        :src="em.src"
                        mode="aspectFit"
                        :lazy-load="false"
                      />
                    </view>
                  </view>
                  <view class="entry-btn" @tap.stop="goEmoji">
                    <text class="entry-text">进入 Emoji 表情包</text>
                    <text class="entry-arrow">›</text>
                  </view>
                </view>
              </view>
              <text class="card-caption">进入后可左右翻页查看配语</text>
            </template>

            <!-- 关于立绘说明 -->
            <template v-else-if="page.type === 'intro'">
              <text class="card-tag">说明</text>
              <text class="card-title">关于立绘</text>
              <scroll-view
                class="intro-scroll"
                :scroll-y="current === introIndex && !animating"
                :show-scrollbar="false"
                :style="{ height: imageH + 'px' }"
              >
                <rich-text class="card-body" :nodes="creationStoryHtml" />
              </scroll-view>
            </template>

            <!-- 立绘 / 草图 -->
            <template v-else>
              <text class="card-tag">{{ page.tag }}</text>
              <text class="card-title">{{ page.title }}</text>
              <view class="image-wrap" :style="{ height: imageH + 'px' }">
                <image
                  v-if="shouldMount(i)"
                  class="art-img"
                  :src="page.src"
                  mode="aspectFit"
                  :lazy-load="false"
                  @error="onImgError(page)"
                />
              </view>
              <text class="card-caption">{{ page.caption }}</text>
            </template>
          </view>
        </view>
      </view>
    </view>

    <view class="dots">
      <view
        v-for="n in pages.length"
        :key="n"
        class="dot"
        :class="{ active: current === n - 1 }"
      />
    </view>
  </view>
</template>

<script setup>
import { ART_IMAGES, CREATION_STORY, EMOJI_LIST } from '@/utils/artAssets.js'
import { mdToHtml } from '@/utils/agentMarkdown.js'
import { useCardGallery } from '@/utils/useCardGallery.js'

const creationStoryHtml = mdToHtml(CREATION_STORY)
/** 入口卡展示全部 16 张（缩略图尺寸接近原 4 张预览） */
const emojiAll = EMOJI_LIST

const pages = [
  { type: 'intro', key: 'intro' },
  { type: 'emoji', key: 'emoji-entry' },
  {
    type: 'image',
    key: 'half',
    tag: '立绘',
    title: '半身像',
    src: ART_IMAGES.half,
    caption: '智能体对话页头像与形象展示'
  },
  {
    type: 'image',
    key: 'full',
    tag: '立绘',
    title: '全身像',
    src: ART_IMAGES.full,
    caption: '左滑全身形象 · 完整校园助手造型'
  },
  {
    type: 'image',
    key: 'sketch',
    tag: '草图',
    title: '手绘半身草图',
    src: ART_IMAGES.sketch,
    caption: '创作初期的线稿与构思'
  }
]

const introIndex = pages.findIndex((p) => p.type === 'intro')

const {
  current,
  stageH,
  imageH,
  animating,
  trackStyle,
  slideStyle,
  shouldMount,
  onTouchStart,
  onTouchMove,
  onTouchEnd
} = useCardGallery({
  length: () => pages.length,
  getSrcAt: (i) => (pages[i] && pages[i].src) || '',
  imageHeadRpx: 280,
  animMs: 500,
  keepRadius: 2
})

const onImgError = (item) => {
  console.error('立绘图片加载失败', item && item.src)
  uni.showToast({ title: '图片加载失败', icon: 'none' })
}

const goEmoji = () => {
  uni.navigateTo({ url: '/pages/emoji/emoji' })
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
  flex-shrink: 0;
}

.card-title {
  display: block;
  font-size: 40rpx;
  font-weight: 600;
  color: #334155;
  margin-bottom: 16rpx;
  flex-shrink: 0;
}

.intro-scroll {
  width: 100%;
  flex-shrink: 0;
  box-sizing: border-box;
}

.card-body {
  display: block;
  width: 100%;
  font-size: 28rpx;
  line-height: 1.75;
  color: #475569;
  margin-bottom: 16rpx;
}

.emoji-panel {
  width: 100%;
  flex-shrink: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: stretch;
  padding: 0;
}

.emoji-block {
  display: flex;
  flex-direction: column;
  align-items: stretch;
  gap: 36rpx;
}

.emoji-stage {
  width: 100%;
  box-sizing: border-box;
  padding: 22rpx 18rpx;
  background: #f8fafc;
  border-radius: 20rpx;
  border: 1px solid #e2eaf0;
}

.emoji-grid {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-content: flex-start;
  row-gap: 16rpx;
}

.emoji-thumb {
  width: 132rpx;
  height: 132rpx;
  border-radius: 20rpx;
  background: #fff;
  border: 1px solid #e8eef3;
  box-sizing: border-box;
}

.entry-btn {
  display: flex;
  align-items: center;
  gap: 16rpx;
  padding: 26rpx 32rpx;
  border-radius: 24rpx;
  background: linear-gradient(135deg, #90cdf4 0%, #63b3ed 100%);
  box-shadow: 0 6rpx 20rpx rgba(99, 179, 237, 0.35);
  flex-shrink: 0;
}

.entry-text {
  flex: 1;
  font-size: 30rpx;
  font-weight: 600;
  color: #fff;
}

.entry-arrow {
  font-size: 40rpx;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1;
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
  margin: 4rpx 0 12rpx;
  overflow: hidden;
  box-sizing: border-box;
}

.art-img {
  width: 100%;
  height: 100%;
  display: block;
}

.card-caption {
  font-size: 24rpx;
  color: #94a3b8;
  text-align: center;
  line-height: 1.5;
  flex-shrink: 0;
  padding-bottom: 4rpx;
}

.dots {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12rpx;
  padding: 8rpx 0 24rpx;
  flex-shrink: 0;
}

.dot {
  width: 12rpx;
  height: 12rpx;
  border-radius: 50%;
  background: rgba(148, 193, 224, 0.45);
}

.dot.active {
  width: 24rpx;
  border-radius: 8rpx;
  background: #529bcc;
}
</style>
