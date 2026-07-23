<template>
  <view class="page">
    <view
      class="main-stage"
      @touchstart="onTouchStart"
      @touchend="onTouchEnd"
    >
      <!-- 对话层 -->
      <view class="chat-page" :class="{ dimmed: showPortrait }">
        <view class="header">
          <image class="header-avatar" :src="ART_IMAGES.half" mode="aspectFill" />
          <view class="header-meta">
            <text class="header-title">华工智能体</text>
            <text class="header-sub">左滑看形象 · 长按气泡可复制</text>
          </view>
          <view
            class="new-chat-btn"
            :class="{ disabled: sending }"
            @tap="onNewChatTap"
          >
            <text class="new-chat-text">新对话</text>
          </view>
        </view>

        <scroll-view
          class="chat-scroll"
          scroll-y
          :scroll-into-view="scrollIntoView"
          :scroll-with-animation="true"
        >
          <view class="chat-list">
            <view
              v-for="msg in messages"
              :id="'msg-' + msg.key"
              :key="msg.key"
              class="message-row"
              :class="msg.role"
            >
              <image
                v-if="msg.role === 'agent'"
                class="msg-avatar"
                :src="ART_IMAGES.half"
                mode="aspectFill"
              />
              <view class="msg-bubble" :class="msg.role">
                <view v-if="msg.loading" class="loading-text">思考中...</view>

                <view v-else class="msg-body">
                  <view
                    v-if="msg.thinkHtml"
                    class="think-block"
                    @longpress.stop="copyMsgPart(msg, 'think')"
                  >
                    <view class="think-header" @tap="toggleThink(msg)">
                      <text class="think-title">{{
                        msg.thinkExpanded ? '深度思考（长按复制）' : '深度思考完成（点击展开）'
                      }}</text>
                      <text class="think-arrow">{{ msg.thinkExpanded ? '▾' : '▸' }}</text>
                    </view>
                    <view v-if="msg.thinkExpanded" class="think-body">
                      <rich-text class="md-rich" :nodes="msg.thinkHtml" />
                    </view>
                  </view>

                  <view
                    v-if="msg.mainHtml"
                    class="main-copy-zone"
                    @longpress.stop="copyMsgPart(msg, 'main')"
                  >
                    <rich-text class="md-rich" :nodes="msg.mainHtml" />
                  </view>
                  <view
                    v-if="msg.setupDocsUrl"
                    class="setup-docs-link"
                    @tap.stop="openSetupDocs(msg.setupDocsUrl)"
                  >
                    <text class="setup-docs-text">查看后端配置说明（点击打开）</text>
                    <text class="setup-docs-url">{{ msg.setupDocsUrl }}</text>
                  </view>
                </view>
              </view>
            </view>
            <view id="msg-bottom" class="scroll-pad" />
          </view>
        </scroll-view>

        <view class="input-panel">
          <textarea
            class="input-area"
            v-model="inputText"
            :disabled="sending"
            :auto-height="true"
            :maxlength="-1"
            confirm-type="send"
            placeholder="输入消息，点发送或完成键"
            @confirm="sendMessage"
          />
          <view
            class="send-btn"
            :class="{ disabled: sending || !inputText.trim() }"
            @tap="sendMessage"
          >
            <text class="send-icon">➤</text>
          </view>
        </view>
      </view>

      <!-- 全身像：左滑从右侧滑入 -->
      <view class="portrait-page" :class="{ show: showPortrait }">
        <image class="portrait-img" :src="ART_IMAGES.full" mode="aspectFill" />
        <view class="portrait-mask" />
        <view class="portrait-card">
          <text class="portrait-name">华工智能体</text>
          <view class="portrait-badge" @tap="closePortrait">
            <view class="status-dot" />
            <text class="portrait-badge-text">右滑返回对话</text>
          </view>
        </view>
      </view>
    </view>
  </view>
</template>

<script setup>
import { ref, nextTick } from 'vue'
import { onShow } from '@dcloudio/uni-app'
import { getAgentBaseUrl, AGENT_SETUP_DOCS_URL } from '@/utils/agentConfig.js'
import { ART_IMAGES } from '@/utils/artAssets.js'
import {
  parseStreamParts,
  mdToHtml,
  buildErrorHtml,
  htmlToPlain
} from '@/utils/agentMarkdown.js'
import { runAgentActions, cancelPendingAgentActions } from '@/utils/agentActions.js'
import { buildDeviceContext } from '@/utils/agentContext.js'
import { openCampusWeb } from '@/utils/webvpn.js'

