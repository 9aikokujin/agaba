from django.db import models
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import viewsets, serializers
from rest_framework.permissions import (
    AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
)
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action

from ..mixins import AuthorOrAdminPermissionMixin

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from django.db.models import Prefetch


from account.paginations import (
    ProductPagination
)
from products.models import (
    Product, PriceHistory, Category, Subcategory,
    Attribute, ProductAttribute, ProductDocument,
    ProductPhoto, Dimensions, AdditionalOption,
    Question, Comparison, ProductReview, Favorite,
    # Answer,
)
from products.serializers import (
    ProductSerializer, PriceHistorySerializer,
    AttributeSerializer, ProductAttributeSerializer,
    ProductDocumentSerializer, ProductPhotoSerializer,
    DimensionsSerializer, AdditionalOptionSerializer,
    CategorySerializer, SubcategorySerializer,
    QuestionSerializer, ProductShortSerializer,
    # AnswerSerializer,
    ComparisonSerializer, ProductComparisonSerializer,
    ProductReviewSerializer, FavoriteSerializer
)
from ..permissions import (
    ReadOnly,
    IsSellerOrAdminOrReadOnly,
    IsAuthorOrSuperuser, CanLeaveReview
)



class ProductViewSet(AuthorOrAdminPermissionMixin, viewsets.ModelViewSet):
    queryset = Product.objects.select_related(
        'category', 'subcategory', 'author', 'company'
    ).prefetch_related(
        Prefetch(
            'attributes',
            queryset=ProductAttribute.objects.select_related('attribute')
        ),
        'documents', 'photos', 'additional_options',
        Prefetch(
            'product_reviews',
            queryset=ProductReview.objects.filter(
                status='approved'
            )
        )
    ).order_by('-created_at')
    serializer_class = ProductSerializer
    pagination_class = ProductPagination
    filter_backends = [DjangoFilterBackend]
    filter_fields = [
        'brand', 'name', 'category',
        'category__name', 'author', 'condition',
        'delivery_time', 'location',
        'subcategory', 'subcategory__name',
        'availability', 'status', 'cur_price', 'rating'
    ]
    read_only_fields = ['rating']

    def get_permissions(self):
        """
        Определяем разные разрешения для разных действий.
        """
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsSellerOrAdminOrReadOnly()]

    @swagger_auto_schema(
        operation_summary="Создать новый товар",
        operation_description="""Создает новый товар.
         Только для продавцов и администраторов.""",
        request_body=ProductSerializer,
        responses={
            201: openapi.Response(
                description="Товар успешно создан",
                examples={
                    "application/json": {
                        "id": 1,
                        "brand": "Toyota",
                        "name": "Corolla",
                        "slug": "toyota-corolla-2023",
                        "description": "Надежный автомобиль...",
                        "cur_price": 25000,
                        "category": 1,
                        "subcategory": 2,
                        "author": 1,
                        "company": 1,
                        "condition": "new",
                        "delivery_time": 7,
                        "availability": "in_stock",
                        "location": "Moscow",
                        "min_deposit": 5000,
                        "video_url": "https://example.com/video.mp4",
                        "status": "active",
                        "created_at": "2025-04-02T12:02:47...",
                        "updated_at": "2025-04-02T12:02:47..."
                    }
                }
            ),
            400: "Неверный запрос",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Переопределение метода для создания нового товара.
        """
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Автоматически привязывает автора (текущего пользователя)
        к создаваемому товару.
        """
        serializer.save(author=self.request.user)

    @swagger_auto_schema(
        operation_summary="Получить список товаров",
        operation_description="Возвращает список всех товаров с пагинацией.",
        manual_parameters=[
            openapi.Parameter(
                name='page',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Номер страницы",
                required=False
            ),
            openapi.Parameter(
                name='page_size',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Количество элементов на странице",
                required=False
            )
        ],
        responses={
            200: openapi.Response(
                description="Список товаров с пагинацией",
                examples={
                    "application/json": {
                        "count": 50,
                        "next": "http://domain/api/v1/products/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "brand": "Toyota",
                                "name": "Corolla",
                                "slug": "toyota-corolla-2023",
                                "description": "Надежный автомобиль...",
                                "cur_price": 25000,
                                "category": 1,
                                "subcategory": 2,
                                "author": 1,
                                "company": 1,
                                "condition": "new",
                                "delivery_time": 7,
                                "availability": "in_stock",
                                "location": "Moscow",
                                "min_deposit": 5000,
                                "video_url": "https://example.com/video.mp4",
                                "status": "active",
                                "created_at": "2025-04-02T12:02:47...",
                                "updated_at": "2025-04-02T12:02:47..."
                            }
                        ]
                    }
                }
            ),
            401: "Неавторизованный доступ (только для некоторых методов)"
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Переопределение метода для получения списка товаров.
        """
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['get'], url_path='short')
    def short(self, request, *args, **kwargs):
        """
        Возвращает краткую информацию о товарах.
        """
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ProductShortSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = ProductShortSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Получить товар по ID",
        operation_description="Возвращает информацию о конкретном товаре.",
        responses={
            200: openapi.Response(
                description="Информация о товаре",
                examples={
                    "application/json": {
                        "id": 1,
                        "brand": "Toyota",
                        "name": "Corolla",
                        "slug": "toyota-corolla-2023",
                        "description": "Надежный автомобиль...",
                        "cur_price": 25000,
                        "category": 1,
                        "subcategory": 2,
                        "author": 1,
                        "company": 1,
                        "condition": "new",
                        "delivery_time": 7,
                        "availability": "in_stock",
                        "location": "Moscow",
                        "min_deposit": 5000,
                        "video_url": "https://example.com/video.mp4",
                        "status": "active",
                        "created_at": "2025-04-02T12:02:47...",
                        "updated_at": "2025-04-02T12:02:47..."
                    }
                }
            ),
            404: "Товар не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Переопределение метода для получения товара по ID.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Обновить товар",
        operation_description="""Обновляет существующий товар.
         Только для продавцов и администраторов.""",
        request_body=ProductSerializer,
        responses={
            200: openapi.Response(
                description="Товар успешно обновлен",
                examples={
                    "application/json": {
                        "id": 1,
                        "brand": "Toyota",
                        "name": "Corolla",
                        "slug": "toyota-corolla-2023",
                        "description": "Надежный автомобиль...",
                        "cur_price": 24000,
                        "category": 1,
                        "subcategory": 2,
                        "author": 1,
                        "company": 1,
                        "condition": "new",
                        "delivery_time": 7,
                        "availability": "in_stock",
                        "location": "Moscow",
                        "min_deposit": 5000,
                        "video_url": "https://example.com/video.mp4",
                        "status": "active",
                        "created_at": "2025-04-02T12:02:47.570489+03:00",
                        "updated_at": "2025-04-02T12:02:47.570489+03:00"
                    }
                }
            ),
            400: "Неверный запрос",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен",
            404: "Товар не найден"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Переопределение метода для обновления товара.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Частично обновить товар",
        operation_description="""Частично обновляет существующий товар.
        Только для продавцов и администраторов.""",
        request_body=ProductSerializer,
        responses={
            200: openapi.Response(
                description="Товар успешно обновлен",
                examples={
                    "application/json": {
                        "id": 1,
                        "brand": "Toyota",
                        "name": "Corolla",
                        "slug": "toyota-corolla-2023",
                        "description": "Надежный автомобиль...",
                        "cur_price": 24000,
                        "category": 1,
                        "subcategory": 2,
                        "author": 1,
                        "company": 1,
                        "condition": "new",
                        "delivery_time": 7,
                        "availability": "in_stock",
                        "location": "Moscow",
                        "min_deposit": 5000,
                        "video_url": "https://example.com/video.mp4",
                        "status": "active",
                        "created_at": "2025-04-02T12:02:47.570489+03:00",
                        "updated_at": "2025-04-02T12:02:47.570489+03:00"
                    }
                }
            ),
            400: "Неверный запрос",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен",
            404: "Товар не найден"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Переопределение метода для частичного обновления товара.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить товар",
        operation_description="""Удаляет товар.
         Только для продавцов и администраторов.""",
        responses={
            204: "Товар успешно удален",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен",
            404: "Товар не найден"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Переопределение метода для удаления товара.
        """
        return super().destroy(request, *args, **kwargs)


class PriceHistoryViewSet(viewsets.ModelViewSet):
    queryset = PriceHistory.objects.order_by('-changed_at')
    serializer_class = PriceHistorySerializer
    http_method_names = ['get',]


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_fields = [
        'name', 'slug',
    ]


class SubcategoryViewSet(viewsets.ModelViewSet):
    queryset = Subcategory.objects.all()
    serializer_class = SubcategorySerializer
    permission_classes = [ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_fields = [
        'name', 'slug',
    ]


class AttributeViewSet(viewsets.ModelViewSet):
    queryset = Attribute.objects.all()
    serializer_class = AttributeSerializer
    permission_classes = [ReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_fields = [
        'name',
    ]


class ProductAttributeViewSet(viewsets.ModelViewSet):
    queryset = ProductAttribute.objects.all()
    serializer_class = ProductAttributeSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]


class ProductDocumentViewSet(viewsets.ModelViewSet):
    queryset = ProductDocument.objects.all()
    serializer_class = ProductDocumentSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]


class ProductPhotoViewSet(viewsets.ModelViewSet):
    queryset = ProductPhoto.objects.all()
    serializer_class = ProductPhotoSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]


class DimensionsViewSet(viewsets.ModelViewSet):
    queryset = Dimensions.objects.all()
    serializer_class = DimensionsSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]


