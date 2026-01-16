import { useState } from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'
import { motion, AnimatePresence } from 'framer-motion'
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch'
import CheckCircleIcon from '@mui/icons-material/CheckCircle'
import EmojiEventsIcon from '@mui/icons-material/EmojiEvents'
import TrendingUpIcon from '@mui/icons-material/TrendingUp'

const slides = [
    {
        icon: RocketLaunchIcon,
        title: 'Welcome to TaskBot!',
        subtitle: 'Your AI-powered task manager',
        description: 'Create, manage, and complete tasks with gamification rewards',
        gradient: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)'
    },
    {
        icon: CheckCircleIcon,
        title: 'Complete Tasks',
        subtitle: 'Earn XP for every task',
        description: 'Higher priority tasks = more XP. Build your streak!',
        gradient: 'linear-gradient(135deg, #4CAF50 0%, #45a049 100%)'
    },
    {
        icon: EmojiEventsIcon,
        title: 'Unlock Achievements',
        subtitle: '7 unique achievements to earn',
        description: 'First Task, Week Warrior, Early Bird, and more!',
        gradient: 'linear-gradient(135deg, #FFD700 0%, #FFA500 100%)'
    },
    {
        icon: TrendingUpIcon,
        title: 'Level Up!',
        subtitle: 'Track your progress',
        description: 'Gain XP, level up, and become a productivity master',
        gradient: 'linear-gradient(135deg, #2AABEE 0%, #229ED9 100%)'
    }
]

const Onboarding = ({ onComplete, user }) => {
    const [currentSlide, setCurrentSlide] = useState(0)

    const handleNext = () => {
        if (currentSlide < slides.length - 1) {
            setCurrentSlide(currentSlide + 1)
        } else {
            onComplete()
        }
    }

    const handleSkip = () => {
        onComplete()
    }

    const slide = slides[currentSlide]
    const IconComponent = slide.icon

    return (
        <Box sx={{
            minHeight: '100vh',
            backgroundColor: '#0A2E4D',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            p: 3,
            position: 'relative',
            overflow: 'hidden'
        }}>
            {/* Background decoration */}
            <Box sx={{
                position: 'absolute',
                top: -100,
                right: -100,
                width: 300,
                height: 300,
                borderRadius: '50%',
                background: 'rgba(255, 107, 53, 0.1)',
                filter: 'blur(60px)'
            }} />
            <Box sx={{
                position: 'absolute',
                bottom: -50,
                left: -50,
                width: 200,
                height: 200,
                borderRadius: '50%',
                background: 'rgba(42, 171, 238, 0.1)',
                filter: 'blur(40px)'
            }} />

            {/* Skip button */}
            <Button
                onClick={handleSkip}
                sx={{
                    position: 'absolute',
                    top: 20,
                    right: 20,
                    color: 'rgba(255,255,255,0.6)',
                    fontFamily: '"Inter", sans-serif'
                }}
            >
                Skip
            </Button>

            {/* Welcome message */}
            {currentSlide === 0 && user?.first_name && (
                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <Typography
                        variant="h6"
                        sx={{
                            color: '#FF6B35',
                            mb: 4,
                            fontFamily: '"Inter", sans-serif',
                            fontWeight: 600
                        }}
                    >
                        Hey, {user.first_name}! 👋
                    </Typography>
                </motion.div>
            )}

            {/* Slide content */}
            <AnimatePresence mode="wait">
                <motion.div
                    key={currentSlide}
                    initial={{ opacity: 0, scale: 0.9, x: 50 }}
                    animate={{ opacity: 1, scale: 1, x: 0 }}
                    exit={{ opacity: 0, scale: 0.9, x: -50 }}
                    transition={{ duration: 0.3 }}
                    style={{ textAlign: 'center', width: '100%', maxWidth: 400 }}
                >
                    {/* Icon */}
                    <motion.div
                        animate={{
                            y: [0, -10, 0],
                            rotate: [0, 5, -5, 0]
                        }}
                        transition={{
                            duration: 3,
                            repeat: Infinity,
                            repeatType: 'reverse'
                        }}
                    >
                        <Paper
                            elevation={8}
                            sx={{
                                width: 100,
                                height: 100,
                                borderRadius: 4,
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                background: slide.gradient,
                                mx: 'auto',
                                mb: 4,
                                boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
                            }}
                        >
                            <IconComponent sx={{ fontSize: 50, color: 'white' }} />
                        </Paper>
                    </motion.div>

                    {/* Title */}
                    <Typography
                        variant="h4"
                        sx={{
                            color: 'white',
                            fontWeight: 700,
                            mb: 1,
                            fontFamily: '"Inter", sans-serif'
                        }}
                    >
                        {slide.title}
                    </Typography>

                    {/* Subtitle */}
                    <Typography
                        variant="h6"
                        sx={{
                            color: '#FF6B35',
                            fontWeight: 600,
                            mb: 2,
                            fontFamily: '"Inter", sans-serif'
                        }}
                    >
                        {slide.subtitle}
                    </Typography>

                    {/* Description */}
                    <Typography
                        sx={{
                            color: '#B8CBD9',
                            mb: 4,
                            fontFamily: '"Inter", sans-serif'
                        }}
                    >
                        {slide.description}
                    </Typography>
                </motion.div>
            </AnimatePresence>

            {/* Progress dots */}
            <Box sx={{ display: 'flex', gap: 1, mb: 4 }}>
                {slides.map((_, index) => (
                    <motion.div
                        key={index}
                        animate={{
                            scale: currentSlide === index ? 1.2 : 1,
                            backgroundColor: currentSlide === index ? '#FF6B35' : 'rgba(255,255,255,0.3)'
                        }}
                        style={{
                            width: 10,
                            height: 10,
                            borderRadius: '50%',
                            cursor: 'pointer'
                        }}
                        onClick={() => setCurrentSlide(index)}
                    />
                ))}
            </Box>

            {/* Next button */}
            <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <Button
                    variant="contained"
                    onClick={handleNext}
                    sx={{
                        background: 'linear-gradient(135deg, #FF6B35 0%, #E55A2B 100%)',
                        color: 'white',
                        px: 6,
                        py: 1.5,
                        borderRadius: 3,
                        fontWeight: 600,
                        fontFamily: '"Inter", sans-serif',
                        fontSize: '1rem',
                        textTransform: 'none',
                        boxShadow: '0 4px 20px rgba(255, 107, 53, 0.4)',
                        '&:hover': {
                            background: 'linear-gradient(135deg, #E55A2B 0%, #D44920 100%)'
                        }
                    }}
                >
                    {currentSlide < slides.length - 1 ? 'Next' : "Let's Go! 🚀"}
                </Button>
            </motion.div>

            {/* Footer */}
            <Typography
                variant="caption"
                sx={{
                    position: 'absolute',
                    bottom: 20,
                    color: 'rgba(255,255,255,0.4)',
                    fontFamily: '"Inter", sans-serif'
                }}
            >
                Made by Artur Martirosyan
            </Typography>
        </Box>
    )
}

export default Onboarding