const MSG_KEY = 'agent_chat_messages_v1'
const TID_KEY = 'agent_thread_id_v1'
const MAX_STORE = 40

const WELCOME_TEXT =
  '你好！我是华工助手。\n\n可以问我「今天有什么课」「我签到了吗」，也可以说「打开课表」「我要查分」等让我帮你跳转。'

const showPortrait = ref(false)
let touchStartX = 0
let touchStartY = 0
/** 长按复制后短暂忽略滑动，避免误开全身像 */
let suppressSwipeUntil = 0

const defaultWelcome = () => ({
  key: 'welcome',
  role: 'agent',
  thinkHtml: '',
  thinkText: '',
  thinkExpanded: false,
  plainText: WELCOME_TEXT,
  mainHtml: mdToHtml(WELCOME_TEXT),
  loading: false
})

const newThreadId = () => 'app-' + Date.now()

const messages = ref([defaultWelcome()])
const inputText = ref('')
const sending = ref(false)
const scrollIntoView = ref('')
const threadId = ref(newThreadId())
let actionTimer = null

const clearActionTimer = () => {
  if (actionTimer) {
    clearTimeout(actionTimer)
    actionTimer = null
  }
}

/** 通知后端丢掉旧 thread 记忆（失败不影响前端开启新对话） */
const resetBackendThread = (oldTid) => {
  if (!oldTid) return
  const base = getAgentBaseUrl()
  try {
    uni.request({
      url: `${base}/chat/reset`,
      method: 'POST',
      timeout: 8000,
      header: { 'Content-Type': 'application/json' },
      data: { thread_id: oldTid },
      fail: () => {}
    })
  } catch (_) {}
}

const startNewChat = () => {
  if (sending.value) {
    uni.showToast({ title: '请等待当前回复结束', icon: 'none' })
    return
  }
  const oldTid = threadId.value
  clearActionTimer()
  cancelPendingAgentActions()
  resetBackendThread(oldTid)

  threadId.value = newThreadId()
  messages.value = [defaultWelcome()]
  inputText.value = ''
  scrollIntoView.value = ''
  try {
    uni.removeStorageSync(MSG_KEY)
    uni.setStorageSync(TID_KEY, threadId.value)
  } catch (_) {}
  uni.showToast({ title: '已开启新对话', icon: 'none' })
}

const onNewChatTap = () => {
  if (sending.value) {
    uni.showToast({ title: '请等待当前回复结束', icon: 'none' })
    return
  }
  const hasHistory = messages.value.some((m) => m.key !== 'welcome')
  if (!hasHistory) {
    startNewChat()
    return
  }
  uni.showModal({
    title: '开启新对话',
    content: '将清空当前聊天记录并开始新会话，是否继续？',
    confirmText: '开启',
    cancelText: '取消',
    success: (res) => {
      if (res.confirm) startNewChat()
    }
  })
}

const persistChat = () => {
  try {
    const slim = messages.value
      .filter((m) => !m.loading)
      .slice(-MAX_STORE)
      .map((m) => ({
        key: m.key,
        role: m.role,
        thinkHtml: m.thinkHtml || '',
        thinkText: m.thinkText || '',
        thinkExpanded: !!m.thinkExpanded,
        plainText: m.plainText || '',
        mainHtml: m.mainHtml || '',
        setupDocsUrl: m.setupDocsUrl || '',
        loading: false
      }))
    uni.setStorageSync(MSG_KEY, slim)
    uni.setStorageSync(TID_KEY, threadId.value)
  } catch (_) {}
}

const normalizeMsg = (m) => {
  const thinkHtml = m.thinkHtml || ''
  const mainHtml = m.mainHtml || ''
  return {
    ...m,
    loading: false,
    thinkExpanded: !!m.thinkExpanded,
    thinkHtml,
    mainHtml,
    // 旧缓存可能没有纯文本字段，从 HTML 兜底还原
    thinkText: m.thinkText || (thinkHtml ? htmlToPlain(thinkHtml) : ''),
    plainText: m.plainText || (mainHtml ? htmlToPlain(mainHtml) : ''),
    setupDocsUrl: m.setupDocsUrl || ''
  }
}

