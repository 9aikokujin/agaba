from django.contrib import admin
from django.utils.html import format_html
import json

from .models import (
    Balance, Replenishment,
    Withdrawal,
    OrderOperation,
    AllOperation
)


@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    """Админ панель для модели Balance."""

    list_display = ('get_username', 'cash_account', 'date_update')

    def get_username(self, obj):
        return getattr(obj.user, 'username', "Пользователь удален")

    get_username.short_description = 'Пользователь'
    get_username.admin_order_field = 'user__username'
    readonly_fields = ('date_update',)


@admin.register(Replenishment)
class ReplenishmentAdmin(admin.ModelAdmin):
    """Админ панель для модели Пополнение баланса."""

    list_display = (
        'operation_id', 'user_id', 'amount_replenishment',
        'get_payment_type', 'status_operation', 'formatted_date',
        'time_since_creation', 
    )
    list_filter = ('status_operation', 'payment_type')
    search_fields = ('user_id__username', 'operation_id')
    readonly_fields = (
        'formatted_date',
        'time_since_creation'
    )

    actions = ['mark_as_success', 'mark_as_failure']

    fields = (
        'user',
        'amount_replenishment',
        'payment_type',
        'status_operation',
        # 'path_invoice',
        'number_transaction',
        'formatted_date'
        'time_since_creation',
        'company',
    )

    def mark_as_success(self, request, queryset):
        for replenishment in queryset:
            try:
                replenishment.mark_as_success()
                replenishment.save()
                self.message_user(request, f"Операция {replenishment.operation_id} успешно выполнена.")
            except Exception as e:
                self.message_user(request, f"Ошибка при обработке операции {replenishment.operation_id}: {e}")
    mark_as_success.short_description = "Пометить выбранные операции как успешные"

    def mark_as_failure(self, request, queryset):
        for replenishment in queryset:
            try:
                replenishment.mark_as_failure()
                replenishment.save()
                self.message_user(request, f"Операция {replenishment.operation_id} отменена.")
            except Exception as e:
                self.message_user(request, f"Ошибка при обработке операции {replenishment.operation_id}: {e}")
    mark_as_failure.short_description = "Пометить выбранные операции как неудачные"

    def time_since_creation(self, obj):
        """
        Возвращает время с момента создания только для операций со статусом 'pending'.
        Для других статусов возвращает Выполнен.
        """
        if obj.status_operation != 'pending':
            return "Выполнен"
        return obj.time_since_creation
    time_since_creation.short_description = 'Время с момента создания'

    def formatted_date(self, obj):
        return obj.formatted_date()
    formatted_date.short_description = 'Дата создания'

    def get_payment_type(self, obj):
        return obj.get_payment_type_display()

    get_payment_type.short_description = 'Тип операции'
    get_payment_type.admin_order_field = 'payment_type'


@admin.register(Withdrawal)
class WithdrawalAdmin(admin.ModelAdmin):
    """Админ панель для модели Вывод средств."""

    list_display = (
        'withdrawal_operation_id', 'user_id', 'amount_withdrawal',
        'type_operation', 'status_operation', 'formatted_date', 'time_since_creation'
    )
    list_filter = ('status_operation', 'type_operation')
    search_fields = ('user_id__username', 'withdrawal_operation_id')
    readonly_fields = ('formatted_date', 'time_since_creation')

    actions = ['mark_as_success', 'mark_as_failure']

    def mark_as_success(self, request, queryset):
        for withdrawal in queryset:
            try:
                withdrawal.mark_as_success()
                withdrawal.save()
                self.message_user(request, f"Операция {withdrawal.withdrawal_operation_id} успешно выполнена.")
            except Exception as e:
                self.message_user(request, f"Ошибка при обработке операции {withdrawal.withdrawal_operation_id}: {e}")
    mark_as_success.short_description = "Пометить выбранные операции как успешные"

    def mark_as_failure(self, request, queryset):
        for withdrawal in queryset:
            try:
                withdrawal.mark_as_failure()
                withdrawal.save()
                self.message_user(request, f"Операция {withdrawal.withdrawal_operation_id} отменена.")
            except Exception as e:
                self.message_user(request, f"Ошибка при обработке операции {withdrawal.withdrawal_operation_id}: {e}")
    mark_as_failure.short_description = "Пометить выбранные операции как неудачные"

    def time_since_creation(self, obj):
        """
        Возвращает время с момента создания только для операций со статусом 'pending'.
        Для других статусов возвращает Выполнен.
        """
        if obj.status_operation != 'pending':
            return "Выполнен" 
        return obj.time_since_creation
    time_since_creation.short_description = 'Время с момента создания'

    def formatted_date(self, obj):
        return obj.formatted_date()
    formatted_date.short_description = 'Дата создания'


@admin.register(OrderOperation)
class OrderOperationAdmin(admin.ModelAdmin):
    """Админ панель для модели Операция по заказу."""

    list_display = (
        'order_operation_id', 
        'user_id', 
        'get_order_number',
        'get_order_stage', 
        'type_operation', 
        'formatted_date'
    )
    list_filter = ('type_operation',)
    search_fields = ('user_id__username', 'order_operation_id', 'order_id__number')
    readonly_fields = ('formatted_date',)

    def formatted_date(self, obj):
        return obj.formatted_date()
    formatted_date.short_description = 'Дата создания'

    def get_order_number(self, obj):
        return obj.order_id.number if obj.order_id else "Заказ удален"
    get_order_number.short_description = 'Номер заказа'

    def get_order_stage(self, obj):
        return obj.order_id.get_stage_display() if obj.order_id else "Заказ удален"
    get_order_stage.short_description = 'Статус заказа'


@admin.register(AllOperation)
class AllOperationAdmin(admin.ModelAdmin):
    """Админ панель для модели Операция пользователя."""

    list_display = ('user', 'type_operation', 'payment_type',
                    'status_operation', 'formatted_date', 'amount')
    list_filter = ('date_created',)

    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'type_operation', 'status_operation', 'amount', 'payment_type'),
        }),
        ('Детали операции', {
            'fields': ('formatted_details',),
        }),
        ('Время', {
            'fields': ('formatted_date',),
        }),
    )

    readonly_fields = ('user', 'formatted_date', 'formatted_details',
                       'type_operation', 'amount')

    def formatted_date(self, obj):
        """Форматирует дату создания объекта."""
        return obj.formatted_date()
    formatted_date.short_description = 'Дата создания'

    def formatted_details(self, obj):
        """
        Возвращает отформатированное представление поля details.
        """
        if not obj.details:
            return "Нет деталей"

        details_str = json.dumps(obj.details, ensure_ascii=False, indent=4)
        return format_html('<pre>{}</pre>', details_str)
    formatted_details.short_description = 'Детали операции'
