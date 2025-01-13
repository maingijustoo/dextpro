from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Order, OrderItem, OrderStatusUpdate
from .forms import OrderForm, OrderSearchForm
from inventory.models import Product

@login_required
def order_list(request):
    # Search and filter functionality
    search_form = OrderSearchForm(request.GET)
    orders = Order.objects.filter(user=request.user)

    if search_form.is_valid():
        status = search_form.cleaned_data.get('status')
        start_date = search_form.cleaned_data.get('start_date')
        end_date = search_form.cleaned_data.get('end_date')

        if status:
            orders = orders.filter(status=status)
        
        if start_date:
            orders = orders.filter(order_date__gte=start_date)
        
        if end_date:
            orders = orders.filter(order_date__lte=end_date)

    # Pagination
    paginator = Paginator(orders, 10)  # 10 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'orders/order_list.html', {
        'page_obj': page_obj,
        'search_form': search_form
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    status_updates = OrderStatusUpdate.objects.filter(order=order).order_by('-update_date')
    
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'status_updates': status_updates
    })

@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            
            # Calculate total amount
            total_amount = 0
            selected_products = form.cleaned_data.get('products')
            
            if selected_products:
                for product_id, quantity in selected_products.items():
                    product = Product.objects.get(id=product_id)
                    total_amount += product.price * quantity
                    
                    # Create OrderItem
                    OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity,
                        price=product.price
                    )
            
            order.total_amount = total_amount
            order.save()
            
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    
    # Get available products
    available_products = Product.objects.filter(stock_quantity__gt=0)
    
    return render(request, 'orders/create_order.html', {
        'form': form,
        'available_products': available_products
    })

@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        # Create status update record
        OrderStatusUpdate.objects.create(
            order=order,
            updated_by=request.user,
            old_status=order.status,
            new_status=new_status,
            notes=notes
        )
        
        # Update order status
        order.status = new_status
        order.save()
        
        # TODO: Implement email notification
        
        return redirect('order_detail', order_id=order.id)
    
    return render(request, 'orders/update_status.html', {'order': order})