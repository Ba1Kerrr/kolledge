const API_BASE_URL = '/api'

class FitLogAPI {
    constructor() {
        this.token = localStorage.getItem('accessToken')
        this.user = JSON.parse(localStorage.getItem('user') || 'null')
    }

    async request(endpoint, options = {}) {
        const url = `${API_BASE_URL}${endpoint}`
        
        const headers = {
            'Content-Type': 'application/json',
            ...options.headers
        }

        if (this.token) {
            headers['Authorization'] = `Bearer ${this.token}`
        }

        try {
            const response = await fetch(url, {
                ...options,
                headers
            })

            if (!response.ok) {
                let errorData
                try {
                    errorData = await response.json()
                } catch (e) {
                    throw new Error(`Ошибка (${response.status})`)
                }
                
                if (errorData.detail) {
                    throw new Error(errorData.detail)
                }
                
                throw new Error(errorData.message || 'Ошибка сервера')
            }

            return await response.json()

        } catch (error) {
            const msg = error.message
            if (msg.includes('User with this email or username already exists')) {
                throw new Error('Пользователь с таким email уже существует')
            }
            if (msg.includes('Incorrect username or password')) {
                throw new Error('Неверный email или пароль')
            }
            if (msg.includes('email already registered')) {
                throw new Error('Email уже зарегистрирован')
            }
            
            throw error
        }
    }

    async register(userData) {
        if (!userData.email || !userData.password) {
            throw new Error('Email и пароль обязательны')
        }
        
        if (userData.password.length < 8) {
            throw new Error('Пароль минимум 8 символов')
        }
        
        if (!userData.username) {
            userData.username = userData.email.split('@')[0]
        }
        
        return await this.request('/users/register', {
            method: 'POST',
            body: JSON.stringify({
                email: userData.email,
                username: userData.username,
                password: userData.password,
                full_name: userData.full_name || ""
            })
        })
    }

    async login(emailOrUsername, password) {
        if (!emailOrUsername || !password) {
            throw new Error('Введите email и пароль')
        }
        
        const formData = new FormData()
        formData.append('username', emailOrUsername)
        formData.append('password', password)
        
        try {
            const response = await fetch(`${API_BASE_URL}/users/login`, {
                method: 'POST',
                body: formData
            })
            
            if (!response.ok) {
                let error
                try {
                    error = await response.json()
                } catch (e) {
                    throw new Error('Ошибка входа')
                }
                
                throw new Error(error.detail || 'Ошибка входа')
            }
            
            const data = await response.json()
            
            this.token = data.access_token
            this.user = data.user || data
            
            localStorage.setItem('accessToken', this.token)
            localStorage.setItem('user', JSON.stringify(this.user))
            
            return data
            
        } catch (error) {
            const msg = error.message
            if (msg.includes('Incorrect username or password')) {
                throw new Error('Неверный email или пароль')
            }
            throw error
        }
    }

    async getCurrentUser() {
        try {
            if (!this.token) return null
            
            const user = await this.request('/users/me')
            this.user = user
            localStorage.setItem('user', JSON.stringify(user))
            return user
            
        } catch (error) {
            return null
        }
    }

    logout() {
        this.token = null
        this.user = null
        localStorage.removeItem('accessToken')
        localStorage.removeItem('user')
        window.location.href = '/'
    }
}

window.FitLogAPI = new FitLogAPI()