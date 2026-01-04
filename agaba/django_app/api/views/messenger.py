from django.shortcuts import get_object_or_404
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from messenger.models import Notification, Chat, Message
from products.models import Product
from order.models import Order
from messenger.serializers import (
    NotificationSerializer, MarkAsReadSerializer,
    ChatSerializer, MessageSerializer,
    InitProductChatSerializer
)


class NotificationListView(APIView):
    """Вью для получения списка уведомлений"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить список уведомлений",
        operation_description="Возвращает до 50 последних уведомлений",
        responses={200: NotificationSerializer(many=True)}
    )
    def get(self, request):
        notifications = request.user.notifications.order_by('-created_at')[:50]
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data)


class NotificationDeleteView(APIView):
    """Вью для удаления уведомления"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Удалить уведомление",
        operation_description="Удаляет уведомление по ID",
        manual_parameters=[
            openapi.Parameter(
                'notification_id',
                openapi.IN_PATH,
                description="ID уведомления для удаления",
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: openapi.Response(
            description="Уведомление удалено",
            examples={"application/json": {"status": "deleted"}}
        ),
                   404: "Уведомление не найдено"}
    )
    def delete(self, request, notification_id):
        notification = get_object_or_404(
            Notification, id=notification_id,
            user=request.user
        )
        notification.delete()
        return Response({'status': 'deleted'})


class UnreadNotificationCountView(APIView):
    """Вью для получения количества непрочитанных уведомлений"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить количество непрочитанных уведомлений",
        operation_description="Возвращает число непрочитанных уведомлений",
        responses={200: openapi.Response(
            description="Количество непрочитанных уведомлений",
            examples={"application/json": {"count": 3}}
        )}
    )
    def get(self, request):
        count = request.user.notifications.filter(is_read=False).count()
        return Response({'count': count})


class MarkAsReadView(APIView):
    """Вью для пометки уведомлений как прочитанные"""
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Отметить уведомления как прочитанные",
        operation_description="""
        Помечает уведомления по переданным ID как прочитанные.
        """,
        request_body=MarkAsReadSerializer,
        responses={
            200: openapi.Response(
                description="Успешно помечено",
                examples={"application/json": {"status": "marked as read"}}
            ),
            400: "Ошибка валидации данных"
        }
    )
    def post(self, request):
        serializer = MarkAsReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        request.user.notifications.filter(
            id__in=serializer.validated_data['ids'],
            is_read=False
        ).update(is_read=True)

        return Response({'status': 'marked as read'})


class ChatListView(APIView):
    """Отображение чатов."""
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()

    @swagger_auto_schema(
        operation_summary="Получить список чатов пользователя",
        responses={200: ChatSerializer(many=True)}
    )
    def get(self, request):
        chats = request.user.chats.all(
        ).prefetch_related('participants', 'messages')
        serializer = ChatSerializer(
            chats, many=True, context={'request': request})
        return Response(serializer.data)


class ChatViewSet(viewsets.ModelViewSet):
    """Отображение конкретного чата."""
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer

    @action(
            detail=False, methods=['post'],
            serializer_class=InitProductChatSerializer
        )
    def init_product_chat(self, request):
        serializer = InitProductChatSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product = Product.objects.get(
            id=serializer.validated_data['product_id']
        )
        buyer = request.user
        seller = product.author
        if not seller:
            seller = Order.objects.filter(
                user=buyer
            ).first().product.author

        existing_chat = Chat.objects.filter(
            chat_type=Chat.PRODUCT_CHAT,
            product=product,
            participants=buyer
        ).first()

        if existing_chat:
            return Response(
                ChatSerializer(
                    existing_chat, context={'request': request}
                ).data,
                status=status.HTTP_200_OK
            )

        chat = Chat.objects.create(
            chat_type=Chat.PRODUCT_CHAT,
            product=product
        )
        chat.participants.add(buyer, seller)

        if serializer.validated_data.get('initial_message'):
            Message.objects.create(
                chat=chat,
                sender=buyer,
                content=serializer.validated_data['initial_message']
            )

        return Response(
            ChatSerializer(chat, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )


class ChatDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить детали чата",
        responses={200: ChatSerializer()}
    )
    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        serializer = ChatSerializer(chat, context={'request': request})
        return Response(serializer.data)


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Получить сообщения чата",
        responses={200: MessageSerializer(many=True)}
    )
    def get(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
        messages = chat.messages.all().order_by('created_at')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)


class MarkMessagesAsReadView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_summary="Пометить сообщения как прочитанные"
    )
    def post(self, request, chat_id):
        chat = get_object_or_404(Chat, id=chat_id, participants=request.user)

        chat.messages.filter(
            is_read=False
        ).exclude(
            sender=request.user
        ).update(is_read=True)
        return Response({'status': 'marked as read'})
