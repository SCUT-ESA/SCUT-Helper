<template>
	<view class="page">
		<!-- #ifdef APP-PLUS -->
		<cover-view class="guide-bar" v-if="guideText">
			<cover-view class="guide-text">{{ guideText }}</cover-view>
			<cover-view class="guide-action" v-if="showEnterBtn" @tap="goToTarget">进入</cover-view>
			<cover-view class="guide-action" v-if="phase === 'failed'" @tap="restartLogin">重试</cover-view>
		</cover-view>
		<!-- #endif -->
		<!-- #ifndef APP-PLUS -->
		<view class="guide-bar" v-if="guideText">
			<text class="guide-text">{{ guideText }}</text>
			<text class="guide-action" v-if="showEnterBtn" @tap="goToTarget">进入</text>
			<text class="guide-action" v-if="phase === 'failed'" @tap="restartLogin">重试</text>
		</view>
		<!-- #endif -->
		<web-view :src="targetUrl" id="webvpn-gateway"></web-view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onLoad, onReady, onUnload, onNavigationBarButtonTap } from '@dcloudio/uni-app'
import {
	WEBVPN_HOME,
	isAuthUrl,
	isLoginFailedUrl,
	isTargetReached,
	isWebvpnPortalUrl
} from '@/utils/webvpn.js'

/** 最终要打开的深链 */
const destUrl = ref('')
const pageTitle = ref('校园服务')

/** 当前 WebView 加载地址：先门户，登录后再切深链 */
const targetUrl = ref(WEBVPN_HOME)
/** auth | jumping | ready | failed */
const phase = ref('auth')

const guideText = computed(() => {
	const name = pageTitle.value || '目标页'
	switch (phase.value) {
		case 'auth':
			return `请先登录 WebVPN（建议账号密码）。完成后点「进入」打开「${name}」`
		case 'jumping':
			return `正在打开「${name}」，请等待页面加载…`
		case 'ready':
			return `已进入「${name}」，可正常使用`
		case 'failed':
			return '登录失败，请改用账号密码后点「重试」'
		default:
			return ''
	}
})

const showEnterBtn = computed(() => phase.value === 'auth' || phase.value === 'jumping')

let wv = null
let urlWatchTimer = null
let hasJumped = false
let seenAuthPage = false
let lastHandledFailAt = 0

const enableThirdPartyCookies = () => {
	// #ifdef APP-PLUS
	try {
		if (uni.getSystemInfoSync().platform !== 'android') return
		const CookieManager = plus.android.importClass('android.webkit.CookieManager')
		const cm = CookieManager.getInstance()
		cm.setAcceptCookie(true)
		if (wv) {
			try {
				plus.android.invoke(cm, 'setAcceptThirdPartyCookies', wv, true)
			} catch (e) {}
		}
		try {
			cm.flush()
		} catch (e) {}
	} catch (err) {
		console.warn('开启第三方 Cookie 失败', err)
	}
	// #endif
}

const applyChromeLikeUA = () => {
	// #ifdef APP-PLUS
	try {
		if (!wv || typeof wv.setUserAgent !== 'function') return
		const isIOS = uni.getSystemInfoSync().platform === 'ios'
		wv.setUserAgent(
			isIOS
				? 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1'
				: 'Mozilla/5.0 (Linux; Android 13; Mobile) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36'
		)
	} catch (err) {
		console.warn('设置 UA 失败', err)
	}
	// #endif
}

const openExternalScheme = (url) => {
	// #ifdef APP-PLUS
	try {
		plus.runtime.openURL(url, () => {
			uni.showToast({
				title: '请安装微信，或改用账号密码登录',
				icon: 'none',
				duration: 3000
			})
		})
	} catch (e) {
		uni.showToast({ title: '无法打开微信，请改用账号密码', icon: 'none' })
	}
	// #endif
}

const loadInWebview = (url) => {
	try {
		if (wv && typeof wv.loadURL === 'function') {
			wv.loadURL(url)
			return
		}
	} catch (e) {}
	targetUrl.value = url
}

const goToTarget = () => {
	if (!destUrl.value) {
		uni.showToast({ title: '未配置目标链接', icon: 'none' })
		return
	}
	if (phase.value === 'ready' && hasJumped) return
	hasJumped = true
	phase.value = 'jumping'
	uni.showToast({ title: `正在打开${pageTitle.value || '目标页'}…`, icon: 'none', duration: 1500 })
	loadInWebview(destUrl.value)
}

const restartLogin = () => {
	hasJumped = false
	seenAuthPage = false
	phase.value = 'auth'
	loadInWebview(WEBVPN_HOME)
}

