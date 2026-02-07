<template>
	<view>
		<!-- 每日抽签卡片 -->
		<view class="daily-draw" @tap="handleDailyDraw">
		  <view class="draw-icon">🎡</view>
		  <view class="draw-text">每日抽签</view>
		  <view class="draw-icon">🎡</view>
		</view>
	</view>
</template>
	
<script setup>
	
	// 处理每日抽签点击
	const handleDailyDraw = () => {
	  uni.showToast({
	    title: '每日抽签功能',
	    icon: 'none',
	    duration: 2000
	  })
	}
	
</script>

<style lang="scss" scoped>
	
	/* 每日抽签卡片 */
	.daily-draw {
	  background: linear-gradient(135deg, #b794f6 0%, #9f7aea 100%);
	  border-radius: 32rpx;
	  padding: 48rpx;
	  margin-bottom: 48rpx;
	  display: flex;
	  align-items: center;
	  justify-content: center;
	  gap: 32rpx;
	  box-shadow: 0 8rpx 24rpx rgba(183, 148, 246, 0.3);
	}
	
	.draw-icon {
	  width: 64rpx;
	  height: 64rpx;
	  background: rgba(255, 255, 255, 0.3);
	  border-radius: 50%;
	  display: flex;
	  align-items: center;
	  justify-content: center;
	  font-size: 40rpx;
	}
	
	.draw-text {
	  color: #fff;
	  font-size: 40rpx;
	  font-weight: 600;
	}
	
</style>
