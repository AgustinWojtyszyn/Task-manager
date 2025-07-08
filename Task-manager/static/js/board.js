// Board-specific JavaScript for drag and drop functionality

$(document).ready(function() {
    initializeDragAndDrop();
    initializeQuickActions();
    initializeKeyboardShortcuts();
});

function initializeDragAndDrop() {
    // Make tasks draggable
    $('.task-card').each(function() {
        $(this).attr('draggable', true);
    });

    // Drag start event
    $(document).on('dragstart', '.task-card', function(e) {
        var taskId = $(this).data('task-id');
        e.originalEvent.dataTransfer.setData('text/plain', taskId);
        e.originalEvent.dataTransfer.effectAllowed = 'move';
        
        $(this).addClass('dragging');
        
        // Add visual feedback to drop zones
        $('.tasks-container').addClass('drop-zone');
        
        // Store original position for potential rollback
        $(this).data('original-list', $(this).closest('.tasks-container').attr('id'));
        $(this).data('original-position', $(this).index());
    });

    // Drag end event
    $(document).on('dragend', '.task-card', function(e) {
        $(this).removeClass('dragging');
        $('.tasks-container').removeClass('drop-zone drag-over');
    });

    // Drag over event for task containers
    $(document).on('dragover', '.tasks-container', function(e) {
        e.preventDefault();
        e.originalEvent.dataTransfer.dropEffect = 'move';
        $(this).addClass('drag-over');
    });

    // Drag leave event
    $(document).on('dragleave', '.tasks-container', function(e) {
        // Only remove drag-over if we're actually leaving the container
        if (!$(this)[0].contains(e.relatedTarget)) {
            $(this).removeClass('drag-over');
        }
    });

    // Drop event
    $(document).on('drop', '.tasks-container', function(e) {
        e.preventDefault();
        
        var taskId = e.originalEvent.dataTransfer.getData('text/plain');
        var taskElement = $('.task-card[data-task-id="' + taskId + '"]');
        var newListContainer = $(this);
        var newListId = newListContainer.attr('id').split('-')[1];
        
        // Remove visual feedback
        $(this).removeClass('drag-over');
        $('.tasks-container').removeClass('drop-zone');
        
        // Calculate new position
        var newPosition = calculateDropPosition(e, newListContainer);
        
        // Move task in DOM immediately for better UX
        moveTaskInDOM(taskElement, newListContainer, newPosition);
        
        // Send AJAX request to update backend
        updateTaskPosition(taskId, newListId, newPosition);
    });
}

function calculateDropPosition(event, container) {
    var tasks = container.find('.task-card:not(.dragging)');
    var mouseY = event.originalEvent.clientY;
    var position = tasks.length;
    
    tasks.each(function(index) {
        var taskRect = this.getBoundingClientRect();
        var taskMiddle = taskRect.top + (taskRect.height / 2);
        
        if (mouseY < taskMiddle) {
            position = index;
            return false; // Break the loop
        }
    });
    
    return position;
}

function moveTaskInDOM(taskElement, newContainer, position) {
    var tasks = newContainer.find('.task-card');
    
    if (position >= tasks.length) {
        newContainer.append(taskElement);
    } else {
        taskElement.insertBefore(tasks.eq(position));
    }
    
    // Add animation
    taskElement.hide().fadeIn(300);
}

function updateTaskPosition(taskId, newListId, newPosition) {
    // Show loading indicator
    var taskElement = $('.task-card[data-task-id="' + taskId + '"]');
    var originalContent = taskElement.html();
    
    $.ajax({
        url: '/tasks/' + taskId + '/move/',
        method: 'POST',
        data: {
            'new_list_id': newListId,
            'new_position': newPosition,
            'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
        },
        success: function(response) {
            if (response.success) {
                // Show success feedback
                taskElement.addClass('move-success');
                setTimeout(function() {
                    taskElement.removeClass('move-success');
                }, 1000);
                
                // Update task counts
                updateTaskCounts();
            } else {
                handleMoveError(taskElement, response.error);
            }
        },
        error: function(xhr, status, error) {
            handleMoveError(taskElement, 'Error de conexión');
        }
    });
}

