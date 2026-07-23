/**
 * WebVPN 相关：先门户登录、再进深链，避免内嵌 WebView 深链登录卡顿
 */

export const WEBVPN_HOME = 'https://webvpn.scut.edu.cn/'

/** 是否为认证 / SSO / 企微扫码等登录相关页 */
export function isAuthUrl(url = '') {
	const u = String(url).toLowerCase()
	return (
		u.includes('/users/sign_in') ||
		u.includes('/users/auth') ||
		u.includes('/cas/login') ||
		u.includes('sso.scut.edu.cn') ||
		u.includes('sso-443.webvpn') ||
		u.includes('open.weixin.qq.com') ||
		u.includes('login.work.weixin') ||
		u.includes('work.weixin.qq.com')
	)
}

/** 登录失败回调页 */
export function isLoginFailedUrl(url = '') {
	const u = String(url || '').toLowerCase()
	return (
		u.includes('login%20failed') ||
		u.includes('login failed') ||
		u.includes('login_failed') ||
		u.includes('auth/failure') ||
		u.includes('authenticationfailed') ||
		u.includes('wwlogin_err') ||
		u.includes('error=access_denied')
	)
}

/**
 * 是否需要「先 WebVPN 登录再跳转」的深链
 * - *.webvpn.scut.edu.cn 子站 / 资源站：需要
 * - 门户本身 webvpn.scut.edu.cn/ ：不需要（已是登录入口）
 */
export function needsWebvpnGateway(url = '') {
	try {
		const u = new URL(String(url).trim())
		const host = u.hostname.toLowerCase()
		if (!host.endsWith('webvpn.scut.edu.cn')) return false
		if (host === 'webvpn.scut.edu.cn') {
			const path = u.pathname || '/'
			return path !== '/' && path !== ''
		}
		return true
	} catch (_) {
		const s = String(url).toLowerCase()
		if (!s.includes('webvpn.scut.edu.cn')) return false
		if (/^https?:\/\/webvpn\.scut\.edu\.cn\/?$/i.test(s.trim())) return false
		return true
	}
}

/** 当前地址是否已到达目标深链（同 host；根路径或文件名匹配即可） */
export function isTargetReached(currentUrl = '', targetUrl = '') {
	if (!currentUrl || !targetUrl) return false
	try {
		const cur = new URL(currentUrl)
		const tgt = new URL(targetUrl)
		if (cur.hostname.toLowerCase() !== tgt.hostname.toLowerCase()) return false
		const tgtPath = tgt.pathname || '/'
		const curPath = cur.pathname || '/'
		if (tgtPath === '/' || tgtPath === '') return true
		if (curPath === tgtPath) return true
		const tgtFile = tgtPath.split('/').filter(Boolean).pop() || ''
		const stem = tgtFile.replace(/\.html?$/i, '')
		if (stem && curPath.toLowerCase().includes(stem.toLowerCase())) return true
		return false
	} catch (_) {
		const c = String(currentUrl).toLowerCase()
		const t = String(targetUrl).toLowerCase()
		const bare = t.split('?')[0]
		return c.includes(bare) || c.startsWith(bare)
	}
}

/** 是否落在 WebVPN 门户（登录后首页），用于自动跳深链 */
export function isWebvpnPortalUrl(url = '') {
	try {
		const u = new URL(String(url))
		return u.hostname.toLowerCase() === 'webvpn.scut.edu.cn'
	} catch (_) {
		return /https?:\/\/webvpn\.scut\.edu\.cn(\/|$|\?)/i.test(String(url))
	}
}

/**
 * 打开需登录的 WebVPN 深链（App 网关页）；普通链接走通用 webview
 * @param {string} url
 * @param {{ title?: string }} [opts]
 */
export function openCampusWeb(url, opts = {}) {
	const title = opts.title || ''
	if (needsWebvpnGateway(url)) {
		const q = [`url=${encodeURIComponent(url)}`]
		if (title) q.push(`title=${encodeURIComponent(title)}`)
		uni.navigateTo({ url: `/pages/webvpn/webvpn?${q.join('&')}` })
		return
	}
	uni.navigateTo({
		url: `/pages/webview/webview?url=${encodeURIComponent(url)}`
	})
}
