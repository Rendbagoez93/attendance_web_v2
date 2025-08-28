/**
 * Login page specific JavaScript functionality using jQuery
 */

$(document).ready(function() {
    console.log('Login.js loaded successfully!');
    
    // Initialize login page
    initLoginPage();
    
    // Form validation and enhancement
    enhanceLoginForm();
    
    // Demo credentials functionality
    initDemoCredentials();
    
});

function initLoginPage() {
    
    // Add entrance animation to login card
    $('.card').hide().fadeIn(800);
    
    // Focus on username field
    $('#username').focus();
    
    // Add typing effect to company name
    animateCompanyName();
    
    // Update current time
    updateCurrentTime();
    setInterval(updateCurrentTime, 1000);
    
}

function enhanceLoginForm() {
    
    // Real-time form validation
    $('#username, #password').on('input', function() {
        validateField($(this));
    });
    
    // Enhanced form submission - use normal form submission but with validation
    $('#loginForm').on('submit', function(e) {
        if (!validateForm()) {
            e.preventDefault();
            return false;
        }
        
        // Form is valid, show loading state and submit normally
        const submitBtn = $(this).find('button[type="submit"]');
        const originalText = submitBtn.html();
        
        submitBtn.prop('disabled', true);
        submitBtn.html('<i class="fas fa-spinner fa-spin"></i> Signing In...');
        
        // Save username if remember is checked
        if ($('#rememberUsername').is(':checked')) {
            localStorage.setItem('rememberedUsername', $('#username').val());
        }
        
        // Let the form submit normally
        return true;
    });
    
    // Show/hide password functionality
    addPasswordToggle();
    
    // Remember username functionality
    loadRememberedUsername();
    
}

function validateField(field) {
    const value = field.val().trim();
    const fieldGroup = field.closest('.mb-3');
    
    // Remove previous validation states
    fieldGroup.removeClass('has-error has-success');
    fieldGroup.find('.field-error').remove();
    
    if (value.length === 0) {
        field.removeClass('is-valid is-invalid');
    } else {
        fieldGroup.addClass('has-success');
        field.removeClass('is-invalid').addClass('is-valid');
    }
}

function validateForm() {
    const username = $('#username').val().trim();
    const password = $('#password').val().trim();
    
    let isValid = true;
    
    if (username.length === 0) {
        showFieldError('#username', 'Username is required');
        isValid = false;
    }
    
    if (password.length === 0) {
        showFieldError('#password', 'Password is required');
        isValid = false;
    }
    
    return isValid;
}

function showFieldError(fieldSelector, message) {
    const field = $(fieldSelector);
    const fieldGroup = field.closest('.mb-3');
    
    field.addClass('is-invalid');
    fieldGroup.append(`<div class="field-error text-danger small mt-1">${message}</div>`);
}

function addPasswordToggle() {
    const passwordField = $('#password');
    const passwordGroup = passwordField.closest('.input-group');
    
    // Create toggle button with proper styling to match the input
    const toggleButton = $(`
        <button type="button" class="btn password-toggle" 
                style="border: 2px solid #e9ecef; border-left: none; border-radius: 0 12px 12px 0; background: #f8f9fa; color: #6c757d;">
            <i class="fas fa-eye"></i>
        </button>
    `);
    
    // Add the toggle button to the input group
    passwordGroup.append(toggleButton);
    
    // Update password field styling to remove right border radius
    passwordField.css('border-radius', '0');
    
    // Handle toggle functionality
    toggleButton.on('click', function() {
        const type = passwordField.attr('type') === 'password' ? 'text' : 'password';
        passwordField.attr('type', type);
        
        const icon = $(this).find('i');
        icon.toggleClass('fa-eye fa-eye-slash');
        
        // Update button styling on hover/focus
        $(this).on('mouseenter', function() {
            $(this).css({
                'background': '#e9ecef',
                'color': '#495057'
            });
        }).on('mouseleave', function() {
            $(this).css({
                'background': '#f8f9fa',
                'color': '#6c757d'
            });
        });
    });
}

function initDemoCredentials() {
    console.log('initDemoCredentials called');
    const credentialItems = $('.credential-item');
    console.log('Found credential items:', credentialItems.length);
    
    credentialItems.on('click', function() {
        console.log('Credential item clicked');
        const username = $(this).data('username');
        const password = $(this).data('password');
        
        console.log('Username:', username, 'Password:', password);
        
        // Fill in the login form
        $('#username').val(username).trigger('input');
        $('#password').val(password).trigger('input');
        
        // Add visual feedback
        $(this).addClass('bg-success text-white');
        setTimeout(() => {
            $(this).removeClass('bg-success text-white');
        }, 1000);
        
        // Show notification if notification system is available
        if (typeof showNotification === 'function') {
            showNotification('Demo credentials filled!', 'success');
        } else {
            // Fallback notification
            const notification = $('<div class="alert alert-success alert-dismissible fade show" style="position: fixed; top: 20px; right: 20px; z-index: 9999; min-width: 250px;">' +
                '<strong>✅</strong> Demo credentials filled!' +
                '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                '</div>');
            $('body').append(notification);
            setTimeout(() => notification.alert('close'), 3000);
        }
        
        // Focus on the submit button
        $('.login-btn').focus();
    });
    
    // Add hover effect
    credentialItems.hover(
        function() {
            $(this).addClass('shadow-sm').css('transform', 'translateX(5px)');
        },
        function() {
            $(this).removeClass('shadow-sm').css('transform', 'translateX(0px)');
        }
    );
}

function animateCompanyName() {
    const companyName = $('.company-name');
    const text = companyName.text();
    companyName.text('');
    
    let i = 0;
    const typeEffect = setInterval(function() {
        companyName.text(text.substring(0, i + 1));
        i++;
        
        if (i === text.length) {
            clearInterval(typeEffect);
        }
    }, 100);
}

function updateCurrentTime() {
    console.log('updateCurrentTime called');
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    
    const dayString = now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Update the time element if it exists
    const timeElement = $('#currentTime');
    console.log('Time element found:', timeElement.length);
    if (timeElement.length > 0) {
        const content = `${dayString}<br><span style="font-weight: 600; color: #fff;">${timeString}</span>`;
        console.log('Setting time content:', content);
        timeElement.html(content);
    } else {
        console.log('Time element not found');
    }
}

function loadRememberedUsername() {
    const rememberedUsername = localStorage.getItem('rememberedUsername');
    if (rememberedUsername) {
        $('#username').val(rememberedUsername);
        
        // Add remember checkbox if not exists
        if ($('#rememberUsername').length === 0) {
            const checkboxHtml = `
                <div class="mb-3 form-check">
                    <input type="checkbox" class="form-check-input" id="rememberUsername" checked>
                    <label class="form-check-label" for="rememberUsername">
                        Remember username
                    </label>
                </div>
            `;
            $('#password').closest('.mb-3').after(checkboxHtml);
        }
    }
}