function handleMoveError(taskElement, errorMessage) {
    // Revert the move
    var originalList = $('#' + taskElement.data('original-list'));
    var originalPosition = taskElement.data('original-position');
    
    if (originalList.length) {
        var tasks = originalList.find('.task-card');
        if (originalPosition >= tasks.length) {
            originalList.append(taskElement);
        } else {
            taskElement.insertBefore(tasks.eq(originalPosition));
        }
    }
    
    // Show error message
    showNotification('Error al mover la tarea: ' + errorMessage, 'danger');
    
    // Add error animation
    taskElement.addClass('move-error');
    setTimeout(function() {
        taskElement.removeClass('move-error');
    }, 1000);
}

function updateTaskCounts() {
    $('.task-list').each(function() {
        var listId = $(this).data('list-id');
        var taskCount = $(this).find('.task-card').length;
        $(this).find('.task-count').text(taskCount);
    });
}

function initializeQuickActions() {
    // Quick task creation
    $(document).on('submit', '.quick-task-form', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var listId = form.data('list-id');
        var title = form.find('input[name="title"]').val().trim();
        var submitBtn = form.find('button[type="submit"]');
        
        if (!title) {
            form.find('input[name="title"]').focus();
            return;
        }
        
        // Show loading state
        var originalBtnContent = submitBtn.html();
        submitBtn.prop('disabled', true).html('<span class="loading"></span>');
        
        $.ajax({
            url: '/lists/' + listId + '/tasks/quick-create/',
            method: 'POST',
            data: {
                'title': title,
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Add new task to DOM
                    addTaskToDOM(response.task, listId);
                    
                    // Clear form
                    form.find('input[name="title"]').val('');
                    
                    // Show success message
                    showNotification('Tarea creada exitosamente', 'success');
                } else {
                    showNotification('Error al crear la tarea', 'danger');
                }
            },
            error: function() {
                showNotification('Error de conexión', 'danger');
            },
            complete: function() {
                // Reset button state
                submitBtn.prop('disabled', false).html(originalBtnContent);
            }
        });
    });

    // Quick task completion toggle
    $(document).on('click', '.quick-complete', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var taskId = $(this).data('task-id');
        var taskCard = $(this).closest('.task-card');
        
        $.ajax({
            url: '/tasks/' + taskId + '/toggle-complete/',
            method: 'POST',
            data: {
                'csrfmiddlewaretoken': $('[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                if (response.success) {
                    // Update UI based on completion status
                    if (response.completed) {
                        taskCard.addClass('completed');
                        $(this).html('<i class="fas fa-undo"></i>');
                    } else {
                        taskCard.removeClass('completed');
                        $(this).html('<i class="fas fa-check"></i>');
                    }
                }
            },
            error: function() {
                showNotification('Error al actualizar la tarea', 'danger');
            }
        });
    });
}

