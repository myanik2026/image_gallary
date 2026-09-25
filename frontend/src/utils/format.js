const UNITS = ['B', 'KB', 'MB', 'GB']

export function formatFileSize(bytes) {
  if (bytes === null || bytes === undefined || Number.isNaN(bytes)) return '—'

  let value = Number(bytes)
  let unitIndex = 0
  while (value >= 1024 && unitIndex < UNITS.length - 1) {
    value /= 1024
    unitIndex += 1
  }
  return `${value.toFixed(unitIndex === 0 ? 0 : 1)} ${UNITS[unitIndex]}`
}

export function getFileFormat(image) {
  const name = image.original_filename || ''
  const extension = name.includes('.') ? name.split('.').pop() : ''
  if (extension) return extension.toUpperCase()

  const mime = image.file_type || ''
  return mime.includes('/') ? mime.split('/').pop().toUpperCase() : mime.toUpperCase() || '—'
}
