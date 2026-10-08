import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react'
import {
  deleteImage as deleteImageRequest,
  getImages,
  searchImages,
  uploadImage as uploadImageRequest,
} from '../api/images'

const SEARCH_DEBOUNCE_MS = 300

const ImagesContext = createContext(null)

export function ImagesProvider({ children }) {
  const [images, setImages] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [uploading, setUploading] = useState(false)
  const [deletingId, setDeletingId] = useState(null)

  const requestIdRef = useRef(0)
  const isFirstRun = useRef(true)

  const fetchImages = useCallback(async (query) => {
    const requestId = ++requestIdRef.current
    setLoading(true)
    setError(null)
    try {
      const data = query ? await searchImages(query) : await getImages()
      if (requestId === requestIdRef.current) setImages(data)
    } catch (err) {
      if (requestId === requestIdRef.current) {
        setError(err.response?.data?.error || err.message || 'Failed to load images')
      }
    } finally {
      if (requestId === requestIdRef.current) setLoading(false)
    }
  }, [])

  const refresh = useCallback(
    () => fetchImages(searchQuery.trim()),
    [fetchImages, searchQuery],
  )

  // Runs the search against the backend (debounced), and re-runs it whenever
  // the query changes so /images/search stays the single source of truth.
  useEffect(() => {
    const query = searchQuery.trim()

    if (isFirstRun.current) {
      isFirstRun.current = false
      fetchImages(query)
      return undefined
    }

    const handle = setTimeout(() => fetchImages(query), SEARCH_DEBOUNCE_MS)
    return () => clearTimeout(handle)
  }, [searchQuery, fetchImages])

  const upload = useCallback(
    async (file) => {
      setUploading(true)
      setError(null)
      try {
        const created = await uploadImageRequest(file)
        await fetchImages(searchQuery.trim())
        return created
      } catch (err) {
        setError(err.response?.data?.error || err.message || 'Failed to upload image')
        throw err
      } finally {
        setUploading(false)
      }
    },
    [fetchImages, searchQuery],
  )

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

  const value = useMemo(
    () => ({
      images,
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
    [images, loading, error, searchQuery, refresh, upload, uploading, remove, deletingId],
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
