$(document).ready(function() {
    // Employee dashboard initialization
});

function showNotification(message, type) {
    var $container = $('#notificationContainer');
    var bgClass = 'bg-primary';
    var icon = '🔔';
    
    switch(type) {
        case 'success':
            bgClass = 'bg-success';
            icon = '✅';
            break;
        case 'error':
            bgClass = 'bg-danger';
            icon = '❌';
            break;
        case 'warning':
            bgClass = 'bg-warning';
            icon = '⚠️';
            break;
    }
    
    var $notification = $('<div></div>', {
        'class': 'alert ' + bgClass + ' text-white alert-dismissible fade show shadow-lg',
        'css': {'min-width': '300px', 'margin-bottom': '10px'},
        'html': '<strong>' + icon + '</strong> ' + message +
                '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>'
    });
    
    $container.append($notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        $notification.alert('close');
    }, 5000);
}

function checkIn() {
    if (confirm('🕒 Check In Confirmation\n\nAre you sure you want to check in to NovaTech Corp. now?\n\nThis will record your arrival time.')) {
        // Disable button to prevent double clicks
        var $btn = $('#checkInBtn');
        if ($btn.length) {
            $btn.prop('disabled', true).text('Checking in...');
        }
        
        $.ajax({
            url: checkInUrl,
            type: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            contentType: 'application/json',
            success: function(data) {
                showNotification(data.message, data.type);
                if (data.success) {
                    setTimeout(function() { location.reload(); }, 2000);
                } else {
                    if ($btn.length) {
                        $btn.prop('disabled', false).text('Clock In');
                    }
                }
            },
            error: function() {
                showNotification('Network error occurred', 'error');
                if ($btn.length) {
                    $btn.prop('disabled', false).text('Clock In');
                }
            }
        });
    }
}

function checkOut() {
    if (confirm('🕐 Check Out Confirmation\n\nAre you sure you want to check out from NovaTech Corp. now?\n\nThis will record your departure time and end your work day.')) {
        // Disable button to prevent double clicks
        var $btn = $('#checkOutBtn');
        if ($btn.length) {
            $btn.prop('disabled', true).text('Checking out...');
        }
        
        $.ajax({
            url: checkOutUrl,
            type: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            contentType: 'application/json',
            success: function(data) {
                showNotification(data.message, data.type);
                if (data.success) {
                    setTimeout(function() { location.reload(); }, 2000);
                } else {
                    if ($btn.length) {
                        $btn.prop('disabled', false).text('Clock Out');
                    }
                }
            },
            error: function() {
                showNotification('Network error occurred', 'error');
                if ($btn.length) {
                    $btn.prop('disabled', false).text('Clock Out');
                }
            }
        });
    }
}
