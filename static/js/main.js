// Main JavaScript for Trello Clone

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Confirm delete actions
    $('.confirm-delete').on('click', function(e) {
        if (!confirm('¿Estás seguro de que quieres eliminar este elemento? Esta acción no se puede deshacer.')) {
            e.preventDefault();
        }
    });

    // Auto-resize textareas
    $('textarea').each(function() {
        this.setAttribute('style', 'height:' + (this.scrollHeight) + 'px;overflow-y:hidden;');
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Form validation
    $('form').on('submit', function() {
        var form = $(this);
        var submitBtn = form.find('button[type="submit"]');
        
        // Disable submit button to prevent double submission
        submitBtn.prop('disabled', true);
        
        // Add loading spinner
        var originalText = submitBtn.html();
        submitBtn.html('<span class="loading me-2"></span>Procesando...');
        
        // Re-enable after 3 seconds (in case of errors)
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.html(originalText);
        }, 3000);
    });

    // Search functionality
    $('#search-form').on('submit', function(e) {
        var query = $(this).find('input[name="q"]').val().trim();
        if (query.length < 2) {
            e.preventDefault();
            alert('Por favor, ingresa al menos 2 caracteres para buscar.');
        }
    });

    // Keyboard shortcuts
    $(document).on('keydown', function(e) {
        // Ctrl/Cmd + K for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            $('input[name="q"]').focus();
        }
        
        // Escape to close modals
        if (e.key === 'Escape') {
            $('.modal').modal('hide');
            $('.dropdown-menu').removeClass('show');
        }
    });

    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        var target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });

    // Copy to clipboard functionality
    $('.copy-to-clipboard').on('click', function() {
        var text = $(this).data('text');
        navigator.clipboard.writeText(text).then(function() {
            // Show success message
            var btn = $('.copy-to-clipboard');
            var originalText = btn.html();
            btn.html('<i class="fas fa-check me-2"></i>Copiado!');
            setTimeout(function() {
                btn.html(originalText);
            }, 2000);
        });
    });

    // Dynamic form fields
    $('.add-field').on('click', function() {
        var template = $(this).data('template');
        var container = $(this).data('container');
        $(container).append(template);
    });

    $('.remove-field').on('click', function() {
        $(this).closest('.field-group').remove();
    });

    // File upload preview
    $('input[type="file"]').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                var preview = $(this).siblings('.file-preview');
                if (file.type.startsWith('image/')) {
                    preview.html('<img src="' + e.target.result + '" class="img-thumbnail" style="max-width: 200px;">');
                } else {
                    preview.html('<p>Archivo seleccionado: ' + file.name + '</p>');
                }
            }.bind(this);
            reader.readAsDataURL(file);
        }
    });

    // Progress bars animation
    $('.progress-bar').each(function() {
        var width = $(this).data('width');
        $(this).animate({width: width + '%'}, 1000);
    });

    // Lazy loading for images
    if ('IntersectionObserver' in window) {
        var imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    var img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });

        document.querySelectorAll('img[data-src]').forEach(function(img) {
            imageObserver.observe(img);
        });
    }

    // Dark mode toggle
    $('.dark-mode-toggle').on('click', function() {
        $('body').toggleClass('dark-mode');
        var isDark = $('body').hasClass('dark-mode');
        localStorage.setItem('darkMode', isDark);
    });

    // Load dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        $('body').addClass('dark-mode');
    }

    // Print functionality
    $('.print-page').on('click', function() {
        window.print();
    });

    // Export functionality
    $('.export-data').on('click', function() {
        var format = $(this).data('format');
        var url = $(this).data('url');
        
        // Show loading state
        $(this).prop('disabled', true).html('<span class="loading me-2"></span>Exportando...');
        
        // Create download link
        var link = document.createElement('a');
        link.href = url;
        link.download = '';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        // Reset button state
        var btn = $(this);
        setTimeout(function() {
            btn.prop('disabled', false).html('<i class="fas fa-download me-2"></i>Exportar ' + format.toUpperCase());
        }, 2000);
    });

    // Auto-save functionality for forms
    var autoSaveTimeout;
    $('.auto-save').on('input', function() {
        clearTimeout(autoSaveTimeout);
        var form = $(this).closest('form');
        
        autoSaveTimeout = setTimeout(function() {
            // Show saving indicator
            $('.save-indicator').text('Guardando...').show();
            
            // Simulate auto-save (you can implement actual AJAX save here)
            setTimeout(function() {
                $('.save-indicator').text('Guardado').fadeOut(2000);
            }, 1000);
        }, 2000);
    });

    // Notification system
    function showNotification(message, type = 'info') {
        var notification = $('<div class="alert alert-' + type + ' alert-dismissible fade show notification" role="alert">' +
            message +
            '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
            '</div>');
        
        $('.notification-container').append(notification);
        
        setTimeout(function() {
            notification.fadeOut(function() {
                $(this).remove();
            });
        }, 5000);
    }

    // Global error handler
    window.addEventListener('error', function(e) {
        console.error('Error:', e.error);
        showNotification('Ha ocurrido un error inesperado. Por favor, recarga la página.', 'danger');
    });

    // AJAX setup
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", $('[name=csrfmiddlewaretoken]').val());
            }
        }
    });

    // Global AJAX error handler
    $(document).ajaxError(function(event, xhr, settings, error) {
        if (xhr.status === 403) {
            showNotification('No tienes permisos para realizar esta acción.', 'warning');
        } else if (xhr.status === 404) {
            showNotification('El recurso solicitado no fue encontrado.', 'warning');
        } else if (xhr.status >= 500) {
            showNotification('Error del servidor. Por favor, intenta nuevamente.', 'danger');
        } else {
            showNotification('Error de conexión. Verifica tu conexión a internet.', 'warning');
        }
    });

    // Performance monitoring
    if ('performance' in window) {
        window.addEventListener('load', function() {
            setTimeout(function() {
                var perfData = performance.getEntriesByType('navigation')[0];
                if (perfData.loadEventEnd - perfData.loadEventStart > 3000) {
                    console.warn('Página cargó lentamente:', perfData.loadEventEnd - perfData.loadEventStart + 'ms');
                }
            }, 0);
        });
    }

    // Service Worker registration (for PWA functionality)
    if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
            navigator.serviceWorker.register('/sw.js').then(function(registration) {
                console.log('SW registered: ', registration);
            }).catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
        });
    }
});

// Utility functions
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function formatDate(date) {
    return new Date(date).toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatTime(date) {
    return new Date(date).toLocaleTimeString('es-ES', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

function debounce(func, wait, immediate) {
    var timeout;
    return function() {
        var context = this, args = arguments;
        var later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        var callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

function throttle(func, limit) {
    var inThrottle;
    return function() {
        var args = arguments;
        var context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(function() {
                inThrottle = false;
            }, limit);
        }
    };
}

// Export functions for use in other scripts
window.TrelloClone = {
    getCookie: getCookie,
    formatDate: formatDate,
    formatTime: formatTime,
    debounce: debounce,
    throttle: throttle
};