const handleCurrentUrl = (url) => {
	if (!url) return

	if (isAuthUrl(url)) {
		seenAuthPage = true
		if (phase.value !== 'failed') phase.value = 'auth'
		return
	}

	if (isLoginFailedUrl(url)) {
		const now = Date.now()
		if (now - lastHandledFailAt > 3000) {
			lastHandledFailAt = now
			phase.value = 'failed'
			uni.showModal({
				title: '登录失败',
				content:
					'二次验证/扫码回调在内嵌浏览器中容易失败。建议改用「账号密码」登录，然后点「进入」。',
				confirmText: '重新登录',
				success: (res) => {
					if (res.confirm) restartLogin()
				}
			})
		}
		return
	}

	if (destUrl.value && isTargetReached(url, destUrl.value)) {
		phase.value = 'ready'
		hasJumped = true
		return
	}

	// 已过认证页，回到 WebVPN 门户后自动进入目标深链
	if (!hasJumped && seenAuthPage && isWebvpnPortalUrl(url)) {
		goToTarget()
	}
}

const setupUrlWatch = () => {
	// #ifdef APP-PLUS
	if (!wv) return
	if (urlWatchTimer) clearInterval(urlWatchTimer)
	urlWatchTimer = setInterval(() => {
		try {
			handleCurrentUrl(wv.getURL && wv.getURL())
		} catch (e) {}
	}, 800)

	try {
		wv.addEventListener(
			'loading',
			(e) => {
				handleCurrentUrl((e && e.url) || (wv.getURL && wv.getURL()))
			},
			false
		)
	} catch (e) {}

	try {
		wv.addEventListener(
			'loaded',
			() => {
				handleCurrentUrl(wv.getURL && wv.getURL())
			},
			false
		)
	} catch (e) {}
	// #endif
}

const setupOverrideLoading = () => {
	// #ifdef APP-PLUS
	if (!wv || typeof wv.overrideUrlLoading !== 'function') return

	wv.overrideUrlLoading(
		{
			mode: 'reject',
			match: '^(weixin://|wxwork://|weixinwork://|wxworklocal://).*'
		},
		(e) => {
			const url = (e && e.url) || ''
			if (/^(weixin|wxwork|weixinwork|wxworklocal):\/\//i.test(url)) {
				uni.showToast({ title: '正在打开微信完成验证…', icon: 'none', duration: 2000 })
				openExternalScheme(url)
			}
		}
	)
	// #endif
}

onLoad((options) => {
	const raw = (options && options.url) || ''
	destUrl.value = raw ? decodeURIComponent(raw) : ''
	if (options && options.title) {
		try {
			pageTitle.value = decodeURIComponent(options.title)
		} catch (_) {
			pageTitle.value = options.title
		}
	}
	if (pageTitle.value) {
		uni.setNavigationBarTitle({ title: pageTitle.value })
	}
	if (!destUrl.value) {
		uni.showToast({ title: '链接无效', icon: 'none' })
	}
})

onReady(() => {
	// #ifdef APP-PLUS
	const currentWebview = getCurrentPages()[getCurrentPages().length - 1].$getAppWebview()
	setTimeout(() => {
		wv = currentWebview.children()[0]
		if (!wv) {
			uni.showToast({ title: '页面加载中，请稍候', icon: 'none' })
			return
		}
		enableThirdPartyCookies()
		applyChromeLikeUA()
		setupOverrideLoading()
		setupUrlWatch()
		uni.showModal({
			title: '登录说明',
			content:
				'1. 校园网环境下无法登录 VPN，请先切换到非校园网（如手机流量）\n2. 请先用账号密码登录学校 WebVPN（扫码容易失败）\n3. 登录成功后会自动进入目标页，也可点顶部「进入」\n4. 与课表导入相同：先门户、再深链，避免登录卡住',
			showCancel: false,
			confirmText: '知道了'
		})
	}, 500)
	// #endif

	// #ifndef APP-PLUS
	uni.showModal({
		title: '提示',
		content: '完整「先登录再进入」能力主要在 App 端可用。当前将打开 WebVPN，请自行登录后再点「进入」。',
		showCancel: false
	})
	// #endif
})

onUnload(() => {
	if (urlWatchTimer) {
		clearInterval(urlWatchTimer)
		urlWatchTimer = null
	}
})

onNavigationBarButtonTap(() => {
	goToTarget()
})
</script>

<style scoped>
.page {
	width: 100%;
	height: 100vh;
	position: relative;
	background: #f5f5f5;
}

.guide-bar {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	z-index: 999;
	display: flex;
	flex-direction: row;
	align-items: center;
	justify-content: space-between;
	padding: 12px 14px;
	background-color: rgba(232, 243, 255, 0.96);
}

.guide-text {
	flex: 1;
	font-size: 12px;
	color: #334455;
	line-height: 18px;
	padding-right: 8px;
}

.guide-action {
	font-size: 13px;
	color: #0770cd;
	font-weight: bold;
	padding: 6px 8px;
}
</style>