const openSetupDocs = (url) => {
  const target = (url || AGENT_SETUP_DOCS_URL || '').trim()
  if (!target) return
  openCampusWeb(target, { title: '后端配置说明' })
}

const restoreChat = () => {
  try {
    const tid = uni.getStorageSync(TID_KEY)
    const list = uni.getStorageSync(MSG_KEY)
    if (tid && typeof tid === 'string') threadId.value = tid
    if (Array.isArray(list) && list.length) {
      messages.value = list.map(normalizeMsg)
    }
  } catch (_) {}
}

restoreChat()

onShow(() => {
  // switchTab 保活页面；仅在消息异常少时兜底恢复
  if (messages.value.length <= 1) restoreChat()
})

const onTouchStart = (e) => {
  const t = (e.touches && e.touches[0]) || (e.changedTouches && e.changedTouches[0])
  if (!t) return
  touchStartX = t.clientX
  touchStartY = t.clientY
}

const onTouchEnd = (e) => {
  if (Date.now() < suppressSwipeUntil) return
  const t = e.changedTouches && e.changedTouches[0]
  if (!t) return
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  if (Math.abs(dx) < 60 || Math.abs(dx) < Math.abs(dy) * 1.2) return

  // 左滑打开全身像；右滑关闭
  if (dx < 0) {
    showPortrait.value = true
    return
  }
  if (dx > 0) {
    showPortrait.value = false
  }
}

const closePortrait = () => {
  showPortrait.value = false
}

const scrollToBottom = async () => {
  await nextTick()
  scrollIntoView.value = ''
  await nextTick()
  scrollIntoView.value = 'msg-bottom'
}

const toggleThink = (msg) => {
  if (!msg) return
  msg.thinkExpanded = !msg.thinkExpanded
}

const resolveCopyText = (msg, part) => {
  if (!msg) return ''
  if (part === 'think') {
    return (msg.thinkText || htmlToPlain(msg.thinkHtml) || '').trim()
  }
  return (msg.plainText || htmlToPlain(msg.mainHtml) || '').trim()
}

const copyMsgPart = (msg, part) => {
  if (msg && msg.loading) return
  suppressSwipeUntil = Date.now() + 500
  const text = resolveCopyText(msg, part)
  if (!text) {
    uni.showToast({ title: '没有可复制内容', icon: 'none' })
    return
  }
  uni.setClipboardData({
    data: text,
    showToast: false,
    success: () => {
      uni.showToast({
        title: part === 'think' ? '已复制思考过程' : '已复制到剪贴板',
        icon: 'none',
        duration: 1500
      })
    },
    fail: () => {
      uni.showToast({ title: '复制失败', icon: 'none' })
    }
  })
}

