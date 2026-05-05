const VIDEO_EXTS = ['.mp4', '.mov', '.webm', '.avi', '.mkv', '.m4v']

export function isVideoFile(file) {
  return file && VIDEO_EXTS.some(ext => file.name?.toLowerCase().endsWith(ext))
}

export function isVideoUrl(url) {
  if (!url) return false
  const lower = url.toLowerCase().split('?')[0]
  return VIDEO_EXTS.some(ext => lower.endsWith(ext))
}
