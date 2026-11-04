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


/* ---- Variant: pishtaq (courtyard portal with tiled arch) — used by the stats band ---- */
function scenePortal(canvas: HTMLCanvasElement, dusk: boolean) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const W = canvas.clientWidth, H = canvas.clientHeight
  if (!W || !H) return
  canvas.width = W * dpr; canvas.height = H * dpr
  const c = canvas.getContext('2d')!
  c.scale(dpr, dpr)
  const R = rng(21)
  let g = c.createLinearGradient(0, 0, 0, H)
  if (dusk) { g.addColorStop(0, '#2B2620'); g.addColorStop(1, '#6E5742') } else { g.addColorStop(0, '#EADFCE'); g.addColorStop(1, '#E2CFB3') }
  c.fillStyle = g; c.fillRect(0, 0, W, H)
  const ground = H * 0.88
  const cx = W * 0.62, pw = Math.min(W * 0.46, 620), top = H * 0.04
  // wings with small arched windows
  const wing = (x: number, w: number) => {
    c.fillStyle = dusk ? '#4D4034' : '#D9C7AC'; c.fillRect(x, H * 0.34, w, ground - H * 0.34)
    c.fillStyle = dusk ? '#5C4C3D' : '#E7D8C0'; c.fillRect(x, H * 0.34, w, 7)
    const n = Math.max(2, Math.floor(w / 46))
    for (let i = 0; i < n; i++) {
      const wx = x + (i + 0.5) * (w / n) - 11, wy = H * 0.46
      c.fillStyle = dusk ? (R() < 0.5 ? '#E9B877' : '#2A231C') : '#8A765E'
      c.beginPath(); c.moveTo(wx, wy + 40); c.lineTo(wx, wy + 12); c.quadraticCurveTo(wx + 11, wy - 8, wx + 22, wy + 12); c.lineTo(wx + 22, wy + 40); c.fill()
    }
  }
  wing(cx - pw / 2 - Math.min(W * 0.36, 460), Math.min(W * 0.36, 460) - 8)
  wing(cx + pw / 2 + 8, Math.min(W * 0.36, 460))
  // portal block
  c.fillStyle = dusk ? '#614F3F' : '#E9DAC2'; c.fillRect(cx - pw / 2, top, pw, ground - top)
  c.fillStyle = dusk ? '#4A3C30' : '#CDB99C'; c.fillRect(cx - pw / 2, top, 10, ground - top); c.fillRect(cx + pw / 2 - 10, top, 10, ground - top)
  // tiled frame (diamond band)
  const ts = 16
  for (let y = top + 14; y < ground - 20; y += ts) for (const x of [cx - pw / 2 + 22, cx + pw / 2 - 22 - ts]) {
    c.save(); c.translate(x + ts / 2, y + ts / 2); c.rotate(Math.PI / 4)
    c.fillStyle = ((y / ts) | 0) % 2 ? (dusk ? '#D9A869' : '#9C7F5F') : (dusk ? '#3B3027' : '#C9B190'); c.fillRect(-ts * 0.32, -ts * 0.32, ts * 0.64, ts * 0.64); c.restore()
  }
  // pointed niche
  const nw = pw * 0.56, nb = ground, nh = (ground - top) * 0.82, nx = cx - nw / 2
  c.beginPath(); c.moveTo(nx, nb); c.lineTo(nx, nb - nh * 0.55); c.quadraticCurveTo(nx, nb - nh * 0.96, cx, nb - nh); c.quadraticCurveTo(nx + nw, nb - nh * 0.96, nx + nw, nb - nh * 0.55); c.lineTo(nx + nw, nb); c.closePath()
  g = c.createLinearGradient(0, nb - nh, 0, nb); if (dusk) { g.addColorStop(0, '#F3C985'); g.addColorStop(1, '#8B5E34') } else { g.addColorStop(0, '#F4DDB4'); g.addColorStop(1, '#B58D5F') }
  c.fillStyle = g; c.fill()
  c.lineWidth = 6; c.strokeStyle = dusk ? '#3B3027' : '#7B6650'; c.stroke()
  // muqarnas-like honeycomb inside the niche
  c.save(); c.clip()
  for (let r = 0; r < 9; r++) for (let k = 0; k < 7; k++) {
    const hx = nx + 14 + k * (nw / 6.5) + (r % 2) * 10, hy = nb - nh * 0.96 + r * 18
    c.fillStyle = `rgba(${dusk ? '40,28,18' : '90,66,40'},${0.10 + (r % 3) * 0.05})`; c.beginPath(); c.arc(hx, hy, 8, Math.PI, 0); c.fill()
  }
  c.restore()
  // pool + ground
  g = c.createLinearGradient(0, ground, 0, H); g.addColorStop(0, dusk ? '#52442F' : '#D7C6A9'); g.addColorStop(1, dusk ? '#2F271F' : '#BFAA8A'); c.fillStyle = g; c.fillRect(0, ground, W, H - ground)
  c.fillStyle = dusk ? 'rgba(243,201,133,.22)' : 'rgba(255,248,232,.6)'; c.fillRect(cx - pw * 0.34, ground + 10, pw * 0.68, H - ground - 18)
  // chinar trees
  const tree = (tx: number, s: number) => {
    c.fillStyle = dusk ? '#26201A' : '#5E5242'; c.fillRect(tx - s * 0.05, ground - s * 0.9, s * 0.1, s * 0.9)
    for (let i = 0; i < 24; i++) {
      const a = R() * Math.PI * 2, rr = R() * s * 0.5
      c.fillStyle = dusk ? `rgba(${36 + (R() * 18) | 0},${32 + (R() * 14) | 0},${22 + (R() * 8) | 0},.94)` : `rgba(${80 + (R() * 28) | 0},${82 + (R() * 22) | 0},${58 + (R() * 14) | 0},.92)`
      c.beginPath(); c.arc(tx + Math.cos(a) * rr * 1.1, ground - s * 1.1 + Math.sin(a) * rr * 0.75, s * (0.13 + R() * 0.12), 0, Math.PI * 2); c.fill()
    }
  }
  tree(W * 0.05, Math.min(W, H) * 0.3); tree(W * 0.97, Math.min(W, H) * 0.34)
  grain(c, canvas, R)
}

