<script setup>
import { useToast } from '../composables/toast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <Teleport to="body">
    <div class="toast-container">
      <div
        v-for="t in toasts"
        :key="t.id"
        class="toast"
        :class="[`toast-${t.type}`, { 'toast-leave': t.leaving }]"
        @click="dismiss(t.id)"
      >
        <span class="toast-icon">
          <template v-if="t.type === 'success'">&#10003;</template>
          <template v-else-if="t.type === 'error'">&#10007;</template>
          <template v-else>&#8505;</template>
        </span>
        <span class="toast-msg">{{ t.message }}</span>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 8px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 20px;
  border-radius: 10px;
  font-size: 14px;
  font-family: 'Noto Sans SC', sans-serif;
  color: #fff;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: auto;
  animation: toastIn 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  backdrop-filter: blur(10px);
  white-space: nowrap;
  max-width: 90vw;
  overflow: hidden;
  text-overflow: ellipsis;
}

.toast-leave {
  animation: toastOut 0.3s ease forwards;
}

.toast-success { background: rgba(76, 175, 80, 0.92); }
.toast-error   { background: rgba(229, 57, 53, 0.92); }
.toast-info    { background: rgba(92, 107, 192, 0.92); }

.toast-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.toast-msg {
  overflow: hidden;
  text-overflow: ellipsis;
}

@keyframes toastIn {
  from {
    opacity: 0;
    transform: translateY(-12px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes toastOut {
  from {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  to {
    opacity: 0;
    transform: translateY(-12px) scale(0.95);
  }
}
</style>
