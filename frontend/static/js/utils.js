window.notificationQueue = []
let notificationVisible = false

window.showNotification = function(message, type = 'info') {
    window.notificationQueue.push({ message, type })
    
    if (!notificationVisible) {
        showNextNotification()
    }
}

function showNextNotification() {
    if (window.notificationQueue.length === 0) {
        notificationVisible = false
        return
    }
    
    notificationVisible = true
    const { message, type } = window.notificationQueue.shift()
    
    const oldNotifications = document.querySelectorAll('.notification')
    oldNotifications.forEach(n => {
        n.classList.remove('show')
        setTimeout(() => { if (n.parentNode) n.remove() }, 300)
    })
    
    const notification = document.createElement('div')
    
    notification.style.cssText = `
        position: fixed !important
        top: 20px !important
        right: 20px !important
        background: white !important
        border-radius: 8px !important
        padding: 16px 20px !important
        min-width: 300px !important
        max-width: 400px !important
        z-index: 10000 !important
        opacity: 0 !important
        transform: translateY(-20px) !important
        transition: all 0.3s ease !important
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important
        display: flex !important
        justify-content: space-between !important
        align-items: center !important
        border-left: 4px solid ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'} !important
    `
    
    notification.className = `notification notification-${type}`
    
    let icon = 'info-circle'
    if (type === 'success') icon = 'check-circle'
    if (type === 'error') icon = 'exclamation-circle'
    
    notification.innerHTML = `
        <div class="notification-content" style="display: flex; align-items: center; gap: 10px;">
            <i class="fas fa-${icon}" style="font-size: 18px; color: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'}"></i>
            <span style="font-size: 14px; line-height: 1.4;">${message}</span>
        </div>
        <button class="notification-close" style="background: none; border: none; font-size: 20px; cursor: pointer; color: #666; padding: 0; margin-left: 10px; line-height: 1;">&times;</button>
    `
    
    document.body.appendChild(notification)
    
    setTimeout(() => {
        notification.style.opacity = '1'
        notification.style.transform = 'translateY(0)'
        notification.classList.add('show')
    }, 10)
    
    const autoHide = setTimeout(() => {
        hideNotification(notification)
        showNextNotification()
    }, 3000)
    
    const closeBtn = notification.querySelector('.notification-close')
    closeBtn.addEventListener('click', () => {
        clearTimeout(autoHide)
        hideNotification(notification)
        showNextNotification()
    })
    
    function hideNotification(notif) {
        notif.style.opacity = '0'
        notif.style.transform = 'translateY(-20px)'
        notif.classList.remove('show')
        setTimeout(() => { if (notif.parentNode) notif.remove() }, 300)
    }
}