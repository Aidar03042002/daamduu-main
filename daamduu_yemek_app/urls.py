from django.urls import path
from . import views

app_name = 'daamduu_yemek'

urlpatterns = [
    path('', views.root_redirect, name='root'),
    path('index/', views.index, name='index'),
    path('home/', views.home, name='home'),
    path('hakkimizda/', views.hakkimizda, name='hakkimizda'),
    path('takim/', views.takim, name='takim'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('today-menu/', views.today_menu, name='today_menu'),
    path('weekly-menu/', views.weekly_menu, name='weekly_menu'),
    path('process-payment/', views.process_payment, name='process_payment'),
    path('about/', views.hakkimizda, name='about'),
    path('team/', views.takim, name='team'),
    
    # Admin pages
    path('panel/login/', views.admin_login_view, name='admin_login'),
    path('panel/reset-password/', views.admin_reset_password, name='admin_reset_password'),
    path('panel/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('panel/users/', views.admin_users, name='admin_users'),
    path('panel/menu/', views.admin_menu, name='admin_menu'),
    path('panel/qr-tarayici/', views.admin_qr_scanner, name='admin_qr_scanner'),
    path('panel/orders/', views.admin_orders, name='admin_orders'),
    path('api/verify-qr/', views.verify_qr, name='verify_qr'),
    path('api/buy/', views.api_buy, name='api_buy'),
    path('staff/qr-tarayici/', views.staff_qr_scanner, name='staff_qr_scanner'),
    path('api/order-info/', views.api_order_info, name='api_order_info'),
] 