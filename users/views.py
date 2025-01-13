from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserChangeForm, StudentVerificationForm
from .models import CustomUser, StudentVerification
from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum, Q
from django.shortcuts import render
from inventory.models import Product
from orders.models import Order
from payment.models import Payment


@login_required
def profile(request):
    return render(request, 'users/profile.html')


@login_required
def dashboard(request):
    # Fetch recent data for the dashboard
    recent_orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]
    low_stock_products = Product.objects.filter(
        user=request.user, 
        stock_quantity__lte=F('low_stock_threshold')
    )
    total_revenue = Payment.objects.filter(
        user=request.user, 
        status='completed'
    ).aggregate(total=Sum('amount'))['total'] or 0

    context = {
        'recent_orders': recent_orders,
        'low_stock_products': low_stock_products,
        'total_revenue': total_revenue,
    }
    return render(request, 'users/dashboard.html', context)

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})

@login_required
def verify_student_status(request):
    try:
        verification = request.user.studentverification
    except StudentVerification.DoesNotExist:
        verification = None

    if request.method == 'POST':
        form = StudentVerificationForm(request.POST, request.FILES, instance=verification)
        if form.is_valid():
            verification = form.save(commit=False)
            verification.user = request.user
            verification.save()
            messages.success(request, 'Student verification submitted. Pending approval.')
            return redirect('users:profile')
    else:
        form = StudentVerificationForm(instance=verification)
    
    return render(request, 'users/verify_students.html', {'form': form})

# Admin views for user management
def admin_user_list(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('users:profile')
    
    users = CustomUser.objects.all()
    return render(request, 'users/admin_user_list.html', {'users': users})

def admin_verify_student(request, user_id):
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('home')
    
    user = CustomUser.objects.get(id=user_id)
    verification = user.studentverification
    
    if request.method == 'POST':
        verification.is_verified = True
        verification.save()
        
        user.is_student_verified = True
        user.save()
        
        messages.success(request, f'Student {user.email} verified successfully')
        return redirect('admin_user_list')
    
    return render(request, 'users/admin_verify_student.html', {'verification': verification})