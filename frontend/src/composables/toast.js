import { ref } from 'vue'

const toasts = ref([])
let _id = 0

export function useToast() {
  function show(message, type = 'info', duration = 3000) {
    const id = ++_id
    toasts.value.push({ id, message, type })
    if (duration > 0) {
      setTimeout(() => dismiss(id), duration)
    }
  }

  function dismiss(id) {
    const idx = toasts.value.findIndex(t => t.id === id)
    if (idx >= 0) {
      toasts.value[idx].leaving = true
      setTimeout(() => {
        toasts.value = toasts.value.filter(t => t.id !== id)
      }, 300)
    }
  }

  return { toasts, show, dismiss }
}
