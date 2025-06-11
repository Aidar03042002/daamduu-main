from django.contrib import admin
from .models import Order, Dish, DailyMenu

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'order_number', 'amount', 'payment_date', 'status', 'card_last_four')
    list_filter = ('status', 'user')
    search_fields = ('order_number', 'user__username', 'card_last_four')

admin.site.register(Dish)
admin.site.register(DailyMenu)
