import { useState, useEffect } from 'react'

export const useTelegram = () => {
    const [userId, setUserId] = useState(null)
    const [user, setUser] = useState(null)
    const [initData, setInitData] = useState(null)
    const [isLoading, setIsLoading] = useState(true)
    const [error, setError] = useState(null)
    const [tg] = useState(window.Telegram?.WebApp)

    useEffect(() => {
        const authenticate = () => {
            setIsLoading(true)

            // Initialize Telegram WebApp
            if (tg) {
                tg.ready()
                tg.expand()
            }

            console.log('=== AUTHENTICATION START ===')

            // METHOD 1: Try native Telegram initData
            if (tg?.initDataUnsafe?.user) {
                console.log('📱 Using Telegram native auth')
                const telegramUser = tg.initDataUnsafe.user
                setUserId(telegramUser.id)
                setUser(telegramUser)
                setInitData(tg.initData)
                setIsLoading(false)
                console.log('✅ Authenticated as:', telegramUser.id)
                return // Success!
            }

            // METHOD 2: Check URL params (from /app command)
            const urlParams = new URLSearchParams(window.location.search)
            const userIdParam = urlParams.get('userId')

            if (userIdParam) {
                console.log('🔑 User ID from URL:', userIdParam)
                setUserId(parseInt(userIdParam))
                setUser({ id: parseInt(userIdParam), first_name: 'User' })
                setInitData('')
                setIsLoading(false)
                return // Success!
            }

            // METHOD 3: Development mode - use mock user
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                console.log('🧪 Development mode - using mock user')
                setUserId(12345)
                setUser({ id: 12345, first_name: 'Dev User' })
                setInitData('')
                setIsLoading(false)
                return
            }

            // No auth available
            console.warn('⚠️ No authentication method available')
            setError('Please open via Telegram bot')
            setIsLoading(false)
        }

        authenticate()
    }, [tg])

    return {
        tg,
        user,
        userId,
        initData,
        isLoading,
        error,
        isReady: !!userId && !isLoading
    }
}