/* ---- Variant: Tashkent skyline at dusk (TV tower + towers) — used by the CTA ---- */
function sceneSkyline(canvas: HTMLCanvasElement) {
  const dpr = Math.min(window.devicePixelRatio || 1, 2)
  const W = canvas.clientWidth, H = canvas.clientHeight
  if (!W || !H) return
  canvas.width = W * dpr; canvas.height = H * dpr
  const c = canvas.getContext('2d')!
  c.scale(dpr, dpr)
  const R = rng(33)
  let g = c.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#231F1B'); g.addColorStop(0.5, '#6A5340'); g.addColorStop(0.85, '#D3A576'); g.addColorStop(1, '#E9C79B')
  c.fillStyle = g; c.fillRect(0, 0, W, H)
  g = c.createRadialGradient(W * 0.2, H * 0.8, 0, W * 0.2, H * 0.8, W * 0.6); g.addColorStop(0, 'rgba(255,214,150,.55)'); g.addColorStop(1, 'rgba(255,214,150,0)'); c.fillStyle = g; c.fillRect(0, 0, W, H)
  const ground = H * 0.9
  const layer = (n: number, hMin: number, hMax: number, col: string, lit: number) => {
    let x = -20
    while (x < W) {
      const w = 34 + R() * 70, h = H * (hMin + R() * (hMax - hMin))
      c.fillStyle = col; c.fillRect(x, ground - h, w, h)
      if (lit > 0) for (let yy = ground - h + 10; yy < ground - 12; yy += 14) for (let xx = x + 6; xx < x + w - 8; xx += 12) if (R() < lit) { c.fillStyle = R() < 0.5 ? '#F2C37F' : '#E9A862'; c.fillRect(xx, yy, 5, 7) }
      x += w + 2 + R() * 6
    }
  }
  layer(0, 0.18, 0.42, 'rgba(98,78,60,.75)', 0)
  layer(1, 0.22, 0.58, '#3C3128', 0.28)
  // TV tower
  const tx = W * 0.74
  c.fillStyle = '#2B231C'; c.beginPath(); c.moveTo(tx - 9, ground); c.lineTo(tx - 3, H * 0.18); c.lineTo(tx + 3, H * 0.18); c.lineTo(tx + 9, ground); c.fill()
  c.beginPath(); c.ellipse(tx, H * 0.4, 20, 11, 0, 0, Math.PI * 2); c.fill(); c.fillRect(tx - 1.2, H * 0.04, 2.4, H * 0.16)
  c.fillStyle = '#F2C37F'; for (let i = -2; i <= 2; i++) c.fillRect(tx + i * 6 - 1.5, H * 0.395, 3, 4)
  // glass tower with slanted top
  const gx = W * 0.5, gw = 70, gh = H * 0.66
  c.fillStyle = '#2F261F'; c.beginPath(); c.moveTo(gx, ground); c.lineTo(gx, ground - gh); c.lineTo(gx + gw, ground - gh - 26); c.lineTo(gx + gw, ground); c.fill()
  for (let yy = ground - gh + 6; yy < ground - 10; yy += 12) for (let xx = gx + 6; xx < gx + gw - 6; xx += 10) if (R() < 0.42) { c.fillStyle = '#F2C37F'; c.fillRect(xx, yy - ((xx - gx) / gw) * 26 * 0, 5, 7) }
  g = c.createLinearGradient(0, ground, 0, H); g.addColorStop(0, '#2C241D'); g.addColorStop(1, '#1D1814'); c.fillStyle = g; c.fillRect(0, ground, W, H - ground)
  // foreground chinars
  const tree = (tx2: number, s: number) => {
    c.fillStyle = '#1D1712'; c.fillRect(tx2 - s * 0.05, ground - s * 0.9, s * 0.1, s * 0.95)
    for (let i = 0; i < 26; i++) { const a = R() * Math.PI * 2, rr = R() * s * 0.55; c.fillStyle = `rgba(${28 + (R() * 12) | 0},${25 + (R() * 10) | 0},${18 + (R() * 8) | 0},.96)`; c.beginPath(); c.arc(tx2 + Math.cos(a) * rr * 1.1, ground - s * 1.1 + Math.sin(a) * rr * 0.75, s * (0.14 + R() * 0.13), 0, Math.PI * 2); c.fill() }
  }
  tree(W * 0.04, Math.min(W, H) * 0.32); tree(W * 0.34, Math.min(W, H) * 0.2); tree(W * 0.97, Math.min(W, H) * 0.36)
  grain(c, canvas, R)
}

function grain(c: CanvasRenderingContext2D, canvas: HTMLCanvasElement, R: () => number) {
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
    scenePortal(cv.value, dk)
  } else {
    sceneSkyline(cv.value)
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
