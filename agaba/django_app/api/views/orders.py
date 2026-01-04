# Добавить короткое отображение товара.
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import NotAuthenticated
from rest_framework.exceptions import PermissionDenied

from rest_framework import viewsets, serializers
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from account.models import CustomUser
from products.models import (
    AdditionalOption,
    Product
)
from order.models import (
    Order, OrderManagerAssignment,
    DeliveryOrder, Bank
)

from order.serializers import (
    OrderSerializer,
    OrderDetailSerializer,
    OrderManagerAssignmentSerializer,
    DeliveryOrderSerializer,
    DeliveryOrderCreateSerializer
)
from ..permissions import (
    IsAdminOrManager, OrderUpdatePermission,
    CanCreateDelivery, DeliveryAccessPermission,
)

from django_app.services import send_notification


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'product', 'user', 'company'
    ).order_by('-date_created')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, OrderUpdatePermission]
    filterset_fields = ['status', 'stage', 'payment_type']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        user = self.request.user
        if user.is_superuser:
            return self.queryset

        # Менеджеры видят только назначенные им заказы
        if hasattr(user, 'role') and user.role == 'manager':
            return self.queryset.filter(
                manager_assignment__manager=user
            )

        # Обычные пользователи видят только свои заказы
        return self.queryset.filter(user=user)

    @swagger_auto_schema(
        operation_summary="Создать новый заказ",
        operation_description="""
        Создает заказ с автоматическим расчетом:
        - суммы заказа (цена товара + доп. опции)
        - первоначального взноса
        - генерацией номеров заказа и доставки
        При payment_type=is_leasing обязательны дополнительные поля:
        - turnover
        - count_of_contracts
        - amount_of_leasing
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product', 'payment_type'],
            properties={
                'product': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID товара'
                ),
                'additional_options': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_INTEGER),
                    description='ID выбранных доп. опций'
                ),
                'payment_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['is_cash', 'is_leasing'],
                    description='Тип оплаты'
                ),
                'address': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Адрес доставки'
                ),
                'down_payment_percent': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    default=10,
                    description='Процент первоначального взноса'
                ),
                'company': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Компания'
                ),
                'turnover': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    format=openapi.FORMAT_DECIMAL,
                    description='Оборот (обязателен при leasing)',
                ),
                'count_of_contracts': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="""
                    Количество контрактов (обязателен при leasing)
                    """
                ),
                'amount_of_leasing': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    format=openapi.FORMAT_DECIMAL,
                    description="""
                    Сумма покупки на лизинг (обязателен при leasing)
                    """
                ),
                'bank': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='Банк для линзинга (обязателен при leasing)'
                )
            }
        ),
        responses={
            201: OrderDetailSerializer,
            400: "Неверные данные (не указан товар или некорректные опции)",
            401: "Требуется авторизация",
            403: "Нет прав на создание заказа"
        }
    )
    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def perform_create(self, serializer):
        """Дополнительная обработка при создании заказа"""
        product_id = self.request.data.get('product')
        selected_options = self.request.data.get('additional_options', [])
        down_payment_percent = self.request.data.get(
            'down_payment_percent', 10
        )
        bank_id = self.request.data.get('bank_for_leasing', None)

        bank = get_object_or_404(Bank, id=bank_id) if bank_id else None

        try:
            product = Product.objects.get(id=product_id)
            product_price = product.cur_price
        except Product.DoesNotExist:
            raise ValueError("Указанный продукт не существует")

        # Рассчитываем сумму дополнительных опций
        options_total = Decimal('0')
        if selected_options:
            options = AdditionalOption.objects.filter(id__in=selected_options)
            options_total = sum(option.price for option in options)

        total_amount = product_price + options_total

        # Рассчитываем первый взнос
        first_payment = (
            total_amount * Decimal(down_payment_percent / 100)
        ).quantize(Decimal('0.01'))

        order = serializer.save(
            user=self.request.user,
            amount=total_amount,
            first_payment=first_payment,
            bank_for_leasing=bank
        )
        # Отправляем уведомление через WebSocket
        send_notification(
            user_id=self.request.user.id,
            message_type='order_created',
            data={
                'order_nuber': str(order.number),
                'total_amount': str(order.amount),
                'product_name': order.product.name,
                'brand': order.product.brand,
                'subcategory': order.product.subcategory.name,
                'year_of_release': str(order.product.year_of_release),
            }
        )
        if selected_options:
            order.selected_additional_options.set(options)

        # Назначение менеджера
        manager = self._assign_manager()
        if manager:
            OrderManagerAssignment.objects.create(order=order, manager=manager)

    def _assign_manager(self):
        """Логика автоматического назначения менеджера"""
        return CustomUser.objects.filter(
            is_staff=True,
            is_active=True
        ).order_by('?').first()

    @swagger_auto_schema(
        operation_summary="Список заказов",
        operation_description="""
        Возвращает список заказов с пагинацией.
        Для администраторов - все заказы, для пользователей - только свои.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Фильтр по статусу'
            ),
            openapi.Parameter(
                name='stage',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Фильтр по этапу'
            )
        ],
        responses={
            200: OrderSerializer(many=True),
            401: "Требуется авторизация"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderDetailViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related(
        'product', 'user', 'company'
    ).order_by('-date_created')
    serializer_class = OrderDetailSerializer
    permission_classes = [IsAuthenticated, OrderUpdatePermission]
    http_method_names = ['get', 'patch', 'put', 'delete']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        user = self.request.user
        if user.is_superuser:
            return self.queryset

        # Менеджеры видят доставки, связанные с их заказами
        if hasattr(user, 'role') and user.role == 'manager':
            return self.queryset.filter(
                manager_assignment__manager=user
            )

        return self.queryset.filter(user=user)

    @swagger_auto_schema(
        operation_summary="Детали заказа",
        operation_description="Полная информация о заказе с товаром и опциями",
        responses={
            200: OrderDetailSerializer,
            401: "Требуется авторизация",
            403: "Нет прав на просмотр заказа",
            404: "Заказ не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить заказ",
        operation_description="""
        Полное обновление заказа (только для владельца/админа)
        """,
        request_body=OrderDetailSerializer,
        responses={
            200: OrderDetailSerializer,
            400: "Неверные данные",
            401: "Требуется авторизация",
            403: "Нет прав на обновление",
            404: "Заказ не найден"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частичное обновление заказа",
        operation_description="""
        Обновление отдельных полей заказа
        Чаще будет использоваться для менеджеров,
        что бы изменить статус заказа.
        Stage_1 - ожидание оплаты
        Stage_2 - в процессе оформления
        Stage_3 - отгрузка
        Stage_4 - заказ отгружен
        """,
        request_body=OrderDetailSerializer,
        responses={
            200: OrderDetailSerializer,
            400: "Неверные данные",
            401: "Требуется авторизация",
            403: "Нет прав на обновление",
            404: "Заказ не найден"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()

        old_stage = instance.stage

        response = super().partial_update(request, *args, **kwargs)

        new_stage = instance.stage
        if old_stage != new_stage:
            send_notification(
                user_id=instance.user.id,
                message_type='order_stage_updated',
                data={
                    'order_number': instance.number,
                    'new_stage': new_stage,
                }
            )

        return response

    @swagger_auto_schema(
        operation_summary="Удалить заказ",
        operation_description="Удаление заказа (только для владельца/админа)",
        responses={
            204: "Заказ удален",
            401: "Требуется авторизация",
            403: "Нет прав на удаление",
            404: "Заказ не найден"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method='get',
        operation_summary="Данные для первого этапа заказа",
        operation_description="""
        Информация для отображения на первом этапе оформления
        """,
        responses={
            200: openapi.Response(
                description="Данные первого этапа",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'order': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'id': openapi.Schema(
                                    type=openapi.TYPE_INTEGER
                                ),
                                'number': openapi.Schema(
                                    type=openapi.TYPE_STRING
                                ),
                            }
                        ),
                        'product_images': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(type=openapi.TYPE_STRING)
                        )
                    }
                )
            ),
            404: "Заказ не найден"
        }
    )
    @action(detail=True, methods=['get'])
    def first_step(self, request, pk=None):
        """Получение данных для первого этапа оформления заказа"""
        order = self.get_object()
        serializer = self.get_serializer(order)
        # Получаем URL изображений товара
        product_images = []
        for photo in order.product.photos.all():
            if hasattr(photo, 'image') and photo.image:
                product_images.append(photo.image.url)
        return Response({
            'order': serializer.data,
            'product_images': product_images
        })


class OrderManagerAssignmentViewSet(viewsets.ModelViewSet):
    queryset = OrderManagerAssignment.objects.all()
    serializer_class = OrderManagerAssignmentSerializer
    http_method_names = ['get', 'post', 'patch']
    permission_classes = [IsAdminOrManager]

    @swagger_auto_schema(
        operation_summary="Переопределить менеджера заказа",
        operation_description="""Переопределяет менеджера заказа""",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id', 'order', 'manager'],
            properties={
                'id': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID товара'
                ),
                'order': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID заказа'
                ),
                'manager': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID менеджера'
                ),
            }
        ),
        responses={
            201: OrderDetailSerializer,
            400: "Неверные данные (не указан заказ или некорректные данные)",
            401: "Требуется авторизация",
            403: "Нет прав на переназначение менеджера"
        }
    )
    @action(detail=False, methods=['patch'], url_path='assign-manager')
    def assign_manager(self, request, *args, **kwargs):
        """
        Назначить нового менеджера к заказу.
        """
        order_id = request.data.get('order')
        manager_id = request.data.get('manager')

        if not order_id or not manager_id:
            return Response(
                {"error": "Необходимо указать 'order' и 'manager'."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Заказ не существует."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            manager = CustomUser.objects.get(id=manager_id)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Менеджер не существует."},
                status=status.HTTP_404_NOT_FOUND
            )

        # # Проверяем, что менеджер активен
        # if not manager.is_active:
        #     return Response(
        #         {"error": "Менеджер неактивен."},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )

        if manager.role != 'manager':
            return Response(
                {"error": "Пользователь не является менеджером."},
                status=status.HTTP_400_BAD_REQUEST
            )
        assignment, created = OrderManagerAssignment.objects.update_or_create(
            order=order,
            defaults={'manager': manager}
        )


        serializer = self.get_serializer(assignment)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeliveryOrderViewSet(viewsets.ModelViewSet):
    queryset = DeliveryOrder.objects.select_related(
        'user', 'cargo', 'company', 'order'
    ).prefetch_related(
        'order__manager_assignment'
    ).order_by('-date_created')

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()
        user = self.request.user
        if user.is_superuser:
            return self.queryset

        if hasattr(user, 'role') and user.role == 'manager':
            return self.queryset.filter(
                order__manager_assignment__manager=user
            )

        return self.queryset.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'create':
            return DeliveryOrderCreateSerializer
        return DeliveryOrderSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [CanCreateDelivery()]
        return [DeliveryAccessPermission()]

    @swagger_auto_schema(
        operation_summary="Создать доставку заказа",
        operation_description="""
        Создает запись о доставке с автоматическим заполнением:
        - пользователя (текущий авторизованный)
        - товара (из заказа)
        - компании (из заказа)
        - суммы (из заказа)
        - габаритов (из характеристик товара)

        Доступно только для заказов на этапе Stage_3.
        Создать может только владелец заказа или администратор.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['order', 'delivery_type', 'address_delivery'],
            properties={
                'order': openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description='ID заказа'
                ),
                'delivery_type': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['trall', 'train', 'sea', 'self'],
                    description='Тип доставки'
                ),
                'address_delivery': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Адрес доставки'
                ),
            }
        ),
        responses={
            201: DeliveryOrderSerializer,
            400: "Неверные данные(неверный ID заказа или заказ не на Stage_3)",
            401: "Требуется авторизация",
            403: "Нет прав на создание доставки"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Список доставок",
        operation_description="""
        Возвращает список доставок с пагинацией.
        Для администраторов - все доставки.
        Для менеджеров - доставки их заказов.
        Для пользователей - только их доставки.
        Для создателей товара - доставки их товаров.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='delivery_stage',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Фильтр по этапу доставки'
            ),
            openapi.Parameter(
                name='delivery_type',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Фильтр по типу доставки'
            ),
            openapi.Parameter(
                name='order',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description='Фильтр по ID заказа'
            )
        ],
        responses={
            200: DeliveryOrderSerializer(many=True),
            401: "Требуется авторизация"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Детали доставки",
        operation_description="""
        Возвращает полную информацию о доставке.
        Доступно для:
        - администраторов
        - менеджеров заказа
        - владельца доставки
        - создателя товара
        """,
        responses={
            200: DeliveryOrderSerializer,
            401: "Требуется авторизация",
            403: "Нет прав доступа",
            404: "Доставка не найдена"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить доставку",
        operation_description="""
        Обновляет информацию о доставке.
        Доступно для администраторов и менеджеров заказа.
        """,
        request_body=DeliveryOrderCreateSerializer,
        responses={
            200: DeliveryOrderSerializer,
            400: "Неверные данные",
            401: "Требуется авторизация",
            403: "Нет прав на обновление",
            404: "Доставка не найдена"
        }
    )
    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        if not (request.user.is_superuser or instance.user == request.user):
            raise PermissionDenied(
                """Только менеджер заказа или
                администратор могут изменять дату доставки"""
                )

        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частично обновить доставку",
        operation_description="""
        Частично обновляет информацию о доставке.
        Доступно для администраторов и менеджеров заказа.
        """,
        request_body=DeliveryOrderCreateSerializer,
        responses={
            200: DeliveryOrderSerializer,
            400: "Неверные данные",
            401: "Требуется авторизация",
            403: "Нет прав на обновление",
            404: "Доставка не найдена"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить доставку",
        operation_description="""
        Удаляет запись о доставке.
        Доступно только для администраторов.
        """,
        responses={
            204: "Доставка удалена",
            401: "Требуется авторизация",
            403: "Нет прав на удаление",
            404: "Доставка не найдена"
        }
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.validated_data['order']
        product = order.product
        # Рассчитываем сумму для доставки (общая сумма - первый взнос)
        delivery_amount = order.amount - order.first_payment
        dimensions = getattr(product, 'dimensions', None)
        # Автоматический расчет даты (если не передана вручную)
        date_delivery = serializer.validated_data.get('date_delivery')
        if not date_delivery:
            try:
                if product.delivery_time:
                    now = timezone.now()
                    date_delivery = now + timezone.timedelta(
                        days=product.delivery_time
                    )
                    date_delivery = date_delivery.date()
            except AttributeError:
                pass
            if not self.request.user.is_authenticated:
                raise NotAuthenticated(
                    "Для начала авторизуйтесь или зарегистрируйтесь."
                )

        serializer.save(
            user=self.request.user,
            cargo=product,
            company=order.company,
            amount=delivery_amount,
            dimensions=dimensions,
            number=order.delivery_number,
            date_delivery=date_delivery
        )


class DetailDeliveryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryOrderSerializer
    permission_classes = [DeliveryAccessPermission]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Order.objects.none()

        user = self.request.user

        if not user.is_authenticated:
            raise NotAuthenticated(
                "Для начала авторизуйтесь или зарегистрируйтесь."
            )

        if user.is_superuser:
            return DeliveryOrder.objects.all()

        queryset = DeliveryOrder.objects.filter(user=user)

        if hasattr(user, 'role') and user.role == 'manager':
            queryset |= DeliveryOrder.objects.filter(
                order__manager_assignment__manager=user
            )

        queryset |= DeliveryOrder.objects.filter(cargo__user=user)

        return queryset.distinct().order_by('-date_created')
