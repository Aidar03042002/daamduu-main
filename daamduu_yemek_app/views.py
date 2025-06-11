from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.http import JsonResponse
import re
from .models import Order, Dish, DailyMenu
import json
from django.utils import timezone
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.dateparse import parse_date
from django.db import IntegrityError
import datetime

def index(request):
    from django.utils import timezone
    today = timezone.localdate()
    today_menu = DailyMenu.objects.filter(date=today).first()
    return render(request, 'daamduu_yemek_app/index.html', {'today_menu': today_menu})

@login_required
def home(request):
    return render(request, 'daamduu_yemek_app/home.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
        except User.DoesNotExist:
            user = None
        
        if user is not None:
            login(request, user)
            messages.success(request, 'Giriş başarılı! Hoş geldiniz.')
            if user.is_superuser:
                return redirect('daamduu_yemek:home')
            elif user.is_staff:
                return redirect('daamduu_yemek:staff_qr_scanner')
            else:
                return redirect('daamduu_yemek:home')
        else:
            messages.error(request, 'Geçersiz e-posta veya şifre.')
    
    return render(request, 'daamduu_yemek_app/login.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Başarıyla çıkış yaptınız.')
    return redirect('/')

def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        full_name = request.POST.get('full_name')

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Geçersiz e-posta formatı.')
            return render(request, 'daamduu_yemek_app/register.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu e-posta adresi zaten kullanılıyor.')
            return render(request, 'daamduu_yemek_app/register.html')

        # Validate password strength
        if len(password) < 8:
            messages.error(request, 'Şifre en az 8 karakter olmalıdır.')
            return render(request, 'daamduu_yemek_app/register.html')

        try:
            # Create user with email as username
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password
            )

            # Split full name into first and last name
            name_parts = full_name.split()
            if len(name_parts) > 1:
                user.first_name = name_parts[0]
                user.last_name = ' '.join(name_parts[1:])
            else:
                user.first_name = full_name

            user.save()

            # Log the user in
            login(request, user)
            messages.success(request, 'Kayıt başarılı! Hoş geldiniz.')
            return redirect('daamduu_yemek:home')

        except Exception as e:
            messages.error(request, f'Kayıt sırasında bir hata oluştu: {str(e)}')
            return render(request, 'daamduu_yemek_app/register.html')

    return render(request, 'daamduu_yemek_app/register.html')

def reset_password(request):
    return render(request, 'daamduu_yemek_app/reset-password.html')

@login_required
def today_menu(request):
    today = timezone.localdate()
    today_menu = DailyMenu.objects.filter(date=today).first()
    # Get the latest active order for the user (только за сегодня и только активные)
    latest_order = Order.objects.filter(user=request.user, payment_date__date=today, status='active').order_by('-payment_date').first()
    return render(request, 'daamduu_yemek_app/bugun-menu.html', {
        'today_menu': today_menu,
        'latest_order': latest_order
    })

def weekly_menu(request):
    return render(request, 'daamduu_yemek_app/haftalik-menu.html')

def hakkimizda(request):
    return render(request, 'daamduu_yemek_app/hakkimizda.html')

def takim(request):
    return render(request, 'daamduu_yemek_app/takim.html')

def admin_login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            messages.error(request, 'Geçersiz e-posta formatı.')
            return render(request, 'daamduu_yemek_app/admin-login.html')

        # Try to find user by email
        try:
            user = User.objects.get(email=email)
            # Authenticate with username and password
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                # Check if user is admin
                if user.is_staff or user.is_superuser:
                    login(request, user)
                    messages.success(request, 'Yönetici girişi başarılı!')
                    return redirect('daamduu_yemek:admin_dashboard')
                else:
                    messages.error(request, 'Bu hesap yönetici yetkisine sahip değil.')
            else:
                messages.error(request, 'Geçersiz e-posta veya şifre.')
        except User.DoesNotExist:
            messages.error(request, 'Geçersiz e-posta veya şifre.')

    return render(request, 'daamduu_yemek_app/admin-login.html')

@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('daamduu_yemek:home')
    return render(request, 'daamduu_yemek_app/admin.html')

