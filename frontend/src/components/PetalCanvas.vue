<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref(null)
let animId = 0
const petals = []
const baseCount = 8
const maxExtra = 40
let targetIntensity = 0.35
let intensity = 0

const COLORS = ['#BBDEFB', '#E3F2FD', '#B3E5FC', '#E1F5FE', '#90CAF9']

function spawn(w, h) {
  return {
    x: Math.random() * (w + 80) - 40,
    y: Math.random() * -h - 20,
    size: 6 + Math.random() * 12,
    rot: Math.random() * Math.PI * 2,
    rotSpeed: (Math.random() - 0.5) * 0.03,
    speed: 0.5 + Math.random() * 1.8,
    wobbleFreq: 0.005 + Math.random() * 0.015,
    wobbleAmp: 0.3 + Math.random() * 0.8,
    color: COLORS[Math.floor(Math.random() * COLORS.length)],
    alpha: 0.35 + Math.random() * 0.45,
  }
}

function draw(ctx, w, h) {
  intensity += (targetIntensity - intensity) * 0.03
  const desired = Math.floor(baseCount + intensity * maxExtra)
  while (petals.length < desired) petals.push(spawn(w, h))
  while (petals.length > desired) petals.pop()

  ctx.clearRect(0, 0, w, h)

  for (const p of petals) {
    p.y += p.speed
    p.x += Math.sin(p.y * p.wobbleFreq) * p.wobbleAmp
    p.rot += p.rotSpeed
    if (p.y > h + 40) {
      p.y = -40
      p.x = Math.random() * (w + 80) - 40
    }

    ctx.save()
    ctx.translate(p.x, p.y)
    ctx.rotate(p.rot)
    ctx.globalAlpha = p.alpha
    ctx.fillStyle = p.color
    ctx.beginPath()
    const s = p.size
    ctx.moveTo(0, -s)
    ctx.bezierCurveTo(-s * 0.6, -s * 0.5, -s * 0.55, s * 0.2, 0, s * 0.4)
    ctx.bezierCurveTo(s * 0.55, s * 0.2, s * 0.6, -s * 0.5, 0, -s)
    ctx.fill()
    ctx.restore()
  }
}

onMounted(() => {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  const resize = () => {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }
  resize()
  window.addEventListener('resize', resize)

  function animate() {
    draw(ctx, canvas.width, canvas.height)
    animId = requestAnimationFrame(animate)
  }
  animate()
})

onUnmounted(() => cancelAnimationFrame(animId))
</script>

<template>
  <canvas ref="canvasRef" class="petal-canvas" />
</template>

<style scoped>
.petal-canvas {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; z-index: 1000;
}
</style>
