import client from './client'

export const getImages = async () => {
  const { data } = await client.get('/images')
  return data
}

export const searchImages = async (query) => {
  const { data } = await client.get('/images/search', { params: { q: query } })
  return data
}

export const uploadImage = async (file) => {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export const deleteImage = async (id) => {
  const { data } = await client.delete(`/images/${id}`)
  return data
}
