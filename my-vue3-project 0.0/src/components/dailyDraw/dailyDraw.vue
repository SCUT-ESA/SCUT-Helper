<template>
	<view>
		<view class="daily-draw" @tap="handleDailyDraw">
			
			<view v-if="!hasDrawn" class="draw-content-initial">
				<view class="draw-icon">🎡</view>
				<view class="draw-text">每日抽签</view>
				<view class="draw-icon">🎡</view>
			</view>
			
			<view v-else class="draw-content-result">
				<view class="result-title">今日运势</view>
				
				<view class="result-big">§ {{ fortuneResult.level }} §</view>
				
				<view class="result-grid">
					<view class="grid-col">
						<view class="action-row yi">
							<text class="label">宜: {{ fortuneResult.good.name }}</text>
						</view>
						<view class="desc">{{ fortuneResult.good.desc }}</view>
					</view>
					
					<view class="grid-col">
						<view class="action-row ji">
							<text class="label">忌: {{ fortuneResult.bad.name }}</text>
						</view>
						<view class="desc">{{ fortuneResult.bad.desc }}</view>
					</view>
				</view>
				
				<view class="result-footer">
					我的华工 · 抽到的总是最好的
				</view>
			</view>

		</view>
	</view>
</template>

<script setup>
import { ref } from 'vue'

const hasDrawn = ref(false)

// 1. 定义运势结果容器
const fortuneResult = ref({
	level: '',
	good: { name: '', desc: '' },
	bad: { name: '', desc: '' }
})

// 2. 运势等级配置（带权重）
const fortuneLevels = [
    { level: '大大吉', weight: 8 },
    { level: '大吉', weight: 9 },
    { level: '中吉', weight: 15 },
    { level: '小吉', weight: 22 },
    { level: '平', weight: 15 },
    { level: '小寄', weight: 10 },
    { level: '中寄', weight: 11 },
    { level: '大寄', weight: 5 },
    { level: '大大寄', weight: 5 }
]

// 3.活动库
// weight: 被抽中的概率权重
// desc_good: 作为"宜"时的描述（积极）
// desc_bad: 作为"忌"时的描述（消极）
const activities = [
	// 学习类
	{ name: '去图书馆', weight: 5, desc_good: '空位置等着你', desc_bad: '座位难抢，昏昏欲睡' },
	{ name: '做作业', weight: 8, desc_good: '雷霆完成，继续CS', desc_bad: '题海淹没，怀疑人生' },
	{ name: '复习', weight: 6, desc_good: '过目不忘', desc_bad: '手机太好玩了，哈哈' },
	{ name: '听课', weight: 8, desc_good: '我听懂了！', desc_bad: '来了但忘记签到' },
	
	// 生活类 
	{ name: '早睡早起', weight: 8, desc_good: '精神小伙', desc_bad: '大熊猫' },
	{ name: '出去溜溜', weight: 10, desc_good: '一路顺风', desc_bad: '同样一路顺风' },
	
	// 饮食类
	{ name: '喝奶茶', weight: 12, desc_good: '甜甜的，美美的', desc_bad: '防御塔已锁定' },
	{ name: '点外卖', weight: 12, desc_good: '便宜，准时，好吃', desc_bad: '被偷了，嘿嘿' },
	
	// 社交娱乐类
	{ name: '约会', weight: 6, desc_good: '桃花朵朵，心动瞬间', desc_bad: '尬聊，分手' },
	{ name: '打游戏', weight: 15, desc_good: '超神上分', desc_bad: '连跪掉分，人机队友' },
	{ name: '看电影', weight: 4, desc_good: '豪看', desc_bad: '全场就你一个单身狗' },
	{ name: 'KTV', weight: 8, desc_good: '不要掌声，只要尖叫', desc_bad: '自己人别开腔' },
	
	// 特殊类
	{ name: '摸鱼', weight: 4, desc_good: '美哉,爽之', desc_bad: 'ddl像狗一样追着咬' },
	{ name: '逃课', weight: 8, desc_good: '老师不会点名', desc_bad: '点名签到，分数没了' },
	{ name: '表白', weight: 5, desc_good: '么么哒', desc_bad: '我是小丑' },
	{ name: '抽卡', weight: 13, desc_good: '欧皇竟是我自己', desc_bad: '非酋本酋' }
]

