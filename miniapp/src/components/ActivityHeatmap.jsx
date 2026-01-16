import { Box, Typography, Paper, Tooltip } from '@mui/material';
import { motion } from 'framer-motion';

const ActivityHeatmap = ({ activityLog }) => {
    // Generate last 60 days
    const days = [];
    const today = new Date();

    for (let i = 59; i >= 0; i--) {
        const d = new Date(today);
        d.setDate(d.getDate() - i);
        const iso = d.toISOString().split('T')[0];
        days.push({
            date: iso,
            count: activityLog?.[iso] || 0,
            dayOfWeek: d.getDay() // 0 = Sun
        });
    }

    const getColor = (count) => {
        if (count === 0) return 'rgba(255,255,255,0.1)';
        if (count <= 2) return '#1A8CD8'; // Light blue
        if (count <= 4) return '#2AABEE'; // Medium blue
        return '#FFD700'; // Gold/Yellow
    };

    return (
        <Paper
            elevation={4}
            sx={{
                p: 2,
                mb: 3,
                borderRadius: 4,
                background: 'rgba(26, 32, 39, 0.8)', // Dark semi-transparent
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.1)'
            }}
        >
            <Typography variant="h6" color="white" gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                📊 Activity History
            </Typography>

            <Box sx={{
                display: 'grid',
                gridTemplateColumns: 'repeat(20, 1fr)', // 3 rows * 20 cols = 60 days roughly? No.
                // We want 7 rows (days of week) x N cols (weeks) like GitHub
                // But simplified: Flex wrap or simple grid
                // Let's do simple flex wrap for mobile friendly
                gap: 0.5,
                mt: 1
            }}>
                {days.map((day) => (
                    <Tooltip key={day.date} title={`${day.date}: ${day.count} tasks`} arrow>
                        <motion.div
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            transition={{ delay: 0.005 * days.indexOf(day) }}
                            style={{
                                width: '100%',
                                aspectRatio: '1/1',
                                backgroundColor: getColor(day.count),
                                borderRadius: 4,
                                cursor: 'pointer'
                            }}
                        />
                    </Tooltip>
                ))}
            </Box>
            <Typography variant="caption" color="gray" sx={{ display: 'block', mt: 1, textAlign: 'right' }}>
                Last 60 Days
            </Typography>
        </Paper>
    );
};

export default ActivityHeatmap;
