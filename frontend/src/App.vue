<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue'
import PetalCanvas from './components/PetalCanvas.vue'
import PhotoWall from './components/PhotoWall.vue'
import Lightbox from './components/Lightbox.vue'
import AddPhotoModal from './components/AddPhotoModal.vue'
import EditPhotoModal from './components/EditPhotoModal.vue'
import ToastContainer from './components/ToastContainer.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import { fetchPhotos } from './api'

const photos = ref([])
const lightboxIndex = ref(-1)
const showAddModal = ref(false)
const editingPhoto = ref(null)
const loveDays = ref(0)

const glowRef = ref(null)
const LOVE_START = '2025-10-01'

function onMouseMove(e) {
  if (glowRef.value) {
    glowRef.value.style.left = e.clientX + 'px'
    glowRef.value.style.top = e.clientY + 'px'
  }
}

function updateLoveDays() {
  const start = new Date(LOVE_START)
  const now = new Date()
  loveDays.value = Math.floor((now - start) / (1000 * 60 * 60 * 24)) + 1
}

function openLightbox(index) {
  lightboxIndex.value = index
}

function closeLightbox() {
  lightboxIndex.value = -1
}

function prevPhoto() {
  if (lightboxIndex.value > 0) lightboxIndex.value--
}

function nextPhoto() {
  if (lightboxIndex.value < photos.value.length - 1) lightboxIndex.value++
}

async function loadPhotos() {
  try {
    photos.value = await fetchPhotos()
  } catch (e) {
    console.error('Failed to load photos:', e)
  }
}

function onPhotoAdded(result) {
  const added = Array.isArray(result) ? result : [result]
  photos.value = [...photos.value, ...added]
  showAddModal.value = false
}

function onPhotoDeleted(id) {
  photos.value = photos.value.filter(p => p.id !== id)
  if (lightboxIndex.value >= photos.value.length) {
    lightboxIndex.value = -1
  }
}

function onPhotoEdited({ id, date, note }) {
  const idx = photos.value.findIndex(p => p.id === id)
  if (idx >= 0) {
    photos.value[idx] = { ...photos.value[idx], date, note }
    photos.value = [...photos.value] // trigger reactivity
  }
  editingPhoto.value = null
}

provide('photos', photos)

onMounted(() => {
  loadPhotos()
  updateLoveDays()
  setInterval(updateLoveDays, 60000)
  document.addEventListener('mousemove', onMouseMove)
})
onUnmounted(() => {
  document.removeEventListener('mousemove', onMouseMove)
})
</script>

<template>
  <PetalCanvas />
  <div class="cursor-glow" ref="glowRef"></div>

  <header class="main-header">
    <h1>我们的故事</h1>
    <div class="subtitle">Our Story</div>
  </header>

  <PhotoWall
    :photos="photos"
    @open-lightbox="openLightbox"
    @delete-photo="onPhotoDeleted"
    @edit-photo="photo => editingPhoto = photo"
  />

  <footer class="main-footer">
    <div class="love-counter">
      我们已经一起走过了 <span>{{ loveDays }}</span> 天 ❤️
    </div>
  </footer>

  <button class="add-fab" @click="showAddModal = true" title="添加照片">+</button>

  <Lightbox
    v-if="lightboxIndex >= 0 && photos[lightboxIndex]"
    :photo="photos[lightboxIndex]"
    @close="closeLightbox"
    @prev="prevPhoto"
    @next="nextPhoto"
  />

  <AddPhotoModal
    v-if="showAddModal"
    @close="showAddModal = false"
    @added="onPhotoAdded"
  />

  <EditPhotoModal
    v-if="editingPhoto"
    :photo="editingPhoto"
    @close="editingPhoto = null"
    @updated="onPhotoEdited"
  />

  <ToastContainer />
  <ConfirmDialog />

</template>

<style>
/* ── Variables ── */
:root {
  --bg-end: #E3F2FD;
  --bg-mid: #90CAF9;
  --card-bg: #FAFCFF;
  --accent: #5C6BC0;
  --gold: #7E9CB5;
  --gold-light: #90AFC5;
  --text: #37474F;
  --text-light: #78909C;
  --shadow: rgba(10,22,42,0.10);
  --shadow-strong: rgba(10,22,42,0.18);
  --card-width: 260px;
  --card-gap: 24px;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { scroll-behavior: smooth; }
body {
  font-family: 'Noto Sans SC', sans-serif;
  background: linear-gradient(170deg, var(--bg-end), var(--bg-mid), #E8F0F8, var(--bg-end));
  background-size: 400% 400%;
  animation: bgBreathe 30s ease-in-out infinite;
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}
@keyframes bgBreathe {
  0%, 100% { background-position: 0% 50%; }
  25% { background-position: 100% 0%; }
  50% { background-position: 100% 100%; }
  75% { background-position: 0% 100%; }
}

/* ── Header ── */
.main-header {
  position: sticky; top: 0; z-index: 500;
  padding: 18px 28px 14px; text-align: center;
  background: linear-gradient(180deg, rgba(227,242,253,0.95) 0%, rgba(227,242,253,0.6) 100%);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(126,156,181,0.2);
}
.main-header h1 {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(22px, 3.5vw, 32px);
  font-weight: 600; color: var(--text);
  letter-spacing: 4px; margin-bottom: 4px;
}
.subtitle {
  font-family: 'Dancing Script', cursive;
  font-size: 16px; color: var(--text-light);
}

/* ── Footer ── */
.main-footer {
  text-align: center; padding: 30px 20px 40px;
}
.love-counter {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(16px, 2.5vw, 20px);
  color: var(--accent); letter-spacing: 3px;
}
.love-counter span {
  font-family: 'Dancing Script', cursive; font-size: 1.3em;
}

/* ── FAB ── */
.add-fab {
  position: fixed; bottom: 28px; right: 28px; z-index: 900;
  width: 52px; height: 52px; border-radius: 50%;
  border: none; background: var(--accent);
  color: #fff; font-size: 28px; line-height: 1; cursor: pointer;
  box-shadow: 0 4px 16px rgba(92,107,192,0.35);
  display: flex; align-items: center; justify-content: center;
  transition: transform 0.25s cubic-bezier(0.34,1.56,0.64,1), box-shadow 0.25s ease;
}
.add-fab:hover {
  transform: scale(1.12);
  box-shadow: 0 6px 24px rgba(92,107,192,0.5);
}

/* ── Cursor Glow ── */
.cursor-glow {
  position: fixed; pointer-events: none; z-index: 999;
  width: 300px; height: 300px; border-radius: 50%;
  background: radial-gradient(circle, rgba(144,175,197,0.10) 0%, transparent 70%);
  transform: translate(-50%, -50%);
}
</style>
