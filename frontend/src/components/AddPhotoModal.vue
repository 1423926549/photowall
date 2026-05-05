<script setup>
import { ref } from 'vue'
import { uploadPhoto } from '../api'

const emit = defineEmits(['close', 'added'])

const files = ref([])           // [{ file, preview }]
const dateVal = ref(new Date().toISOString().slice(0, 10))
const note = ref('')
const uploading = ref(false)
const progress = ref({ done: 0, total: 0 })

function onFileChange(e) {
  const selected = Array.from(e.target.files)
  files.value = selected.map(f => ({
    file: f,
    name: f.name,
    preview: URL.createObjectURL(f),
  }))
}

function removeFile(idx) {
  URL.revokeObjectURL(files.value[idx].preview)
  files.value.splice(idx, 1)
}

async function submit() {
  if (!files.value.length) return alert('请选择照片')
  uploading.value = true
  progress.value = { done: 0, total: files.value.length }
  const dateStr = dateVal.value.replace(/-/g, '.')

  const added = []
  for (const item of files.value) {
    try {
      const photo = await uploadPhoto(item.file, dateStr, note.value || '美好的回忆')
      added.push(photo)
    } catch (e) {
      console.error('Upload failed:', item.name, e)
    }
    progress.value.done++
  }

  uploading.value = false
  if (added.length) emit('added', added)
}
</script>

<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal">
      <h3>添加照片</h3>

      <label>选择照片（可多选）</label>
      <label class="file-picker" :class="{ 'has-files': files.length }">
        <template v-if="files.length">
          <div class="preview-grid">
            <div v-for="(item, i) in files" :key="i" class="preview-item">
              <img :src="item.preview" />
              <button class="remove-btn" @click.prevent.stop="removeFile(i)">&times;</button>
              <span class="file-name">{{ item.name }}</span>
            </div>
          </div>
          <div class="add-more">+ 添加更多</div>
        </template>
        <template v-else>
          <div class="picker-placeholder">
            <span class="picker-icon">+</span>
            <span class="picker-text">点击选择照片</span>
          </div>
        </template>
        <input type="file" accept="image/*" multiple @change="onFileChange" hidden />
      </label>
      <div v-if="files.length" class="file-count">已选择 {{ files.length }} 张照片</div>

      <label>日期</label>
      <div class="date-input-wrap">
        <input type="date" v-model="dateVal" />
      </div>

      <label>备注</label>
      <textarea v-model="note" placeholder="一句话备注..." />

      <div v-if="uploading" class="upload-progress">
        上传中 {{ progress.done }}/{{ progress.total }}
      </div>

      <div class="modal-actions">
        <button class="btn-cancel" @click="$emit('close')">取消</button>
        <button class="btn-submit" :disabled="uploading || !files.length" @click="submit">
          {{ uploading ? '上传中...' : `上传 (${files.length})` }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 3500; display: flex; align-items: center; justify-content: center;
  background: rgba(10,22,42,0.75); backdrop-filter: blur(8px);
}
.modal {
  background: var(--card-bg); border-radius: 12px; padding: 28px 24px 22px;
  width: min(92vw, 480px); max-height: 90vh; overflow-y: auto;
  box-shadow: 0 12px 48px rgba(0,0,0,0.25);
}
.modal h3 {
  font-family: 'Noto Serif SC', serif; font-size: 20px; color: var(--text);
  text-align: center; letter-spacing: 3px; margin-bottom: 18px;
}
.modal label {
  display: block; font-size: 13px; color: var(--text-light);
  margin-bottom: 4px; margin-top: 12px;
}

/* File picker */
.file-picker {
  display: block; width: 100%; min-height: 160px;
  border: 2px dashed rgba(126,156,181,0.4);
  border-radius: 10px; cursor: pointer; position: relative;
  transition: border-color 0.25s, background 0.25s;
  background: #f8fafd;
}
.file-picker:hover { border-color: var(--accent); background: #f0f4ff; }
.file-picker.has-files { border-style: solid; border-color: rgba(126,156,181,0.15); }

.picker-placeholder {
  position: absolute; top: 50%; left: 50%;
  transform: translate(-50%, -50%);
  display: flex; flex-direction: column; align-items: center;
}
.picker-icon {
  font-size: 36px; color: var(--accent); opacity: 0.5; line-height: 1;
}
.picker-text {
  font-size: 13px; color: var(--text-light); margin-top: 6px;
}

/* Preview grid */
.preview-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 8px; padding: 10px;
}
.preview-item {
  position: relative; aspect-ratio: 1;
  border-radius: 6px; overflow: hidden; background: #e8ecf0;
}
.preview-item img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}
.remove-btn {
  position: absolute; top: 2px; right: 2px;
  width: 20px; height: 20px; border-radius: 50%;
  border: none; background: rgba(0,0,0,0.5); color: #fff;
  font-size: 12px; cursor: pointer; display: flex;
  align-items: center; justify-content: center;
  line-height: 1;
}
.file-name {
  position: absolute; bottom: 0; left: 0; right: 0;
  padding: 3px 4px; font-size: 10px; color: #fff;
  background: rgba(0,0,0,0.45);
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.add-more {
  text-align: center; padding: 8px; font-size: 13px;
  color: var(--accent); border-top: 1px solid rgba(126,156,181,0.1);
}
.file-count { font-size: 12px; color: var(--text-light); margin-top: 4px; }

/* Date */
.date-input-wrap input[type="date"] {
  width: 100%; padding: 10px 12px;
  border: 1px solid rgba(126,156,181,0.35);
  border-radius: 8px; font-size: 14px;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--text); background: #fff; outline: none;
}
.date-input-wrap input[type="date"]:focus { border-color: var(--accent); }

/* Textarea */
.modal textarea {
  width: 100%; padding: 10px 12px; resize: vertical; min-height: 60px;
  border: 1px solid rgba(126,156,181,0.35);
  border-radius: 8px; font-size: 14px;
  font-family: 'Noto Sans SC', sans-serif;
  color: var(--text); background: #fff; outline: none;
}
.modal textarea:focus { border-color: var(--accent); }

.upload-progress {
  text-align: center; margin-top: 8px;
  font-size: 13px; color: var(--accent);
}

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
