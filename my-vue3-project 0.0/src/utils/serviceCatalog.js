/**
 * 校园服务目录（与 00.my-agent/data/service_catalog.json、首页/用户页入口对齐）
 * Agent 打开服务时强制走本目录的 url/path，效果等同点击对应按钮。
 */
export const SERVICE_CATALOG = {
  home: {
    title: '首页签到',
    type: 'switch_tab',
    path: '/pages/index/index'
  },
  timetable: {
    title: '我的课表',
    type: 'switch_tab',
    path: '/pages/timetable/timetable'
  },
  art: {
    title: '立绘鉴赏',
    type: 'navigate_to',
    path: '/pages/art/art'
  },
  emoji: {
    title: 'Emoji 表情包',
    type: 'navigate_to',
    path: '/pages/emoji/emoji'
  },
  contact: {
    title: '联系开发者',
    type: 'switch_tab',
    path: '/pages/user/user'
  },
  help: {
    title: '使用说明',
    type: 'open_webview',
    url: 'https://dcnmcid6v0ct.feishu.cn/wiki/Yvxzwo85hieZTBkbKdhcvyy2nMe?from=from_copylink'
  },
  feedback: {
    title: '一键反馈',
    type: 'open_webview',
    url: 'https://dcnmcid6v0ct.feishu.cn/wiki/RFEbw4pV8iP6IUkiAzMcmBwKn7c'
  },
  grade: {
    title: '查分',
    type: 'open_campus_web',
    url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/cjcx/cjcx_cxDgXscj.html?gnmkdm=N305005&layout=default'
  },
  gpa: {
    title: 'GPA',
    type: 'open_campus_web',
    url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/design/viewFunc_cxDesignFuncPageIndex.html?gnmkdm=N3091hg05&layout=default'
  },
  course_select: {
    title: '自主选课',
    type: 'open_campus_web',
    url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/xsxk/zzxkyzb_cxZzxkYzbIndex.html?gnmkdm=N253512&layout=default'
  },
  jw_home: {
    title: '教务系统',
    type: 'open_campus_web',
    url: 'https://xsjw2018-jw.webvpn.scut.edu.cn/jwglxt/xtgl/index_initMenu.html?jsdm=xs&_t=1769041397669&echarts=1'
  },
  webvpn: {
    title: 'WebVPN',
    type: 'open_campus_web',
    url: 'https://webvpn.scut.edu.cn/'
  },
  ecourse: {
    title: '课程中心',
    type: 'open_campus_web',
    url: 'https://ecourse.scut.edu.cn'
  },
  ecard: {
    title: '一卡通',
    type: 'open_campus_web',
    url: 'https://ecardwxnew.scut.edu.cn/plat/shouyeUser'
  },
  jw_office: {
    title: '教务处',
    type: 'open_campus_web',
    url: 'https://jw.scut.edu.cn/zhinan/cms/index.do'
  },
  cnki: {
    title: '知网资源',
    type: 'open_campus_web',
    url: 'https://www-cnki-net-443.webvpn.scut.edu.cn/'
  },
  wanfang: {
    title: '万方资源',
    type: 'open_campus_web',
    url: 'https://www-wanfangdata-com-cn-443.webvpn.scut.edu.cn/index.html'
  }
}

const TAB_PATHS = new Set([
  '/pages/index/index',
  '/pages/agent/agent',
  '/pages/user/user',
  '/pages/timetable/timetable'
])

/** 把目录项转成可执行 action（与首页/用户页同一 url/path） */
export function actionFromCatalogKey(key) {
  const item = SERVICE_CATALOG[key]
  if (!item) return null
  if (item.type === 'switch_tab') {
    return { type: 'switch_tab', path: item.path, title: item.title, service_key: key }
  }
  if (item.type === 'navigate_to') {
    return { type: 'navigate_to', path: item.path, title: item.title, service_key: key }
  }
  if (item.type === 'open_campus_web' || item.type === 'open_webview') {
    // 飞书说明/反馈等非 WebVPN 链也走 openCampusWeb：内部会进普通 webview
    return {
      type: 'open_campus_web',
      url: item.url,
      title: item.title,
      service_key: key
    }
  }
  return null
}

function findKeyByUrl(url) {
  const u = String(url || '')
  if (!u) return ''
  for (const [key, item] of Object.entries(SERVICE_CATALOG)) {
    if (item.url && item.url === u) return key
  }
  return ''
}

function findKeyByPath(path) {
  const p = String(path || '').split('?')[0]
  if (!p) return ''
  for (const [key, item] of Object.entries(SERVICE_CATALOG)) {
    if (item.path && item.path === p) return key
  }
  return ''
}

/** 用目录白名单规范化动作；非法则返回 null */
export function sanitizeAction(action) {
  if (!action || typeof action !== 'object') return null
  const type = action.type
  let key = action.service_key

  if (!key || !SERVICE_CATALOG[key]) {
    key = findKeyByUrl(action.url) || findKeyByPath(action.path) || key
  }

  if (key && SERVICE_CATALOG[key]) {
    return actionFromCatalogKey(key)
  }

  if (type === 'switch_tab') {
    const path = String(action.path || '').split('?')[0]
    if (!TAB_PATHS.has(path)) return null
    return {
      type: 'switch_tab',
      path,
      title: action.title || '',
      service_key: key || ''
    }
  }

  if (type === 'navigate_to') {
    const path = String(action.path || '')
    if (!path.startsWith('/pages/')) return null
    if (TAB_PATHS.has(path.split('?')[0])) {
      return { type: 'switch_tab', path: path.split('?')[0], title: action.title || '' }
    }
    return { type: 'navigate_to', path, title: action.title || '' }
  }

  if (type === 'open_campus_web' || type === 'open_webview') {
    const url = String(action.url || '')
    if (!/^https?:\/\//i.test(url)) return null
    // 飞书 / 华工域名
    const hostOk = /scut\.edu\.cn/i.test(url) || /feishu\.cn/i.test(url)
    if (!hostOk) return null
    return {
      type: 'open_campus_web',
      url,
      title: action.title || '',
      service_key: ''
    }
  }

  return null
}

export function sanitizeActions(list) {
  if (!Array.isArray(list)) return []
  const out = []
  const seen = new Set()
  for (const raw of list) {
    const act = sanitizeAction(raw)
    if (!act) continue
    const id =
      act.type === 'switch_tab' || act.type === 'navigate_to'
        ? `${act.type}:${act.path}`
        : `${act.type}:${act.url}`
    if (seen.has(id)) continue
    seen.add(id)
    out.push(act)
  }
  return out
}
