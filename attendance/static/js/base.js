/**
 * Base JavaScript functionality using jQuery
 * Common functions and utilities for the attendance system
 */

$(document).ready(function() {
    
    // Setup CSRF token for AJAX requests
    setupCSRFToken();
    
    // Initialize notification system
    initializeNotifications();
    
    // Auto-dismiss alerts after 5 seconds
    $('.alert').each(function() {
        const alert = $(this);
        setTimeout(function() {
            alert.fadeOut('slow');
        }, 5000);
    });
    
    // Add loading state to forms
    $('form').on('submit', function() {
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true);
        submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Processing...');
        
        // Re-enable after 10 seconds as fallback
        setTimeout(function() {
            submitBtn.prop('disabled', false);
            submitBtn.html(originalText);
        }, 10000);
    });
    
    // Smooth scrolling for anchor links
    $('a[href^="#"]').on('click', function(e) {
        e.preventDefault();
        const target = $(this.getAttribute('href'));
        if (target.length) {
            $('html, body').stop().animate({
                scrollTop: target.offset().top - 100
            }, 1000);
        }
    });
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in');
    
    // Tooltip initialization
    if ($.fn.tooltip) {
        $('[data-bs-toggle="tooltip"]').tooltip();
    }
    
    // Confirm dialogs for important actions
    $('.confirm-action').on('click', function(e) {
        const message = $(this).data('confirm') || 'Are you sure you want to perform this action?';
        if (!confirm(message)) {
            e.preventDefault();
            return false;
        }
    });
    
    // Add ripple effect to buttons
    $('.btn').on('click', function(e) {
        const button = $(this);
        const ripple = $('<span class="ripple"></span>');
        
        const size = Math.max(button.outerWidth(), button.outerHeight());
        const x = e.pageX - button.offset().left - size / 2;
        const y = e.pageY - button.offset().top - size / 2;
        
        ripple.css({
            width: size,
            height: size,
            left: x,
            top: y
        });
        
        button.append(ripple);
        
        setTimeout(function() {
            ripple.remove();
        }, 1000);
    });
    
});

/**
 * Setup CSRF token for all AJAX requests
 */
function setupCSRFToken() {
    // Get CSRF token from various possible sources
    const csrfToken = $('[name="csrfmiddlewaretoken"]').val() || 
                     $('meta[name="csrf-token"]').attr('content') ||
                     document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    
    if (csrfToken) {
        // Setup AJAX to send CSRF token with every request
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                    // Only send the token to relative URLs i.e. locally.
                    xhr.setRequestHeader("X-CSRFToken", csrfToken);
                }
            }
        });
    }
}

/**
 * Utility functions
 */
const AttendanceUtils = {
    
    // Show notification
    showNotification: function(message, type = 'info') {
        const alertClass = `alert-${type}`;
        const alert = $(`
            <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `);
        
        $('main .container').prepend(alert);
        
        // Auto-dismiss after 5 seconds
        setTimeout(function() {
            alert.fadeOut('slow');
        }, 5000);
    },
    
    // Format time
    formatTime: function(time) {
        return new Date('1970-01-01T' + time + 'Z').toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true
        });
    },
    
    // Get current time
    getCurrentTime: function() {
        return new Date().toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: true
        });
    },
    
    // AJAX error handler
    handleAjaxError: function(xhr, status, error) {
        let message = 'An error occurred. Please try again.';
        
        if (xhr.responseJSON && xhr.responseJSON.message) {
            message = xhr.responseJSON.message;
        } else if (xhr.responseText) {
            try {
                const response = JSON.parse(xhr.responseText);
                message = response.message || message;
            } catch (e) {
                // Use default message
            }
        }
        
        AttendanceUtils.showNotification(message, 'danger');
    }
};

/**
 * Notification System
 */
function initializeNotifications() {
    // Check for Django messages and show as notifications
    if (typeof djangoMessages !== 'undefined') {
        djangoMessages.forEach(function(message) {
            showNotification(message.message, message.tags);
        });
    }
}

