<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as THREE from 'three'

const containerRef = ref<HTMLDivElement | null>(null)
let scene: THREE.Scene
let camera: THREE.PerspectiveCamera
let renderer: THREE.WebGLRenderer
let animFrameId: number
let cityGroup: THREE.Group
let floatingKeyGroup: THREE.Group
let particlesMesh: THREE.Points

// Mouse interaction states
let mouseX = 0
let mouseY = 0
let targetRotationX = 0.2
let targetRotationY = -0.5
let isDragging = false
let previousMouseX = 0
let previousMouseY = 0

const activeBadge = ref<number | null>(null)

onMounted(() => {
  if (!import.meta.client || !containerRef.value) return

  const container = containerRef.value
  const width = container.clientWidth || 400
  const height = container.clientHeight || 300

  // 1. Scene & Background
  scene = new THREE.Scene()
  const isDark = document.documentElement.dataset.theme === 'dark'
  scene.background = null // Transparent for seamless CSS backdrop

  // 2. Camera
  camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 1000)
  camera.position.set(16, 13, 17)
  camera.lookAt(0, 2.5, 0)

  // 3. Renderer with antialiasing
  renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: 'high-performance' })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  container.appendChild(renderer.domElement)

  // 4. Lights
  const ambientLight = new THREE.AmbientLight(isDark ? 0x1e293b : 0xe2e8f0, isDark ? 1.5 : 2.2)
  scene.add(ambientLight)

  const sunLight = new THREE.DirectionalLight(0xffffff, isDark ? 2.0 : 2.8)
  sunLight.position.set(15, 25, 12)
  sunLight.castShadow = true
  sunLight.shadow.mapSize.width = 1024
  sunLight.shadow.mapSize.height = 1024
  scene.add(sunLight)

  // Forest Green brand accent light
  const emeraldLight = new THREE.PointLight(0x174d3a, isDark ? 4.5 : 3.0, 30)
  emeraldLight.position.set(0, 8, 4)
  scene.add(emeraldLight)

  // Warm mint fill light
  const cyanLight = new THREE.PointLight(0xb9f2d0, isDark ? 3.0 : 1.8, 25)
  cyanLight.position.set(-6, 5, -5)
  scene.add(cyanLight)

  // 5. Construct 3D Tashkent City Model
  cityGroup = new THREE.Group()
  scene.add(cityGroup)

  // Materials
  const buildingMaterialLight = new THREE.MeshStandardMaterial({
    color: isDark ? 0x1e2b24 : 0xf4f6f2,
    roughness: 0.25,
    metalness: 0.15,
  })

  const glassMaterial = new THREE.MeshPhysicalMaterial({
    color: isDark ? 0x103b2e : 0x174d3a,
    roughness: 0.1,
    metalness: 0.8,
    transmission: 0.4,
    transparent: true,
    opacity: 0.9,
  })

  const windowMaterial = new THREE.MeshStandardMaterial({
    color: 0xfef08a,
    emissive: 0xfbbf24,
    emissiveIntensity: isDark ? 0.9 : 0.4,
    roughness: 0.1,
  })

  const accentMaterial = new THREE.MeshStandardMaterial({
    color: 0x174d3a,
    roughness: 0.2,
    metalness: 0.4,
  })

  // Frameless, transparent ground shadow receiver (buildings cast soft shadows directly onto the page)
  const shadowGeo = new THREE.PlaneGeometry(35, 35)
  const shadowMat = new THREE.ShadowMaterial({
    opacity: isDark ? 0.35 : 0.12,
  })
  const shadowMesh = new THREE.Mesh(shadowGeo, shadowMat)
  shadowMesh.rotation.x = -Math.PI / 2
  shadowMesh.position.y = 0
  shadowMesh.receiveShadow = true
  cityGroup.add(shadowMesh)

  // Helper to create a modern architectural building with windows
  const createBuilding = (
    w: number,
    h: number,
    d: number,
    x: number,
    z: number,
    mat: THREE.Material,
    roofMat?: THREE.Material
  ) => {
    const bGroup = new THREE.Group()
    bGroup.position.set(x, h / 2, z)

    const geo = new THREE.BoxGeometry(w, h, d)
    const mesh = new THREE.Mesh(geo, mat)
    mesh.castShadow = true
    mesh.receiveShadow = true
    bGroup.add(mesh)

    // Add glowing window bands
    const windowRows = Math.floor(h / 0.8)
    const windowCols = Math.max(1, Math.floor(w / 0.7))
    for (let r = 1; r < windowRows; r++) {
      for (let c = 0; c < windowCols; c++) {
        // Randomly skip some windows for natural look
        if ((r + c + Math.floor(x * 3)) % 3 === 0) continue

        const winGeo = new THREE.PlaneGeometry(0.35, 0.35)
        const winMesh = new THREE.Mesh(winGeo, windowMaterial)
        const winX = -w / 2 + (c + 0.5) * (w / windowCols)
        const winY = -h / 2 + r * 0.8
        winMesh.position.set(winX, winY, d / 2 + 0.02)
        bGroup.add(winMesh)

        // Opposite side
        const winMeshBack = winMesh.clone()
        winMeshBack.position.z = -d / 2 - 0.02
        winMeshBack.rotation.y = Math.PI
        bGroup.add(winMeshBack)
      }
    }

    // Roof details / helipad or terrace
    if (roofMat) {
      const roofGeo = new THREE.BoxGeometry(w * 0.8, 0.3, d * 0.8)
      const roofMesh = new THREE.Mesh(roofGeo, roofMat)
      roofMesh.position.y = h / 2 + 0.15
      bGroup.add(roofMesh)

      // Spire / Antenna on tallest buildings
      if (h > 6) {
        const spireGeo = new THREE.CylinderGeometry(0.04, 0.08, 1.8, 8)
        const spireMesh = new THREE.Mesh(spireGeo, accentMaterial)
        spireMesh.position.y = h / 2 + 1.0
        bGroup.add(spireMesh)

        // Glowing red beacon on antenna
        const beaconGeo = new THREE.SphereGeometry(0.12, 8, 8)
        const beaconMat = new THREE.MeshBasicMaterial({ color: 0xef4444 })
        const beaconMesh = new THREE.Mesh(beaconGeo, beaconMat)
        beaconMesh.position.y = h / 2 + 1.9
        bGroup.add(beaconMesh)
      }
    }

    cityGroup.add(bGroup)
    return bGroup
  }

  // 1. Central Tashkent City Landmark Skyscraper (Nest One style)
  createBuilding(2.4, 7.5, 2.4, 0, 0, glassMaterial, accentMaterial)

  // 2. High-rise residential tower A (East)
  createBuilding(2.0, 5.8, 1.8, 3.2, -0.8, buildingMaterialLight, accentMaterial)

  // 3. High-rise residential tower B (West)
  createBuilding(1.8, 5.2, 2.2, -3.2, 0.6, buildingMaterialLight, glassMaterial)

  // 4. North modern office block
  createBuilding(2.2, 4.0, 1.6, 0.4, -3.4, buildingMaterialLight, accentMaterial)

  // 5. South residential terraces
  createBuilding(2.6, 3.2, 1.8, -0.6, 3.2, buildingMaterialLight)

  // 6. Corner complexes
  createBuilding(1.5, 2.6, 1.5, 2.8, 2.8, glassMaterial)
  createBuilding(1.6, 2.4, 1.4, -2.6, -2.8, buildingMaterialLight)
  createBuilding(1.4, 2.0, 1.4, 3.8, -3.2, buildingMaterialLight)

  // 6. Floating 3D Golden/Emerald House Key hovering over center
  floatingKeyGroup = new THREE.Group()
  floatingKeyGroup.position.set(0, 9.8, 0)

  // Key head (Ring)
  const ringGeo = new THREE.TorusGeometry(0.65, 0.14, 16, 32)
  const keyMat = new THREE.MeshStandardMaterial({
    color: 0x10b981,
    metalness: 0.8,
    roughness: 0.15,
    emissive: 0x059669,
    emissiveIntensity: 0.3,
  })
  const keyHead = new THREE.Mesh(ringGeo, keyMat)
  keyHead.rotation.x = Math.PI / 2
  floatingKeyGroup.add(keyHead)

  // Key shaft
  const shaftGeo = new THREE.CylinderGeometry(0.12, 0.12, 1.4, 16)
  const keyShaft = new THREE.Mesh(shaftGeo, keyMat)
  keyShaft.position.z = 1.1
  keyShaft.rotation.x = Math.PI / 2
  floatingKeyGroup.add(keyShaft)

  // Key teeth
  const tooth1 = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.35, 0.2), keyMat)
  tooth1.position.set(0, -0.22, 1.6)
  floatingKeyGroup.add(tooth1)

  const tooth2 = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.25, 0.15), keyMat)
  tooth2.position.set(0, -0.18, 1.3)
  floatingKeyGroup.add(tooth2)

  // Glowing beacon ring below key
  const pulseRingGeo = new THREE.RingGeometry(0.8, 1.05, 32)
  const pulseRingMat = new THREE.MeshBasicMaterial({
    color: 0x10b981,
    side: THREE.DoubleSide,
    transparent: true,
    opacity: 0.6,
  })
  const pulseRing = new THREE.Mesh(pulseRingGeo, pulseRingMat)
  pulseRing.rotation.x = -Math.PI / 2
  pulseRing.position.y = -0.5
  floatingKeyGroup.add(pulseRing)

  cityGroup.add(floatingKeyGroup)

  // 7. Ambient Particle Motes (Floating light dust)
  const particlesCount = 75
  const posArray = new Float32Array(particlesCount * 3)
  for (let i = 0; i < particlesCount * 3; i += 3) {
    posArray[i] = (Math.random() - 0.5) * 16
    posArray[i + 1] = Math.random() * 12
    posArray[i + 2] = (Math.random() - 0.5) * 16
  }

  const particlesGeo = new THREE.BufferGeometry()
  particlesGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3))

  const particlesMat = new THREE.PointsMaterial({
    size: 0.18,
    color: 0x10b981,
    transparent: true,
    opacity: 0.7,
  })
  particlesMesh = new THREE.Points(particlesGeo, particlesMat)
  cityGroup.add(particlesMesh)

  // 8. Event listeners for mouse interaction & drag
  const onMouseMove = (e: MouseEvent) => {
    const rect = container.getBoundingClientRect()
    mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1
    mouseY = -(((e.clientY - rect.top) / rect.height) * 2 - 1)

    if (isDragging) {
      const deltaX = e.clientX - previousMouseX
      const deltaY = e.clientY - previousMouseY
      targetRotationY += deltaX * 0.012
      targetRotationX += deltaY * 0.008
      targetRotationX = Math.max(0.05, Math.min(0.55, targetRotationX))
      previousMouseX = e.clientX
      previousMouseY = e.clientY
    } else {
      targetRotationY = -0.5 + mouseX * 0.35
      targetRotationX = 0.25 - mouseY * 0.2
    }
  }

  const onMouseDown = (e: MouseEvent) => {
    isDragging = true
    previousMouseX = e.clientX
    previousMouseY = e.clientY
  }

  const onMouseUp = () => {
    isDragging = false
  }

  // Touch controls for mobile
  const onTouchMove = (e: TouchEvent) => {
    if (e.touches.length === 1) {
      const touch = e.touches[0]
      const deltaX = touch.clientX - previousMouseX
      targetRotationY += deltaX * 0.015
      previousMouseX = touch.clientX
    }
  }

  const onTouchStart = (e: TouchEvent) => {
    if (e.touches.length === 1) {
      previousMouseX = e.touches[0].clientX
    }
  }

  container.addEventListener('mousemove', onMouseMove)
  container.addEventListener('mousedown', onMouseDown)
  window.addEventListener('mouseup', onMouseUp)
  container.addEventListener('touchmove', onTouchMove, { passive: true })
  container.addEventListener('touchstart', onTouchStart, { passive: true })

  // 9. Resize Observer
  const resizeObserver = new ResizeObserver(() => {
    if (!container) return
    const w = container.clientWidth || 400
    const h = container.clientHeight || 300
    camera.aspect = w / h
    camera.updateProjectionMatrix()
    renderer.setSize(w, h)
  })
  resizeObserver.observe(container)

  // 10. Animation Loop
  let clock = new THREE.Clock()
  const animate = () => {
    animFrameId = requestAnimationFrame(animate)
    const elapsed = clock.getElapsedTime()

    // Smooth rotational lerp and organic floating levitation of the 3D city
    cityGroup.rotation.y += (targetRotationY - cityGroup.rotation.y) * 0.06
    cityGroup.rotation.x += (targetRotationX - cityGroup.rotation.x) * 0.06
    cityGroup.position.y = Math.sin(elapsed * 1.5) * 0.22

    // Floating key animation (hover bobbing & rotation)
    floatingKeyGroup.position.y = 9.8 + Math.sin(elapsed * 2.2) * 0.35
    floatingKeyGroup.rotation.y += 0.02
    pulseRing.scale.setScalar(1 + Math.sin(elapsed * 3.5) * 0.15)

    // Drift particles
    const positions = particlesMesh.geometry.attributes.position.array as Float32Array
    for (let i = 1; i < positions.length; i += 3) {
      positions[i] += 0.015
      if (positions[i] > 12) {
        positions[i] = 0
      }
    }
    particlesMesh.geometry.attributes.position.needsUpdate = true

    renderer.render(scene, camera)
  }

  animate()

  onBeforeUnmount(() => {
    cancelAnimationFrame(animFrameId)
    resizeObserver.disconnect()
    container.removeEventListener('mousemove', onMouseMove)
    container.removeEventListener('mousedown', onMouseDown)
    window.removeEventListener('mouseup', onMouseUp)
    renderer.dispose()
  })
})
</script>

