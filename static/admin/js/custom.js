// Кастомный JavaScript для админки Hart Citizens

document.addEventListener('DOMContentLoaded', function() {
    // Инициализация функций
    initCustomFeatures();
    initTooltips();
    initAnimations();
    initExportFeatures();
});

// Основные кастомные функции
function initCustomFeatures() {
    // Добавляем индикатор загрузки для форм
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.value = 'Сохранение...';
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Сохранение...';
            }
        });
    });

    // Добавляем подтверждение для удаления
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Вы уверены, что хотите удалить этот элемент?')) {
                e.preventDefault();
            }
        });
    });

    // Добавляем подсветку для важных полей
    const importantFields = document.querySelectorAll('input[name*="email"], input[name*="name"]');
    importantFields.forEach(field => {
        field.addEventListener('focus', function() {
            this.style.borderColor = '#667eea';
            this.style.boxShadow = '0 0 0 0.2rem rgba(102, 126, 234, 0.25)';
        });
        
        field.addEventListener('blur', function() {
            this.style.borderColor = '';
            this.style.boxShadow = '';
        });
    });
}

// Инициализация тултипов
function initTooltips() {
    // Добавляем тултипы для иконок
    const icons = document.querySelectorAll('.fas, .far, .fab');
    icons.forEach(icon => {
        if (!icon.title) {
            const iconClass = icon.className;
            if (iconClass.includes('fa-crown')) {
                icon.title = 'Королевство';
            } else if (iconClass.includes('fa-user-tie')) {
                icon.title = 'Король';
            } else if (iconClass.includes('fa-user')) {
                icon.title = 'Подданный';
            } else if (iconClass.includes('fa-clipboard-check')) {
                icon.title = 'Тестовое испытание';
            } else if (iconClass.includes('fa-question-circle')) {
                icon.title = 'Вопрос';
            } else if (iconClass.includes('fa-history')) {
                icon.title = 'Лог действий';
            }
        }
    });
}

// Инициализация анимаций
function initAnimations() {
    // Анимация появления карточек
    const cards = document.querySelectorAll('.info-box, .card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'all 0.5s ease';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Анимация при наведении на строки таблицы
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
            this.style.transform = 'scale(1.01)';
            this.style.transition = 'all 0.2s ease';
        });
        
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
            this.style.transform = 'scale(1)';
        });
    });
}

// Функции для экспорта
function initExportFeatures() {
    // Добавляем кнопки быстрого экспорта
    const exportButtons = document.querySelectorAll('a[href*="export"]');
    exportButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const url = this.href;
            
            // Показываем индикатор загрузки
            const originalText = this.innerHTML;
            this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Экспорт...';
            this.disabled = true;
            
            // Создаем скрытую ссылку для скачивания
            const link = document.createElement('a');
            link.href = url;
            link.download = '';
            link.style.display = 'none';
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            // Восстанавливаем кнопку
            setTimeout(() => {
                this.innerHTML = originalText;
                this.disabled = false;
            }, 2000);
        });
    });
}

// Функция для показа уведомлений
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show`;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';
    notification.style.minWidth = '300px';
    
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(notification);
    
    // Автоматически скрываем через 5 секунд
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Функция для валидации форм
function validateForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.style.borderColor = '#dc3545';
            isValid = false;
        } else {
            field.style.borderColor = '';
        }
    });
    
    return isValid;
}

// Функция для форматирования дат
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Функция для подсчета статистики
function updateStats() {
    const statsElements = document.querySelectorAll('.stats-number');
    statsElements.forEach(element => {
        const targetValue = parseInt(element.textContent);
        let currentValue = 0;
        const increment = targetValue / 50;
        
        const timer = setInterval(() => {
            currentValue += increment;
            if (currentValue >= targetValue) {
                currentValue = targetValue;
                clearInterval(timer);
            }
            element.textContent = Math.floor(currentValue);
        }, 20);
    });
}

// Функция для поиска
function initSearch() {
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const rows = document.querySelectorAll('tbody tr');
            
            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                if (text.includes(searchTerm)) {
                    row.style.display = '';
                } else {
                    row.style.display = 'none';
                }
            });
        });
    }
}

// Функция для темной темы (если нужно)
function toggleDarkMode() {
    const body = document.body;
    const isDark = body.classList.contains('dark-mode');
    
    if (isDark) {
        body.classList.remove('dark-mode');
        localStorage.setItem('darkMode', 'false');
    } else {
        body.classList.add('dark-mode');
        localStorage.setItem('darkMode', 'true');
    }
}

// Загружаем сохраненную тему
function loadSavedTheme() {
    const savedTheme = localStorage.getItem('darkMode');
    if (savedTheme === 'true') {
        document.body.classList.add('dark-mode');
    }
}

// Инициализация при загрузке страницы
window.addEventListener('load', function() {
    loadSavedTheme();
    updateStats();
    initSearch();
    
    // Показываем приветственное сообщение
    if (window.location.pathname === '/admin/') {
        showNotification('Добро пожаловать в админку кадровой службы королевства!', 'success');
    }
});

// Обработка ошибок
window.addEventListener('error', function(e) {
    console.error('Ошибка в кастомном JavaScript:', e.error);
});

// Экспорт функций для использования в других скриптах
window.HartCitizensAdmin = {
    showNotification,
    validateForm,
    formatDate,
    toggleDarkMode
};
