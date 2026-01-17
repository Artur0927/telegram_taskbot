import { useState, useEffect, useCallback } from 'react'
import logo from './assets/logo.png'
import { Box, Container, Tabs, Tab, AppBar, Typography, CircularProgress, Fab, Snackbar, Alert, Slide } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import confetti from 'canvas-confetti'
import ChecklistIcon from '@mui/icons-material/Checklist'
import CalendarMonthIcon from '@mui/icons-material/CalendarMonth'
import PersonIcon from '@mui/icons-material/Person'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import AddIcon from '@mui/icons-material/Add'
import TaskBoard from './components/TaskBoard'
import Calendar from './components/Calendar'
import Profile from './components/Profile'
import CreateTaskDialog from './components/CreateTaskDialog'
import Onboarding from './components/Onboarding'
import DailyInspiration from './components/DailyInspiration'
import GameNotification from './components/GameNotification'
import { useTelegram } from './hooks/useTelegram'
import { useTasks } from './hooks/useTasks'

// Page transition variants
const pageVariants = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0, transition: { duration: 0.3, ease: 'easeOut' } },
    exit: { opacity: 0, x: -20, transition: { duration: 0.2 } }
}

// Confetti celebration effect
const fireConfetti = (isLevelUp = false) => {
    const defaults = {
        spread: 360,
        ticks: 100,
        gravity: 0.8,
        decay: 0.94,
        startVelocity: 30,
        colors: ['#FF6B35', '#FFD700', '#2AABEE', '#4CAF50', '#E91E63']
    }

    if (isLevelUp) {
        // Big celebration for level up
        confetti({ ...defaults, particleCount: 100, origin: { x: 0.5, y: 0.6 } })
        setTimeout(() => confetti({ ...defaults, particleCount: 50, origin: { x: 0.3, y: 0.7 } }), 200)
        setTimeout(() => confetti({ ...defaults, particleCount: 50, origin: { x: 0.7, y: 0.7 } }), 400)
    } else {
        // Small celebration for XP
        confetti({ ...defaults, particleCount: 30, origin: { x: 0.5, y: 0.7 } })
    }
}

// Haptic feedback helper
const triggerHaptic = (type = 'medium') => {
    try {
        const tg = window.Telegram?.WebApp
        if (tg?.HapticFeedback) {
            if (type === 'success') {
                tg.HapticFeedback.notificationOccurred('success')
            } else if (type === 'error') {
                tg.HapticFeedback.notificationOccurred('error')
            } else if (type === 'light') {
                tg.HapticFeedback.impactOccurred('light')
            } else {
                tg.HapticFeedback.impactOccurred('medium')
            }
        }
    } catch (e) {
        // Haptic not available
    }
}