@login_required
def admin_users(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('daamduu_yemek:home')
    if request.method == 'POST':
        if 'delete_user_id' in request.POST:
            user_id = request.POST.get('delete_user_id')
            try:
                user = User.objects.get(id=user_id)
                if user.is_superuser:
                    messages.error(request, 'Суперпользователя удалить нельзя!')
                else:
                    user.delete()
                    messages.success(request, 'Пользователь успешно удалён.')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден.')
            return redirect('daamduu_yemek:admin_users')
        elif 'toggle_staff_id' in request.POST:
            user_id = request.POST.get('toggle_staff_id')
            try:
                user = User.objects.get(id=user_id)
                if user.is_superuser:
                    messages.error(request, 'Суперпользователь всегда staff!')
                else:
                    user.is_staff = not user.is_staff
                    user.save()
                    if user.is_staff:
                        messages.success(request, f'Пользователь {user.username} теперь STAFF.')
                    else:
                        messages.success(request, f'Пользователь {user.username} теперь обычный пользователь.')
            except User.DoesNotExist:
                messages.error(request, 'Пользователь не найден.')
            return redirect('daamduu_yemek:admin_users')
    users = User.objects.all().order_by('id')
    return render(request, 'daamduu_yemek_app/admin-users.html', {'users': users})

@login_required
def admin_menu(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('daamduu_yemek:home')
    message = None
    # Добавление блюда
    if request.method == 'POST' and 'add_dish' in request.POST:
        name = request.POST.get('dish_name')
        calories = request.POST.get('dish_calories')
        image = request.FILES.get('dish_image')
        if name and calories and image:
            dish = Dish(name=name, calories=calories, image=image)
            dish.save()
            message = {'type': 'success', 'text': 'Блюдо успешно добавлено!'}
        else:
            message = {'type': 'danger', 'text': 'Заполните все поля для блюда.'}
    # Составление меню на день
    elif request.method == 'POST' and 'add_menu' in request.POST:
        date = request.POST.get('menu_date')
        dish1 = request.POST.get('dish1')
        dish2 = request.POST.get('dish2')
        dish3 = request.POST.get('dish3')
        dish4 = request.POST.get('dish4')
        if date and dish1 and dish2 and dish3 and dish4:
            try:
                DailyMenu.objects.create(
                    date=parse_date(date),
                    dish1_id=dish1,
                    dish2_id=dish2,
                    dish3_id=dish3,
                    dish4_id=dish4
                )
                message = {'type': 'success', 'text': 'Меню на день успешно создано!'}
            except IntegrityError:
                message = {'type': 'danger', 'text': 'Меню на этот день уже существует!'}
        else:
            message = {'type': 'danger', 'text': 'Заполните все поля для меню.'}
    # Удаление меню на день
    elif request.method == 'POST' and 'delete_menu_id' in request.POST:
        menu_id = request.POST.get('delete_menu_id')
        DailyMenu.objects.filter(id=menu_id).delete()
        message = {'type': 'success', 'text': 'Меню удалено.'}
    # Данные для шаблона
    dishes = Dish.objects.all().order_by('name')
    menus = DailyMenu.objects.select_related('dish1','dish2','dish3','dish4').order_by('-date')
    return render(request, 'daamduu_yemek_app/admin-menu.html', {
        'dishes': dishes,
        'menus': menus,
        'message': message
    })

@login_required
def admin_qr_scanner(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('daamduu_yemek:home')
    return render(request, 'daamduu_yemek_app/admin-qr-tarayici.html')

def admin_reset_password(request):
    return render(request, 'daamduu_yemek_app/reset-password-admin.html')

@login_required
def process_payment(request):
    if request.method == 'POST':
        # Get form data
        card_name = request.POST.get('card_name')
        card_number = request.POST.get('card_number')
        expiry = request.POST.get('expiry')
        cvv = request.POST.get('cvv')

        # Get last 4 digits of card number
        card_last_four = card_number.replace(" ", "")[-4:]

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=Order.generate_order_number(),
            amount=100.00,  # Fixed amount for now
            card_last_four=card_last_four
        )

        # Create QR code data
        qr_data = {
            'order_number': order.order_number,
            'user': request.user.username,
            'amount': str(order.amount),
            'date': order.payment_date.isoformat(),
            'card_last_four': card_last_four
        }
        
        # Save QR data to order
        order.qr_code_data = json.dumps(qr_data, ensure_ascii=False)
        order.save()

        messages.success(request, 'Ödeme başarıyla tamamlandı! QR kodunuz hazırlanıyor...')
        return redirect('daamduu_yemek:today_menu')
    return redirect('daamduu_yemek:today_menu')

@login_required
def verify_qr(request):
    if request.method == 'POST':
        try:
            qr_data = json.loads(request.POST.get('qr_data', '{}'))
            order_number = qr_data.get('order_number')
            
            if not order_number:
                return JsonResponse({
                    'success': False,
                    'message': 'Geçersiz QR kod formatı'
                })
            
            try:
                order = Order.objects.get(order_number=order_number)
                
                # Check if QR code exists and order is active
                if not order.qr_code_data or order.status != 'active':
                    return JsonResponse({
                        'success': False,
                        'message': 'Bu QR kod daha önce kullanılmış'
                    })
                
                # Mark QR code as used and update status
                order.qr_code_data = None
                order.status = 'used'
                order.save()
                
                return JsonResponse({
                    'success': True,
                    'message': 'QR kod başarıyla doğrulandı'
                })
                
            except Order.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Geçersiz sipariş numarası'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Geçersiz QR kod formatı'
            })
    
    return JsonResponse({
        'success': False,
        'message': 'Geçersiz istek'
    })