function addTaskToDOM(task, listId) {
    var taskHtml = `
        <div class="task-card mb-2" draggable="true" data-task-id="${task.id}">
            <div class="card task-item">
                <div class="card-body p-3">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <h6 class="card-title mb-1">
                            <a href="/tasks/${task.id}/" class="text-decoration-none">
                                ${task.title}
                            </a>
                        </h6>
                        <span class="badge bg-${task.priority_color}">
                            ${task.priority}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    var container = $('#tasks-' + listId);
    container.append(taskHtml);
    
    // Animate the new task
    var newTask = container.find('.task-card').last();
    newTask.hide().slideDown(300);
    
    // Make it draggable
    newTask.attr('draggable', true);
}

function initializeKeyboardShortcuts() {
    $(document).on('keydown', function(e) {
        // Only handle shortcuts when not in input fields
        if ($(e.target).is('input, textarea, select')) {
            return;
        }
        
        switch(e.key) {
            case 'n':
                // Create new task (focus on first quick-add form)
                e.preventDefault();
                $('.quick-task-form input[name="title"]').first().focus();
                break;
                
            case 'l':
                // Create new list
                e.preventDefault();
                $('input[name="name"]').last().focus();
                break;
                
            case 'f':
                // Focus search
                e.preventDefault();
                $('input[name="q"]').focus();
                break;
                
            case 'Escape':
                // Clear focus and close any open forms
                e.preventDefault();
                $(document.activeElement).blur();
                $('.quick-task-form').removeClass('show');
                break;
        }
    });
}

function showNotification(message, type = 'info') {
    var notification = $(`
        <div class="alert alert-${type} alert-dismissible fade show position-fixed" 
             style="top: 20px; right: 20px; z-index: 9999; min-width: 300px;" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `);
    
    $('body').append(notification);
    
    // Auto-remove after 5 seconds
    setTimeout(function() {
        notification.fadeOut(function() {
            $(this).remove();
        });
    }, 5000);
}

// Touch support for mobile devices
function initializeTouchSupport() {
    var touchStartY = 0;
    var touchStartX = 0;
    var isDragging = false;
    var draggedElement = null;
    
    $(document).on('touchstart', '.task-card', function(e) {
        touchStartY = e.originalEvent.touches[0].clientY;
        touchStartX = e.originalEvent.touches[0].clientX;
        draggedElement = $(this);
        isDragging = false;
    });
    
    $(document).on('touchmove', '.task-card', function(e) {
        if (!draggedElement) return;
        
        var touchY = e.originalEvent.touches[0].clientY;
        var touchX = e.originalEvent.touches[0].clientX;
        var deltaY = Math.abs(touchY - touchStartY);
        var deltaX = Math.abs(touchX - touchStartX);
        
        if (deltaY > 10 || deltaX > 10) {
            isDragging = true;
            e.preventDefault();
            
            // Add visual feedback
            draggedElement.addClass('dragging');
            
            // Move element with finger
            draggedElement.css({
                'position': 'fixed',
                'top': touchY - 50,
                'left': touchX - 150,
                'z-index': 1000,
                'transform': 'rotate(5deg)',
                'opacity': 0.8
            });
        }
    });
    
    $(document).on('touchend', '.task-card', function(e) {
        if (!isDragging || !draggedElement) {
            draggedElement = null;
            return;
        }
        
        var touchY = e.originalEvent.changedTouches[0].clientY;
        var touchX = e.originalEvent.changedTouches[0].clientX;
        
        // Find drop target
        var dropTarget = $(document.elementFromPoint(touchX, touchY)).closest('.tasks-container');
        
        if (dropTarget.length && dropTarget.attr('id') !== draggedElement.closest('.tasks-container').attr('id')) {
            // Perform the drop
            var taskId = draggedElement.data('task-id');
            var newListId = dropTarget.attr('id').split('-')[1];
            
            // Reset element styles
            draggedElement.css({
                'position': '',
                'top': '',
                'left': '',
                'z-index': '',
                'transform': '',
                'opacity': ''
            });
            
            // Move in DOM
            dropTarget.append(draggedElement);
            
            // Update backend
            updateTaskPosition(taskId, newListId, dropTarget.find('.task-card').length - 1);
        } else {
            // Reset element styles
            draggedElement.css({
                'position': '',
                'top': '',
                'left': '',
                'z-index': '',
                'transform': '',
                'opacity': ''
            });
        }
        
        draggedElement.removeClass('dragging');
        draggedElement = null;
        isDragging = false;
    });
}

// Initialize touch support on mobile devices
if ('ontouchstart' in window) {
    initializeTouchSupport();
}

// Auto-refresh board data every 30 seconds
setInterval(function() {
    // Only refresh if the page is visible
    if (!document.hidden) {
        refreshBoardData();
    }
}, 30000);

function refreshBoardData() {
    // This could be implemented to fetch updated task data via AJAX
    // For now, we'll just update timestamps
    $('.task-meta .small').each(function() {
        var text = $(this).text();
        if (text.includes('hace')) {
            // Update relative timestamps
            var timestamp = $(this).data('timestamp');
            if (timestamp) {
                $(this).text(formatRelativeTime(timestamp));
            }
        }
    });
}

function formatRelativeTime(timestamp) {
    var now = new Date();
    var time = new Date(timestamp);
    var diff = now - time;
    
    var minutes = Math.floor(diff / 60000);
    var hours = Math.floor(diff / 3600000);
    var days = Math.floor(diff / 86400000);
    
    if (minutes < 1) return 'hace un momento';
    if (minutes < 60) return `hace ${minutes} minuto${minutes > 1 ? 's' : ''}`;
    if (hours < 24) return `hace ${hours} hora${hours > 1 ? 's' : ''}`;
    return `hace ${days} día${days > 1 ? 's' : ''}`;
}

// Export functions for testing
window.BoardJS = {
    updateTaskPosition: updateTaskPosition,
    addTaskToDOM: addTaskToDOM,
    showNotification: showNotification
};