const sendMessage = async () => {
  const text = inputText.value.trim()
  if (!text || sending.value) return

  showPortrait.value = false
  // 新一轮对话：取消上一轮尚未执行/正在执行的跳转
  clearActionTimer()
  cancelPendingAgentActions()

  messages.value.push({
    key: 'u-' + Date.now(),
    role: 'user',
    thinkHtml: '',
    thinkText: '',
    thinkExpanded: false,
    plainText: text,
    mainHtml: mdToHtml(text),
    loading: false
  })

  inputText.value = ''
  sending.value = true
  await scrollToBottom()

  const agentIndex = messages.value.length
  messages.value.push({
    key: 'a-' + Date.now(),
    role: 'agent',
    thinkHtml: '',
    thinkText: '',
    thinkExpanded: false,
    plainText: '',
    mainHtml: '',
    loading: true
  })
  await scrollToBottom()

  const base = getAgentBaseUrl()

  try {
    const res = await new Promise((resolve, reject) => {
      uni.request({
        url: `${base}/chat`,
        method: 'POST',
        timeout: 180000,
        header: { 'Content-Type': 'application/json' },
        data: {
          message: text,
          thread_id: threadId.value,
          device_context: buildDeviceContext(text)
        },
        success: (r) => resolve(r),
        fail: (e) => reject(e)
      })
    })

    if (res.statusCode < 200 || res.statusCode >= 300) {
      throw new Error(`HTTP ${res.statusCode}`)
    }

    const answer = (res.data && res.data.answer) || '未获取到回复'
    if (res.data && res.data.thread_id) {
      threadId.value = res.data.thread_id
    }

    const parts = parseStreamParts(answer)
    const msg = messages.value[agentIndex]
    msg.loading = false
    if (parts.thinkHtml) {
      msg.thinkHtml = parts.thinkHtml
      msg.thinkText = parts.thinkText || ''
      msg.thinkExpanded = false
    } else {
      msg.thinkHtml = ''
      msg.thinkText = ''
      msg.thinkExpanded = false
    }
    const mainPlain = (parts.mainText || '').trim() || '（空回复）'
    msg.plainText = mainPlain
    msg.mainHtml = parts.mainHtml || mdToHtml(mainPlain)
    persistChat()

    // 只执行本轮 actions（后端已按「最后一条用户消息之后」过滤）
    const actions = (res.data && res.data.actions) || []
    if (actions.length) {
      await scrollToBottom()
      clearActionTimer()
      actionTimer = setTimeout(() => {
        actionTimer = null
        runAgentActions(actions)
      }, 400)
    }
  } catch (err) {
    const tip = (err && (err.errMsg || err.message)) || '请求失败'
    const errText =
      `请求失败：${tip}\n请确认电脑已启动 Agent（8000）。\n真机需 adb reverse 或改电脑局域网 IP。\n当前：${base}\n也有可能是您未配置后端，请点下方链接查看配置说明。`
    const msg = messages.value[agentIndex]
    msg.loading = false
    msg.thinkHtml = ''
    msg.thinkText = ''
    msg.plainText = `${errText}\n${AGENT_SETUP_DOCS_URL}`
    msg.mainHtml = buildErrorHtml(errText)
    msg.setupDocsUrl = AGENT_SETUP_DOCS_URL
    persistChat()
  } finally {
    sending.value = false
    await scrollToBottom()
  }
}
</script>

<style lang="scss" scoped>
.page {
  height: 100vh;
  background: linear-gradient(165deg, #ebf2f7 0%, #e8eef3 100%);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  padding-bottom: 0;
  overflow: hidden;
}

.main-stage {
  flex: 1;
  height: 0;
  position: relative;
  overflow: hidden;
}

.chat-page {
  height: 100%;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
  transition: opacity 0.25s ease;
}

.chat-page.dimmed {
  opacity: 0.35;
  pointer-events: none;
}

.header {
  display: flex;
  align-items: center;
  gap: 36rpx;
  padding: 28rpx 32rpx;
  background: rgba(244, 248, 250, 0.96);
  border-bottom: 1px solid #e2eaf0;
  flex-shrink: 0;
}

.header-avatar {
  width: 132rpx;
  height: 132rpx;
  border-radius: 30rpx;
  border: 3rpx solid #e2eaf0;
  background: #fff;
  flex-shrink: 0;
}

.header-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10rpx;
  min-width: 0;
}

.header-title {
  font-size: 40rpx;
  font-weight: 600;
  color: #334155;
}

.header-sub {
  font-size: 26rpx;
  color: #76a9cc;
}

.new-chat-btn {
  flex-shrink: 0;
  padding: 12rpx 22rpx;
  border-radius: 16rpx;
  background: #e3f2fd;
  border: 1px solid rgba(82, 155, 204, 0.35);
}

.new-chat-btn.disabled {
  opacity: 0.45;
}

.new-chat-text {
  font-size: 24rpx;
  color: #529bcc;
  font-weight: 600;
}

.chat-scroll {
  flex: 1;
  height: 0;
  box-sizing: border-box;
}

.chat-list {
  display: flex;
  flex-direction: column;
  padding: 28rpx 24rpx 8rpx;
  box-sizing: border-box;
}

.message-row {
  display: flex;
  gap: 24rpx;
  margin-bottom: 32rpx;
  max-width: 94%;
}

