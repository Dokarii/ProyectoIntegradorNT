/**
 * JavaScript principal para la Plataforma de Bienestar Emocional
 * Funcionalidades interactivas y mejoras de UX
 */

// Configuración global
const CONFIG = {
    API_BASE_URL: '/api',
    ANIMATION_DURATION: 300,
    TOAST_DURATION: 5000
};

// Utilidades generales
const Utils = {
    // Mostrar notificaciones toast
    showToast: function(message, type = 'info') {
        const toastContainer = document.getElementById('toast-container') || this.createToastContainer();
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${this.getToastIcon(type)}"></i> ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;
        
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: true,
            delay: CONFIG.TOAST_DURATION
        });
        
        bsToast.show();
        
        // Remover el toast del DOM después de que se oculte
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    },
    
    // Crear contenedor de toasts si no existe
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        container.style.zIndex = '9999';
        document.body.appendChild(container);
        return container;
    },
    
    // Obtener icono para toast según el tipo
    getToastIcon: function(type) {
        const icons = {
            'success': 'check-circle',
            'danger': 'exclamation-triangle',
            'warning': 'exclamation-circle',
            'info': 'info-circle'
        };
        return icons[type] || 'info-circle';
    },
    
    // Validar email
    validateEmail: function(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },
    
    // Formatear fecha
    formatDate: function(date) {
        return new Intl.DateTimeFormat('es-ES', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        }).format(new Date(date));
    },
    
    // Debounce para optimizar eventos
    debounce: function(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Manejo de formularios
const FormHandler = {
    // Inicializar validación de formularios
    initValidation: function() {
        const forms = document.querySelectorAll('.needs-validation');
        
        forms.forEach(form => {
            form.addEventListener('submit', (event) => {
                if (!form.checkValidity()) {
                    event.preventDefault();
                    event.stopPropagation();
                    this.showValidationErrors(form);
                }
                form.classList.add('was-validated');
            });
        });
    },
    
    // Mostrar errores de validación
    showValidationErrors: function(form) {
        const invalidFields = form.querySelectorAll(':invalid');
        if (invalidFields.length > 0) {
            invalidFields[0].focus();
            Utils.showToast('Por favor, corrige los errores en el formulario', 'danger');
        }
    },
    
    // Validación en tiempo real
    setupRealTimeValidation: function() {
        // Validación de username
        const usernameInputs = document.querySelectorAll('input[name="username"]');
        usernameInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce((e) => {
                this.validateUsername(e.target);
            }, 300));
        });
        
        // Validación de email
        const emailInputs = document.querySelectorAll('input[type="email"]');
        emailInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce((e) => {
                this.validateEmailField(e.target);
            }, 300));
        });
        
        // Validación de edad
        const ageInputs = document.querySelectorAll('input[name="age"]');
        ageInputs.forEach(input => {
            input.addEventListener('input', Utils.debounce((e) => {
                this.validateAge(e.target);
            }, 300));
        });
    },
    
    // Validar campo username
    validateUsername: function(input) {
        const value = input.value;
        const pattern = /^[a-zA-Z0-9_]+$/;
        const isValid = value.length >= 3 && value.length <= 20 && pattern.test(value);
        
        this.updateFieldValidation(input, isValid);
    },
    
    // Validar campo email
    validateEmailField: function(input) {
        const isValid = Utils.validateEmail(input.value);
        this.updateFieldValidation(input, isValid);
    },
    
    // Validar campo edad
    validateAge: function(input) {
        const value = parseInt(input.value);
        const isValid = value >= 13 && value <= 25;
        this.updateFieldValidation(input, isValid);
    },
    
    // Actualizar estado visual de validación
    updateFieldValidation: function(input, isValid) {
        input.classList.remove('is-valid', 'is-invalid');
        
        if (input.value.length > 0) {
            input.classList.add(isValid ? 'is-valid' : 'is-invalid');
        }
    }
};

