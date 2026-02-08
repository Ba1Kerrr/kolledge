
    // JavaScript для новых фишек
    
    // Показ/скрытие кнопки "Наверх"
    const scrollToTopBtn = document.getElementById('scrollToTop');
    window.addEventListener('scroll', () => {
      if (window.pageYOffset > 300) {
        scrollToTopBtn.classList.add('visible');
      } else {
        scrollToTopBtn.classList.remove('visible');
      }
    });
    
    scrollToTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
    
    // Анимированные счетчики
    const counters = document.querySelectorAll('.counter-value');
    const speed = 200;
    
    const animateCounters = () => {
      counters.forEach(counter => {
        const target = +counter.getAttribute('data-target');
        const count = +counter.innerText;
        const increment = target / speed;
        
        if (count < target) {
          counter.innerText = Math.ceil(count + increment);
          setTimeout(animateCounters, 10);
        } else {
          counter.innerText = target.toLocaleString();
        }
      });
    };
    
    // Запуск счетчиков при прокрутке до них
    const observerOptions = {
      root: null,
      rootMargin: '0px',
      threshold: 0.3
    };
    
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          if (entry.target.classList.contains('counter-value') && entry.target.innerText === '0') {
            animateCounters();
          }
          
          // Анимация прогресс-баров
          if (entry.target.classList.contains('progress-fill')) {
            const width = entry.target.getAttribute('data-width');
            setTimeout(() => {
              entry.target.style.width = width + '%';
            }, 300);
          }
        }
      });
    }, observerOptions);
    
    // Наблюдение за элементами
    document.querySelectorAll('.counter-value').forEach(el => observer.observe(el));
    document.querySelectorAll('.progress-fill').forEach(el => observer.observe(el));
    
    // Плавная прокрутка для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function(e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const targetElement = document.querySelector(targetId);
        if (targetElement) {
          window.scrollTo({
            top: targetElement.offsetTop - 80,
            behavior: 'smooth'
          });
        }
      });
    });
    
    // Инициализация при загрузке
    document.addEventListener('DOMContentLoaded', () => {
      // Запуск начальных анимаций
      setTimeout(() => {
        document.querySelectorAll('.interactive-card').forEach(card => {
          card.style.opacity = '1';
          card.style.transform = 'translateY(0)';
        });
      }, 500);
    });