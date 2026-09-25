import { useEffect, useMemo, useRef, useState } from 'react'
import Avatar from '@mui/material/Avatar'
import Box from '@mui/material/Box'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import IconButton from '@mui/material/IconButton'
import Table from '@mui/material/Table'
import TableBody from '@mui/material/TableBody'
import TableCell from '@mui/material/TableCell'
import TableContainer from '@mui/material/TableContainer'
import TableHead from '@mui/material/TableHead'
import TableRow from '@mui/material/TableRow'
import Typography from '@mui/material/Typography'
import DeleteOutlineRoundedIcon from '@mui/icons-material/DeleteOutlineRounded'
import ImageRoundedIcon from '@mui/icons-material/ImageRounded'
import { API_BASE_URL } from '../api/client'
import { useImages } from '../context/ImagesContext'
import { useScrollContainerRef } from '../context/ScrollContainerContext'
import { formatFileSize, getFileFormat } from '../utils/format'

const PAGE_SIZE = 30

function PhotosPage() {
  const { images, loading, error, searchQuery, remove, deletingId } = useImages()
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE)
  const [pendingDelete, setPendingDelete] = useState(null)
  const [deleteError, setDeleteError] = useState(null)
  const sentinelRef = useRef(null)
  const scrollContainerRef = useScrollContainerRef()

  useEffect(() => {
    setVisibleCount(PAGE_SIZE)
  }, [images])

  useEffect(() => {
    const node = sentinelRef.current
    if (!node) return undefined

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setVisibleCount((prev) => Math.min(prev + PAGE_SIZE, images.length))
        }
      },
      { root: scrollContainerRef.current, rootMargin: '400px' },
    )

    observer.observe(node)
    return () => observer.disconnect()
  }, [images.length, scrollContainerRef])

  const visibleImages = useMemo(() => images.slice(0, visibleCount), [images, visibleCount])

  const handleDeleteClick = (image) => {
    setDeleteError(null)
    setPendingDelete(image)
  }

  const handleCancelDelete = () => {
    if (deletingId) return
    setPendingDelete(null)
    setDeleteError(null)
  }

  const handleConfirmDelete = async () => {
    if (!pendingDelete) return
    try {
      await remove(pendingDelete.id)
      setPendingDelete(null)
    } catch (err) {
      setDeleteError(err.response?.data?.error || err.message || 'Failed to delete image')
    }
  }

  if (loading) return <Typography color="text.secondary">Loading photos…</Typography>
  if (error) return <Typography color="error">{error}</Typography>

  if (images.length === 0) {
    return (
      <Typography color="text.secondary">
        {searchQuery.trim() ? `No photos matching "${searchQuery.trim()}"` : 'No photos yet'}
      </Typography>
    )
  }

  return (
    <Box>
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        {images.length} photo{images.length === 1 ? '' : 's'}
        {searchQuery.trim() ? ` matching "${searchQuery.trim()}"` : ''}
      </Typography>

      <TableContainer>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Format</TableCell>
              <TableCell>Size</TableCell>
              <TableCell align="right" />
            </TableRow>
          </TableHead>
          <TableBody>
            {visibleImages.map((image) => (
              <TableRow key={image.id} hover>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                    <Avatar
                      variant="rounded"
                      src={`${API_BASE_URL}${image.url}`}
                      alt=""
                      sx={{ width: 36, height: 36, bgcolor: 'action.hover' }}
                    >
                      <ImageRoundedIcon fontSize="small" />
                    </Avatar>
                    <Typography noWrap sx={{ maxWidth: 420 }}>
                      {image.original_filename}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>{getFileFormat(image)}</TableCell>
                <TableCell>{formatFileSize(image.size)}</TableCell>
                <TableCell align="right">
                  <IconButton
                    aria-label={`Delete ${image.original_filename}`}
                    onClick={() => handleDeleteClick(image)}
                  >
                    <DeleteOutlineRoundedIcon fontSize="small" />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {visibleCount < images.length && (
        <Box
          ref={sentinelRef}
          sx={{ display: 'flex', justifyContent: 'center', py: 3 }}
        >
          <CircularProgress size={24} />
        </Box>
      )}

      <Dialog open={Boolean(pendingDelete)} onClose={handleCancelDelete}>
        <DialogTitle>Delete photo?</DialogTitle>
        <DialogContent>
          <DialogContentText>
            "{pendingDelete?.original_filename}" will be permanently
            deleted. This action cannot be undone.
          </DialogContentText>
          {deleteError && (
            <Typography color="error" sx={{ mt: 1.5 }}>
              {deleteError}
            </Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCancelDelete} disabled={Boolean(deletingId)}>
            Cancel
          </Button>
          <Button
            onClick={handleConfirmDelete}
            color="error"
            variant="contained"
            disabled={Boolean(deletingId)}
            startIcon={deletingId ? <CircularProgress size={16} color="inherit" /> : null}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}

export default PhotosPage
