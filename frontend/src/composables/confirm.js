import { ref } from 'vue'

const state = ref({
  show: false,
  title: '',
  message: '',
  resolve: null,
})

export function useConfirm() {
  function open(title, message) {
    return new Promise((resolve) => {
      state.value = { show: true, title, message, resolve }
    })
  }

  function confirm() {
    state.value.resolve?.(true)
    state.value = { show: false, title: '', message: '', resolve: null }
  }

  function cancel() {
    state.value.resolve?.(false)
    state.value = { show: false, title: '', message: '', resolve: null }
  }

  return { state, open, confirm, cancel }
}
