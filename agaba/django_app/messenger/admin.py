from django.contrib import admin
from .models import Message, Chat


class MessageAdmin(admin.ModelAdmin):
    """Админ панель для модели Сообщение."""
    list_display = ('chat', 'sender', 'content', 'is_read', 'created_at')
    list_filter = ('chat', 'sender', 'is_read')
    search_fields = ('content',)


class ChatAdmin(admin.ModelAdmin):
    """Админ панель для модели Чат."""
    list_display = ('id', 'chat_type', 'product', 'created_at', 'updated_at')
    list_filter = ('chat_type', 'product')
    search_fields = ('participants__username',)


admin.site.register(Message, MessageAdmin)
admin.site.register(Chat, ChatAdmin)