class AdditionalOptionViewSet(viewsets.ModelViewSet):
    queryset = AdditionalOption.objects.all()
    serializer_class = AdditionalOptionSerializer
    permission_classes = [IsSellerOrAdminOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer

    def get_permissions(self):
        """
        Динамическое назначение пермишенов в зависимости от действия.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        elif self.action in ['create']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthorOrSuperuser]
        return [permission() for permission in permission_classes]


# class AnswerViewSet(viewsets.ModelViewSet):
#     queryset = Answer.objects.all()
#     serializer_class = AnswerSerializer


class ComparisonViewSet(viewsets.ModelViewSet):
    queryset = Comparison.objects.all()
    serializer_class = ComparisonSerializer
    permission_classes = [AllowAny]

    def _get_session_key(self):
        return (
            self.request.query_params.get('session_key')
            or self.request.headers.get('X-Session-Key')
            or getattr(self.request.session, 'session_key', None)
        )

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Comparison.objects.filter(user=user)

        session_key = self._get_session_key()
        if not session_key:
            return Comparison.objects.none()

        return Comparison.objects.filter(session_key=session_key)

    @swagger_auto_schema(
        operation_summary="Создать новое сравнение",
        operation_description="""
        Создает новое сравнение товаров или обновляет существующее.
        Доступно только авторизованным пользователям.
        Пользователь автоматически привязывается к сравнению.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['products'],
            properties={
                "products": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(type=openapi.TYPE_INTEGER),
                    description="Список ID товаров для сравнения"
                ),
                "session_key": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Ключ сессии (необязательно)",
                    nullable=True
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Сравнение успешно создано или обновлено",
                examples={
                    "application/json": {
                        "id": 1,
                        "products": [1, 2, 3],
                        "user": 1,
                        "session_key": None,
                        "timestamp": 1698765432
                    }
                }
            ),
            400: "Неверный запрос (например, отсутствуют необходимые поля)",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен"
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Переопределение метода для создания/обновления сравнения.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Получить все продукты из сравнений пользователя",
        operation_description="""
        Возвращает список всех продуктов, добавленных
        сравнение текущего пользователя.
        Доступно только авторизованным пользователям.
        """,
        responses={
            200: openapi.Response(
                description="Список всех продуктов в сравнении",
                examples={
                    "application/json": [
                        {
                            "first_photo": "Ссылка на фото продукта",
                            "brand": "Brand A",
                            "name": "Product 1",
                            "cur_price": "100.00",
                            "subcategory": "Subcategory A",
                            "year_of_release": 2022,
                            "availability": "in_stock",
                            "characteristics": {
                                "Цвет": "Красный",
                                "Вес": "1.5 кг"
                            }
                        }
                    ]
                }
            ),
            401: "Неавторизованный доступ"
        }
    )
    @action(detail=False, methods=['get'], url_path='all-products')
    def get_all_comparison_products(self, request):
        """
        Возвращает все продукты, добавленные в сравнение текущего пользователя.
        """
        user = request.user
        session_key = None
        if not user.is_authenticated:
            session_key = self._get_session_key()
            if not session_key:
                return Response(
                    {"detail": "session_key is required for anonymous users."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        try:
            if user.is_authenticated:
                comparison = Comparison.objects.get(user=user)
            else:
                comparison = Comparison.objects.get(session_key=session_key)
            products = comparison.products.all()
            serializer = ProductComparisonSerializer(products, many=True)
            return Response(serializer.data)
        except Comparison.DoesNotExist:
            return Response(
                {"detail": "Сравнение не найдено."},
                status=status.HTTP_404_NOT_FOUND
            )


class ProductReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ProductReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, CanLeaveReview]
    pagination_class = None

    def get_queryset(self):
        user = self.request.user
        queryset = ProductReview.objects.all()

        if not user.is_authenticated:
            return queryset.filter(status='approved')

        if user.is_superuser or user.role in ['moderator', 'modertor']:
            return queryset

        return queryset.filter(
            models.Q(user=user) | models.Q(status='approved')
        )

    @swagger_auto_schema(
        operation_summary="Создать новый отзыв",
        operation_description="""
        Создает новый отзыв для продукта.
        Отзыв автоматически привязывается к текущему пользователю.
        После создания отзыв отправляется на модерацию.
        Доступно только авторизованным пользователям.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['product', 'rating', 'comment', 'pros', 'cons'],
            properties={
                "product": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID продукта, для которого оставляется отзыв"
                ),
                "rating": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Оценка продукта (от 1 до 5)",
                    minimum=1,
                    maximum=5
                ),
                "comment": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Текст отзыва"
                ),
                "pros": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Плюсы"
                ),
                "cons": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Минусы"
                )
            }
        ),
        responses={
            201: openapi.Response(
                description="Отзыв успешно создан",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 1,
                        "product": 1,
                        "rating": 5,
                        "text": "Отличный продукт!",
                        "status": "moderation",
                        "created_at": "2023-10-01T12:00:00Z"
                    }
                }
            ),
            400: """
            Неверный запрос
            (например, отсутствуют необходимые поля
            или рейтинг вне диапазона)
            """,
            401: "Неавторизованный доступ",
            403: """
            Пользователь не имеет права оставлять отзыв
            (например, уже оставил отзыв)
            """
        }
    )
    def create(self, request, *args, **kwargs):
        """
        Переопределение метода для создания нового отзыва.
        После создания отзыва возвращаем данные о продукте и отзыве.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        review = serializer.instance

        product_serializer = ProductShortSerializer(review.product)

        response_data = {
            "product": product_serializer.data,
            "review": serializer.data
        }

        headers = self.get_success_headers(serializer.data)
        return Response(
            response_data, status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_summary="Получить список отзывов",
        operation_description="""
        Возвращает список отзывов в зависимости от роли пользователя:
        - Анонимные пользователи видят только утвержденные отзывы.
        - Авторизованные пользователи видят свои отзывы независимо
        от статуса и утвержденные отзывы других пользователей.
        - Модераторы и администраторы видят все отзывы.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='product',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_INTEGER,
                description="Фильтр по ID продукта (необязательно)"
            ),
            openapi.Parameter(
                name='status',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description="""
                Фильтр по статусу
                ('approved', 'rejected', 'moderation') (необязательно)
                """
            )
        ],
        responses={
            200: openapi.Response(
                description="Список отзывов",
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "user": 1,
                            "product": 1,
                            "rating": 5,
                            "text": "Отличный продукт!",
                            "status": "approved",
                            "created_at": "2023-10-01T12:00:00Z"
                        },
                        {
                            "id": 2,
                            "user": 2,
                            "product": 1,
                            "rating": 4,
                            "text": "Хороший продукт, но дорогой.",
                            "status": "moderation",
                            "created_at": "2023-10-02T15:30:00Z"
                        }
                    ]
                }
            ),
            401: """
            Неавторизованный доступ
            (если требуется просмотр скрытых отзывов)
            """
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Переопределение метода для получения списка отзывов.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить конкретный отзыв",
        operation_description="""
        Возвращает конкретный отзыв по его ID.
        Доступность отзыва зависит от роли пользователя:
        - Анонимные пользователи могут видеть только утвержденные отзывы.
        - Авторизованные пользователи могут видеть
        свои отзывы независимо от статуса.
        - Модераторы и администраторы могут видеть любой отзыв.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID отзыва",
                required=True
            )
        ],
        responses={
            200: openapi.Response(
                description="Информация об отзыве",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 1,
                        "product": 1,
                        "rating": 5,
                        "text": "Отличный продукт!",
                        "status": "approved",
                        "created_at": "2023-10-01T12:00:00Z"
                    }
                }
            ),
            401: "Неавторизованный доступ",
            403: "Доступ запрещен.",
            404: "Отзыв не найден"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Переопределение метода для получения конкретного отзыва.
        """
        return super().retrieve(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, status='moderation')

    @swagger_auto_schema(
        operation_summary="Обновить отзыв",
        operation_description="""
        Обновляет текст и/или рейтинг существующего отзыва.
        Доступно только владельцу отзыва или модераторам/администраторам.
        Статус отзыва может быть изменен только модераторами.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "rating": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Новый рейтинг продукта (от 1 до 5)",
                    minimum=1,
                    maximum=5
                ),
                "text": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Новый текст отзыва"
                ),
                "status": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="""
                    Новый статус отзыва
                    ('approved', 'rejected', 'moderation')
                    (только для модераторов)
                    """,
                    enum=["approved", "rejected", "moderation"]
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Отзыв успешно обновлен",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 1,
                        "product": 1,
                        "rating": 4,
                        "text": "Хороший продукт, но цена высокая.",
                        "status": "moderation",
                        "created_at": "2023-10-01T12:00:00Z"
                    }
                }
            ),
            400: "Неверный запрос (например, рейтинг вне диапазона)",
            401: "Неавторизованный доступ",
            403: "Доступ запрещен.",
            404: "Отзыв не найден"
        }
    )
    def update(self, request, *args, **kwargs):
        """
        Переопределение метода для обновления отзыва.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Удалить отзыв",
        operation_description="""
        Удаляет отзыв.
        Доступно только владельцу отзыва или модераторам/администраторам.
        """,
        manual_parameters=[
            openapi.Parameter(
                name='pk',
                in_=openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID отзыва",
                required=True
            )
        ],
        responses={
            204: openapi.Response(
                description="Отзыв успешно удален"
            ),
            401: "Неавторизованный доступ",
            403: "Доступ запрещен.",
            404: "Отзыв не найден"
        }
    )
    def destroy(self, request, *args, **kwargs):
        """
        Переопределение метода для удаления отзыва.
        """
        return super().destroy(request, *args, **kwargs)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Вьюсет Избранные товары."""
    serializer_class = FavoriteSerializer
    permission_classes = [AllowAny]

    def _get_session_key(self):
        return (
            self.request.query_params.get('session_key')
            or self.request.headers.get('X-Session-Key')
            or getattr(self.request.session, 'session_key', None)
        )

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user).order_by('-created_at')

        session_key = self._get_session_key()
        if not session_key:
            return Favorite.objects.none()

        return Favorite.objects.filter(
            session_key=session_key
        ).order_by('-created_at')

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_authenticated:
            serializer.save(user=user)
            return

        session_key = self._get_session_key()
        if not session_key:
            raise serializers.ValidationError(
                "session_key обязателен для не авторизованных пользователей."
            )

        serializer.save(session_key=session_key)
