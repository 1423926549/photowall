<script setup>
import { onMounted, onUnmounted } from 'vue'

const props = defineProps({ photo: { type: Object, required: true } })
const emit = defineEmits(['close', 'prev', 'next'])

function onKey(e) {
  if (e.key === 'Escape') emit('close')
  if (e.key === 'ArrowLeft') emit('prev')
  if (e.key === 'ArrowRight') emit('next')
}

onMounted(() => {
  document.addEventListener('keydown', onKey)
  document.body.style.overflow = 'hidden'
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKey)
  document.body.style.overflow = ''
})
</script>

<template>
  <div class="lightbox" @click.self="$emit('close')">
    <button class="lb-close" @click="$emit('close')">&times;</button>
    <button class="lb-nav lb-prev" @click="$emit('prev')">&lsaquo;</button>
    <button class="lb-nav lb-next" @click="$emit('next')">&rsaquo;</button>
    <div class="lb-content">
      <img :src="photo.url" :alt="photo.note" />
      <div class="lb-info">
        <div class="lb-date">{{ photo.date }}</div>
        <div class="lb-note">{{ photo.note }}</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.lightbox {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 3000; display: flex; align-items: center; justify-content: center;
  background: rgba(20,2,8,0.85); backdrop-filter: blur(14px);
}
.lb-close {
  position: fixed; top: 20px; right: 28px; z-index: 3001;
  width: 40px; height: 40px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.3);
  background: rgba(255,255,255,0.08);
  color: #fff; font-size: 20px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.3s;
}
.lb-close:hover { background: rgba(255,255,255,0.18); }
.lb-nav {
  position: fixed; top: 50%; transform: translateY(-50%); z-index: 3001;
  width: 48px; height: 48px; border-radius: 50%;
  border: 1px solid rgba(255,255,255,0.25);
  background: rgba(255,255,255,0.06);
  color: #fff; font-size: 22px; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: background 0.3s;
}
.lb-nav:hover { background: rgba(255,255,255,0.16); }
.lb-prev { left: 20px; }
.lb-next { right: 20px; }
.lb-content {
  max-width: 85vw; max-height: 80vh;
  display: flex; flex-direction: column; align-items: center;
}
.lb-content img {
  max-width: 85vw; max-height: 75vh; object-fit: contain;
  border-radius: 10px; box-shadow: 0 8px 40px rgba(0,0,0,0.5);
  border: 3px solid rgba(255,255,255,0.15);
}
.lb-info { margin-top: 14px; text-align: center; color: rgba(255,255,255,0.85); }
.lb-date { font-family: 'Noto Serif SC', serif; font-size: 14px; letter-spacing: 2px; }
.lb-note { font-family: 'Long Cang', cursive; font-size: 20px; color: #90AFC5; margin-top: 2px; }

@media (max-width: 640px) {
  .lb-nav { width: 36px; height: 36px; font-size: 16px; }
  .lb-prev { left: 8px; }
  .lb-next { right: 8px; }
}
</style>
