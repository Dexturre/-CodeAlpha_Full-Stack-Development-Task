document.addEventListener('DOMContentLoaded', () => {
    // Add to cart buttons
    document.querySelectorAll('.add-to-cart').forEach(button => {
        button.addEventListener('click', () => {
            const productId = button.getAttribute('data-product-id');
            fetch(`/cart/add/${productId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Product added to cart');
                } else {
                    alert('Failed to add product to cart');
                }
            });
        });
    });

    // Update cart item quantity
    document.querySelectorAll('.update-item').forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const itemId = row.getAttribute('data-item-id');
            const quantityInput = row.querySelector('.quantity-input');
            const quantity = parseInt(quantityInput.value);

            fetch(`/cart/update/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ quantity }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    row.querySelector('.item-total').textContent = `$${data.item_total}`;
                    document.querySelector('.cart-total').textContent = `Total: $${data.total_price}`;
                } else {
                    alert('Failed to update cart item');
                }
            });
        });
    });

    // Remove cart item
    document.querySelectorAll('.remove-item').forEach(button => {
        button.addEventListener('click', () => {
            const row = button.closest('tr');
            const itemId = row.getAttribute('data-item-id');

            fetch(`/cart/remove/${itemId}/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    row.remove();
                    document.querySelector('.cart-total').textContent = `Total: $${data.total_price}`;
                } else {
                    alert('Failed to remove cart item');
                }
            });
        });
    });

    // Helper function to get CSRF token cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
