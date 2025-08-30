// AJAX for liking posts
document.addEventListener('DOMContentLoaded', function() {
    // Like button functionality
    const likeButtons = document.querySelectorAll('.like-btn');
    likeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.dataset.postId;
            likePost(postId, this);
        });
    });

    // Follow button functionality
    const followButtons = document.querySelectorAll('.follow-btn');
    followButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            const form = this.closest('form');
            followUser(form);
        });
    });

    // Comment form submission with AJAX
    const commentForms = document.querySelectorAll('.comment-form');
    commentForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitComment(this);
        });
    });
});

function likePost(postId, button) {
    fetch(`/like_post/${postId}/`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.liked) {
            button.innerHTML = `❤️ Liked (<span class="likes-count">${data.likes_count}</span>)`;
        } else {
            button.innerHTML = `🤍 Like (<span class="likes-count">${data.likes_count}</span>)`;
        }
    })
    .catch(error => console.error('Error:', error));
}

function followUser(form) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const button = form.querySelector('.follow-btn');
        if (data.followed) {
            button.textContent = 'Unfollow';
        } else {
            button.textContent = 'Follow';
        }
        // Reload to update follower counts
        location.reload();
    })
    .catch(error => console.error('Error:', error));
}

function submitComment(form) {
    const formData = new FormData(form);
    
    fetch(form.action, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: formData
    })
    .then(response => {
        if (response.ok) {
            form.reset();
            // Reload to show new comment
            location.reload();
        }
    })
    .catch(error => console.error('Error:', error));
}

// Helper function to get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
