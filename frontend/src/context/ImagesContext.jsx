import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import {
  deleteImage as deleteImageRequest,
  getImages,
  uploadImage as uploadImageRequest,
} from '../api/images'

const ImagesContext = createContext(null)

export function ImagesProvider({ children }) {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  const refresh = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getImages()
      setImages(data)
    } catch (err) {
      setError(err.message || 'Failed to load images')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const upload = useCallback(async (file) => {
    setUploading(true)
    setError(null)
    try {
      const created = await uploadImageRequest(file)
      setImages((prev) => [created, ...prev])
      return created
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to upload image')
      throw err
    } finally {
      setUploading(false)
    }
  }, [])

  const remove = useCallback(async (id) => {
    setDeletingId(id)
    setError(null)
    try {
      await deleteImageRequest(id)
      setImages((prev) => prev.filter((image) => image.id !== id))
    } catch (err) {
      setError(err.response?.data?.error || err.message || 'Failed to delete image')
      throw err
    } finally {
      setDeletingId(null)
    }
  }, [])

  const visibleImages = useMemo(() => {
    const query = searchQuery.trim().toLowerCase()
    if (!query) return images
    return images.filter((image) =>
      (image.original_filename || '').toLowerCase().includes(query),
    )
  }, [images, searchQuery])

  const value = useMemo(
    () => ({
      images: visibleImages,
      allImagesCount: images.length,
      loading,
      error,
      searchQuery,
      setSearchQuery,
      refresh,
      upload,
      uploading,
      remove,
      deletingId,
    }),
    [
      visibleImages,
      images.length,
      loading,
      error,
      searchQuery,
      refresh,
      upload,
      uploading,
      remove,
      deletingId,
    ],
  )

  return <ImagesContext.Provider value={value}>{children}</ImagesContext.Provider>
}

export function useImages() {
  const context = useContext(ImagesContext)
  if (!context) {
    throw new Error('useImages must be used within an ImagesProvider')
  }
  return context
}
