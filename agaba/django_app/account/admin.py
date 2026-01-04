from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Company


class CustomUserAdmin(UserAdmin):
    """Админ панель для модели Юзер."""
    model = CustomUser
    list_display = ('username', 'email', 'role', 'is_staff', 'last_seen')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
            'role', 'is_mobile_verified', 'image', 'companies', 'last_seen'
        )}),
    )


admin.site.register(CustomUser, CustomUserAdmin)


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    """Админ панель для модели Компания."""
    model = Company
    list_display = (
        'name', 'inn',  'legal_address', 'kpp',
        'ogrn', 'edo', 'is_hidden', 'logistic_org', 'updated'
    )
    list_filter = ('user', 'is_hidden', 'logistic_org')
    search_fields = ('inn', 'name', 'legal_address', 'kpp', 'ogrn', 'edo')
    readonly_fields = ('created', 'updated')

    fieldsets = (
        (None, {
            'fields': (
                'user', 'inn', 'name', 'legal_address',
                'kpp', 'ogrn', 'edo', 'is_hidden', 'logistic_org'
            )
        }),
        ('Дополнительная информация', {
            'fields': ('created', 'updated')
        }),
        ('Банковский счет', {
            'fields': ('bank_account', 'bik')
        }),
    )
