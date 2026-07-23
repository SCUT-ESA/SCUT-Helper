<template>
	<view class="page">
		<!-- App 上 web-view 为原生全屏，覆盖层需用 cover-view -->
		<!-- #ifdef APP-PLUS -->
		<cover-view class="guide-bar" v-if="guideText">
			<cover-view class="guide-text">{{ guideText }}</cover-view>
			<cover-view class="guide-action" v-if="showEnterBtn" @tap="goToTimetable">进课表</cover-view>
			<cover-view class="guide-action" v-if="phase === 'failed'" @tap="restartLogin">重试</cover-view>
		</cover-view>
		<!-- #endif -->
		<!-- #ifndef APP-PLUS -->
		<view class="guide-bar" v-if="guideText">
			<text class="guide-text">{{ guideText }}</text>
			<text class="guide-action" v-if="showEnterBtn" @tap="goToTimetable">进课表</text>
			<text class="guide-action" v-if="phase === 'failed'" @tap="restartLogin">重试</text>
		</view>
		<!-- #endif -->
		<web-view :src="targetUrl" id="schedule-webview"></web-view>
	</view>
</template>

<script setup>
import { ref, computed } from 'vue'
import { onReady, onUnload, onNavigationBarButtonTap } from '@dcloudio/uni-app'
import { WEBVPN_HOME, isAuthUrl, isLoginFailedUrl, isWebvpnPortalUrl } from '@/utils/webvpn.js'

/** 登录完成后再进入的课表页 */
const TIMETABLE_URL =
	'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/kbcx/xskbcx_cxXskbcxIndex.html?gnmkdm=N2151&layout=default'

const targetUrl = ref(WEBVPN_HOME)
/** auth | jumping | timetable | failed */
const phase = ref('auth')

const guideText = computed(() => {
	switch (phase.value) {
		case 'auth':
			return '请先登录 WebVPN（建议账号密码）。完成后点「进课表」'
		case 'jumping':
			return '正在打开课表页，请等待页面加载完成…'
		case 'timetable':
			return '课表加载完成后，点右上角「提取课表」'
		case 'failed':
			return '登录失败，请改用账号密码后点「重试」'
		default:
			return ''
	}
})

const showEnterBtn = computed(() => phase.value === 'auth' || phase.value === 'jumping')

let wv = null
let urlWatchTimer = null
let hasJumpedToTimetable = false
/** 是否已经出现过认证页；用于避免一打开门户就误跳课表 */
let seenAuthPage = false
let lastHandledFailAt = 0

const isTimetableUrl = (url = '') => {
	const u = url.toLowerCase()
	// 必须是教务课表查询页，不能仅凭 /jwglxt/ 判断
	return (
		u.includes('xsjw2018-jw.webvpn') &&
		(u.includes('xskbcx') || u.includes('/kbcx/xskbcx') || u.includes('xskbcx_cxxskbcx'))
	)
}

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

const goToTimetable = () => {
	if (phase.value === 'timetable' && hasJumpedToTimetable) return
	hasJumpedToTimetable = true
	phase.value = 'jumping'
	uni.showToast({ title: '正在打开课表…', icon: 'none', duration: 1500 })
	try {
		if (wv && typeof wv.loadURL === 'function') {
			wv.loadURL(TIMETABLE_URL)
		} else {
			targetUrl.value = TIMETABLE_URL
		}
	} catch (e) {
		targetUrl.value = TIMETABLE_URL
	}
	// 不再盲等转正：仅当 URL 真正进入课表页时由 handleCurrentUrl 置为 timetable
}

