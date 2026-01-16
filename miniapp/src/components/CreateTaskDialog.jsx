import { useState } from 'react'
import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    Button,
    TextField,
    Box,
    Chip,
    ToggleButton,
    ToggleButtonGroup,
    Typography,
    Slide,
    IconButton
} from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import CloseIcon from '@mui/icons-material/Close'
import AddTaskIcon from '@mui/icons-material/AddTask'
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment'
import BoltIcon from '@mui/icons-material/Bolt'
import RemoveCircleOutlineIcon from '@mui/icons-material/RemoveCircleOutline'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import CircularProgress from '@mui/material/CircularProgress'

const Transition = (props) => <Slide direction="up" {...props} />

const CreateTaskDialog = ({ open, onClose, onCreate }) => {
    const [text, setText] = useState('')
    const [priority, setPriority] = useState('medium')
    const [tags, setTags] = useState([])
    const [tagInput, setTagInput] = useState('')
    const [dateTime, setDateTime] = useState('')
    const [loading, setLoading] = useState(false)

    const handleCreate = async () => {
        if (!text.trim() || !dateTime) return

        setLoading(true)

        const task = {
            text: text.trim(),
            priority,
            tags,
            remindAt: Math.floor(new Date(dateTime).getTime() / 1000)
        }

        try {
            await onCreate(task)
            // Reset form
            setText('')
            setPriority('medium')
            setTags([])
            setDateTime('')
        } finally {
            setLoading(false)
        }
    }

    const handleAddTag = (e) => {
        if (e.key === 'Enter' && tagInput.trim()) {
            e.preventDefault()
            const tag = tagInput.trim().replace('#', '')
            if (!tags.includes(tag)) {
                setTags([...tags, tag])
            }
            setTagInput('')
        }
    }

    const handleDeleteTag = (tagToDelete) => {
        setTags(tags.filter(tag => tag !== tagToDelete))
    }

    const getDefaultDateTime = () => {
        const date = new Date(Date.now() + 3600000)
        return date.toISOString().slice(0, 16)
    }

    const priorityConfig = {
        low: {
            color: '#2AABEE',
            label: 'Low',
            icon: <RemoveCircleOutlineIcon sx={{ fontSize: 18 }} />,
            xp: '+10 XP'
        },
        medium: {
            color: '#FFA500',
            label: 'Medium',
            icon: <BoltIcon sx={{ fontSize: 18 }} />,
            xp: '+20 XP'
        },
        high: {
            color: '#FF6B35',
            label: 'High',
            icon: <LocalFireDepartmentIcon sx={{ fontSize: 18 }} />,
            xp: '+30 XP'
        }
    }

    // AI Parsing Logic
    const handleSmartParse = async () => {
        if (!text.trim() || text.length < 5) return

        setLoading(true)
        try {
            // Using direct fetch for now, assuming relative path proxy in vite or direct URL
            const response = await fetch('https://hh2myi12y8.execute-api.us-east-1.amazonaws.com/prod/ai/parse-task', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    action: 'parse_task',
                    data: { text }
                })
            })

            const data = await response.json()

            if (data.text) setText(data.text)
            if (data.priority) setPriority(data.priority.toLowerCase())
            if (data.due_date) setDateTime(data.due_date.slice(0, 16))

            // Visual feedback
            const tg = window.Telegram?.WebApp
            tg?.HapticFeedback?.notificationOccurred('success')

        } catch (e) {
            console.error('AI Parse failed', e)
        } finally {
            setLoading(false)
        }
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            maxWidth="sm"
            fullWidth
            TransitionComponent={Transition}
            PaperProps={{
                sx: {
                    borderRadius: 4,
                    background: 'linear-gradient(135deg, #0A2E4D 0%, #1A4A6F 100%)',
                    border: '1px solid rgba(255,255,255,0.1)',
                    overflow: 'hidden'
                }
            }}
        >
            <DialogTitle sx={{
                background: 'linear-gradient(135deg, rgba(255, 107, 53, 0.2) 0%, transparent 100%)',
                color: 'white',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                fontFamily: '"Inter", sans-serif',
                fontWeight: 700
            }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <AddTaskIcon sx={{ color: '#FF6B35' }} />
                    New Task
                </Box>
                <IconButton onClick={onClose} sx={{ color: 'rgba(255,255,255,0.6)' }}>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>

            <DialogContent sx={{ pt: 3 }}>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
                    {/* Task text with Auto-Magic button */}
                    <Box sx={{ position: 'relative' }}>
                        <TextField
                            autoFocus
                            label="What needs to be done?"
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            fullWidth
                            multiline
                            rows={3}
                            placeholder="e.g. Buy milk tomorrow at 10am (AI will auto-detect!)"
                            sx={{
                                '& .MuiOutlinedInput-root': {
                                    color: 'white',
                                    fontFamily: '"Inter", sans-serif',
                                    '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                                    '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' },
                                    '&.Mui-focused fieldset': { borderColor: '#FF6B35' }
                                },
                                '& .MuiInputLabel-root': {
                                    color: 'rgba(255,255,255,0.6)',
                                    fontFamily: '"Inter", sans-serif'
                                }
                            }}
                        />
                        {text.length > 5 && (
                            <motion.div
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                style={{ position: 'absolute', right: 10, bottom: 10, zIndex: 10 }}
                            >
                                <Button
                                    size="small"
                                    onClick={handleSmartParse}
                                    disabled={loading}
                                    sx={{
                                        color: '#E91E63',
                                        background: 'rgba(233, 30, 99, 0.1)',
                                        borderRadius: 2,
                                        textTransform: 'none',
                                        '&:hover': { background: 'rgba(233, 30, 99, 0.2)' }
                                    }}
                                    startIcon={loading ? <CircularProgress size={12} color="inherit" /> : <AutoAwesomeIcon />}
                                >
                                    AI Magic
                                </Button>
                            </motion.div>
                        )}
                    </Box>

                    {/* Priority selector */}
                    <Box>
                        <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)', mb: 1, display: 'block', fontFamily: '"Inter", sans-serif' }}>
                            Priority Level
                        </Typography>
                        <ToggleButtonGroup
                            value={priority}
                            exclusive
                            onChange={(e, val) => val && setPriority(val)}
                            fullWidth
                            sx={{ gap: 1 }}
                        >
                            {Object.entries(priorityConfig).map(([key, config]) => (
                                <ToggleButton
                                    key={key}
                                    value={key}
                                    sx={{
                                        flex: 1,
                                        border: `1px solid ${priority === key ? config.color : 'rgba(255,255,255,0.1)'}`,
                                        borderRadius: '12px !important',
                                        color: priority === key ? 'white' : 'rgba(255,255,255,0.6)',
                                        background: priority === key ? `${config.color}22` : 'transparent',
                                        fontFamily: '"Inter", sans-serif',
                                        textTransform: 'none',
                                        py: 1.5,
                                        '&.Mui-selected': {
                                            background: `${config.color}33`,
                                            color: 'white',
                                            '&:hover': { background: `${config.color}44` }
                                        },
                                        '&:hover': { background: 'rgba(255,255,255,0.05)' }
                                    }}
                                >
                                    <Box sx={{ textAlign: 'center' }}>
                                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5, color: config.color }}>
                                            {config.icon}
                                            <span>{config.label}</span>
                                        </Box>
                                        <Typography variant="caption" sx={{ color: config.color, display: 'block', mt: 0.5 }}>
                                            {config.xp}
                                        </Typography>
                                    </Box>
                                </ToggleButton>
                            ))}
                        </ToggleButtonGroup>
                    </Box>

                    {/* Due date/time */}
                    <TextField
                        label="Due Date & Time"
                        type="datetime-local"
                        value={dateTime || getDefaultDateTime()}
                        onChange={(e) => setDateTime(e.target.value)}
                        fullWidth
                        InputLabelProps={{ shrink: true }}
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                color: 'white',
                                fontFamily: '"Inter", sans-serif',
                                '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' },
                                '&.Mui-focused fieldset': { borderColor: '#FF6B35' }
                            },
                            '& .MuiInputLabel-root': {
                                color: 'rgba(255,255,255,0.6)',
                                fontFamily: '"Inter", sans-serif'
                            },
                            '& input::-webkit-calendar-picker-indicator': {
                                filter: 'invert(1)'
                            }
                        }}
                    />

                    {/* Tags */}
                    <TextField
                        label="Tags (press Enter)"
                        value={tagInput}
                        onChange={(e) => setTagInput(e.target.value)}
                        onKeyDown={handleAddTag}
                        placeholder="work, personal, urgent..."
                        fullWidth
                        sx={{
                            '& .MuiOutlinedInput-root': {
                                color: 'white',
                                fontFamily: '"Inter", sans-serif',
                                '& fieldset': { borderColor: 'rgba(255,255,255,0.2)' },
                                '&:hover fieldset': { borderColor: 'rgba(255,255,255,0.4)' },
                                '&.Mui-focused fieldset': { borderColor: '#FF6B35' }
                            },
                            '& .MuiInputLabel-root': {
                                color: 'rgba(255,255,255,0.6)',
                                fontFamily: '"Inter", sans-serif'
                            }
                        }}
                    />

                    <AnimatePresence>
                        {tags.length > 0 && (
                            <motion.div
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: 'auto' }}
                                exit={{ opacity: 0, height: 0 }}
                            >
                                <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                                    {tags.map(tag => (
                                        <motion.div
                                            key={tag}
                                            initial={{ scale: 0 }}
                                            animate={{ scale: 1 }}
                                            exit={{ scale: 0 }}
                                        >
                                            <Chip
                                                label={`#${tag}`}
                                                onDelete={() => handleDeleteTag(tag)}
                                                sx={{
                                                    background: 'rgba(255, 107, 53, 0.2)',
                                                    color: '#FF6B35',
                                                    fontFamily: '"Inter", sans-serif',
                                                    '& .MuiChip-deleteIcon': { color: '#FF6B35' }
                                                }}
                                                size="small"
                                            />
                                        </motion.div>
                                    ))}
                                </Box>
                            </motion.div>
                        )}
                    </AnimatePresence>
                </Box>
            </DialogContent>

            <DialogActions sx={{ p: 2.5, gap: 1 }}>
                <Button
                    onClick={onClose}
                    sx={{
                        color: 'rgba(255,255,255,0.6)',
                        fontFamily: '"Inter", sans-serif',
                        textTransform: 'none'
                    }}
                >
                    Cancel
                </Button>
                <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Button
                        onClick={handleCreate}
                        variant="contained"
                        disabled={!text.trim() || !dateTime || loading}
                        sx={{
                            background: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)',
                            color: 'white',
                            fontFamily: '"Inter", sans-serif',
                            fontWeight: 600,
                            textTransform: 'none',
                            px: 4,
                            py: 1,
                            borderRadius: 2,
                            boxShadow: '0 4px 15px rgba(255, 107, 53, 0.3)',
                            '&:hover': {
                                background: 'linear-gradient(135deg, #E55A2B 0%, #D44920 100%)'
                            },
                            '&:disabled': {
                                background: 'rgba(255,255,255,0.1)',
                                color: 'rgba(255,255,255,0.3)'
                            }
                        }}
                    >
                        {loading ? 'Thinking...' : 'Create Task ✨'}
                    </Button>
                </motion.div>
            </DialogActions>
        </Dialog>
    )
}

export default CreateTaskDialog
