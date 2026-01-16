import { useState } from 'react'
import { Box, Typography, Paper, Grid, Chip, IconButton, Tooltip, Skeleton } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import DeleteIcon from '@mui/icons-material/Delete'
import AccessTimeIcon from '@mui/icons-material/AccessTime'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'

// Motion wrapper for Paper
const MotionPaper = motion(Paper)

// Animation variants
const cardVariants = {
    hidden: {
        opacity: 0,
        y: 20,
        scale: 0.95
    },
    visible: {
        opacity: 1,
        y: 0,
        scale: 1,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    },
    exit: {
        opacity: 0,
        scale: 0.8,
        x: 100,
        transition: {
            duration: 0.3
        }
    },
    hover: {
        y: -4,
        boxShadow: "0 12px 24px rgba(0,0,0,0.4)",
        transition: {
            type: "spring",
            stiffness: 400
        }
    }
}

const TaskCard = ({ task, onComplete, onDelete, index }) => {
    const [deleting, setDeleting] = useState(false)
    const [completing, setCompleting] = useState(false)

    const timestamp = typeof task.remindAt === 'string' ? parseInt(task.remindAt) : task.remindAt
    const dueDate = new Date(timestamp * 1000)

    const priorityConfig = {
        high: { color: '#FF6B35', glow: 'rgba(255, 107, 53, 0.3)', label: '🔥 High' },
        medium: { color: '#FFA500', glow: 'rgba(255, 165, 0, 0.2)', label: '⚡ Medium' },
        low: { color: '#2AABEE', glow: 'rgba(42, 171, 238, 0.2)', label: '💤 Low' }
    }
    const priority = priorityConfig[task.priority] || priorityConfig.medium

    const handleComplete = async () => {
        setCompleting(true)
        try {
            await onComplete(task.id || task.taskId)
        } catch (err) {
            setCompleting(false)
        }
    }

    const handleDelete = async () => {
        if (window.confirm('Delete this task?')) {
            setDeleting(true)
            try {
                await onDelete(task.id || task.taskId)
            } catch (err) {
                setDeleting(false)
                alert('Failed to delete task')
            }
        }
    }

    return (
        <MotionPaper
            variants={cardVariants}
            initial="hidden"
            animate="visible"
            exit="exit"
            whileHover="hover"
            layout
            elevation={6}
            sx={{
                p: 2.5,
                mb: 2,
                borderRadius: 3,
                bgcolor: 'background.paper',
                backgroundImage: 'linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0) 100%)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.08)',
                borderLeft: 4,
                borderLeftColor: priority.color,
                boxShadow: `0 4px 20px ${priority.glow}`,
                opacity: (deleting || completing) ? 0.5 : 1,
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                    content: '""',
                    position: 'absolute',
                    top: 0,
                    left: 0,
                    right: 0,
                    height: 3,
                    background: `linear-gradient(90deg, ${priority.color}, transparent)`,
                    opacity: 0.5
                }
            }}
        >
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <Box sx={{ flex: 1, mr: 1 }}>
                    <Typography
                        variant="body1"
                        sx={{
                            mb: 1.5,
                            fontWeight: 600,
                            color: 'white',
                            lineHeight: 1.5,
                            fontSize: '1rem'
                        }}
                    >
                        {task.text}
                    </Typography>

                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexWrap: 'wrap' }}>
                        <Chip
                            label={priority.label}
                            size="small"
                            sx={{
                                background: `${priority.color}22`,
                                color: priority.color,
                                fontWeight: 600,
                                fontSize: '0.7rem',
                                height: 24
                            }}
                        />

                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                            <AccessTimeIcon sx={{ fontSize: 14, color: '#B8CBD9' }} />
                            <Typography variant="caption" sx={{ color: '#B8CBD9', fontSize: '0.75rem' }}>
                                {dueDate.toLocaleDateString()} {dueDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </Typography>
                        </Box>

                        {task.tags && task.tags.map((tag, idx) => (
                            <Chip
                                key={idx}
                                label={`#${tag}`}
                                size="small"
                                sx={{
                                    backgroundColor: 'rgba(255, 107, 53, 0.15)',
                                    color: '#FF6B35',
                                    fontSize: '0.65rem',
                                    height: 20,
                                    fontWeight: 600
                                }}
                            />
                        ))}
                    </Box>
                </Box>

                <Box sx={{ display: 'flex', gap: 0.5, flexDirection: 'column' }}>
                    <Tooltip title="Complete task (+XP)" placement="left">
                        <motion.div whileTap={{ scale: 0.9 }}>
                            <IconButton
                                onClick={handleComplete}
                                disabled={deleting || completing}
                                size="small"
                                sx={{
                                    background: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)',
                                    color: 'white',
                                    width: 36,
                                    height: 36,
                                    '&:hover': {
                                        background: 'linear-gradient(135deg, #45a049 0%, #3d8b40 100%)',
                                        transform: 'scale(1.1)'
                                    },
                                    '&:disabled': {
                                        background: 'rgba(76, 175, 80, 0.3)',
                                        color: 'rgba(255,255,255,0.5)'
                                    }
                                }}
                            >
                                {completing ? (
                                    <AutoAwesomeIcon fontSize="small" sx={{ animation: 'spin 1s linear infinite' }} />
                                ) : (
                                    <CheckCircleIcon fontSize="small" />
                                )}
                            </IconButton>
                        </motion.div>
                    </Tooltip>

                    <Tooltip title="Delete task (-XP)" placement="left">
                        <motion.div whileTap={{ scale: 0.9 }}>
                            <IconButton
                                onClick={handleDelete}
                                disabled={deleting || completing}
                                size="small"
                                sx={{
                                    background: 'rgba(244, 67, 54, 0.2)',
                                    color: '#F44336',
                                    width: 36,
                                    height: 36,
                                    '&:hover': {
                                        background: 'rgba(244, 67, 54, 0.3)',
                                        transform: 'scale(1.1)'
                                    }
                                }}
                            >
                                <DeleteIcon fontSize="small" />
                            </IconButton>
                        </motion.div>
                    </Tooltip>
                </Box>
            </Box>
        </MotionPaper>
    )
}

