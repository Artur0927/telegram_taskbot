import { useState } from 'react'
import { Box, Typography, Paper } from '@mui/material'

const Calendar = ({ tasks }) => {
    const [currentDate] = useState(new Date())

    const getDaysInMonth = (date) => {
        const year = date.getFullYear()
        const month = date.getMonth()
        const firstDay = new Date(year, month, 1).getDay()
        const daysInMonth = new Date(year, month + 1, 0).getDate()

        return { firstDay, daysInMonth }
    }

    const getTasksForDay = (day) => {
        return tasks.filter(task => {
            const timestamp = typeof task.remindAt === 'string' ? parseInt(task.remindAt) : task.remindAt
            const taskDate = new Date(timestamp * 1000)
            return taskDate.getDate() === day &&
                taskDate.getMonth() === currentDate.getMonth() &&
                taskDate.getFullYear() === currentDate.getFullYear()
        })
    }

    const { firstDay, daysInMonth } = getDaysInMonth(currentDate)
    const days = []

    // Empty cells for days before month starts
    for (let i = 0; i < firstDay; i++) {
        days.push(null)
    }

    // Days of the month
    for (let i = 1; i <= daysInMonth; i++) {
        days.push(i)
    }

    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December']

    const priorityColors = {
        high: '#FF6B35',
        medium: '#FFA500',
        low: '#B8CBD9'
    }

    return (
        <Box sx={{ width: '100%', maxWidth: '600px', margin: '0 auto' }}>
            {/* Month Header */}
            <Box sx={{
                mb: 2,
                p: 2,
                bgcolor: 'background.paper',
                border: '1px solid rgba(255, 255, 255, 0.05)',
                borderRadius: 2
            }}>
                <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main', textAlign: 'center' }}>
                    {monthNames[currentDate.getMonth()]} {currentDate.getFullYear()}
                </Typography>
            </Box>

            {/* Day Labels */}
            <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(7, 1fr)',
                gap: 0.5,
                mb: 1,
                px: 1
            }}>
                {['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, idx) => (
                    <Typography
                        key={idx}
                        variant="caption"
                        sx={{
                            textAlign: 'center',
                            fontWeight: 600,
                            color: '#B8CBD9',
                            fontSize: '0.7rem'
                        }}
                    >
                        {day}
                    </Typography>
                ))}
            </Box>

            {/* Calendar Grid */}
            <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(7, 1fr)',
                gap: 0.5,
                px: 1
            }}>
                {days.map((day, index) => {
                    const dayTasks = day ? getTasksForDay(day) : []
                    const isToday = day === new Date().getDate() &&
                        currentDate.getMonth() === new Date().getMonth() &&
                        currentDate.getFullYear() === new Date().getFullYear()

                    return (
                        <Paper
                            key={index}
                            elevation={day ? 2 : 0}
                            sx={{
                                aspectRatio: '1',
                                p: 0.5,
                                backgroundColor: day ? (isToday ? 'primary.main' : 'background.paper') : 'transparent',
                                display: 'flex',
                                flexDirection: 'column',
                                alignItems: 'center',
                                justifyContent: 'flex-start',
                                minHeight: 0,
                                overflow: 'hidden'
                            }}
                        >
                            {day && (
                                <>
                                    <Typography
                                        variant="caption"
                                        sx={{
                                            fontWeight: isToday ? 700 : 500,
                                            color: isToday ? 'white' : '#B8CBD9',
                                            fontSize: '0.75rem',
                                            mb: 0.25
                                        }}
                                    >
                                        {day}
                                    </Typography>
                                    {dayTasks.length > 0 && (
                                        <Box sx={{
                                            display: 'flex',
                                            flexWrap: 'wrap',
                                            gap: 0.25,
                                            justifyContent: 'center',
                                            alignItems: 'center'
                                        }}>
                                            {dayTasks.slice(0, 2).map((task, idx) => (
                                                <Box
                                                    key={idx}
                                                    sx={{
                                                        width: 4,
                                                        height: 4,
                                                        borderRadius: '50%',
                                                        backgroundColor: priorityColors[task.priority] || priorityColors.medium
                                                    }}
                                                />
                                            ))}
                                            {dayTasks.length > 2 && (
                                                <Typography variant="caption" sx={{ fontSize: '0.5rem', color: '#FF6B35', fontWeight: 700 }}>
                                                    +{dayTasks.length - 2}
                                                </Typography>
                                            )}
                                        </Box>
                                    )}
                                </>
                            )}
                        </Paper>
                    )
                })}
            </Box>

            {/* Tasks Summary */}
            <Box sx={{ mt: 2, px: 1 }}>
                <Typography variant="caption" sx={{ display: 'block', color: '#B8CBD9', textAlign: 'center' }}>
                    📊 {tasks.length} tasks this month
                </Typography>
            </Box>
        </Box>
    )
}

export default Calendar
