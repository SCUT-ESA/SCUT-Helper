<template>
	<view class="page">
		你好呀，喵喵喵。
		<!-- 底部导航栏 -->
		<TabBar :current="1" />
	</view>
</template>

<script setup>
	import TabBar from '@/components/TabBar.vue'
</script>

<style lang="scss" scoped>
	.page {
	  min-height: 100vh;
	  background-color: #f5f5f5;
	  padding: 32rpx;
	  padding-bottom: 160rpx; // 为底部导航栏留出空间
	  box-sizing: border-box;
	}
	
</style>
