'use client'

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { useRouter } from 'next/navigation'
import { authApi, usersApi } from '@/lib/api'

interface User {
    id: string
    email: string
    username: string
    plan: string
    is_active: boolean
}

interface AuthContextType {
    user: User | null
    token: string | null
    login: (email: string, password: string) => Promise<void>
    register: (email: string, username: string, password: string) => Promise<void>
    logout: () => void
    isLoading: boolean
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null)
    const [token, setToken] = useState<string | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const router = useRouter()

    useEffect(() => {
        const stored = localStorage.getItem('auth_token')
        if (stored) {
            setToken(stored)
            usersApi.me()
                .then(r => setUser(r.data))
                .catch(() => {
                    localStorage.removeItem('auth_token')
                    setToken(null)
                })
                .finally(() => setIsLoading(false))
        } else {
            setIsLoading(false)
        }
    }, [])

    const login = async (email: string, password: string) => {
        const res = await authApi.login(email, password)
        const { access_token } = res.data
        localStorage.setItem('auth_token', access_token)
        setToken(access_token)
        const userRes = await usersApi.me()
        setUser(userRes.data)
        router.push('/dashboard')
    }

    const register = async (email: string, username: string, password: string) => {
        await authApi.register(email, username, password)
        await login(email, password)
    }

    const logout = () => {
        localStorage.removeItem('auth_token')
        setToken(null)
        setUser(null)
        router.push('/login')
    }

    return (
        <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth() {
    const ctx = useContext(AuthContext)
    if (!ctx) throw new Error('useAuth must be used within AuthProvider')
    return ctx
}