// 4. 算法：带权重的随机抽取
const getWeightedRandom = (list, isActivity = false) => {
	// 计算总权重
	const totalWeight = list.reduce((sum, item) => sum + item.weight, 0)
	let random = Math.random() * totalWeight
	
	for (const item of list) {
		random -= item.weight
		if (random <= 0) {
			if (isActivity) {
				return item  // 返回整个对象，包含 name/desc_good/desc_bad
			}
			return item.level
		}
	}
	return isActivity ? list[0] : list[0].level
}

// 5. 处理点击抽签
const handleDailyDraw = () => {
	if (hasDrawn.value) return 
	
	uni.showLoading({ title: '请等待...', mask: true })
	
	setTimeout(() => {
		// A. 算出运势等级
		const level = getWeightedRandom(fortuneLevels)
		
		// B. 权重随机取"宜"
		const goodItem = getWeightedRandom(activities, true)
		
		// C. 权重随机取"忌"（不能和宜一样）
		let badItem = getWeightedRandom(activities, true)
		let safetyCounter = 0 // 防止死循环
		while (badItem.name === goodItem.name && safetyCounter < 50) {
			badItem = getWeightedRandom(activities, true)
			safetyCounter++
		}
		
		// D. 赋值（根据宜/忌选择对应描述）
		fortuneResult.value = {
			level: level,
			good: {
				name: goodItem.name,
				desc: goodItem.desc_good  // 宜用 desc_good
			},
			bad: {
				name: badItem.name,
				desc: badItem.desc_bad     // 忌用 desc_bad
			}
		}
		
		hasDrawn.value = true
		uni.hideLoading()
	}, 800)
}
</script>

<style lang="scss" scoped>
	/* 保持原样，未做修改 */
	.daily-draw {
	  background: linear-gradient(135deg, #b794f6 0%, #9f7aea 100%);
	  border-radius: 32rpx;
	  padding: 48rpx;
	  margin-bottom: 48rpx;
	  display: flex;
	  align-items: center;
	  justify-content: center;
	  box-shadow: 0 8rpx 24rpx rgba(183, 148, 246, 0.3);
	  min-height: 200rpx;
	  transition: all 0.3s ease;
	}
	
	.draw-content-initial {
			display: flex;
			align-items: center;
			gap: 40rpx;  /* 增加间距 */
			width: 100%;
			justify-content: center;
		}
	
		.draw-icon {
		  width: 80rpx;  /* 增加宽度 */
		  height: 80rpx;  /* 增加高度 */
		  background: rgba(255, 255, 255, 0.3);
		  border-radius: 50%;
		  display: flex;
		  align-items: center;
		  justify-content: center;
		  font-size: 48rpx;  /* 增加图标字体大小 */
		}
		
		.draw-text {
		  color: #fff;
		  font-size: 48rpx;  /* 增加文字大小 */
		  font-weight: 600;
		  letter-spacing: 2rpx;  /* 增加字间距，使文字更清晰 */
		}


	.draw-content-result {
		width: 100%;
		display: flex;
		flex-direction: column;
		align-items: center;
		color: #fff;
	}

	.result-title {
		font-size: 28rpx;
		opacity: 0.9;
		margin-bottom: 10rpx;
	}

	.result-big {
		font-size: 80rpx;
		font-weight: bold;
		margin: 10rpx 0 30rpx 0;
		color: #fff;
		text-shadow: 0 4rpx 8rpx rgba(0,0,0,0.1); 
	}

	.result-grid {
		display: flex;
		justify-content: space-between;
		width: 100%;
		margin-bottom: 30rpx;
		padding: 0 20rpx;
	}

	.grid-col {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
	}

	.action-row {
		font-size: 32rpx;
		font-weight: 600;
		margin-bottom: 8rpx;
	}

	.yi { color: #ffd1d1; }
	.ji { color: #e2e8f0; }

	.desc {
		font-size: 24rpx;
		opacity: 0.8;
	}

	.result-footer {
		font-size: 24rpx;
		opacity: 0.6;
		margin-top: 10rpx;
		border-top: 1px solid rgba(255,255,255,0.2);
		padding-top: 16rpx;
		width: 80%;
		text-align: center;
	}
</style>