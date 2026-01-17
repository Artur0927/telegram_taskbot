import { Box, Typography, IconButton } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import ErrorIcon from '@mui/icons-material/Error'
import InfoIcon from '@mui/icons-material/Info'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import CloseIcon from '@mui/icons-material/Close'
import { useEffect } from 'react'

const variants = {
    exp: {
        icon: <EmojiEventsIcon sx={{ color: '#FFD700', fontSize: 24 }} />,
        bg: 'linear-gradient(135deg, rgba(81, 45, 168, 0.95), rgba(49, 27, 146, 0.95))',
        border: '1px solid rgba(255, 215, 0, 0.5)',
        shadow: '0 8px 32px rgba(255, 215, 0, 0.2)'
    },
    success: {
        icon: <CheckCircleIcon sx={{ color: '#4CAF50', fontSize: 24 }} />,
        bg: 'rgba(10, 46, 77, 0.95)',
        border: '1px solid rgba(76, 175, 80, 0.3)',
        shadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
    },
    error: {
        icon: <ErrorIcon sx={{ color: '#F44336', fontSize: 24 }} />,
        bg: 'rgba(40, 10, 10, 0.95)',
        border: '1px solid rgba(244, 67, 54, 0.3)',
        shadow: '0 8px 32px rgba(244, 67, 54, 0.1)'
    },
    info: {
        icon: <InfoIcon sx={{ color: '#2AABEE', fontSize: 24 }} />,
        bg: 'rgba(10, 46, 77, 0.95)',
        border: '1px solid rgba(42, 171, 238, 0.3)',
        shadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
    }
}

const GameNotification = ({ open, message, type = 'success', onClose }) => {
    useEffect(() => {
        if (open) {
            const timer = setTimeout(onClose, 4000)
            return () => clearTimeout(timer)
        }
    }, [open, onClose])

    const style = variants[type] || variants.success

    return (
        <AnimatePresence>
            {open && (
                <motion.div
                    initial={{ opacity: 0, y: -50, scale: 0.9 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    exit={{ opacity: 0, y: -20, scale: 0.9 }}
                    transition={{ type: "spring", stiffness: 400, damping: 25 }}
                    style={{
                        position: 'fixed',
                        top: 16,
                        left: 16,
                        right: 16,
                        display: 'flex',
                        justifyContent: 'center',
                        zIndex: 2000,
                        pointerEvents: 'none' // Allow clicks to pass through around the toast
                    }}
                >
                    <Box sx={{
                        pointerEvents: 'auto',
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1.5,
                        background: style.bg,
                        border: style.border,
                        boxShadow: style.shadow,
                        backdropFilter: 'blur(10px)',
                        borderRadius: 3,
                        px: 2,
                        py: 1.5,
                        maxWidth: '90%',
                        minWidth: 300
                    }}>
                        {style.icon}

                        <Typography variant="body2" sx={{
                            color: 'white',
                            fontWeight: 600,
                            flex: 1
                        }}>
                            {message}
                        </Typography>

                        <IconButton size="small" onClick={onClose} sx={{ color: 'rgba(255,255,255,0.5)' }}>
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </Box>
                </motion.div>
            )}
        </AnimatePresence>
    )
}

export default GameNotification