function showNotification(message, type = 'info', duration = 5000) {
    const notificationContainer = document.getElementById('notificationContainer');
    if (!notificationContainer) return;

    // Map Django message types to Bootstrap alert types
    const typeMap = {
        'error': 'danger',
        'warning': 'warning',
        'success': 'success',
        'info': 'info',
        'debug': 'secondary'
    };
    
    const alertType = typeMap[type] || type;
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${alertType} alert-dismissible fade show`;
    notification.style.minWidth = '300px';
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(alertType)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to container
    notificationContainer.appendChild(notification);
    
    // Auto-remove after duration
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 150);
        }
    }, duration);
}

function getNotificationIcon(type) {
    const icons = {
        'success': 'check-circle',
        'danger': 'exclamation-triangle',
        'warning': 'exclamation-circle',
        'info': 'info-circle',
        'secondary': 'cog'
    };
    return icons[type] || 'info-circle';
}

/**
 * Confirmation System
 */
function showConfirmation(options) {
    const {
        title = 'Confirm Action',
        message = 'Are you sure you want to proceed?',
        confirmText = 'Confirm',
        cancelText = 'Cancel',
        type = 'warning',
        onConfirm = null,
        onCancel = null
    } = options;

    const modal = document.getElementById('confirmationModal');
    const titleElement = document.getElementById('confirmationTitle');
    const messageElement = document.getElementById('confirmationMessage');
    const confirmButton = document.getElementById('confirmButton');
    const iconElement = document.getElementById('confirmationIcon');

    // Set content
    titleElement.textContent = title;
    messageElement.textContent = message;
    confirmButton.textContent = confirmText;

    // Set icon and button style based on type
    const typeConfig = {
        'warning': { icon: 'fa-exclamation-triangle text-warning', btnClass: 'btn-warning' },
        'danger': { icon: 'fa-exclamation-circle text-danger', btnClass: 'btn-danger' },
        'info': { icon: 'fa-info-circle text-info', btnClass: 'btn-primary' },
        'success': { icon: 'fa-check-circle text-success', btnClass: 'btn-success' }
    };

    const config = typeConfig[type] || typeConfig.warning;
    iconElement.className = `fas ${config.icon} me-2`;
    confirmButton.className = `btn ${config.btnClass}`;

    // Remove any existing event listeners
    const newConfirmButton = confirmButton.cloneNode(true);
    confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);

    // Add new event listener
    newConfirmButton.addEventListener('click', function() {
        if (onConfirm) onConfirm();
        bootstrap.Modal.getInstance(modal).hide();
    });

    // Show modal
    new bootstrap.Modal(modal).show();
}

/**
 * Logout Confirmation
 */
function confirmLogout(event) {
    event.preventDefault();
    
    showConfirmation({
        title: 'Logout Confirmation',
        message: 'Are you sure you want to logout? You will need to login again to access the system.',
        confirmText: 'Logout',
        type: 'warning',
        onConfirm: function() {
            showNotification('Logging out...', 'info', 2000);
            setTimeout(() => {
                window.location.href = '/logout/';
            }, 500);
        }
    });
}

/**
 * Delete/Deactivate Confirmation
 */
function confirmDelete(element, itemName = 'item', action = 'delete') {
    const form = element.closest('form');
    
    showConfirmation({
        title: `${action.charAt(0).toUpperCase() + action.slice(1)} Confirmation`,
        message: `Are you sure you want to ${action} this ${itemName}? This action may affect related data.`,
        confirmText: action.charAt(0).toUpperCase() + action.slice(1),
        type: 'danger',
        onConfirm: function() {
            if (form) {
                form.submit();
            }
        }
    });
}

/**
 * Login Success Notification
 */
function showLoginSuccess(username) {
    showNotification(`Welcome back, ${username}! You have successfully logged in.`, 'success', 3000);
}
