document.addEventListener('DOMContentLoaded', function() {
    const menuBtn = document.getElementById('menuBtn')
    const closeBtn = document.getElementById('closeBtn')
    const overlay = document.getElementById('overlay')
    const sidebar = document.getElementById('sidebar')
    
    if (menuBtn && sidebar) {
        function openMenu() {
            sidebar.classList.add('open')
            if (overlay) overlay.classList.add('active')
            document.body.style.overflow = 'hidden'
        }
        
        function closeMenu() {
            sidebar.classList.remove('open')
            if (overlay) overlay.classList.remove('active')
            document.body.style.overflow = 'auto'
        }
        
        menuBtn.addEventListener('click', openMenu)
        if (closeBtn) closeBtn.addEventListener('click', closeMenu)
        if (overlay) overlay.addEventListener('click', closeMenu)
        
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && sidebar.classList.contains('open')) {
                closeMenu()
            }
        })
    }
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href')
            if (href === '#' || href.startsWith('#!')) return
            
            e.preventDefault()
            const targetElement = document.querySelector(href)
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                })
            }
        })
    })
})