/**
 * Dashboard specific JavaScript functionality using jQuery
 * Handles check-in, check-out, and real-time updates
 */

$(document).ready(function() {
    
    // Initialize dashboard functionality
    initDashboard();
    
    // Real-time clock
    updateClock();
    setInterval(updateClock, 1000);
    
    // Check-in/Check-out handlers
    setupAttendanceHandlers();
    
    // Auto-refresh attendance status
    setInterval(refreshAttendanceStatus, 30000); // Every 30 seconds
    
});

function initDashboard() {
    
    // Add loading states to cards
    $('.dashboard-card').addClass('fade-in');
    
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Add click animations to cards
    $('.dashboard-card').on('click', function() {
        $(this).addClass('pulse');
        setTimeout(() => {
            $(this).removeClass('pulse');
        }, 200);
    });
    
    // Show current attendance status
    checkCurrentAttendanceStatus();
    
}

function updateClock() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    
    const dateString = now.toLocaleDateString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
    
    // Update clock if exists
    if ($('#currentClock').length === 0) {
        // Add clock to dashboard
        $('.container').prepend(`
            <div id="currentClock" class="alert alert-info text-center mb-4">
                <h5 class="mb-1">${timeString}</h5>
                <small>${dateString}</small>
            </div>
        `);
    } else {
        $('#currentClock h5').text(timeString);
        $('#currentClock small').text(dateString);
    }
}

function setupAttendanceHandlers() {
    
    // Check-in button handler
    $(document).on('click', '.check-in-btn', function(e) {
        e.preventDefault();
        handleCheckIn();
    });
    
    // Check-out button handler
    $(document).on('click', '.check-out-btn', function(e) {
        e.preventDefault();
        handleCheckOut();
    });
    
}

function handleCheckIn() {
    const button = $('.check-in-btn');
    const originalText = button.html();
    
    // Show loading state
    button.prop('disabled', true);
    button.html('<i class="fas fa-spinner fa-spin"></i> Checking In...');
    
    $.ajax({
        url: '/check-in/',
        method: 'POST',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                AttendanceUtils.showNotification(response.message, response.type);
                
                // Update UI
                updateAttendanceUI('checked-in', response);
                
                // Disable check-in button
                button.removeClass('btn-success').addClass('btn-secondary');
                button.html('<i class="fas fa-check"></i> Checked In');
                
                // Enable check-out button
                $('.check-out-btn').prop('disabled', false);
                
            } else {
                AttendanceUtils.showNotification(response.message, response.type);
            }
        },
        error: function(xhr) {
            AttendanceUtils.handleAjaxError(xhr);
        },
        complete: function() {
            if (!$('.check-in-btn').hasClass('btn-secondary')) {
                button.prop('disabled', false);
                button.html(originalText);
            }
        }
    });
}

function handleCheckOut() {
    const button = $('.check-out-btn');
    const originalText = button.html();
    
    // Show loading state
    button.prop('disabled', true);
    button.html('<i class="fas fa-spinner fa-spin"></i> Checking Out...');
    
    $.ajax({
        url: '/check-out/',
        method: 'POST',
        headers: {
            'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                AttendanceUtils.showNotification(response.message, response.type);
                
                // Update UI
                updateAttendanceUI('checked-out', response);
                
                // Update button
                button.removeClass('btn-danger').addClass('btn-secondary');
                button.html('<i class="fas fa-check"></i> Checked Out');
                
            } else {
                AttendanceUtils.showNotification(response.message, response.type);
            }
        },
        error: function(xhr) {
            AttendanceUtils.handleAjaxError(xhr);
        },
        complete: function() {
            if (!$('.check-out-btn').hasClass('btn-secondary')) {
                button.prop('disabled', false);
                button.html(originalText);
            }
        }
    });
}

function updateAttendanceUI(action, response) {
    const attendanceCard = $('.attendance-card');
    
    if (action === 'checked-in') {
        attendanceCard.find('.check-in-time').text(AttendanceUtils.formatTime(new Date().toTimeString().slice(0, 5)));
        attendanceCard.find('.status').text(response.status === 'late' ? 'Late' : 'Present');
        
        if (response.status === 'late') {
            attendanceCard.removeClass('border-success').addClass('border-warning');
        } else {
            attendanceCard.removeClass('border-warning').addClass('border-success');
        }
        
    } else if (action === 'checked-out') {
        attendanceCard.find('.check-out-time').text(AttendanceUtils.formatTime(new Date().toTimeString().slice(0, 5)));
        
        if (response.work_duration) {
            attendanceCard.find('.work-duration').text(response.work_duration);
        }
    }
}

function checkCurrentAttendanceStatus() {
    // Check if attendance buttons need to be disabled based on current status
    const hasCheckedIn = $('.attendance-card .check-in-time').text().trim() !== '-';
    const hasCheckedOut = $('.attendance-card .check-out-time').text().trim() !== '-';
    
    if (hasCheckedIn) {
        $('.check-in-btn').prop('disabled', true)
                          .removeClass('btn-success')
                          .addClass('btn-secondary')
                          .html('<i class="fas fa-check"></i> Checked In');
    }
    
    if (hasCheckedOut) {
        $('.check-out-btn').prop('disabled', true)
                           .removeClass('btn-danger')
                           .addClass('btn-secondary')
                           .html('<i class="fas fa-check"></i> Checked Out');
    }
    
    // Enable check-out only if checked in but not checked out
    if (hasCheckedIn && !hasCheckedOut) {
        $('.check-out-btn').prop('disabled', false);
    }
}

function refreshAttendanceStatus() {
    // Refresh attendance data periodically
    $.ajax({
        url: window.location.href,
        method: 'GET',
        success: function(data) {
            // Update attendance information from response
            const parser = new DOMParser();
            const doc = parser.parseFromString(data, 'text/html');
            
            // Update attendance card content
            const newAttendanceCard = $(doc).find('.attendance-card');
            if (newAttendanceCard.length > 0) {
                $('.attendance-card').html(newAttendanceCard.html());
                checkCurrentAttendanceStatus();
            }
        },
        error: function() {
            // Silently fail for auto-refresh
        }
    });
}

// Add pulse animation class
const pulseCSS = `
    .pulse {
        animation: pulse-animation 0.2s ease-in-out;
    }
    
    @keyframes pulse-animation {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
`;

// Inject pulse CSS
if (!$('#pulseCSS').length) {
    $('<style id="pulseCSS">').text(pulseCSS).appendTo('head');
}
