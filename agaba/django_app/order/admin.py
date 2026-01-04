from django.contrib import admin
from .models import Order, OrderManagerAssignment, DeliveryOrder, Bank


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Админ панель для модели Заказ."""
    list_display = (
        'number', 'product', 'user', 'date_created',
        'payment_type', 'amount', 'stage', 'get_manager'
    )
    list_filter = ('stage', 'payment_type', 'date_created')
    search_fields = ('number', 'product__name', 'user__username')
    readonly_fields = ('number', 'date_created', 'delivery_number')
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'number', 'product', 'user', 'date_created', 'company'
            )
        }),
        ('Финансовые данные', {
            'fields': (
                'payment_type', 'down_payment_percent',
                'first_payment', 'amount', 'bank_for_leasing'
            )
        }),
        ('Доставка и статус', {
            'fields': (
                'stage', 'delivery_number', 'address'
            )
        }),
        ('Дополнительные опции', {
            'fields': ('selected_additional_options',)
        }),
    )
    filter_horizontal = ('selected_additional_options',)
    autocomplete_fields = ('product', 'user', 'company')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)

    def get_manager(self, obj):
        return obj.get_manager()
    get_manager.short_description = 'Менеджер'
    get_manager.admin_order_field = 'manager_assignment__manager'


@admin.register(OrderManagerAssignment)
class OrderManagerAssignmentAdmin(admin.ModelAdmin):
    """Админ панель для модели Менеджер заказа."""
    list_display = ('order', 'manager', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('order__number', 'manager__username')
    autocomplete_fields = ('order', 'manager')
    date_hierarchy = 'assigned_at'
    ordering = ('-assigned_at',)


@admin.register(DeliveryOrder)
class DeliveryOrderAdmin(admin.ModelAdmin):
    """Админ панель для модели Доставка."""
    list_display = (
        'number', 'order', 'user', 'delivery_stage',
        'delivery_type', 'date_delivery'
    )
    list_filter = ('delivery_stage', 'delivery_type', 'date_created')
    search_fields = ('number', 'order__number', 'user__username')
    readonly_fields = ('number', 'date_created')
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'number', 'order', 'user', 'date_created', 'company'
            )
        }),
        ('Данные доставки', {
            'fields': (
                'delivery_stage', 'delivery_type', 'date_delivery',
                'dimensions', 'address_delivery'
            )
        }),
        ('Товар', {
            'fields': ('cargo',)
        }),
    )
    autocomplete_fields = ('order', 'user', 'company', 'cargo')
    date_hierarchy = 'date_created'
    ordering = ('-date_created',)


@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """Админ панель для модели Банк(лизинг)."""
    list_display = ('name', 'logo', 'percentage_year', 'max_sum')
    list_filter = ('name',)
