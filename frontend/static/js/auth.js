document.addEventListener('DOMContentLoaded', function() {
    const api = window.FitLogAPI
    if (!api) return
    
    function notify(message, type = 'info') {
        if (typeof window.showNotification === 'function') {
            window.showNotification(message, type)
        } else {
            const notification = document.createElement('div')
            notification.textContent = message
            notification.style.cssText = `
                position: fixed
                top: 20px
                right: 20px
                background: ${type === 'error' ? '#f44336' : type === 'success' ? '#4CAF50' : '#2196F3'}
                color: white
                padding: 15px 20px
                border-radius: 5px
                z-index: 10000
                box-shadow: 0 2px 10px rgba(0,0,0,0.2)
            `
            document.body.appendChild(notification)
            setTimeout(() => notification.remove(), 5000)
        }
    }
    
    initPasswordToggles()
    initAuthModal()
    checkAuthStatus()
    
    function initPasswordToggles() {
        document.querySelectorAll('.toggle-password').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault()
                const targetId = this.getAttribute('data-target')
                const passwordInput = document.getElementById(targetId)
                const icon = this.querySelector('i')
                
                if (!passwordInput || !icon) return
                
                if (passwordInput.type === 'password') {
                    passwordInput.type = 'text'
                    icon.classList.remove('fa-eye')
                    icon.classList.add('fa-eye-slash')
                } else {
                    passwordInput.type = 'password'
                    icon.classList.remove('fa-eye-slash')
                    icon.classList.add('fa-eye')
                }
            })
        })
    }
    
    function initAuthModal() {
        const modalOverlay = document.getElementById('modalOverlay')
        const authModal = document.getElementById('authModal')
        const modalCloseBtn = document.getElementById('modalCloseBtn')
        const sidebarLoginBtn = document.getElementById('sidebarLoginBtn')
        const heroLoginBtn = document.getElementById('heroLoginBtn')
        const authTabs = document.querySelectorAll('.auth-tab')
        
        if (!modalOverlay || !authModal) return
        
        function openAuthModal() {
            modalOverlay.classList.add('active')
            authModal.classList.add('active')
            document.body.style.overflow = 'hidden'
        }
        
        function closeAuthModal() {
            modalOverlay.classList.remove('active')
            authModal.classList.remove('active')
            document.body.style.overflow = 'auto'
        }
        
        authTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.getAttribute('data-tab')
                authTabs.forEach(t => t.classList.remove('active'))
                tab.classList.add('active')
                
                document.querySelectorAll('.auth-form').forEach(form => {
                    form.classList.remove('active')
                    if (form.id === `${tabName}Form`) {
                        form.classList.add('active')
                    }
                })
            })
        })
        
        if (sidebarLoginBtn) sidebarLoginBtn.addEventListener('click', openAuthModal)
        if (heroLoginBtn) heroLoginBtn.addEventListener('click', openAuthModal)
        
        if (modalCloseBtn) modalCloseBtn.addEventListener('click', closeAuthModal)
        if (modalOverlay) modalOverlay.addEventListener('click', closeAuthModal)
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && authModal.classList.contains('active')) {
                closeAuthModal()
            }
        })
        
        const registerForm = document.getElementById('registerForm')
        if (registerForm) {
            registerForm.addEventListener('submit', async function(e) {
                e.preventDefault()
                
                const email = document.getElementById('regEmail').value
                const password = document.getElementById('regPassword').value
                const confirmPassword = document.getElementById('confirmPassword').value
                const fullName = document.getElementById('regName').value
                
                if (!email || !password || !confirmPassword) {
                    notify('Заполните все поля', 'error')
                    return
                }
                
                if (password !== confirmPassword) {
                    notify('Пароли не совпадают', 'error')
                    return
                }
                
                if (password.length < 8) {
                    notify('Пароль минимум 8 символов', 'error')
                    return
                }
                
                const submitBtn = this.querySelector('.auth-submit-btn')
                const originalText = submitBtn.textContent
                submitBtn.textContent = 'Регистрация...'
                submitBtn.disabled = true
                
                try {
                    const userData = {
                        email: email,
                        password: password,
                        full_name: fullName || ''
                    }
                    
                    const result = await api.register(userData)
                    notify('Регистрация успешна!', 'success')
                    
                    document.querySelector('[data-tab="login"]').click()
                    
                    document.getElementById('email').value = email
                    document.getElementById('password').value = ''
                    
                } catch (error) {
                    notify(error.message || 'Ошибка регистрации', 'error')
                } finally {
                    submitBtn.textContent = originalText
                    submitBtn.disabled = false
                }
            })
        }
        
        const loginForm = document.getElementById('loginForm')
        if (loginForm) {
            loginForm.addEventListener('submit', async function(e) {
                e.preventDefault()
                
                const email = document.getElementById('email').value
                const password = document.getElementById('password').value
                
                if (!email || !password) {
                    notify('Заполните все поля', 'error')
                    return
                }
                
                const submitBtn = this.querySelector('.auth-submit-btn')
                const originalText = submitBtn.textContent
                submitBtn.textContent = 'Вход...'
                submitBtn.disabled = true
                
                try {
                    const result = await api.login(email, password)
                    notify('Вход успешен!', 'success')
                    closeAuthModal()
                    
                    updateUIForLoggedInUser(api.user)
                    
                    setTimeout(() => {
                        window.location.href = '/dashboard'
                    }, 1000)
                    
                } catch (error) {
                    notify(error.message || 'Ошибка входа', 'error')
                } finally {
                    submitBtn.textContent = originalText
                    submitBtn.disabled = false
                }
            })
        }
    }
    
    async function checkAuthStatus() {
        try {
            const user = await api.getCurrentUser()
            if (user) {
                updateUIForLoggedInUser(user)
            }
        } catch (error) {
            // not authenticated
        }
    }
    
    function updateUIForLoggedInUser(user) {
        const heroLoginBtn = document.getElementById('heroLoginBtn')
        const sidebarLoginBtn = document.getElementById('sidebarLoginBtn')
        
        if (heroLoginBtn) {
            heroLoginBtn.textContent = 'Мой кабинет'
            heroLoginBtn.onclick = () => window.location.href = '/dashboard'
        }
        
        if (sidebarLoginBtn) {
            sidebarLoginBtn.textContent = 'Мой кабинет'
            sidebarLoginBtn.onclick = () => {
                window.location.href = '/dashboard'
            }
        }
        
        const sidebarNav = document.querySelector('.sidebar-nav')
        if (sidebarNav && !document.querySelector('.logout-btn')) {
            const logoutBtn = document.createElement('a')
            logoutBtn.href = '#'
            logoutBtn.className = 'logout-btn'
            logoutBtn.innerHTML = '<i class="fas fa-sign-out-alt"></i> Выйти'
            logoutBtn.addEventListener('click', (e) => {
                e.preventDefault()
                api.logout()
            })
            sidebarNav.appendChild(logoutBtn)
        }
    }
})