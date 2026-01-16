import { Box, Paper, Typography, LinearProgress, Chip, Grid, Button } from '@mui/material'
import { motion } from 'framer-motion'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import LocalFireDepartmentIcon from '@mui/icons-material/LocalFireDepartment'
import StarIcon from '@mui/icons-material/Star'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'
import AdminStats from './AdminStats'
import ActivityHeatmap from './ActivityHeatmap'
import { useState } from 'react'

const MotionPaper = motion(Paper)
const MotionBox = motion(Box)

const achievementNames = {
    'first_task': { emoji: '🎯', name: 'First Step', desc: 'Complete your first task' },
    'week_streak': { emoji: '🔥', name: 'Week Warrior', desc: '7-day streak' },
    'early_bird': { emoji: '🌅', name: 'Early Bird', desc: 'Complete before 8am' },
    'night_owl': { emoji: '🦉', name: 'Night Owl', desc: 'Complete after 10pm' },
    'century': { emoji: '💯', name: 'Centurion', desc: '100 tasks completed' },
    'priority_master': { emoji: '⚡', name: 'Priority Master', desc: '10 high priority tasks' },
    'no_quit': { emoji: '💪', name: 'No Quit', desc: '30 days without delete' }
}

const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
        opacity: 1,
        transition: {
            staggerChildren: 0.1
        }
    }
}

const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: {
        opacity: 1,
        y: 0,
        transition: {
            type: "spring",
            stiffness: 300,
            damping: 24
        }
    }
}

