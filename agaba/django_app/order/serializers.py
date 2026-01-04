from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated

from products.models import Product
from order.models import (
    Order, OrderManagerAssignment, DeliveryOrder,
)
from products.models import AdditionalOption, Dimensions
from products.serializers import (
    AdditionalOptionSerializer,
    DimensionsSerializer
)


class OrderSerializer(serializers.ModelSerializer):
    selected_additional_options = AdditionalOptionSerializer(
        many=True, read_only=True
    )
    additional_options = serializers.PrimaryKeyRelatedField(
        queryset=AdditionalOption.objects.all(),
        many=True,
        write_only=True,
        required=False,
        source='selected_additional_options'
    )
    product_title = serializers.CharField(
        source='product.name', read_only=True
    )
    first_payment = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id', 'number', 'product', 'product_title', 'user',
            'date_created', 'payment_type', 'address',
            'down_payment_percent', 'first_payment', 'amount',
            'stage', 'delivery_number', 'selected_additional_options',
            'company', 'turnover', 'count_of_contracts', 'amount_of_leasing',
            'bank_for_leasing', 'additional_options'
        ]
        read_only_fields = [
            'id', 'number', 'date_created',
            'amount', 'delivery_number'
        ]
        required_fields = [
            'product', 'user',
            'payment_type', 'address',
            'company'
        ]
        extra_kwargs = {
            'turnover': {'required': False, 'allow_null': True},
            'count_of_contracts': {'required': False, 'allow_null': True},
            'amount_of_leasing': {'required': False, 'allow_null': True},
            'bank_for_leasing': {'required': False, 'allow_null': True}
        }

    def __init__(self, *args, **kwargs):
        super(OrderSerializer, self).__init__(*args, **kwargs)

        # Динамическая установка обязательности полей
        payment_type = None
        if 'data' in kwargs and isinstance(kwargs['data'], dict):
            payment_type = kwargs['data'].get('payment_type')
        elif self.instance and hasattr(self.instance, 'payment_type'):
            payment_type = self.instance.payment_type

        if payment_type == 'is_leasing':
            self.fields['turnover'].required = True
            self.fields['count_of_contracts'].required = True
            self.fields['amount_of_leasing'].required = True
            self.fields['turnover'].allow_null = False
            self.fields['count_of_contracts'].allow_null = False
            self.fields['amount_of_leasing'].allow_null = False
            self.fields['bank_for_leasing'].allow_null = False

    def validate_down_payment_percent(self, value):
        """Валидация первоначального взноса"""
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "Процент первоначального взноса должен быть от 0 до 100."
            )
        return value

    def validate(self, data):
        request = self.context.get('request')
        instance = getattr(self, 'instance', None)
        user = request.user if request else None

        if not instance:
            payment_type = data.get('payment_type')
            product = data.get('product')

            if payment_type == 'is_leasing':
                required_fields = [
                    'turnover', 'count_of_contracts',
                    'amount_of_leasing', 'bank_for_leasing'
                    ]
                missing_fields = [
                    field for field in required_fields if not data.get(field)
                ]

                if missing_fields:
                    raise serializers.ValidationError(
                        f"Для лизинга обязательны поля: {
                            ', '.join(missing_fields)
                        }"
                    )

            if not product:
                raise serializers.ValidationError("Не указан товар")

            selected_options = data.get('selected_additional_options', [])
            valid_options = AdditionalOption.objects.filter(
                id__in=[opt.id for opt in selected_options],
                product=product
            )

            if len(selected_options) != valid_options.count():
                raise serializers.ValidationError(
                    "Некорректные дополнительные опции"
                )

        if instance and user:
            if instance.user == user:
                changed_fields = set(data.keys()) - {'down_payment_percent'}
                if changed_fields:
                    raise serializers.ValidationError(
                        """Вы можете изменять только
                        процент первоначального взноса"""
                    )

            if 'down_payment_percent' in data:
                percent = data['down_payment_percent']
                if percent < 0 or percent > 101:
                    raise serializers.ValidationError(
                        """Процент первоначального
                        взноса должен быть от 0 до 101"""
                    )

                data['first_payment'] = instance.amount * percent / 100

        return data


class OrderDetailSerializer(OrderSerializer):
    product_images = serializers.SerializerMethodField()
    delivery_days = serializers.IntegerField(
        source='product.delivery_time',
        read_only=True
    )

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + [
            'product_images', 'delivery_days', 'delivery_number'
        ]

    def get_product_images(self, obj):
        """Retrieve product images"""
        photos = getattr(obj.product, 'photos', None)
        if not photos:
            return []

        return [
            photo.image.url for photo in photos.all()
            if hasattr(photo, 'image') and photo.image
        ]

# {
#   "product": 4,
#   "selected_options": [1, 2],
#   "payment_type": "is_cash",
#   "address": "Moscow",
#   "down_payment_percent": 10
# }
# нужно чтоб заказ сохранялся с компанией, и опциями


class OrderManagerAssignmentSerializer(serializers.ModelSerializer):
    """Сериализатор для связи менеджера заказа с компанией"""

    class Meta:
        model = OrderManagerAssignment
        fields = '__all__'

    def validate_manager(self, value):
        """
        Проверяем, что менеджер существует и является активным.
        """
        if not value.is_active:
            raise serializers.ValidationError("Менеджер неактивен.")
        return value

    def validate_order(self, value):
        """
        Проверяем, что заказ существует.
        """
        if not Order.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Заказ не существует.")
        return value


class DeliveryOrderSerializer(serializers.ModelSerializer):
    dimensions = DimensionsSerializer(read_only=True)
    # can_edit = serializers.SerializerMethodField()

    class Meta:
        model = DeliveryOrder
        fields = [
            'id', 'number', 'date_created', 'user', 'delivery_stage',
            'delivery_type', 'amount', 'dimensions', 'date_delivery',
            'cargo', 'company', 'address_delivery', 'order'
        ]
        read_only_fields = [
            'number', 'date_created', 'user',
            'dimensions', 'amount', 'cargo', 'company'
        ]
        
    # def get_can_edit(self, obj):
    #     request = self.context.get('request')
    #     if not request or not request.user.is_authenticated:
    #         return False
            
    #     return (hasattr(obj.order, 'manager_assignment') and
    #             obj.order.manager_assignment.manager == request.user)

    def get_dimensions(self, obj):
        dimensions = Dimensions.objects.filter(product=obj.cargo).first()
        return DimensionsSerializer(dimensions).data if dimensions else None

    def validate(self, data):
        if not self.context['request'].user.is_authenticated:
            raise NotAuthenticated(
                "Для начала авторизуйтесь или зарегистрируйтесь."
            )

        order = data.get('order')
        if order.stage != 'Stage_3':
            raise serializers.ValidationError(
                "Доставку можно оформить только для заказов на этапе Stage_3"
            )
        return data


class DeliveryOrderCreateSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        required=False, max_digits=10, decimal_places=2
    )
    cargo = serializers.PrimaryKeyRelatedField(
        required=False, queryset=Product.objects.all()
    )
    date_delivery = serializers.DateField(required=False)
    dimensions = serializers.PrimaryKeyRelatedField(
        write_only=True,
        required=False,
        queryset=Dimensions.objects.all(),
        allow_null=True
    )

    class Meta(DeliveryOrderSerializer.Meta):
        read_only_fields = [
            f for f in DeliveryOrderSerializer.Meta.read_only_fields if f not in ['amount', 'cargo']
        ]
