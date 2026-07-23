import { openCampusWeb } from '@/utils/webvpn.js'
import { sanitizeActions, actionFromCatalogKey } from '@/utils/serviceCatalog.js'

/** 取消尚未执行的跳转，避免连续对话时旧 actions 迟到叠加 */
let actionRunId = 0

/**
 * 与首页功能按钮同一套打开逻辑：
 * - *.webvpn 深链 → WebVPN 网关页（先登录再进目标）
 * - 普通链接 → webview
 * - 课表 / 首页 → switchTab
 */
function runOne(action) {
  return new Promise((resolve) => {
    const done = () => resolve(true)
    const fail = (err) => {
      console.error('agent action failed', action, err)
      uni.showToast({ title: '打开页面失败', icon: 'none' })
      resolve(false)
    }

    if (action.type === 'switch_tab') {
      uni.switchTab({ url: action.path, success: done, fail })
      return
    }
    if (action.type === 'navigate_to') {
      uni.navigateTo({ url: action.path, success: done, fail })
      return
    }
    if (action.type === 'open_campus_web' || action.type === 'open_webview') {
      try {
        openCampusWeb(action.url, { title: action.title || '' })
        done()
      } catch (e) {
        fail(e)
      }
      return
    }
    resolve(false)
  })
}

/**
 * 按服务 key 打开（与首页「自主选课」「查分」等按钮等价）
 * @param {string} serviceKey
 */
export function openCampusServiceByKey(serviceKey) {
  const act = actionFromCatalogKey(serviceKey)
  if (!act) {
    uni.showToast({ title: '暂不支持该服务', icon: 'none' })
    return Promise.resolve(false)
  }
  return runOne(act)
}

/**
 * 本轮只执行一次跳转意图：若同轮有多条，优先最后一条（最新意图）
 * @param {any[]} actions
 * @returns {Promise<number>}
 */
export async function runAgentActions(actions) {
  const list = sanitizeActions(actions)
  if (!list.length) return 0

  const runId = ++actionRunId
  // 同轮多条时只执行最后一条，避免「先立绘再首页」连环跳
  const toRun = [list[list.length - 1]]

  let ok = 0
  for (const act of toRun) {
    if (runId !== actionRunId) return ok
    // eslint-disable-next-line no-await-in-loop
    const success = await runOne(act)
    if (success) ok += 1
  }
  return ok
}

/** 使尚未跑完的 runAgentActions 失效（新对话发出时调用） */
export function cancelPendingAgentActions() {
  actionRunId += 1
}