// Loading skeleton
const TaskSkeleton = () => (
    <Paper
        elevation={3}
        sx={{
            p: 2.5,
            mb: 2,
            borderRadius: 3,
            background: 'rgba(26, 74, 111, 0.5)',
            backdropFilter: 'blur(10px)'
        }}
    >
        <Skeleton variant="text" width="70%" height={24} sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
        <Box sx={{ display: 'flex', gap: 1, mt: 1.5 }}>
            <Skeleton variant="rounded" width={80} height={24} sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
            <Skeleton variant="rounded" width={120} height={24} sx={{ bgcolor: 'rgba(255,255,255,0.1)' }} />
        </Box>
    </Paper>
)

const TaskBoard = ({ tasks, onUpdate, onComplete, onDelete, loading }) => {
    const handleDelete = async (taskId) => {
        if (onDelete) {
            await onDelete(taskId)
        }
    }

    const categorizeTask = (task) => {
        const now = Date.now() / 1000
        const timestamp = typeof task.remindAt === 'string' ? parseInt(task.remindAt) : task.remindAt
        const diff = timestamp - now

        const oneDay = 86400
        const twoDay = 172800
        const oneWeek = 604800

        if (diff < 0) return 'today'
        if (diff < oneDay) return 'today'
        if (diff < twoDay) return 'tomorrow'
        if (diff < oneWeek) return 'week'
        return 'later'
    }

    const columns = [
        { id: 'today', title: 'Today', emoji: '🎯', gradient: 'linear-gradient(135deg, #FF6B35, #E55A2B)' },
        { id: 'tomorrow', title: 'Tomorrow', emoji: '📅', gradient: 'linear-gradient(135deg, #FFA500, #E59400)' },
        { id: 'week', title: 'This Week', emoji: '📆', gradient: 'linear-gradient(135deg, #2AABEE, #229ED9)' },
        { id: 'later', title: 'Later', emoji: '🔮', gradient: 'linear-gradient(135deg, #9C27B0, #7B1FA2)' }
    ]

    // Filter out completed tasks
    const pendingTasks = tasks.filter(task => task.status !== 'done')

    columns.forEach(col => col.tasks = [])
    pendingTasks.forEach(task => {
        const category = categorizeTask(task)
        const column = columns.find(c => c.id === category)
        if (column) column.tasks.push(task)
    })

    return (
        <Box>
            <Grid container spacing={2}>
                {columns.map((column, colIndex) => (
                    <Grid item xs={12} sm={6} md={3} key={column.id}>
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ delay: colIndex * 0.1 }}
                        >
                            <Box
                                sx={{
                                    mb: 2,
                                    p: 1.5,
                                    borderRadius: 2,
                                    bgcolor: 'rgba(21, 59, 93, 0.5)', // Theme glass
                                    backdropFilter: 'blur(10px)'
                                }}
                            >
                                <Box sx={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: 1,
                                    mb: 1.5
                                }}>
                                    <Typography sx={{ fontSize: '1.2rem' }}>{column.emoji}</Typography>
                                    <Typography variant="h6" sx={{ fontWeight: 700, color: '#FFFFFF', fontSize: '1rem' }}>
                                        {column.title}
                                    </Typography>
                                    <Chip
                                        label={column.tasks.length}
                                        size="small"
                                        sx={{
                                            background: column.gradient,
                                            color: 'white',
                                            fontWeight: 700,
                                            minWidth: 28,
                                            height: 24,
                                            ml: 'auto'
                                        }}
                                    />
                                </Box>

                                <AnimatePresence mode="popLayout">
                                    {loading ? (
                                        <>
                                            <TaskSkeleton />
                                            <TaskSkeleton />
                                        </>
                                    ) : column.tasks.length === 0 ? (
                                        <motion.div
                                            initial={{ opacity: 0 }}
                                            animate={{ opacity: 1 }}
                                            transition={{ delay: 0.3 }}
                                        >
                                            <Typography
                                                variant="caption"
                                                sx={{
                                                    color: 'rgba(184, 203, 217, 0.6)',
                                                    fontStyle: 'italic',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    gap: 1
                                                }}
                                            >
                                                ✨ All clear
                                            </Typography>
                                        </motion.div>
                                    ) : (
                                        column.tasks.map((task, index) => (
                                            <TaskCard
                                                key={task.id || task.taskId}
                                                task={task}
                                                index={index}
                                                onComplete={onComplete}
                                                onDelete={handleDelete}
                                            />
                                        ))
                                    )}
                                </AnimatePresence>
                            </Box>
                        </motion.div>
                    </Grid>
                ))}
            </Grid>
        </Box>
    )
}

export default TaskBoard
