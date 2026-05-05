<script setup>
import { ref, computed } from 'vue'
import { deletePhoto } from '../api'
import { useToast } from '../composables/toast'
import { useConfirm } from '../composables/confirm'
import { isVideoUrl } from '../composables/media'

const { show: toast } = useToast()
const { open: confirmOpen } = useConfirm()

const props = defineProps({
  photo: { type: Object, required: true },
  index: { type: Number, required: true },
})
const emit = defineEmits(['deleted', 'edit', 'preview'])

const imgLoaded = ref(false)
const contextMenu = ref({ show: false, x: 0, y: 0 })

const isVideo = computed(() => isVideoUrl(props.photo.url))

const rotate = computed(() => {
  const n = (props.photo.id * 7 + 3) % 11
  return (n - 5) * 0.8
})

function onClick() {
  emit('preview')
}

function onContextMenu(e) {
  e.preventDefault()
  contextMenu.value = { show: true, x: e.clientX, y: e.clientY }
}

function closeMenu() {
  contextMenu.value.show = false
}

function onDownload() {
  closeMenu()
  const url = props.photo.url
  const ext = url.split('?')[0].split('.').pop() || 'jpg'
  const a = document.createElement('a')
  a.href = url
  a.download = props.photo.date + '_' + (props.photo.note || 'photo') + '.' + ext
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}

function onEdit() {
  closeMenu()
  emit('edit', props.photo)
}

async function onDelete() {
  closeMenu()
  const ok = await confirmOpen('确认删除', '确定要删除这张照片吗？')
  if (!ok) return
  try {
    await deletePhoto(props.photo.id)
    emit('deleted', props.photo.id)
    toast('删除成功', 'success')
  } catch (e) {
    toast('删除失败: ' + e.message, 'error')
  }
}
</script>

<template>
  <div
    class="photo-card"
    :style="{ '--rotate': `rotate(${rotate}deg)` }"
    @click="onClick"
    @contextmenu="onContextMenu"
  >
    <div v-if="!imgLoaded" class="skeleton" />
    <template v-if="isVideo">
      <video :src="photo.url" muted preload="metadata" @loadeddata="imgLoaded = true" @error="imgLoaded = true" />
      <div class="video-play-overlay">▶</div>
    </template>
    <img
      v-else
      :src="photo.url"
      :alt="photo.note"
      :class="{ loading: !imgLoaded }"
      @load="imgLoaded = true"
      @error="imgLoaded = true"
    />
    <span class="card-date">{{ photo.date }}</span>
    <span class="card-note">{{ photo.note }}</span>
  </div>

  <Teleport to="body">
    <div
      v-if="contextMenu.show"
      class="context-menu"
      :style="{ left: contextMenu.x + 'px', top: contextMenu.y + 'px' }"
      @click.stop
      @mouseleave="closeMenu"
    >
      <button class="context-item" @click="onDownload">下载</button>
      <button class="context-item" @click="onEdit">编辑</button>
      <button class="context-item danger" @click="onDelete">删除照片</button>
    </div>
    <div v-if="contextMenu.show" class="context-backdrop" @click="closeMenu" />
  </Teleport>
</template>

<style scoped>
.photo-card {
  background: var(--card-bg);
  padding: 12px 12px 42px 12px;
  border-radius: 4px;
  box-shadow: 2px 3px 12px var(--shadow), 0 1px 3px rgba(0,0,0,0.06);
  transition: transform 0.35s cubic-bezier(0.34,1.56,0.64,1),
              box-shadow 0.35s ease, opacity 0.5s ease;
  cursor: pointer; position: relative;
  break-inside: avoid;
  margin-bottom: var(--card-gap);
  user-select: none;
  opacity: 0;
  transform: translateY(30px) scale(0.9);
}
.photo-card.mounted {
  opacity: 1;
  transform: translateY(0) scale(1) var(--rotate);
}
.photo-card:hover {
  transform: scale(1.06) rotate(0deg) !important;
  box-shadow: 4px 8px 28px var(--shadow-strong), 0 2px 8px rgba(0,0,0,0.08);
  z-index: 10;
}
.photo-card img,
.photo-card video {
  width: 100%; height: auto; display: block; border-radius: 2px;
  background: #F0F4F8;
  transition: opacity 0.4s ease;
  user-select: none; pointer-events: none;
}
.photo-card img.loading { opacity: 0.4; }
.video-play-overlay {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(0,0,0,0.55);
  color: #fff; font-size: 20px;
  display: flex; align-items: center; justify-content: center;
  pointer-events: none;
  transition: transform 0.25s ease, background 0.25s ease;
}
.photo-card:hover .video-play-overlay {
  transform: translate(-50%, -50%) scale(1.15);
  background: rgba(0,0,0,0.7);
}
.card-date {
  position: absolute; bottom: 10px; left: 16px;
  font-family: 'Long Cang', cursive; font-size: 17px;
  color: var(--text-light); line-height: 1;
}
.card-note {
  position: absolute; bottom: 10px; right: 16px;
  font-family: 'Long Cang', cursive; font-size: 15px;
  color: var(--accent); opacity: 0.8; line-height: 1;
}
.skeleton {
  width: 100%; aspect-ratio: 3/4;
  background: linear-gradient(90deg, #F0F4F8 25%, #E3F2FD 50%, #F0F4F8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 2px;
}
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>

<style>
/* Context menu — unscoped so Teleport works */
.context-backdrop {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 4000;
}
.context-menu {
  position: fixed; z-index: 4001;
  background: #fff; border-radius: 8px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.18);
  min-width: 120px; overflow: hidden;
}
.context-item {
  display: block; width: 100%; padding: 10px 16px;
  border: none; background: transparent;
  font-size: 14px; font-family: 'Noto Sans SC', sans-serif;
  cursor: pointer; text-align: left;
  transition: background 0.15s;
}
.context-item:hover { background: #f5f5f5; }
.context-item.danger { color: #e53935; }
.context-item.danger:hover { background: #ffebee; }
</style>
