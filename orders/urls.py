from django.urls import path
from . import views
from django.urls import path
from .views import order_list, order_detail, create_order, update_order_status

app_name='orders'
urlpatterns = [
    #path('', views.index, name='index'),
    path('', order_list, name='order_list'),
    path('create/', create_order, name='create_order'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('<int:order_id>/update', update_order_status, name='update_order_status'),
]

