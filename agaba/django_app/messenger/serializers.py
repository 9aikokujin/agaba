from rest_framework import serializers
from .models import Notification, Chat, Message
from products.models import Product
from account.serializers import UserShortSerializer


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class MarkAsReadSerializer(serializers.Serializer):
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=True
    )


class MessageSerializer(serializers.ModelSerializer):
    sender = UserShortSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'is_read', 'created_at']
        read_only_fields = ['id', 'sender', 'created_at']


class ChatSerializer(serializers.ModelSerializer):
    participants = UserShortSerializer(many=True, read_only=True)
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Chat
        fields = [
            'id', 'chat_type', 'product', 'participants',
            'last_message', 'unread_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        last_message = obj.messages.order_by('-created_at').first()
        if last_message:
            return MessageSerializer(last_message).data
        return None

    def get_unread_count(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.messages.filter(is_read=False).exclude(
                sender=request.user
            ).count()
        return 0


class InitProductChatSerializer(serializers.Serializer):
    product_id = serializers.IntegerField(required=True)
    initial_message = serializers.CharField(required=False, allow_blank=True)

    def validate_product_id(self, value):
        try:
            product = Product.objects.get(id=value)
            if not product.author:
                raise serializers.ValidationError("У товара нет продавца")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Товар не найден")


class CreateChatSerializer(serializers.Serializer):
    order_id = serializers.IntegerField(required=False)
    chat_type = serializers.ChoiceField(choices=Chat.CHAT_TYPE_CHOICES)