const Profile = ({ profile, tasks }) => {
    const [showAdmin, setShowAdmin] = useState(false)

    if (!profile) return null

    if (showAdmin) {
        return <AdminStats userId={profile.userId} onBack={() => setShowAdmin(false)} />
    }

    const level = parseInt(profile.level) || 1
    const totalXP = parseInt(profile.totalXP) || 0
    const xpInLevel = profile.xpProgress || (totalXP % 100)
    const xpForNext = profile.xpForNextLevel || 100
    const progress = (xpInLevel / xpForNext) * 100
    const streak = parseInt(profile.streak) || 0
    const tasksCompleted = parseInt(profile.tasksCompleted) || 0
    const isAdmin = String(profile.userId) === '1685847131'

    return (
        <MotionBox
            variants={containerVariants}
            initial="hidden"
            animate="visible"
        >
            {/* Level Card - Hero Section */}
            <MotionPaper
                variants={itemVariants}
                elevation={8}
                sx={{
                    p: 4,
                    mb: 3,
                    textAlign: 'center',
                    background: 'linear-gradient(135deg, #2AABEE 0%, #1A8CD8 50%, #0A6EBD 100%)',
                    borderRadius: 4,
                    position: 'relative',
                    overflow: 'hidden',
                    '&::before': {
                        content: '""',
                        position: 'absolute',
                        top: -50,
                        right: -50,
                        width: 150,
                        height: 150,
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.1)'
                    },
                    '&::after': {
                        content: '""',
                        position: 'absolute',
                        bottom: -30,
                        left: -30,
                        width: 100,
                        height: 100,
                        borderRadius: '50%',
                        background: 'rgba(255,255,255,0.05)'
                    }
                }}
            >
                <motion.div
                    animate={{
                        scale: [1, 1.05, 1],
                        rotate: [0, 2, -2, 0]
                    }}
                    transition={{
                        duration: 3,
                        repeat: Infinity,
                        repeatType: "reverse"
                    }}
                >
                    <StarIcon sx={{ fontSize: 60, color: '#FFD700', mb: 1 }} />
                </motion.div>

                <Typography variant="h2" fontWeight="bold" color="white" sx={{ textShadow: '0 2px 10px rgba(0,0,0,0.3)' }}>
                    Level {level}
                </Typography>

                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 1, mt: 1 }}>
                    <TrendingUpIcon sx={{ color: 'rgba(255,255,255,0.9)' }} />
                    <Typography variant="h5" color="white" sx={{ opacity: 0.9 }}>
                        {totalXP} XP
                    </Typography>
                </Box>

                <Box sx={{ mt: 3, position: 'relative' }}>
                    <LinearProgress
                        variant="determinate"
                        value={progress}
                        sx={{
                            height: 12,
                            borderRadius: 6,
                            backgroundColor: 'rgba(255,255,255,0.2)',
                            '& .MuiLinearProgress-bar': {
                                backgroundColor: '#FFD700',
                                borderRadius: 6,
                                boxShadow: '0 0 10px rgba(255,215,0,0.5)'
                            }
                        }}
                    />
                    <Typography variant="body2" color="white" sx={{ mt: 1.5, fontWeight: 600 }}>
                        {xpInLevel} / {xpForNext} XP to Level {level + 1}
                    </Typography>
                </Box>
            </MotionPaper>

            <ActivityHeatmap activityLog={profile.activityLog} />

            {/* Admin Button */}
            {
                isAdmin && (
                    <motion.div variants={itemVariants}>
                        <Button
                            fullWidth
                            variant="contained"
                            color="secondary"
                            onClick={() => setShowAdmin(true)}
                            sx={{ mb: 3, borderRadius: 3, py: 1.5, fontWeight: 'bold' }}
                        >
                            🔐 Open Admin Panel
                        </Button>
                    </motion.div>
                )
            }

            {/* Stats Grid */}
            <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                    <MotionPaper
                        variants={itemVariants}
                        elevation={4}
                        sx={{
                            p: 2.5,
                            textAlign: 'center',
                            bgcolor: 'background.paper',
                            backdropFilter: 'blur(10px)',
                            borderRadius: 3,
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}
                    >
                        <motion.div
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.95 }}
                        >
                            <Typography variant="h3" sx={{
                                background: 'linear-gradient(135deg, #4CAF50, #8BC34A)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontWeight: 'bold'
                            }}>
                                {tasksCompleted}
                            </Typography>
                        </motion.div>
                        <Typography variant="body2" sx={{ color: '#B8CBD9', mt: 0.5 }}>
                            ✅ Tasks Done
                        </Typography>
                    </MotionPaper>
                </Grid>

                <Grid item xs={6}>
                    <MotionPaper
                        variants={itemVariants}
                        elevation={4}
                        sx={{
                            p: 2.5,
                            textAlign: 'center',
                            bgcolor: 'background.paper',
                            backdropFilter: 'blur(10px)',
                            borderRadius: 3,
                            border: '1px solid rgba(255,255,255,0.1)'
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                            <motion.div
                                animate={{
                                    scale: streak > 0 ? [1, 1.2, 1] : 1,
                                    rotate: streak > 0 ? [0, 10, -10, 0] : 0
                                }}
                                transition={{
                                    duration: 0.5,
                                    repeat: streak > 0 ? Infinity : 0,
                                    repeatDelay: 2
                                }}
                            >
                                <LocalFireDepartmentIcon sx={{ fontSize: 40, color: '#FF6B35' }} />
                            </motion.div>
                            <Typography variant="h3" sx={{
                                background: 'linear-gradient(135deg, #FF6B35, #FFA500)',
                                WebkitBackgroundClip: 'text',
                                WebkitTextFillColor: 'transparent',
                                fontWeight: 'bold'
                            }}>
                                {streak}
                            </Typography>
                        </Box>
                        <Typography variant="body2" sx={{ color: '#B8CBD9' }}>
                            🔥 Day Streak
                        </Typography>
                    </MotionPaper>
                </Grid>
            </Grid>

            {/* Achievements */}
            <MotionPaper
                variants={itemVariants}
                elevation={4}
                sx={{
                    p: 3,
                    bgcolor: 'background.paper',
                    backdropFilter: 'blur(10px)',
                    borderRadius: 3,
                    border: '1px solid rgba(255,255,255,0.1)'
                }}
            >
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2.5 }}>
                    <motion.div
                        animate={{ rotate: [0, 10, -10, 0] }}
                        transition={{ duration: 2, repeat: Infinity, repeatDelay: 3 }}
                    >
                        <EmojiEventsIcon sx={{ fontSize: 28, color: '#FFD700', mr: 1 }} />
                    </motion.div>
                    <Typography variant="h6" fontWeight={700} sx={{ color: 'white' }}>
                        Achievements
                    </Typography>
                    <Chip
                        label={`${(profile.achievements || []).length}/${profile.totalAchievements || 7}`}
                        size="small"
                        sx={{
                            ml: 'auto',
                            background: 'linear-gradient(135deg, #FFD700, #FFA500)',
                            color: 'black',
                            fontWeight: 700
                        }}
                    />
                </Box>

                <Grid container spacing={1.5}>
                    {(profile.achievements || []).map((achievement, index) => {
                        const achId = typeof achievement === 'object' ? achievement.id : achievement
                        const achInfo = achievementNames[achId] || {
                            emoji: typeof achievement === 'object' ? '🏆' : '🏆',
                            name: typeof achievement === 'object' ? achievement.name : achievement,
                            desc: typeof achievement === 'object' ? achievement.description : ''
                        }
                        const displayName = typeof achievement === 'object' ? achievement.name : achInfo.name

                        return (
                            <Grid item xs={12} sm={6} key={achId || index}>
                                <motion.div
                                    initial={{ opacity: 0, scale: 0.8 }}
                                    animate={{ opacity: 1, scale: 1 }}
                                    transition={{ delay: index * 0.1 }}
                                    whileHover={{ scale: 1.03 }}
                                >
                                    <Paper
                                        elevation={2}
                                        sx={{
                                            p: 1.5,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 1.5,
                                            background: 'linear-gradient(135deg, rgba(255,215,0,0.15), rgba(255,165,0,0.1))',
                                            border: '1px solid rgba(255,215,0,0.3)',
                                            borderRadius: 2
                                        }}
                                    >
                                        <Typography sx={{ fontSize: '1.5rem' }}>
                                            {achInfo.emoji}
                                        </Typography>
                                        <Box>
                                            <Typography variant="body2" sx={{ fontWeight: 600, color: '#FFD700' }}>
                                                {displayName}
                                            </Typography>
                                            {achInfo.desc && (
                                                <Typography variant="caption" sx={{ color: 'rgba(255,255,255,0.6)' }}>
                                                    {achInfo.desc}
                                                </Typography>
                                            )}
                                        </Box>
                                    </Paper>
                                </motion.div>
                            </Grid>
                        )
                    })}
                </Grid>

                {(!profile.achievements || profile.achievements.length === 0) && (
                    <motion.div
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: 0.3 }}
                    >
                        <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.5)', fontStyle: 'italic', textAlign: 'center', py: 2 }}>
                            ✨ Complete tasks to unlock achievements!
                        </Typography>
                    </motion.div>
                )}
            </MotionPaper>

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
            >
                <Box sx={{ mt: 3, textAlign: 'center' }}>
                    <Typography variant="caption" sx={{ color: 'rgba(184, 203, 217, 0.7)' }}>
                        🚀 Keep completing tasks to level up!
                    </Typography>
                </Box>
            </motion.div>

            {/* About Us Section */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
            >
                <Paper
                    elevation={2}
                    sx={{
                        mt: 3,
                        p: 2.5,
                        background: 'linear-gradient(135deg, rgba(255, 107, 53, 0.1) 0%, rgba(10, 46, 77, 0.95) 100%)',
                        backdropFilter: 'blur(10px)',
                        borderRadius: 3,
                        border: '1px solid rgba(255, 107, 53, 0.2)',
                        textAlign: 'center'
                    }}
                >
                    <Typography variant="subtitle2" sx={{ color: '#FF6B35', fontWeight: 700, mb: 1 }}>
                        👨‍💻 About
                    </Typography>
                    <Typography variant="body2" sx={{ color: 'white', fontWeight: 600, mb: 0.5 }}>
                        Artur Martirosyan
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(184, 203, 217, 0.8)', display: 'block', mb: 1 }}>
                        Solo Developer & Creator
                    </Typography>
                    <Typography variant="caption" sx={{ color: 'rgba(184, 203, 217, 0.6)', fontStyle: 'italic' }}>
                        Built with ❤️ as a personal project
                    </Typography>
                </Paper>
            </motion.div>
        </MotionBox >
    )
}

export default Profile