<template>
  <div class="hero-3d-wrapper" ref="containerRef">
    <!-- 3D Canvas dynamically mounted here -->

    <!-- Floating 3D Interactive HUD Badges -->
    <div
      class="float-badge badge-top-left"
      :class="{ hover: activeBadge === 1 }"
      @mouseenter="activeBadge = 1"
      @mouseleave="activeBadge = null"
    >
      <div class="badge-icon">
        <svg viewBox="0 0 24 24">
          <path d="M12 3 4 6v6c0 5 3.5 8 8 9 4.5-1 8-4 8-9V6z" fill="#10b981" />
          <path d="m9 12 2 2 4-4" stroke="#fff" stroke-width="2" fill="none" />
        </svg>
      </div>
      <div>
        <div class="badge-title">Maklersiz 0%</div>
        <div class="badge-sub">Egasidan to‘g‘ridan-to‘g‘ri</div>
      </div>
    </div>

    <div
      class="float-badge badge-top-right"
      :class="{ hover: activeBadge === 2 }"
      @mouseenter="activeBadge = 2"
      @mouseleave="activeBadge = null"
    >
      <div class="badge-icon city">
        <svg viewBox="0 0 24 24">
          <path d="M3 21h18M6 21V7l8-4v18M14 11h4v10" stroke="#0284c7" stroke-width="2" fill="none" />
        </svg>
      </div>
      <div>
        <div class="badge-title">Tashkent City</div>
        <div class="badge-sub">3 xona · 110 m² · 14.4M</div>
      </div>
    </div>

    <div
      class="float-badge badge-bottom-center"
      :class="{ hover: activeBadge === 3 }"
      @mouseenter="activeBadge = 3"
      @mouseleave="activeBadge = null"
    >
      <div class="badge-pulse"></div>
      <span class="badge-text">
        ⚡ <b>82 ta</b> faol e’lon xaritada
      </span>
      <span class="badge-hint">Sichqoncha bilan 3D xaritani aylantiring</span>
    </div>
  </div>
