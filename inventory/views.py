from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Item, ItemImage, ItemTemplate
from .forms import ItemForm, ItemTemplateForm, ItemSearchForm
from .models import Product, StockAdjustment, ProductCategory
from .forms import (
    ProductForm, 
    StockAdjustmentForm, 
    ProductSearchForm
)



@login_required
def product_list(request):
    # Search and filter functionality
    #search_form = ProductSearchForm(request.GET)
    search_form = ItemSearchForm(request.GET)
    products = Product.objects.filter(user=request.user).order_by('-created_at')

    if search_form.is_valid():
        # Apply filters based on form data
        name = search_form.cleaned_data.get('name')
        min_price = search_form.cleaned_data.get('min_price')
        max_price = search_form.cleaned_data.get('max_price')
        category = search_form.cleaned_data.get('category')
        in_stock = search_form.cleaned_data.get('in_stock')

        if name:
            products = products.filter(name__icontains=name)
        
        if min_price:
            products = products.filter(price__gte=min_price)
        
        if max_price:
            products = products.filter(price__lte=max_price)
        
        if category:
            products = products.filter(category=category)
        
        if in_stock:
            products = products.filter(stock_quantity__gt=0)

    # Pagination
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'inventory/product_list.html', {
        'page_obj': page_obj,
        'search_form': search_form
    })

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    stock_adjustments = StockAdjustment.objects.filter(product=product).order_by('-adjustment_date')
    
    return render(request, 'inventory/product_detail.html', {
        'product': product,
        'stock_adjustments': stock_adjustments
    })


'''
@login_required
def create_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            
            messages.success(request, f"Product {product.name} created successfully!")
            return redirect('product_detail', product_id=product.id)
    else:
        form = ProductForm()
    
    return render(request, 'inventory/create_product.html', {'form': form})
    '''

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, f"Product {product.name} updated successfully!")
            return redirect('inventory:product_detail', product_id=product.id)
    else:
        form = ProductForm(instance=product)
    
    return render(request, 'inventory/edit_product.html', {'form': form, 'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, f"Product {product.name} deleted successfully!")
        return redirect('product_list')
    
    return render(request, 'inventory/delete_product.html', {'product': product})

@login_required
def adjust_stock(request, product_id):
    product = get_object_or_404(Product, id=product_id, user=request.user)
    
    if request.method == 'POST':
        form = StockAdjustmentForm(request.POST)
        if form.is_valid():
            adjustment_quantity = form.cleaned_data['adjustment_quantity']
            previous_quantity = product.stock_quantity
            new_quantity = previous_quantity + adjustment_quantity
            
            # Update product stock
            product.stock_quantity = new_quantity
            product.save()
            
            # Log stock adjustment
            StockAdjustment.objects.create(
                product=product,
                user=request.user,
                previous_quantity=previous_quantity,
                new_quantity=new_quantity,
                reason=form.cleaned_data['reason']
            )
            
            messages.success(request, f"Stock for {product.name} adjusted successfully!")
            return redirect('inventory:product_detail', product_id=product.id)
    else:
        form = StockAdjustmentForm()
    
    return render(request, 'inventory/adjust_stock.html', {'form': form, 'product': product})




@login_required
def add_item(request):
    if request.method == "POST":
        print("FILES RECEIVED:", request.FILES)  # Debugging print

        form = ItemForm(request.POST, request.FILES, user=request.user)

        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check if a template is used
                    template_id = request.POST.get("use_template")
                    if template_id:
                        template = get_object_or_404(ItemTemplate, id=template_id)
                        form.instance.name = template.name
                        form.instance.category = template.category
                        form.instance.description = template.description
                        form.instance.price = template.price
                        form.instance.stock_quantity = template.stock_quantity
                        form.instance.condition = template.condition

                    # Save the item
                    item = form.save(commit=False)
                    item.user = request.user
                    item.status = "pending"  # Require admin approval
                    item.save()

                    # Handle image uploads using a loop
                    images = request.FILES.getlist("images[]") 
                    #images = request.FILES.getlist("images")  # Get multiple files
                    print("Images Found:", images)  # Debugging print
                    if images:
                        for index, image in enumerate(images):
                            item_image = ItemImage(item=item, image=image)
                            item_image.is_primary = index == 0  # Mark first image as primary
                            item_image.save()
                        print("Images uploaded successfully.")
                    else:
                        print("No images uploaded.")

                    messages.success(request, "Your item has been submitted for review!")
                    return redirect("inventory:item_list")  # Redirect after success

            except Exception as e:
                messages.error(request, "Something went wrong. Please try again.")
                print(f"Transaction Error: {str(e)}")  # Debugging print
        else:
            messages.error(request, "Please fix the errors in the form.")
            print("Form Errors:", form.errors)  # Debugging print

    else:
        form = ItemForm(user=request.user)

    return render(request, "inventory/add_item.html", {"form": form})

@login_required
def item_list(request):
    items = Item.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'inventory/item_list.html', {'items': items})

@login_required
def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)
    return render(request, 'inventory/item_detail.html', {'item': item})

@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id, user=request.user)
    
    if request.method == 'POST':
        form = ItemForm(request.POST, request.FILES, instance=item, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Item updated successfully!')
            return redirect('inventory:item_detail', item_id=item.id)
    else:
        form = ItemForm(instance=item, user=request.user)

    return render(request, 'inventory/edit_item.html', {'form': form, 'item': item})

# Admin view for reviewing items
@login_required
def admin_review_items(request):
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('home')

    items = Item.objects.filter(status='pending').order_by('-created_at')
    return render(request, 'inventory/admin_review_items.html', {'items': items})

@login_required
def admin_approve_item(request, item_id):
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('home')

    item = get_object_or_404(Item, id=item_id)
    item.status = 'active'
    item.save()
    messages.success(request, f'Item {item.name} approved and is now live!')
    return redirect('admin_review_items')

@login_required
def admin_reject_item(request, item_id):
    if not request.user.is_admin():
        messages.error(request, 'Access denied')
        return redirect('home')

    item = get_object_or_404(Item, id=item_id)
    item.status = 'rejected'
    item.save()
    messages.success(request, f'Item {item.name} has been rejected.')
    return redirect('admin_review_items')