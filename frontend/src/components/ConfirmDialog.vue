<script setup>
import { useConfirm } from '../composables/confirm'

const { state, confirm, cancel } = useConfirm()
</script>

<template>
  <Teleport to="body">
    <div v-if="state.show" class="confirm-overlay" @click.self="cancel">
      <div class="confirm-box">
        <h3>{{ state.title }}</h3>
        <p>{{ state.message }}</p>
        <div class="confirm-actions">
          <button class="btn-cancel" @click="cancel">取消</button>
          <button class="btn-danger" @click="confirm">确认删除</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.confirm-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  z-index: 5000; display: flex; align-items: center; justify-content: center;
  background: rgba(10, 22, 42, 0.6); backdrop-filter: blur(6px);
}

.confirm-box {
  background: var(--card-bg); border-radius: 14px;
  padding: 28px 24px 20px; width: min(88vw, 340px);
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
  text-align: center;
  animation: confirmIn 0.25s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.confirm-box h3 {
  font-family: 'Noto Serif SC', serif; font-size: 18px;
  color: var(--text); margin-bottom: 8px; letter-spacing: 2px;
}

.confirm-box p {
  font-size: 14px; color: var(--text-light); margin-bottom: 20px;
}

.confirm-actions { display: flex; gap: 10px; justify-content: center; }
.confirm-actions button {
  padding: 8px 22px; border-radius: 20px; border: none; cursor: pointer;
  font-size: 14px; font-family: 'Noto Sans SC', sans-serif;
  transition: filter 0.2s;
}
.btn-cancel {
  background: transparent; color: var(--text-light);
  border: 1px solid rgba(126, 156, 181, 0.3) !important;
}
.btn-cancel:hover { border-color: var(--text-light) !important; }
.btn-danger { background: #e53935; color: #fff; }
.btn-danger:hover { filter: brightness(1.1); }

@keyframes confirmIn {
  from { opacity: 0; transform: scale(0.9); }
  to   { opacity: 1; transform: scale(1); }
}
</style>