function App() {
    const [activeTab, setActiveTab] = useState(0)
    const [createDialogOpen, setCreateDialogOpen] = useState(false)
    const [notification, setNotification] = useState({ open: false, message: '', type: 'success' }) // Type: success, error, info, exp
    const [showOnboarding, setShowOnboarding] = useState(false)
    const [showInspiration, setShowInspiration] = useState(false)
    const [isRefreshing, setIsRefreshing] = useState(false)

    // Get auth state
    const { tg, user, userId, initData, isLoading: authLoading, error: authError, isReady } = useTelegram()

    // Get tasks
    const { tasks, profile, loading: tasksLoading, error: tasksError, createTask, completeTask, deleteTask, refreshTasks } = useTasks(userId, initData)

    // Check for first visit
    useEffect(() => {
        const hasSeenOnboarding = localStorage.getItem('taskbot_onboarding_complete')
        if (!hasSeenOnboarding && !authLoading && userId) {
            setShowOnboarding(true)
        } else if (userId && !authLoading) {
            // Show daily inspiration on boot if onboarding is done
            setShowInspiration(true)
        }
    }, [authLoading, userId])

    const handleOnboardingComplete = () => {
        localStorage.setItem('taskbot_onboarding_complete', 'true')
        setShowOnboarding(false)
        triggerHaptic('success')
    }

    // Pull to refresh handler
    const handleRefresh = useCallback(async () => {
        setIsRefreshing(true)
        triggerHaptic('light')
        if (refreshTasks) {
            await refreshTasks()
        }
        setIsRefreshing(false)
    }, [refreshTasks])

    // Notification handlers
    // Notification handlers
    const showNotification = (message, type = 'success') => {
        setNotification({ open: true, message, type })
    }

    const handleCompleteTask = async (taskId) => {
        triggerHaptic('medium')
        try {
            const result = await completeTask(taskId)
            if (result?.xp_earned) {
                const isLevelUp = result.level_up
                const msg = isLevelUp
                    ? `🎉 +${result.xp_earned} XP! Level UP to ${result.new_level}!`
                    : `✅ +${result.xp_earned} XP earned!`
                showNotification(msg, 'exp')
                triggerHaptic('success')
                fireConfetti(isLevelUp)

                if (result.unlocked_achievements?.length > 0) {
                    setTimeout(() => {
                        showNotification(`🏆 Achievement unlocked!`, 'info')
                        fireConfetti(true)
                    }, 2000)
                }
            }
        } catch (err) {
            triggerHaptic('error')
            showNotification('Error completing task', 'error')
        }
    }

    const handleDeleteTask = async (taskId) => {
        triggerHaptic('medium')
        try {
            const result = await deleteTask(taskId)
            if (result?.xp_lost) {
                showNotification(`❌ -${result.xp_lost} XP lost`, 'warning')
            }
        } catch (err) {
            triggerHaptic('error')
            showNotification('Error deleting task', 'error')
        }
    }

    const handleTabChange = (e, newTab) => {
        triggerHaptic('light')
        setActiveTab(newTab)
    }

    useEffect(() => {
        if (tg) {
            tg.ready()
            tg.expand()
            try {
                tg.enableClosingConfirmation()
            } catch (e) { }
        }
    }, [tg])

    const handleCreateTask = async (taskData) => {
        triggerHaptic('medium')
        try {
            await createTask(taskData)
            setCreateDialogOpen(false)
            triggerHaptic('success')
            showNotification('✨ Task created!', 'success')
        } catch (err) {
            triggerHaptic('error')
            console.error('Error creating task:', err)
            showNotification('Error creating task', 'error')
        }
    }

    // Show onboarding
    if (showOnboarding) {
        return <Onboarding onComplete={handleOnboardingComplete} user={user} />
    }

    // Show loading
    if (authLoading) {
        return (
            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                bgcolor: 'background.default',
                gap: 3
            }}>
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                >
                    <RocketLaunchIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                </motion.div>
                <Typography color="text.secondary">
                    Launching TaskBot...
                </Typography>
            </Box>
        )
    }

    // Show error
    if (authError && !userId) {
        return (
            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                alignItems: 'center',
                height: '100vh',
                bgcolor: 'background.default',
                p: 3,
                gap: 2
            }}>
                <RocketLaunchIcon sx={{ fontSize: 60, color: 'primary.main' }} />
                <Typography variant="h5" color="text.primary">
                    TaskBot
                </Typography>
                <Typography color="text.secondary" align="center">
                    Please open via Telegram
                </Typography>
            </Box>
        )
    }

    return (
        <Box sx={{ pb: 7, minHeight: '100vh' }}>
            {/* Header */}
            <AppBar position="static" elevation={0}>
                <Container maxWidth="md">
                    <Box sx={{ py: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                            <motion.div
                                whileHover={{ rotate: 5 }}
                                whileTap={{ scale: 0.9 }}
                            >
                                <img src={logo} alt="TaskBot" style={{ width: 40, height: 40, borderRadius: '50%' }} />
                            </motion.div>
                            <Box>
                                <Typography variant="h6" color="text.primary">
                                    TaskBot
                                </Typography>
                                <Typography variant="caption" color="primary.main" fontWeight={600}>
                                    Productivity App
                                </Typography>
                            </Box>
                        </Box>
                        {user && (
                            <Box sx={{
                                background: 'rgba(255,255,255,0.1)',
                                px: 1.5,
                                py: 0.5,
                                borderRadius: 2,
                                backdropFilter: 'blur(10px)'
                            }}>
                                <Typography variant="caption" color="text.secondary">
                                    {user.first_name || `User`}
                                </Typography>
                            </Box>
                        )}
                    </Box>
                </Container>
            </AppBar>

            {/* Pull to refresh indicator */}
            {isRefreshing && (
                <Box sx={{ display: 'flex', justifyContent: 'center', py: 1 }}>
                    <CircularProgress size={20} sx={{ color: '#FF6B35' }} />
                </Box>
            )}

            {/* Content with page transitions */}
            <Container maxWidth="md" sx={{ mt: 2, mb: 2 }}>
                <AnimatePresence mode="wait">
                    {activeTab === 0 && (
                        <motion.div
                            key="tasks"
                            variants={pageVariants}
                            initial="initial"
                            animate="animate"
                            exit="exit"
                        >
                            <TaskBoard
                                tasks={tasks}
                                loading={tasksLoading}
                                onComplete={handleCompleteTask}
                                onDelete={handleDeleteTask}
                            />
                        </motion.div>
                    )}
                    {activeTab === 1 && (
                        <motion.div
                            key="calendar"
                            variants={pageVariants}
                            initial="initial"
                            animate="animate"
                            exit="exit"
                        >
                            <Calendar tasks={tasks} onCreate={handleCreateTask} />
                        </motion.div>
                    )}
                    {activeTab === 2 && (
                        <motion.div
                            key="profile"
                            variants={pageVariants}
                            initial="initial"
                            animate="animate"
                            exit="exit"
                        >
                            <Profile profile={profile} tasks={tasks} />
                        </motion.div>
                    )}
                </AnimatePresence>
            </Container>

            {/* FAB with animation */}
            <motion.div
                style={{ position: 'fixed', bottom: 80, right: 16, zIndex: 1000 }}
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
            >
                <Fab
                    color="primary"
                    onClick={() => {
                        triggerHaptic('light')
                        setCreateDialogOpen(true)
                    }}
                >
                    <AddIcon />
                </Fab>
            </motion.div>

            {/* Create Dialog */}
            <CreateTaskDialog
                open={createDialogOpen}
                onClose={() => setCreateDialogOpen(false)}
                onCreate={handleCreateTask}
            />

            {/* Bottom Nav */}
            <AppBar
                position="fixed"
                sx={{
                    top: 'auto',
                    bottom: 0,
                    backgroundColor: 'rgba(10, 46, 77, 0.95)',
                    backdropFilter: 'blur(20px)',
                    borderTop: '1px solid rgba(255,255,255,0.1)'
                }}
                elevation={0}
            >
                <Tabs
                    value={activeTab}
                    onChange={handleTabChange}
                    variant="fullWidth"
                    textColor="inherit"
                >
                    <Tab icon={<ChecklistIcon />} label="Tasks" />
                    <Tab icon={<CalendarMonthIcon />} label="Calendar" />
                    <Tab icon={<PersonIcon />} label="Profile" />
                </Tabs>
            </AppBar>

            {/* XP Notification */}
            {/* Daily Inspiration Modal */}
            <DailyInspiration
                open={showInspiration}
                onClose={() => setShowInspiration(false)}
            />

            {/* Custom Game Notification */}
            <GameNotification
                open={notification.open}
                message={notification.message}
                type={notification.type}
                onClose={() => setNotification({ ...notification, open: false })}
            />

        </Box>
    )
}

export default App
