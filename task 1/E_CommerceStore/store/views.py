from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .models import Product, Cart, CartItem, Order, OrderItem
import json

def product_list(request):
    products = Product.objects.all()
    return render(request, 'store/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'store/product_detail.html', {'product': product})

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    total_price = cart.get_total_price()
    
    return render(request, 'store/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return JsonResponse({
        'success': True,
        'message': 'Product added to cart',
        'cart_item_count': cart.items.count()
    })

@require_POST
def update_cart_item(request, item_id):
    data = json.loads(request.body)
    quantity = data.get('quantity', 1)
    
    cart_item = get_object_or_404(CartItem, id=item_id)
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
    else:
        cart_item.delete()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'total_price': str(cart.get_total_price()),
        'item_total': str(cart_item.get_total_price())
    })

@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    
    cart = cart_item.cart
    return JsonResponse({
        'success': True,
        'total_price': str(cart.get_total_price()),
        'cart_item_count': cart.items.count()
    })

@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.all()
    
    if not cart_items:
        return redirect('cart')
    
    total_price = cart.get_total_price()
    
    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        
        # Create order
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            shipping_address=shipping_address
        )
        
        # Create order items
        for cart_item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
        
        # Clear cart
        cart_items.delete()
        
        return redirect('order_confirmation', order_id=order.id)
    
    return render(request, 'store/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_confirmation.html', {'order': order})