</template>

<style scoped>
.hero-3d-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: 440px;
  background: transparent;
  border: none;
  border-radius: 0;
  box-shadow: none;
  overflow: visible;
  cursor: grab;
  user-select: none;
}

.hero-3d-wrapper:active {
  cursor: grabbing;
}

[data-theme='dark'] .hero-3d-wrapper {
  background: transparent;
  border: none;
  box-shadow: none;
}

.hero-3d-wrapper :deep(canvas) {
  display: block;
  outline: none;
  background: transparent;
}

/* Floating 3D HUD Badges */
.float-badge {
  position: absolute;
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border: 1px solid rgba(255, 255, 255, 0.95);
  padding: 8px 14px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  box-shadow: 0 10px 25px -4px rgba(0, 0, 0, 0.1), 0 4px 8px rgba(0, 0, 0, 0.04);
  z-index: 5;
  pointer-events: auto;
  transition: all 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  animation: floatSlow 4s ease-in-out infinite;
}

[data-theme='dark'] .float-badge {
  background: rgba(30, 41, 59, 0.88);
  border-color: rgba(255, 255, 255, 0.12);
  box-shadow: 0 12px 30px -4px rgba(0, 0, 0, 0.4);
}

.float-badge.hover,
.float-badge:hover {
  transform: translateY(-4px) scale(1.04);
  box-shadow: 0 16px 32px -4px rgba(23, 77, 58, 0.2);
  border-color: var(--ac, #174D3A);
}

.badge-top-left {
  top: 10px;
  left: 0;
  animation-delay: 0s;
}

.badge-top-right {
  top: 24px;
  right: 0;
  animation-delay: 1.5s;
}

.badge-bottom-center {
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  animation: floatSlow 4s ease-in-out 0.8s infinite;
  padding: 8px 18px;
  border-radius: 24px;
  flex-direction: column;
  gap: 2px;
  text-align: center;
}

.badge-bottom-center:hover {
  transform: translateX(-50%) translateY(-3px) scale(1.03);
}

.badge-pulse {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--ac, #174D3A);
  box-shadow: 0 0 0 0 rgba(23, 77, 58, 0.7);
  animation: pulse-ring 1.8s infinite;
}

@keyframes pulse-ring {
  0% {
    box-shadow: 0 0 0 0 rgba(23, 77, 58, 0.7);
  }
  70% {
    box-shadow: 0 0 0 8px rgba(23, 77, 58, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(23, 77, 58, 0);
  }
}

.badge-text {
  font-size: 13px;
  font-weight: 500;
  padding-left: 12px;
}

.badge-hint {
  font-size: 10px;
  color: var(--mu, #64748b);
  padding-left: 12px;
}

.badge-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: rgba(16, 185, 129, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
}

.badge-icon svg {
  width: 18px;
  height: 18px;
}

.badge-icon.city {
  background: rgba(2, 132, 199, 0.15);
}

.badge-title {
  font-size: 13px;
  font-weight: 700;
  line-height: 1.2;
}

.badge-sub {
  font-size: 11px;
  color: var(--mu, #64748b);
  line-height: 1.2;
}

@keyframes floatSlow {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}
</style>