const restartLogin = () => {
	hasJumpedToTimetable = false
	seenAuthPage = false
	phase.value = 'auth'
	try {
		if (wv && typeof wv.loadURL === 'function') {
			wv.loadURL(WEBVPN_HOME)
		} else {
			targetUrl.value = WEBVPN_HOME
		}
	} catch (e) {
		targetUrl.value = WEBVPN_HOME
	}
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
					'二次验证/扫码回调在内嵌浏览器中容易失败。建议改用「账号密码」登录，然后点「进课表」。',
				confirmText: '重新登录',
				success: (res) => {
					if (res.confirm) restartLogin()
				}
			})
		}
		return
	}

	if (isTimetableUrl(url)) {
		phase.value = 'timetable'
		hasJumpedToTimetable = true
		return
	}

	// 仅在「已经过认证页」之后，离开认证落到 WebVPN 门户时自动进课表
	if (
		!hasJumpedToTimetable &&
		seenAuthPage &&
		isWebvpnPortalUrl(url)
	) {
		goToTimetable()
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

	// 只拦截自定义 scheme；HTTPS 认证跳转必须全部放行
	wv.overrideUrlLoading(
		{
			mode: 'reject',
			match: '^(app-import://|weixin://|wxwork://|weixinwork://|wxworklocal://).*'
		},
		(e) => {
			const url = (e && e.url) || ''
			if (url.indexOf('app-import://') === 0) {
				const encodedData = url.replace('app-import://data=', '')
				try {
					const courses = JSON.parse(decodeURIComponent(encodedData))
					if (courses && courses.length > 0) {
						uni.setStorageSync('local_course_data', courses)
						uni.showToast({ title: '课表导入成功！', icon: 'success', duration: 2000 })
						setTimeout(() => uni.navigateBack(), 2000)
					} else {
						uni.showToast({
							title: '未提取到数据，请先登录并等待课表加载完毕',
							icon: 'none',
							duration: 3000
						})
					}
				} catch (err) {
					console.error('解析课表数据失败', err)
					uni.showToast({ title: '提取失败，数据格式异常', icon: 'none' })
				}
				return
			}

			if (/^(weixin|wxwork|weixinwork|wxworklocal):\/\//i.test(url)) {
				uni.showToast({ title: '正在打开微信完成验证…', icon: 'none', duration: 2000 })
				openExternalScheme(url)
			}
		}
	)
	// #endif
}

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
			title: '导入课表说明',
			content:
				'1. 校园网环境下无法登录 VPN，请先切换到非校园网（如手机流量）再导入\n2. 请先用账号密码登录学校 WebVPN（扫码容易失败）\n3. 登录成功后会自动进入课表，也可点顶部「进课表」\n4. 课表显示后点右上角「提取课表」',
			showCancel: false,
			confirmText: '知道了'
		})
	}, 500)
	// #endif

	// #ifndef APP-PLUS
	uni.showModal({
		title: '提示',
		content: '完整「登录后提取课表」能力主要在 App 端可用。当前将打开 WebVPN，请自行登录。',
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

const EXTRACT_JS = `
(function() {
	var courses = [];
	var nodes = document.querySelectorAll('#table1 .timetable_con');
	if(nodes.length === 0) {
		window.location.href = 'app-import://data=' + encodeURIComponent('[]');
		return;
	}
	var nameByTd = {};
	for(var i = 0; i < nodes.length; i++) {
		var node = nodes[i];
		var td = node.closest('td');
		if(!td || !td.id) continue;
		var parts = td.id.split('-');
		if(parts.length !== 2) continue;
		var day = parseInt(parts[0], 10);
		var start = parseInt(parts[1], 10);
		var span = parseInt(td.getAttribute('rowspan'), 10) || 1;

		var titleNode = node.querySelector('.title font');
		var name = titleNode ? (titleNode.innerText || titleNode.textContent || '').trim() : '';
		// 同格后续块可能无课名（教务续排），继承本格上一门课名
		if(!name) name = nameByTd[td.id] || '';
		else nameByTd[td.id] = name;
		if(!name) continue;

		var pNodes = node.querySelectorAll('p');
		var weeksStr = '', location = '', teacher = '';
		for(var j = 0; j < pNodes.length; j++) {
			var p = pNodes[j];
			var tooltipSpan = p.querySelector('span[data-toggle="tooltip"]');
			if(!tooltipSpan) continue;
			var titleAttr = tooltipSpan.getAttribute('title') || '';
			var text = (p.innerText || p.textContent || '').replace(/\\s+/g, ' ').trim();
			if(titleAttr.indexOf('节/周') !== -1) weeksStr = text;
			else if(titleAttr.indexOf('上课地点') !== -1) location = text;
			else if(titleAttr.indexOf('教师') !== -1) teacher = text;
		}

		// 优先用 weeksStr 中的 (a-b节) 覆盖 td 的 rowspan（同格多段节次不同）
		if(weeksStr) {
			var pm = weeksStr.match(/\\((\\d+)\\s*-\\s*(\\d+)节\\)/);
			if(pm) {
				start = parseInt(pm[1], 10);
				var endP = parseInt(pm[2], 10);
				if(!isNaN(start) && !isNaN(endP) && endP >= start) span = endP - start + 1;
			} else {
				var ps = weeksStr.match(/\\((\\d+)节\\)/);
				if(ps) {
					start = parseInt(ps[1], 10);
					span = 1;
				}
			}
		}

		courses.push({
			id: td.id + '-' + i,
			name: name,
			day: day,
			start: start,
			span: span,
			weeksStr: weeksStr,
			location: location,
			teacher: teacher
		});
	}
	window.location.href = 'app-import://data=' + encodeURIComponent(JSON.stringify(courses));
})();
`

onNavigationBarButtonTap((e) => {
	// pages.json: 0=提取课表, 1=进课表
	if (e.index === 1) {
		goToTimetable()
		return
	}
	if (e.index !== 0) return

	const currentUrl = (() => {
		try {
			return (wv && wv.getURL && wv.getURL()) || targetUrl.value || ''
		} catch (err) {
			return targetUrl.value || ''
		}
	})()

	// 以真实课表 URL 为准，不允许 phase 误判后空提取
	if (!isTimetableUrl(currentUrl)) {
		uni.showModal({
			title: '还未进入课表页',
			content:
				'当前页面不是教务「个人课表查询」。请先完成 WebVPN 登录，再点「进课表」，等课表表格出现后再提取。',
			confirmText: '进课表',
			success: (res) => {
				if (res.confirm) goToTimetable()
			}
		})
		return
	}

	phase.value = 'timetable'
	hasJumpedToTimetable = true

	if (!wv) {
		uni.showToast({ title: 'WebView 未就绪，请稍候再试', icon: 'none' })
		return
	}

	uni.showLoading({ title: '正在提取中...' })
	try {
		wv.evalJS(EXTRACT_JS)
	} catch (err) {
		uni.hideLoading()
		uni.showToast({ title: '提取失败，请确认已打开课表页', icon: 'none' })
		return
	}
	setTimeout(() => uni.hideLoading(), 1200)
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
