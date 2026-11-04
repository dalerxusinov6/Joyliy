<script setup lang="ts">
/**
 * Drawn Tashkent-modernist facade (panjara sun-screen) used as the hero "photograph".
 * Canvas-only, client-side; redraws on resize and on light/dark theme changes.
 */
const props = withDefaults(defineProps<{ variant?: 'hero' | 'stats' | 'cta' }>(), { variant: 'hero' })
const cv = ref<HTMLCanvasElement | null>(null)

type Opts = Record<string, any>

function rng(seed: number) {
  let s = seed
  return () => ((s = (Math.imul(s ^ (s >>> 15), 1 | s) + 0x6d2b79f5) | 0) >>> 0) / 4294967296
}

function scene(canvas: HTMLCanvasElement, o: Opts) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const W = canvas.clientWidth
  const H = canvas.clientHeight
  if (!W || !H) return
  canvas.width = W * dpr
  canvas.height = H * dpr
  const c = canvas.getContext('2d')!
  c.scale(dpr, dpr)
  const R = rng(o.seed || 7)
  const dusk = !!o.dusk

  let g = c.createLinearGradient(0, 0, 0, H)
  if (dusk) { g.addColorStop(0, '#2E2923'); g.addColorStop(0.55, '#7A6149'); g.addColorStop(1, '#B9926C') }
  else { g.addColorStop(0, '#E4DACB'); g.addColorStop(0.5, '#EFE6D8'); g.addColorStop(0.85, '#EBD8C0') }
  c.fillStyle = g; c.fillRect(0, 0, W, H)

  const sx = W * (o.sunX ?? 0.82), sy = H * (o.sunY ?? 0.22)
  g = c.createRadialGradient(sx, sy, 0, sx, sy, Math.max(W, H) * 0.55)
  g.addColorStop(0, dusk ? 'rgba(255,196,130,.5)' : 'rgba(255,244,222,.95)')
  g.addColorStop(1, 'rgba(255,244,222,0)')
  c.fillStyle = g; c.fillRect(0, 0, W, H)

  const ground = H * (o.ground ?? 0.9)
  c.fillStyle = dusk ? 'rgba(60,50,40,.6)' : 'rgba(196,181,160,.55)'
  for (let x = -20; x < W;) { const w = 30 + R() * 70, h = H * (0.08 + R() * 0.16); c.fillRect(x, ground - h - H * 0.12, w, h + H * 0.12); x += w + 4 + R() * 14 }

  const bx = W * (o.bx ?? 0.5), bw = W * (o.bw ?? 0.44), by = H * (o.by ?? 0.1), bh = ground - by
  c.fillStyle = dusk ? '#5F4F3F' : '#E2D4BF'; c.fillRect(bx, by, bw, bh)
  c.fillStyle = dusk ? '#44392D' : '#CDBBA2'; c.fillRect(bx + bw, by + 8, Math.min(W * 0.06, W - bx - bw), bh - 8)
  const cols = Math.max(6, Math.round(bw / 58)), rows = Math.max(8, Math.round(bh / 52)), cw = bw / cols, rh = bh / rows, pad = Math.max(5, cw * 0.12)
  for (let r = 1; r < rows - 1; r++) for (let k = 0; k < cols; k++) {
    const x = bx + k * cw + pad, y = by + r * rh + pad * 0.8, w = cw - pad * 2, h = rh - pad * 1.6, glow = R() < (dusk ? 0.45 : 0.12)
    const gg = c.createLinearGradient(x, y, x + w, y + h)
    if (glow) { gg.addColorStop(0, dusk ? '#F6C27E' : '#E9C99C'); gg.addColorStop(1, dusk ? '#C98A4E' : '#B99A76') }
    else { gg.addColorStop(0, dusk ? '#2A231C' : '#6E5E4C'); gg.addColorStop(1, dusk ? '#3E342A' : '#8E7B64') }
    c.fillStyle = gg; c.beginPath(); c.moveTo(x + w / 2, y); c.lineTo(x + w, y + h * 0.35); c.lineTo(x + w, y + h); c.lineTo(x, y + h); c.lineTo(x, y + h * 0.35); c.closePath(); c.fill()
    c.fillStyle = dusk ? 'rgba(0,0,0,.22)' : 'rgba(81,68,55,.22)'; c.beginPath(); c.moveTo(x, y + h * 0.35); c.lineTo(x + w / 2, y); c.lineTo(x + w * 0.62, y + h * 0.06); c.lineTo(x + w * 0.14, y + h * 0.42); c.lineTo(x + w * 0.14, y + h); c.lineTo(x, y + h); c.fill()
  }
  c.fillStyle = dusk ? '#715F4C' : '#EDE2D1'; c.fillRect(bx - 6, by, bw + 12, rh * 0.55); c.fillRect(bx - 6, ground - rh * 0.7, bw + 12, rh * 0.7)

  const lx = W * (o.lx ?? 0.12), lw = W * (o.lw ?? 0.34), ly = H * (o.ly ?? 0.55)
  c.fillStyle = dusk ? '#56483A' : '#DCCDB6'; c.fillRect(lx, ly, lw, ground - ly)
  for (let y = ly + 18; y < ground - 20; y += 34) {
    g = c.createLinearGradient(0, y, 0, y + 18); g.addColorStop(0, dusk ? '#E4B47A' : '#BFC3BE'); g.addColorStop(1, dusk ? '#8C6A48' : '#8E9690')
    c.fillStyle = g; c.fillRect(lx + 10, y, lw - 20, 16); c.fillStyle = dusk ? '#71604E' : '#F0E6D7'; c.fillRect(lx + 4, y + 16, lw - 8, 6)
  }
  g = c.createLinearGradient(0, ground, 0, H); g.addColorStop(0, dusk ? '#524436' : '#D2C3AC'); g.addColorStop(1, dusk ? '#352C24' : '#C2B096')
  c.fillStyle = g; c.fillRect(0, ground, W, H - ground)
  c.fillStyle = dusk ? 'rgba(0,0,0,.25)' : 'rgba(81,68,55,.16)'; c.beginPath(); c.moveTo(bx, ground); c.lineTo(bx - W * 0.25, H); c.lineTo(bx + bw - W * 0.25, H); c.lineTo(bx + bw, ground); c.fill()

  const tree = (tx: number, ty: number, s: number) => {
    c.fillStyle = dusk ? '#29221B' : '#5E5242'; c.fillRect(tx - s * 0.05, ty - s * 0.9, s * 0.1, s * 0.9)
    for (let i = 0; i < 26; i++) {
      const a = R() * Math.PI * 2, rr = R() * s * 0.55
      c.fillStyle = dusk ? `rgba(${(38 + R() * 20) | 0},${(34 + R() * 16) | 0},${(24 + R() * 10) | 0},.92)` : `rgba(${(78 + R() * 30) | 0},${(80 + R() * 24) | 0},${(56 + R() * 16) | 0},.9)`
      c.beginPath(); c.arc(tx + Math.cos(a) * rr * 1.1, ty - s * 1.15 + Math.sin(a) * rr * 0.75, s * (0.14 + R() * 0.14), 0, Math.PI * 2); c.fill()
    }
  }
  ;(o.trees || [[0.06, 1, 0.28], [0.42, 1.02, 0.2], [0.98, 1.01, 0.3]]).forEach(([x, y, s]: number[]) => tree(W * x, ground * y, Math.min(W, H) * s))

  const id = c.getImageData(0, 0, canvas.width, canvas.height), d = id.data
  for (let i = 0; i < d.length; i += 4) { const n = (R() - 0.5) * 14; d[i] += n; d[i + 1] += n; d[i + 2] += n }
  c.putImageData(id, 0, 0)
}