.message-row.user {
  align-self: flex-end;
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-row.agent {
  align-self: flex-start;
}

.msg-avatar {
  width: 108rpx;
  height: 108rpx;
  border-radius: 24rpx;
  flex-shrink: 0;
  border: 3rpx solid #e2eaf0;
  background: #fff;
}

.msg-bubble {
  padding: 24rpx 28rpx;
  border-radius: 26rpx;
  line-height: 1.55;
  font-size: 28rpx;
  word-break: break-word;
  max-width: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.msg-bubble.user {
  background: #e3f2fd;
  color: #1e293b;
  border: 1px solid rgba(148, 193, 224, 0.35);
  border-top-right-radius: 8rpx;
}

.msg-bubble.agent {
  background: #fff;
  color: #334155;
  border: 1px solid #e2eaf0;
  border-top-left-radius: 8rpx;
  box-shadow: 0 4rpx 16rpx rgba(148, 193, 224, 0.12);
}

.loading-text {
  color: #94a3b8;
  font-size: 28rpx;
}

.think-block {
  background: #f8fafc;
  border-left: 6rpx solid #94c1e0;
  border-radius: 12rpx;
  padding: 16rpx 18rpx;
  margin-bottom: 16rpx;
}

.think-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12rpx;
}

.think-title {
  font-size: 24rpx;
  color: #94a3b8;
  font-weight: 500;
}

.think-arrow {
  font-size: 24rpx;
  color: #94c1e0;
}

.think-body {
  margin-top: 12rpx;
  padding-top: 12rpx;
  border-top: 1px dashed #e2eaf0;
}

.main-copy-zone {
  width: 100%;
}

.setup-docs-link {
  margin-top: 16rpx;
  padding: 12rpx 0 4rpx;
  display: flex;
  flex-direction: column;
  gap: 8rpx;
}

.setup-docs-text {
  color: #529bcc;
  font-size: 28rpx;
  font-weight: 600;
  text-decoration: underline;
  line-height: 1.5;
}

.setup-docs-url {
  color: #64748b;
  font-size: 24rpx;
  line-height: 1.45;
  word-break: break-all;
  text-decoration: underline;
}

.md-rich {
  width: 100%;
  font-size: 28rpx;
  line-height: 1.6;
  color: #334155;
  word-break: break-word;
  /* H5 端辅助选中；App 端以 longpress 复制为主 */
  user-select: text;
  -webkit-user-select: text;
}

.scroll-pad {
  height: 16rpx;
}

.input-panel {
  display: flex;
  align-items: flex-end;
  gap: 16rpx;
  padding: 16rpx 24rpx 20rpx;
  background: #fff;
  border-top: 1px solid #e2eaf0;
  flex-shrink: 0;
}

.input-area {
  flex: 1;
  min-height: 72rpx;
  max-height: 200rpx;
  padding: 18rpx 22rpx;
  background: #f8fafc;
  border: 1px solid #e2eaf0;
  border-radius: 20rpx;
  font-size: 28rpx;
  color: #334155;
  box-sizing: border-box;
  width: auto;
}

.send-btn {
  width: 88rpx;
  height: 88rpx;
  border-radius: 20rpx;
  background: #94c1e0;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  box-shadow: 0 6rpx 16rpx rgba(148, 193, 224, 0.45);
}

.send-btn.disabled {
  background: #e2eaf0;
  box-shadow: none;
}

.send-icon {
  color: #fff;
  font-size: 32rpx;
  font-weight: 600;
}

.portrait-page {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  background: #f4f8fa;
  transform: translateX(100%);
  transition: transform 0.28s ease;
  z-index: 20;
}

.portrait-page.show {
  transform: translateX(0);
}

.portrait-img {
  width: 100%;
  height: 100%;
}

.portrait-mask {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 42%;
  background: linear-gradient(to top, rgba(244, 248, 250, 0.96) 55%, rgba(244, 248, 250, 0));
  pointer-events: none;
}

.portrait-card {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 48rpx;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16rpx;
  padding: 0 32rpx;
}

.portrait-name {
  font-size: 40rpx;
  font-weight: 600;
  color: #334155;
}

.portrait-badge {
  display: flex;
  align-items: center;
  gap: 10rpx;
  padding: 10rpx 24rpx;
  border-radius: 999rpx;
  background: #e3f2fd;
}

.status-dot {
  width: 14rpx;
  height: 14rpx;
  border-radius: 50%;
  background: #4caf50;
}

.portrait-badge-text {
  font-size: 26rpx;
  color: #529bcc;
  font-weight: 500;
}
</style>
