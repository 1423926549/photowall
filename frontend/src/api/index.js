const BASE = '/api'

export async function fetchPhotos() {
  const res = await fetch(`${BASE}/photos`)
  if (!res.ok) throw new Error('Failed to fetch photos')
  return res.json()
}

export async function uploadPhoto(file, date, note) {
  const form = new FormData()
  form.append('photo', file)
  form.append('date', date)
  form.append('note', note)

  const res = await fetch(`${BASE}/photos`, { method: 'POST', body: form })
  if (!res.ok) {
    const e = await res.json().catch(() => ({}))
    throw new Error(e.error || 'Upload failed')
  }
  return res.json()
}

export async function updatePhoto(id, date, note) {
  const res = await fetch(`${BASE}/photos/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ date, note }),
  })
  if (!res.ok) throw new Error('Update failed')
  return res.json()
}

export async function deletePhoto(id) {
  const res = await fetch(`${BASE}/photos/${id}`, { method: 'DELETE' })
  if (!res.ok) throw new Error('Delete failed')
  return res.json()
}