const isDark = () => document.documentElement.dataset.theme === 'dark'

function draw() {
  if (!cv.value) return
  const m = window.innerWidth < 768
  const dk = isDark()
  if (props.variant === 'hero') {
    scene(cv.value, m
      ? { seed: 11, dusk: dk, bx: 0.36, bw: 0.62, by: 0.3, lx: -0.05, lw: 0.38, ly: 0.62, sunX: 0.7, sunY: 0.25, ground: 0.93, trees: [[0.1, 1, 0.22], [0.95, 1.01, 0.24]] }
      : { seed: 11, dusk: dk })
  } else if (props.variant === 'stats') {
    scene(cv.value, { seed: 5, dusk: dk, bx: 0.08, bw: 0.5, by: -0.05, lx: 0.62, lw: 0.3, ly: 0.4, sunX: 0.85, sunY: 0.15, ground: 1.05, trees: [[0.7, 1, 0.35]] })
  } else {
    scene(cv.value, { seed: 3, dusk: true, bx: 0.45, bw: 0.5, by: 0.06, lx: 0.02, lw: 0.36, ly: 0.5, sunX: 0.2, sunY: 0.5, trees: [[0.03, 1, 0.3], [0.46, 1.02, 0.22], [0.97, 1, 0.3]] })
  }
}

let ro: ResizeObserver | null = null
let mo: MutationObserver | null = null
let t: any = null
onMounted(() => {
  draw()
  ro = new ResizeObserver(() => { clearTimeout(t); t = setTimeout(draw, 120) })
  if (cv.value) ro.observe(cv.value)
  mo = new MutationObserver(draw)
  mo.observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] })
})
onBeforeUnmount(() => { ro?.disconnect(); mo?.disconnect(); clearTimeout(t) })
</script>

<template>
  <canvas ref="cv" class="hero-scene" aria-hidden="true" />
</template>

<style scoped>
.hero-scene { position: absolute; inset: 0; width: 100%; height: 100%; display: block; }
</style>
