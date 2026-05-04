<script setup>
import { ref } from 'vue'
import { updatePhoto } from '../api'

const props = defineProps({ photo: { type: Object, required: true } })
const emit = defineEmits(['close', 'updated'])

const dateVal = ref((props.photo.date || '').replace(/\./g, '-'))
const note = ref(props.photo.note || '')
const saving = ref(false)

async function submit() {
  saving.value = true
  const dateStr = dateVal.value.replace(/-/g, '.')
  try {
    await updatePhoto(props.photo.id, dateStr, note.value)
    emit('updated', { id: props.photo.id, date: dateStr, note: note.value })
  } catch (e) {
    alert('保存失败: ' + e.message)
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>编辑照片</h3>

      <label>日期</label>
      <div class="date-input-wrap">
        <input type="date" v-model="dateVal" />
      </div>

      <label>备注</label>
      <textarea v-model="note" placeholder="一句话备注..." />

      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn-submit" :disabled="saving" @click="submit">
          {{ saving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 3600; display: flex; align-items: center; justify-content: center;
  background: rgba(10,22,42,0.75); backdrop-filter: blur(8px);
}
.modal {
  background: var(--card-bg); border-radius: 12px; padding: 28px 24px 22px;
  width: min(88vw, 380px); box-shadow: 0 12px 48px rgba(0,0,0,0.25);
}
.modal h3 {
  font-family: 'Noto Serif SC', serif; font-size: 20px; color: var(--text);
  text-align: center; letter-spacing: 3px; margin-bottom: 18px;
}
.modal label {
  display: block; font-size: 13px; color: var(--text-light);
  margin-bottom: 4px; margin-top: 12px;
}
.date-input-wrap input[type="date"] {
  width: 100%; padding: 10px 12px;
  border: 1px solid rgba(126,156,181,0.35);
  border-radius: 8px; font-size: 14px;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--text); background: #fff; outline: none;
}
.date-input-wrap input[type="date"]:focus { border-color: var(--accent); }
.modal textarea {
  width: 100%; padding: 10px 12px; resize: vertical; min-height: 60px;
  border: 1px solid rgba(126,156,181,0.35);
  border-radius: 8px; font-size: 14px;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--text); background: #fff; outline: none;
}
.modal textarea:focus { border-color: var(--accent); }
.modal-actions { display: flex; gap: 10px; margin-top: 18px; justify-content: flex-end; }
.modal-actions button {
  padding: 8px 20px; border-radius: 18px; border: none; cursor: pointer;
  font-size: 14px; font-family: 'Noto Sans SC', sans-serif;
}
.btn-cancel {
  background: transparent; color: var(--text-light);
  border: 1px solid rgba(126,156,181,0.3) !important;
}
.btn-cancel:hover { border-color: var(--text-light) !important; }
.btn-submit { background: var(--accent); color: #fff; }
.btn-submit:hover { filter: brightness(1.1); }
.btn-submit:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
