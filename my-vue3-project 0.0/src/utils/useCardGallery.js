import { ref, computed, onMounted, reactive } from 'vue'

/**
 * 连续轨道跟手滑动（非三槽回收）
 *
 * 闪屏根因：切页时重建 slot / 重挂 <image>，即使原图也会先空白再出图。
 * 做法：所有页排在一条 translate 轨道上，滑动只改位移；
 * 图片用稳定 key，邻近页保持挂载，切页不销毁当前可见节点。
 */
export function useCardGallery(options = {}) {
  const { length, getSrcAt, imageHeadRpx = 280, animMs = 500, keepRadius = 2 } = options

  const current = ref(0)
  const stageW = ref(375)
  const stageH = ref(500)
  const imageH = ref(360)
  const dragX = ref(0)
  const animating = ref(false)
  /** 已挂载过的页：在半径外可卸；半径内保持，避免来回闪 */
  const mounted = reactive({})

  let startX = 0
  let startY = 0
  let startDragX = 0
  let tracking = false
  let lockedAxis = ''
  let startTime = 0

  const resolveLength = () => {
    if (typeof length === 'function') return length()
    return length || 0
  }

  const markMountedAround = (c) => {
    const n = resolveLength()
    for (let i = c - keepRadius; i <= c + keepRadius; i++) {
      if (i >= 0 && i < n) mounted[i] = true
    }
  }

  const pruneFar = (c) => {
    const n = resolveLength()
    const limit = keepRadius + 2
    for (let i = 0; i < n; i++) {
      if (mounted[i] && Math.abs(i - c) > limit) {
        delete mounted[i]
      }
    }
  }

  /** 已挂载则尽量保留；仅远处卸载。切页不重建当前可见 image → 不闪 */
  const shouldMount = (i) => {
    if (mounted[i]) return Math.abs(i - current.value) <= keepRadius + 2
    return Math.abs(i - current.value) <= 1
  }

  const trackStyle = computed(() => {
    const x = -current.value * stageW.value + dragX.value
    return {
      width: stageW.value * Math.max(1, resolveLength()) + 'px',
      height: stageH.value + 'px',
      transform: `translate3d(${x}px,0,0)`,
      transition: animating.value
        ? `transform ${animMs / 1000}s cubic-bezier(0.33, 0.1, 0.25, 1)`
        : 'none'
    }
  })

  const slideStyle = computed(() => ({
    width: stageW.value + 'px',
    height: stageH.value + 'px'
  }))

  const measure = () => {
    try {
      const sys = uni.getSystemInfoSync()
      const upx = (r) => (typeof uni.upx2px === 'function' ? uni.upx2px(r) : r / 2)
      stageW.value = sys.windowWidth || 375
      // 给顶部提示、底部圆点、卡片上下边距多留一点，避免底部署名被裁切
      const hint = upx(56)
      const dots = upx(56)
      const cardVMargin = upx(52)
      stageH.value = Math.max(280, (sys.windowHeight || 600) - hint - dots)
      // imageHead：标签+标题+说明文字+内边距
      imageH.value = Math.max(160, stageH.value - cardVMargin - upx(imageHeadRpx))
    } catch (_) {}
  }

  const preloadAround = (c) => {
    if (typeof getSrcAt !== 'function') return
    for (let i = c - 1; i <= c + 2; i++) {
      const src = getSrcAt(i)
      if (!src) continue
      try {
        uni.getImageInfo({ src })
      } catch (_) {}
    }
  }

  const onTouchStart = (e) => {
    if (animating.value) return
    const t = e.touches && e.touches[0]
    if (!t) return
    tracking = true
    lockedAxis = ''
    startX = t.clientX
    startY = t.clientY
    startDragX = dragX.value
    startTime = Date.now()
    // 手指按下时就把邻页挂上并预解码，滑动过程中图已在
    markMountedAround(current.value)
    preloadAround(current.value)
  }

  const onTouchMove = (e) => {
    if (!tracking || animating.value) return
    const t = e.touches && e.touches[0]
    if (!t) return
    const dx = t.clientX - startX
    const dy = t.clientY - startY
    if (!lockedAxis) {
      if (Math.abs(dx) < 6 && Math.abs(dy) < 6) return
      lockedAxis = Math.abs(dx) > Math.abs(dy) * 1.1 ? 'x' : 'y'
    }
    if (lockedAxis !== 'x') return

    // 仅横向跟手时拦截默认滚动；cancelable=false 时勿 preventDefault（会刷控制台警告）
    if (e && e.cancelable) {
      try {
        e.preventDefault()
      } catch (_) {}
    }

    let next = startDragX + dx
    const n = resolveLength()
    if ((current.value === 0 && next > 0) || (current.value === n - 1 && next < 0)) {
      next *= 0.32
    }
    dragX.value = next

    // 拖过半屏时提前挂载目标页
    if (dx < -stageW.value * 0.15) {
      markMountedAround(current.value + 1)
      preloadAround(current.value + 1)
    } else if (dx > stageW.value * 0.15) {
      markMountedAround(current.value - 1)
      preloadAround(current.value - 1)
    }
  }

  const finishTo = (targetIndex) => {
    const w = stageW.value
    const n = resolveLength()
    const from = current.value
    const to = Math.max(0, Math.min(n - 1, targetIndex))

    markMountedAround(to)
    preloadAround(to)

    // 目标：-to*w；当前：-from*w+dragX → 动画到 dragX=(from-to)*w
    // 先关过渡再开，保证 App 上 500ms transition 一定生效（与立绘页同一套）
    const dest = (from - to) * w
    animating.value = false
    setTimeout(() => {
      animating.value = true
      dragX.value = dest
      setTimeout(() => {
        animating.value = false
        current.value = to
        dragX.value = 0
        markMountedAround(to)
        pruneFar(to)
        preloadAround(to)
      }, animMs + 20)
    }, 16)
  }

  const onTouchEnd = () => {
    if (!tracking) return
    tracking = false
    if (lockedAxis !== 'x') {
      dragX.value = 0
      return
    }
    const w = stageW.value
    const dx = dragX.value
    const dt = Math.max(1, Date.now() - startTime)
    const velocity = dx / dt
    // 与立绘卡片同一套：需要更明确的滑动才翻页，避免轻甩「一下就过」
    const threshold = w * 0.22
    let target = current.value
    if (dx < -threshold || velocity < -0.55) target = current.value + 1
    else if (dx > threshold || velocity > 0.55) target = current.value - 1
    finishTo(target)
  }

  onMounted(() => {
    measure()
    markMountedAround(0)
    preloadAround(0)
  })

  return {
    current,
    stageW,
    stageH,
    imageH,
    dragX,
    animating,
    mounted,
    trackStyle,
    slideStyle,
    shouldMount,
    markMountedAround,
    onTouchStart,
    onTouchMove,
    onTouchEnd
  }
}