@csrf_exempt
@login_required
def api_buy(request):
    if request.method == "POST":
        user = request.user
        data = json.loads(request.body.decode("utf-8"))
        amount = data.get("amount", 100)
        # Create order
        order = Order.objects.create(
            user=user,
            order_number=Order.generate_order_number(),
            amount=amount,
            card_last_four="0000",  # Placeholder, update if needed
            payment_date=timezone.now()
        )
        return JsonResponse({
            "transaction_id": order.order_number,
            "amount": float(order.amount),
            "user_id": user.id
        })
    return JsonResponse({"error": "Invalid request"}, status=400)

@login_required
def staff_qr_scanner(request):
    # Только для staff, но не superuser
    if not request.user.is_staff or request.user.is_superuser:
        return redirect('daamduu_yemek:home')
    return render(request, 'daamduu_yemek_app/staff-qr-tarayici.html')

@login_required
def admin_orders(request):
    if not request.user.is_superuser:
        messages.error(request, 'Bu sayfaya erişim yetkiniz yok.')
        return redirect('daamduu_yemek:home')
    message = None
    if request.method == 'POST':
        if 'delete_order_id' in request.POST:
            order_id = request.POST.get('delete_order_id')
            Order.objects.filter(id=order_id).delete()
            message = {'type': 'success', 'text': 'Sipariş silindi!'}
        elif 'set_used_id' in request.POST:
            order_id = request.POST.get('set_used_id')
            Order.objects.filter(id=order_id).update(status='used')
            message = {'type': 'success', 'text': 'Sipariş "used" olarak işaretlendi!'}
    orders = Order.objects.select_related('user').order_by('-payment_date')
    return render(request, 'daamduu_yemek_app/admin-orders.html', {
        'orders': orders,
        'message': message
    })

@login_required
def api_order_info(request):
    today = timezone.localdate()
    order = Order.objects.filter(user=request.user, payment_date__date=today, status='active').order_by('-payment_date').first()
    if order and order.qr_code_data:
        return JsonResponse({
            'success': True,
            'order': {
                'order_number': order.order_number,
                'amount': float(order.amount),
                'qr_code_data': order.qr_code_data,
            }
        })
    else:
        return JsonResponse({'success': False, 'message': 'Заказ не найден или QR отсутствует'})

def root_redirect(request):
    from django.shortcuts import redirect
    return redirect('daamduu_yemek:index')
