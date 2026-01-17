import { useState, useEffect } from 'react'
import { Box, Typography, Modal, Button, Fade, IconButton } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import FormatQuoteIcon from '@mui/icons-material/FormatQuote'
import CloseIcon from '@mui/icons-material/Close'
import { getRandomQuote } from '../data/quotes'

const DailyInspiration = ({ open, onClose }) => {
    const [quote, setQuote] = useState({ text: '', author: '' })

    useEffect(() => {
        if (open) {
            setQuote(getRandomQuote())
        }
    }, [open])

    return (
        <Modal
            open={open}
            onClose={onClose}
            closeAfterTransition
            sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                p: 2,
                backdropFilter: 'blur(5px)'
            }}
        >
            <Fade in={open}>
                <Box sx={{
                    outline: 'none',
                    width: '100%',
                    maxWidth: 400
                }}>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.8, y: 50 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.8, y: 50 }}
                        transition={{ type: "spring", duration: 0.6 }}
                    >
                        <Box sx={{
                            position: 'relative',
                            background: 'linear-gradient(135deg, #1A4A6F 0%, #0A2E4D 100%)',
                            borderRadius: 4,
                            p: 4,
                            pt: 6,
                            textAlign: 'center',
                            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
                            border: '1px solid rgba(255, 255, 255, 0.1)',
                            overflow: 'hidden'
                        }}>
                            {/* Decorative Background Elements */}
                            <FormatQuoteIcon sx={{
                                position: 'absolute',
                                top: -20,
                                left: -20,
                                fontSize: 120,
                                color: 'rgba(255, 255, 255, 0.05)',
                                transform: 'rotate(180deg)'
                            }} />

                            <IconButton
                                onClick={onClose}
                                sx={{
                                    position: 'absolute',
                                    top: 16,
                                    right: 16,
                                    color: 'rgba(255, 255, 255, 0.5)',
                                    '&:hover': { color: 'white' }
                                }}
                            >
                                <CloseIcon />
                            </IconButton>

                            <Typography variant="overline" sx={{ color: '#FF6B35', fontWeight: 700, letterSpacing: 2 }}>
                                Daily Inspiration
                            </Typography>

                            <Box sx={{ mt: 3, mb: 4, position: 'relative' }}>
                                <Typography variant="h5" sx={{
                                    fontFamily: '"Inter", sans-serif',
                                    fontWeight: 600,
                                    color: 'white',
                                    lineHeight: 1.4,
                                    fontStyle: 'italic'
                                }}>
                                    "{quote.text}"
                                </Typography>
                                <Typography variant="body2" sx={{
                                    mt: 2,
                                    color: '#B8CBD9',
                                    fontWeight: 500
                                }}>
                                    — {quote.author}
                                </Typography>
                            </Box>

                            <Button
                                fullWidth
                                variant="contained"
                                onClick={() => {
                                    // Trigger haptic if available (via parent or context, but here just onClick)
                                    onClose()
                                }}
                                sx={{
                                    py: 1.5,
                                    borderRadius: 3,
                                    background: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)',
                                    boxShadow: '0 4px 12px rgba(255, 107, 53, 0.4)',
                                    fontWeight: 700,
                                    fontSize: '1rem',
                                    textTransform: 'none'
                                }}
                            >
                                Let's crush it! 🚀
                            </Button>

                        </Box>
                    </motion.div>
                </Box>
            </Fade>
        </Modal>
    )
}

export default DailyInspiration
