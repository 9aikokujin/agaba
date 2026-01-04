from django.urls import path

from ..views import messenger as messenger_views

urlpatterns = [
    path(
        'notifications/',
        messenger_views.NotificationListView.as_view(),
        name='notification-list'
    ),
    path(
        'notifications/unread-count/',
        messenger_views.UnreadNotificationCountView.as_view(),
        name='unread-count'
    ),
    path(
        'notifications/mark-as-read/',
        messenger_views.MarkAsReadView.as_view(),
        name='mark-as-read'
    ),
    path(
        'notifications/<notification_id>/delete/',
        messenger_views.NotificationDeleteView.as_view(),
        name='notification-delete'
    ),
    path(
        'chats/',
        messenger_views.ChatListView.as_view(),
        name='chat-list'
    ),
    path(
        'chats/<int:chat_id>/',
        messenger_views.ChatDetailView.as_view(),
        name='chat-detail'
    ),
    path(
        'chats/init_product_chat/',
        messenger_views.ChatViewSet.as_view({'post': 'init_product_chat'}),
        name='init-product-chat'
    ),
    path(
        'chats/<int:chat_id>/messages/',
        messenger_views.MessageListView.as_view(),
        name='message-list'
    ),
    path(
        'chats/<int:chat_id>/mark-as-read/',
        messenger_views.MarkMessagesAsReadView.as_view(),
        name='mark-as-read'
    ),
]
