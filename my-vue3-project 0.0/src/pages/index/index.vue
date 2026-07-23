<template>
  <view class="page">
	<!-- 每日签到卡片 -->
	<dailyDraw></dailyDraw>

    <!-- 常用功能 -->
    <view class="section">
      <view class="section-title">常用功能</view>
      <view class="function-grid">
        <view 
          class="function-item" 
          v-for="(item, index) in commonFunctions" 
          :key="index"
          @tap="handleFunctionClick(item)"
        >
          <view class="function-icon" :class="{ 'icon-up': item.name === '一卡通' }">
            {{ item.icon }}
          </view>
          <view class="function-name">{{ item.name }}</view>
        </view>
      </view>
    </view>

    <!-- 更多功能 -->
    <view class="section">
      <view class="section-title">更多</view>
      <view class="function-grid">
        <view 
          class="function-item" 
          v-for="(item, index) in moreFunctions" 
          :key="index"
          @tap="handleFunctionClick(item)"
        >
          <view class="function-icon">
            {{ item.icon }}
          </view>
          <view class="function-name">{{ item.name }}</view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref } from 'vue'
import dailyDraw from "@/components/dailyDraw/dailyDraw.vue"
import { openCampusWeb } from '@/utils/webvpn.js'

// 常用功能列表
const commonFunctions = ref([
  { name: '课程中心', icon: '📚', url: 'https://ecourse.scut.edu.cn', type: 'web' },
  { name: '资料', icon: '📄', url: 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=Mzg3NjgzMjI5OA==', type: 'copy' },
  { name: '猹话会', icon: '💬', url: '#小程序://猹话会/xmyq4nuqwlMg5lp', type: 'miniprogram' },
  { name: 'VPN', icon: '🔒', url: 'https://webvpn.scut.edu.cn/', type: 'web' },
  { name: '一卡通', icon: '🪪', url: 'https://ecardwxnew.scut.edu.cn/plat/shouyeUser', type: 'web' },
  { name: '教务系统', icon: '🏛️', url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=xs&_t=1769041397669&echarts=1', type: 'web' },
  { name: '选课通', icon: '📖', url: '#小程序://华园选课通/ctHUyaZ4rwcg8ym', type: 'miniprogram' },
  { name: '自主选课', icon: '📋', url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default', type: 'web' },
  { name: '长江雨课', icon: '▶️', url: '#小程序://长江雨课堂/Sl4iTWdM7ozmZ4s', type: 'miniprogram' },
  { name: '教务处', icon: '👤', url: 'https://jw.scut.edu.cn/zhinan/cms/index.do', type: 'web' }
])

// 更多功能列表
const moreFunctions = ref([
  { name: '公众号', icon: '💭', url: 'https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=MzA5NDQ1NzE5Ng==', type: 'copy' },
  { name: '校园地图', icon: '📍', url: 'https://map.scut.edu.cn/login_home.html', type: 'copy' },
  { name: '查分', icon: '🔍', url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html?gnmkdm=N305005&layout=default', type: 'web' },
  { name: 'GPA', icon: '💯', url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/design/viewFunc_cxDesignFuncPageIndex.html?gnmkdm=N3091hg05&layout=default', type: 'web' },
  { name: '教材订购', icon: '📥', url: '#小程序://通读大中专/mCuEWIwyvx5Wj0H', type: 'miniprogram' },
  { name: '知网资源', icon: '📚', url: 'https://www-cnki-net-443.webvpn.scut.edu.cn/', type: 'web' },
  { name: '万方资源', icon: '📚', url: 'https://www-wanfangdata-com-cn-443.webvpn.scut.edu.cn/index.html', type: 'web' },
  { name: '敬请期待', icon: '⋯', url: '', type: 'none' }
])


  // 在 <script setup> 中定义
  const lastTap = ref(null)          // 记录上一次点击的项目和时间
  let tapTimeout = null               // 单击延迟跳转的定时器
  
  const handleFunctionClick = (item) => {
    // 占位项或无链接处理
    if (!item.url || item.type === 'none') {
      uni.showToast({ title: item.name, icon: 'none', duration: 2000 })
      return
    }
  
    // 判断是否为网址（http:// 或 https:// 开头）
    const isWebUrl = /^https?:\/\//.test(item.url)
  
    // 非网址，或显式指定 type=copy：单击直接复制（与选课通等一致）
    if (!isWebUrl || item.type === 'copy') {
      uni.setClipboardData({
        data: item.url,
        success: () => {
          uni.showToast({ title: '链接已复制', icon: 'success', duration: 2000 })
        },
        fail: () => {
          uni.showToast({ title: '复制失败', icon: 'none', duration: 2000 })
        }
      })
      return
    }
  
    // 以下是网址的处理：双击复制，单击跳转
    const now = Date.now()
  
    // 双击检测
    if (lastTap.value && lastTap.value.item === item && now - lastTap.value.time < 300) {
      if (tapTimeout) {
        clearTimeout(tapTimeout)
        tapTimeout = null
      }
      uni.setClipboardData({
        data: item.url,
        success: () => {
          uni.showToast({ title: '链接已复制', icon: 'success', duration: 2000 })
        },
        fail: () => {
          uni.showToast({ title: '复制失败', icon: 'none', duration: 2000 })
        }
      })
      lastTap.value = null
      return
    }
  
    // 单击：延迟执行跳转（等待可能出现的双击）
    if (tapTimeout) {
      clearTimeout(tapTimeout)
    }
  
    tapTimeout = setTimeout(() => {
      // *.webvpn 深链：先 WebVPN 门户登录，再进目标页（与课表导入同逻辑）
      openCampusWeb(item.url, { title: item.name })
      lastTap.value = null
      tapTimeout = null
    }, 300)
  
    lastTap.value = { item, time: now }
  }
</script>



<style lang="scss" scoped>
	
.page {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 32rpx;
  padding-bottom: 32rpx;
  box-sizing: border-box;
}

.draw-text {
  color: #fff;
  font-size: 40rpx;
  font-weight: 600;
}

/* 功能区域 */
.section {
  margin-bottom: 48rpx;
}

.section-title {
  font-size: 32rpx;
  font-weight: 600;
  color: #333;
  margin-bottom: 24rpx;
  padding-left: 8rpx;
}

.function-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 24rpx;
  justify-items: center;
  align-items: center;
  padding: 0;
  width: 100%;
  box-sizing: border-box;
}

.function-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0;
  border-radius: 24rpx;
  width: 100%;
  box-sizing: border-box;
}

.function-icon {
  width: 96rpx;
  height: 96rpx;
  background: linear-gradient(135deg, #90cdf4 0%, #63b3ed 100%);
  border-radius: 24rpx;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16rpx;
  font-size: 48rpx;
  box-shadow: 0 4rpx 16rpx rgba(99, 179, 237, 0.3);
}

/* 一卡通图标完全居中，和其他按钮一样 */
.function-icon.icon-up {
  align-items: center;
  justify-content: center;
  padding-top: 0;
}

.function-name {
  font-size: 24rpx;
  color: #333;
  text-align: center;
  line-height: 1.2;
}
</style>