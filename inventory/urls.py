from django.urls import path
from django.urls import path

from .views import adjust_stock, product_list,delete_product,add_item, item_list, item_detail, edit_item, admin_review_items, admin_approve_item, admin_reject_item, delete_image

app_name='inventory'

urlpatterns = [
    #path('', views.index, name='index'),
    path('', product_list, name='product_list'),
    #path('create/', create_product, name='create_product'),
    #path('<int:product_id>/', product_detail, name='product_detail'),
    #path('<int:product_id>/', edit_item, name='edit_product'),
    path('<int:product_id>/', delete_product, name='delete_product'),
    path('<int:product_id>/', adjust_stock, name='adjust_stock'),
    path('add/', add_item, name='add_item'),
    path('items/', item_list, name='item_list'),
    path('<int:item_id>/details', item_detail, name='item_detail'),
    #check hiii path pia same to create_produst hazi conflict
    path('<int:item_id>/edit/', edit_item, name='edit_item'),
    path('delete_image/<int:image_id>/', delete_image, name='delete_image'), 
    # Admin URLs
    path('admin/review/', admin_review_items, name='admin_review_items'),
    path('admin/approve/<int:item_id>/', admin_approve_item, name='admin_approve_item'),
    path('admin/reject/<int:item_id>/', admin_reject_item, name='admin_reject_item'),
]
'''admin logic to be checked'''