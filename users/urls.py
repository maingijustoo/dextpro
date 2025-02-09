from django.urls import path, include
from django.contrib.auth import views as auth_views
from .views import (
    profile, 
    edit_profile, 
    verify_student_status,
    admin_user_list,
    admin_verify_student,
    custom_login_view
)
from users import views

app_name='users'
urlpatterns = [
    # AllAuth URLs
    path('accounts/', include('allauth.urls')),
    path('accounts/login/', custom_login_view, name='account_login'),
    
    # User profile URLs
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
    path('profile/verify-student/', verify_student_status, name='verify_student'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin URLs
    path('admin/users/', admin_user_list, name='admin_user_list'),
    path('admin/verify-student/<int:user_id>/', admin_verify_student, name='admin_verify_student'),

    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    # Optional: password reset views
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done')

]