import React, { useEffect, useState } from 'react';
import { Card, CardContent, Typography, Grid, CircularProgress, Box, Button } from '@mui/material';
import { useTelegram } from '../hooks/useTelegram';
import { motion } from 'framer-motion';

const AdminStats = ({ onBack, userId: propUserId }) => {
    const { userId: hookUserId } = useTelegram();
    const userId = propUserId || hookUserId;
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_BASE = 'https://hh2myi12y8.execute-api.us-east-1.amazonaws.com/prod';

    useEffect(() => {
        const fetchStats = async () => {
            if (!userId) return; // Wait for userId

            try {
                const response = await fetch(`${API_BASE}/admin/stats?userId=${userId}`, {
                    headers: {
                        'X-Telegram-Init-Data': window.Telegram?.WebApp?.initData || ''
                    }
                });

                if (!response.ok) throw new Error('Failed to load stats');

                const data = await response.json();
                setStats(data);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchStats();
    }, [userId]);

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" mt={4}>
                <CircularProgress sx={{ color: '#fff' }} />
            </Box>
        );
    }

    if (error) {
        return (
            <Box textAlign="center" mt={4}>
                <Typography color="error">Error: {error}</Typography>
                <Button onClick={onBack} sx={{ mt: 2, color: '#fff' }}>Back</Button>
            </Box>
        );
    }

    const StatCard = ({ title, value, color }) => (
        <Grid item xs={12} sm={4}>
            <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3 }}
            >
                <Card sx={{
                    background: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '16px',
                    color: '#fff'
                }}>
                    <CardContent>
                        <Typography variant="h6" sx={{ opacity: 0.7, fontSize: '0.9rem' }}>
                            {title}
                        </Typography>
                        <Typography variant="h3" sx={{
                            fontWeight: 'bold',
                            background: color,
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent'
                        }}>
                            {value.toLocaleString()}
                        </Typography>
                    </CardContent>
                </Card>
            </motion.div>
        </Grid>
    );

    return (
        <Box p={2}>
            <Box display="flex" alignItems="center" mb={3}>
                <Button onClick={onBack} sx={{ color: 'rgba(255,255,255,0.7)', mr: 2 }}>
                    ← Back
                </Button>
                <Typography variant="h5" fontWeight="bold" color="#fff">
                    Admin Dashboard 📊
                </Typography>
            </Box>

            <Grid container spacing={2}>
                <StatCard
                    title="Total Users"
                    value={stats.totalUsers}
                    color="linear-gradient(45deg, #FF6B6B, #FF8E53)"
                />
                <StatCard
                    title="Total Tasks Done"
                    value={stats.totalTasks}
                    color="linear-gradient(45deg, #4facfe, #00f2fe)"
                />
                <StatCard
                    title="Total Group XP"
                    value={stats.totalXP}
                    color="linear-gradient(45deg, #43e97b, #38f9d7)"
                />
            </Grid>
        </Box>
    );
};

export default AdminStats;
