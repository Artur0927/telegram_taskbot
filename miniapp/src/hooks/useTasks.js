import { useState, useEffect, useCallback } from 'react'
import axios from 'axios'

const API_BASE = 'https://hh2myi12y8.execute-api.us-east-1.amazonaws.com/prod'

export const useTasks = (userId, authToken) => {
    const [tasks, setTasks] = useState([])
    const [profile, setProfile] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [initialized, setInitialized] = useState(false)

    // Create axios instance with auth
    const getApi = useCallback(() => {
        return axios.create({
            baseURL: API_BASE,
            headers: {
                'X-Telegram-Init-Data': authToken || '',
                'Content-Type': 'application/json'
            },
            params: {
                userId: userId // Always send userId as query param as fallback
            }
        })
    }, [authToken, userId])

    const fetchTasks = useCallback(async () => {
        if (!userId) return

        try {
            setLoading(true)
            console.log('📋 Fetching tasks for user:', userId)
            const api = getApi()
            const response = await api.get('/tasks')
            console.log('✅ Tasks loaded:', response.data.tasks?.length || 0)
            setTasks(response.data.tasks || [])
            setError(null)
        } catch (err) {
            console.error('❌ Error fetching tasks:', err)
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }, [userId, getApi])

    const fetchProfile = useCallback(async () => {
        if (!userId) return

        try {
            console.log('👤 Fetching profile...')
            const api = getApi()
            const response = await api.get('/profile')
            console.log('✅ Profile loaded:', response.data)
            setProfile(response.data)
        } catch (err) {
            console.error('❌ Error fetching profile:', err)
        }
    }, [userId, getApi])

    // Load data when authenticated
    useEffect(() => {
        if (userId && !initialized) {
            console.log('🚀 Starting data load for user:', userId)
            fetchTasks()
            fetchProfile()
            setInitialized(true)
        }
    }, [userId, initialized, fetchTasks, fetchProfile])

    const createTask = async (taskData) => {
        if (!userId) throw new Error('Not authenticated')

        try {
            const api = getApi()
            const response = await api.post('/tasks', taskData)
            console.log('✅ Task created')
            await fetchTasks() // Refresh list
            return response.data.task
        } catch (err) {
            console.error('❌ Error creating task:', err)
            throw err
        }
    }

    const completeTask = async (taskId) => {
        if (!userId) throw new Error('Not authenticated')

        try {
            const api = getApi()
            const response = await api.put(`/tasks/${taskId}/complete`)
            console.log('✅ Task completed', response.data.gamification)
            await fetchTasks()
            await fetchProfile() // Refresh profile XP
            return response.data.gamification // Return XP data for notification
        } catch (err) {
            console.error('❌ Error completing task:', err)
            throw err
        }
    }

    const deleteTask = async (taskId) => {
        if (!userId) throw new Error('Not authenticated')

        try {
            const api = getApi()
            const response = await api.delete(`/tasks/${taskId}`)
            console.log('✅ Task deleted', response.data.gamification)
            await fetchTasks()
            await fetchProfile() // Refresh profile XP
            return response.data.gamification // Return XP penalty for notification
        } catch (err) {
            console.error('❌ Error deleting task:', err)
            throw err
        }
    }

    return {
        tasks,
        profile,
        loading,
        error,
        createTask,
        completeTask,
        deleteTask,
        refreshTasks: fetchTasks
    }
}
