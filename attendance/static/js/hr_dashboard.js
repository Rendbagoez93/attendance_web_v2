
function showNotification(message, type) {
    var $container = $('#notificationContainer');
    var bgClass = 'bg-primary';
    var icon = '🔔';
    switch(type) {
        case 'success': bgClass = 'bg-success'; icon = '✅'; break;
        case 'error': bgClass = 'bg-danger'; icon = '❌'; break;
        case 'warning': bgClass = 'bg-warning'; icon = '⚠️'; break;
    }
    var $notification = $('<div></div>', {
        'class': 'alert ' + bgClass + ' text-white alert-dismissible fade show shadow-lg',
        'css': {'min-width': '300px', 'margin-bottom': '10px'},
        'html': '<strong>' + icon + '</strong> ' + message +
                '<button type="button" class="btn-close btn-close-white" data-bs-dismiss="alert"></button>'
    });
    $container.append($notification);
    setTimeout(function() {
        $notification.alert('close');
    }, 5000);
}

function checkIn() {
    if (confirm('🕒 HR Check In Confirmation\n\nAre you sure you want to check in to NovaTech Corp. now?\n\nThis will record your arrival time.')) {
        $.ajax({
            url: checkInUrl,
            type: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            contentType: 'application/json',
            success: function(data) {
                showNotification(data.message, data.type);
                if (data.success) {
                    setTimeout(function() { location.reload(); }, 2000);
                }
            },
            error: function() {
                showNotification('Network error occurred. Please try again.', 'error');
            }
        });
    }
}

function checkOut() {
    if (confirm('🕐 HR Check Out Confirmation\n\nAre you sure you want to check out from NovaTech Corp. now?\n\nThis will record your departure time and end your work day.')) {
        $.ajax({
            url: checkOutUrl,
            type: 'POST',
            headers: {'X-CSRFToken': csrfToken},
            contentType: 'application/json',
            success: function(data) {
                showNotification(data.message, data.type);
                if (data.success) {
                    setTimeout(function() { location.reload(); }, 2000);
                }
            },
            error: function() {
                showNotification('Network error occurred. Please try again.', 'error');
            }
        });
    }
}