// Manejo de estadísticas en tiempo real
const StatsManager = {
    // Cargar estadísticas
    loadStats: async function() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/stats`);
            
            if (!response.ok) {
                throw new Error('Error al cargar estadísticas');
            }
            
            const stats = await response.json();
            this.updateStatsDisplay(stats);
            
        } catch (error) {
            console.error('Error loading stats:', error);
            this.showStatsError();
        }
    },
    
    // Actualizar visualización de estadísticas
    updateStatsDisplay: function(stats) {
        const elements = {
            'total-users': stats.users,
            'total-responses': stats.responses,
            'total-surveys': stats.surveys
        };
        
        Object.entries(elements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                // Remover clases de spinner antes de animar
                element.classList.remove('spinner-custom');
                this.animateNumber(element, value);
            }
        });
    },
    
    // Animar números
    animateNumber: function(element, targetValue) {
        // Limpiar completamente el contenido HTML (incluyendo spinners)
        element.innerHTML = '';
        element.classList.remove('spinner-custom');
        
        const startValue = 0;
        const duration = 1000;
        const startTime = performance.now();
        
        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            const currentValue = Math.floor(startValue + (targetValue - startValue) * progress);
            element.textContent = currentValue.toLocaleString();
            
            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };
        
        requestAnimationFrame(animate);
    },
    
    // Mostrar error en estadísticas
    showStatsError: function() {
        const errorIcon = '<i class="fas fa-exclamation-triangle text-warning"></i>';
        
        ['total-users', 'total-responses', 'total-surveys'].forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.innerHTML = errorIcon;
            }
        });
    }
};

// Efectos visuales y animaciones
const AnimationManager = {
    // Inicializar animaciones
    init: function() {
        this.setupScrollAnimations();
        this.setupHoverEffects();
        this.setupLoadingAnimations();
    },
    
    // Animaciones al hacer scroll
    setupScrollAnimations: function() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in-up');
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        document.querySelectorAll('.card, .alert, .stat-item').forEach(el => {
            observer.observe(el);
        });
    },
    
    // Efectos hover mejorados
    setupHoverEffects: function() {
        document.querySelectorAll('.card').forEach(card => {
            card.addEventListener('mouseenter', () => {
                card.style.transform = 'translateY(-5px)';
            });
            
            card.addEventListener('mouseleave', () => {
                card.style.transform = 'translateY(0)';
            });
        });
    },
    
    // Animaciones de carga
    setupLoadingAnimations: function() {
        // Mostrar spinner mientras se cargan las estadísticas
        const statsElements = document.querySelectorAll('[id^="total-"]');
        statsElements.forEach(el => {
            if (el.innerHTML.includes('fa-spinner')) {
                el.classList.add('spinner-custom');
            }
        });
    }
};

// Manejo de temas (preparado para modo oscuro)
const ThemeManager = {
    // Detectar preferencia de tema
    detectTheme: function() {
        const savedTheme = localStorage.getItem('theme');
        const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
        
        return savedTheme || systemTheme;
    },
    
    // Aplicar tema
    applyTheme: function(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    },
    
    // Alternar tema
    toggleTheme: function() {
        const currentTheme = this.detectTheme();
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        this.applyTheme(newTheme);
    }
};

// Inicialización cuando el DOM está listo
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌐 Plataforma de Bienestar Emocional - Interfaz Web Cargada');
    
    // Inicializar componentes
    FormHandler.initValidation();
    FormHandler.setupRealTimeValidation();
    AnimationManager.init();
    
    // Cargar estadísticas si estamos en la página principal
    if (document.getElementById('total-users')) {
        StatsManager.loadStats();
        
        // Actualizar estadísticas cada 30 segundos
        setInterval(() => {
            StatsManager.loadStats();
        }, 30000);
    }
    
    // Aplicar tema detectado
    ThemeManager.applyTheme(ThemeManager.detectTheme());
    
    // Mostrar mensaje de bienvenida
    setTimeout(() => {
        if (window.location.pathname === '/') {
            Utils.showToast('¡Bienvenido a la Plataforma de Bienestar Emocional!', 'success');
        }
    }, 1000);
});

// Manejo de errores globales
window.addEventListener('error', function(e) {
    console.error('Error global:', e.error);
    Utils.showToast('Ha ocurrido un error inesperado', 'danger');
});

// Exportar utilidades para uso global
window.PlatformUtils = {
    Utils,
    FormHandler,
    StatsManager,
    AnimationManager,
    ThemeManager
};