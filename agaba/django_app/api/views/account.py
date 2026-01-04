import os
from django.core.cache import cache
from django.conf import settings
from django.http import HttpResponse

from dadata import Dadata

from rest_framework import viewsets, permissions, serializers
from rest_framework.permissions import (
    AllowAny
)
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from ..utils import upload_to_minio, delete_from_minio

from account.paginations import (
    CustomUserPagination, ProductPagination
)
from account.models import Company, CustomUser

from account.serializers import (
    RegistrationOTPSerializer, BuyerVerificationSerializer,
    SellerVerificationSerializer, CompanySerializer,
    CustomUserSerializer, AvatarUpdateSerializer
)

from ..permissions import (
    IsSellerOrAdminOrReadOnly,
)


def serve_react_app(request):
    """Отображение index для React"""
    index_file = os.path.join(settings.REACT_APP_DIR, 'index.html')
    with open(index_file, 'r') as file:
        return HttpResponse(file.read())


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint для просмотра и редактирования пользователей.
    """
    queryset = CustomUser.objects.all().order_by('id')
    serializer_class = CustomUserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsSellerOrAdminOrReadOnly
    ]
    pagination_class = CustomUserPagination

    # Ограничение HTTP-методов
    # http_method_names = ['get', 'patch']  # Разрешаем только GET и PATCH

    @swagger_auto_schema(
        operation_summary="Получить список пользователей",
        operation_description="Возвращает список всех пользователей.",
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
                description="Список пользователей с пагинацией",
                examples={
                    "application/json": {
                        "count": 50,
                        "next": "http://localhost:8000/api/v1/users/?page=2",
                        "previous": None,
                        "results": [
                            {
                                "id": 1,
                                "username": "testuser",
                                "email": "test@example.com",
                                "role": "buyer",
                                "last_seen": "2025-04-02T12:02:47.570489+03:00"
                            }
                        ]
                    }
                }
            ),
            401: "Неавторизованный доступ"
        }
    )
    def list(self, request, *args, **kwargs):
        """
        Переопределение метода для получения списка пользователей.
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Получить текущего пользователя",
        operation_description="Возвращает данные текущего "
        "авторизованного пользователя.",
        responses={
            200: openapi.Response(
                description="Данные текущего пользователя",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "testuser",
                        "email": "test@example.com",
                        "fisrt_name": "Test",
                        "last_name": "User",
                        "image": "https://minio.example.com/agaba/avatar.jpg",
                        "role": "buyer",
                        "last_seen": "2025-04-02T12:02:47.570489+03:00"
                    }
                }
            ),
            401: "Неавторизованный доступ"
        }
    )
    @action(
        detail=False, methods=['get'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """
        Возвращает данные текущего пользователя.
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Изменить данные текущего пользователя",
        operation_description="Изменяет данные текущего ",
        responses={
            200: openapi.Response(
                description="Данные текущего пользователя",
                examples={
                    "application/json": {
                        "id": 1,
                        "username": "new_testuser",
                        "email": "new_test@example.com",
                        "first_name": "New",
                        "last_name": "Test",
                        "image": "https://minio.example.com/agaba/avatar.jpg",
                    }
                }
            ),
            401: "Неавторизованный доступ"
        }
    )
    @me.mapping.patch
    def update_me(self, request):
        """
        Обновление данных текущего пользователя.
        """
        instance = request.user
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Переопределение метода для получения пользователя по ID.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        """
        Отключен метод POST для создания пользователей.
        """
        return Response(
            {"detail": "Метод POST не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def destroy(self, request, *args, **kwargs):
        """
        Отключен метод DELETE для удаления пользователей.
        """
        return Response(
            {"detail": "Метод DELETE не разрешен."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Отключен метод PATCH для /users/<id>/.
        """
        return Response(
            {"detail": "Метод PATCH не разрешен для этого эндпоинта."},
            status=status.HTTP_405_METHOD_NOT_ALLOWED
        )

    @swagger_auto_schema(
        operation_summary="""Регистрация пользователя и генерация OTP.
         Или вход для существующего пользователя""",
        operation_description="""Создает запись в Redis для регистрации"
        и отправляет одноразовый пароль (OTP) для верификации.
        Если передается роль seller то обязательно
        нужно заполнить еще данные компании:
        "username", "role", "inn",
        "name", "legal_address", "kpp",
        "ogrn", "edo", "bank_account", "bik" """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "role"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Имя пользователя (уникальное)",
                    example="new_user123"
                ),
                "role": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Роль для 'seller' обязательна",
                ),
            },
            oneOf=[
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title="BuyerRegistration",
                    required=["username"],
                    properties={
                        "username": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Имя пользователя"
                        ),
                    },
                ),
                openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    title="SellerRegistration",
                    required=[
                        "username", "role", "inn",
                        "name", "legal_address", "kpp",
                        "ogrn", "edo", "bank_account", "bik"
                    ],
                    properties={
                        "username": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Имя пользователя"),
                        "role": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            enum=["seller"], description="Роль продавца"
                        ),
                        "inn": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="ИНН компании"
                        ),
                        "name": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Название компании"
                        ),
                        "legal_address": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Юридический адрес"
                        ),
                        "kpp": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="КПП"
                        ),
                        "ogrn": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="ОГРН"
                        ),
                        "edo": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="ЕДО"
                        ),
                        "is_hidden": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="Скрыта ли компания"
                        ),
                        "logistic_org": openapi.Schema(
                            type=openapi.TYPE_BOOLEAN,
                            description="""Является ли логистической
                             организацией"""
                        ),
                        "bank_account": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="Банковский счет"
                        ),
                        "bik": openapi.Schema(
                            type=openapi.TYPE_STRING,
                            description="БИК"
                        ),
                    },
                ),
            ],
        ),
        responses={
            200: openapi.Response(
                description="OTP успешно сгенерирован",
                examples={
                    "application/json": {
                        "username": "new_user123",
                        "otp_number": "12345"
                    }
                }
            ),
            400: "Ошибка валидации"
        }
    )
    @action(
        detail=False, methods=['post'],
        permission_classes=[AllowAny]
    )
    def register(self, request):
        """
        Вход существующего
        или
        Регистрация нового пользователя и отправка OTP.
        """
        serializer = RegistrationOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        saved_data = serializer.save()

        return Response(saved_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Подтверждение OTP и вход",
        operation_description="Проверяет введенный OTP и "
        "аутентифицирует пользователя, возвращая токен.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["username", "otp_number"],
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Имя пользователя",
                    example="new_user123"
                ),
                "otp_number": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Одноразовый пароль",
                    example="Сгенерированный OTP"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Успешная верификация и вход",
                examples={
                    "application/json": {
                        "access": "your_access_token",
                        "refresh": "your_refresh_token",
                        "user": {
                            "username": "new_user123",
                            "role": "buyer/seller"
                        }
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка верификации",
                examples={
                    "application/json": {"error": "Неверный OTP или он истек."}
                }
            )
        }
    )
    @action(
        detail=False, methods=['post'],
        permission_classes=[AllowAny]
    )
    def verify(self, request):
        """
        Подтверждение OTP и вход в систему.
        """
        data = request.data
        username = data.get("username")
        
        registration_data = cache.get(f"registration:{username}")
        if not registration_data:
            return Response(
                {"error": "Данные регистрации не найдены или истекли."},
                status=status.HTTP_400_BAD_REQUEST
            )

        role = registration_data["role"]

        if role == 'buyer':
            serializer = BuyerVerificationSerializer(data=data)
        elif role == "seller":
            serializer = SellerVerificationSerializer(data=data)
        else:
            return Response(
                {"error": f"Неверная роль. {role}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            serializer.is_valid(raise_exception=True)
            result = serializer.save()
        except serializers.ValidationError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = result if role == "buyer" else result[0]
        refresh = RefreshToken.for_user(user)

        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "username": user.username,
                "role": user.role
            }
        }, status=status.HTTP_200_OK)


class AvatarUpdateView(APIView):
    """
    API endpoint для обновления аватара текущего пользователя.
    """
    permission_classes = [IsSellerOrAdminOrReadOnly]
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary="Обновить аватар текущего пользователя",
        operation_description="Загружает аватар текущего "
        "пользователя на MinIO.",
        request_body=AvatarUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Аватар успешно обновлен",
                examples={
                    "application/json": {
                        "message": "Аватар успешно обновлен",
                        "image_url": """
                        https://minio.example.com/agaba/avatar.jpg
                        """
                    }
                }
            ),
            400: "Неверные данные",
            401: "Неавторизованный доступ"
        }
    )
    def post(self, request):
        """
        Обновление аватара текущего пользователя.
        """
        user = request.user
        serializer = AvatarUpdateSerializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        image_file = request.FILES.get('image')
        if not image_file:
            return Response(
                {"detail": "Файл не найден."},
                status=status.HTTP_400_BAD_REQUEST
            )

        file_name = f"avatar_{user.id}_{image_file.name}"

        # Загружаем файл на MinIO
        image_url = upload_to_minio(image_file, file_name)
        if not image_url:
            return Response(
                {"detail": "Ошибка при загрузке файла на MinIO."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user.image = image_url
        user.save()

        return Response({
            "message": "Аватар успешно обновлен",
            "image_url": image_url
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_summary="Удалить аватар текущего пользователя",
        operation_description="Удаляет аватар текущего пользователя с MinIO"
        "и очищает поле image.",
        responses={
            200: openapi.Response(
                description="Аватар успешно удален",
                examples={
                    "application/json": {
                        "message": "Аватар успешно удален"
                    }
                }
            ),
            401: "Неавторизованный доступ",
            404: "Аватар не найден"
        }
    )
    def delete(self, request):
        """
        Удаление аватара текущего пользователя.
        """
        user = request.user

        if not user.image:
            return Response(
                {"detail": "Аватар не найден."},
                status=status.HTTP_404_NOT_FOUND
            )

        image_url = user.image
        file_name = image_url.split('/')[-1]

        success = delete_from_minio(file_name)
        if not success:
            return Response(
                {"detail": "Ошибка при удалении файла с MinIO."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        user.image = None
        user.save()

        return Response(
            {"message": "Аватар успешно удален"},
            status=status.HTTP_200_OK
        )


class TokenRefreshView(APIView):
    """Обновление access и refresh токенов."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary="Обновление access и refresh токенов",
        operation_description="Обновляет access и refresh "
        "токены на основе старого refresh-токена.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["refresh"],
            properties={
                "refresh": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Старый refresh-токен",
                    example="old_refresh_token"
                )
            }
        ),
        responses={
            200: openapi.Response(
                description="Успешное обновление токенов",
                examples={
                    "application/json": {
                        "access": "new_access_token",
                        "refresh": "new_refresh_token"
                    }
                }
            ),
            400: openapi.Response(
                description="Ошибка обновления токенов",
                examples={
                    "application/json": {"error": "Неверный refresh-токен."}
                }
            )
        }
    )
    def post(self, request, *args, **kwargs):
        old_refresh_token = request.data.get("refresh")
        if not old_refresh_token:
            return Response(
                {"error": "Refresh-токен обязателен."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            token = RefreshToken(old_refresh_token)
            user_id = token.payload.get("user_id")

            if not user_id:
                raise ValueError("Не указан user_id в токене.")

            user = CustomUser.objects.get(id=user_id)
            new_refresh_token = RefreshToken.for_user(user)
            new_access_token = str(new_refresh_token.access_token)
            new_refresh_token = str(new_refresh_token)

            return Response({
                "access": new_access_token,
                "refresh": new_refresh_token
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Неверный refresh-токен. {e}"},
                status=status.HTTP_400_BAD_REQUEST
            )


class CompanyViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с моделью Company."""
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Создать новую компанию.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "inn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ИНН компании"
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Название компании"
                ),
                "legal_address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Юридический адрес"
                ),
                "kpp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="КПП"
                ),
                "ogrn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ОГРН"
                ),
                "edo": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ЕДО"
                ),
                "is_hidden": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Скрыта ли компания"
                ),
                "logistic_org": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Является ли логистической организацией"
                ),
            },
            required=["inn", "name"]
        ),
        responses={
            201: openapi.Response(
                description="Компания успешно создана",
                examples={
                    "application/json": {
                        "id": 1,
                        "user": 11,
                        "inn": "123456789012",
                        "name": "Example LLC",
                        "legal_address": "123 Main St",
                        "kpp": "123456789",
                        "ogrn": "1234567890123",
                        "edo": "example-edo",
                        "is_hidden": 'false',
                        "logistic_org": 'false',
                        "created": "2025-04-02T12:02:47.570489+03:00",
                        "updated": "2025-04-02T12:02:47.570501+03:00",
                        "is_reliable": 'true',
                        "rating": [
                            4.5,
                            "--colorc3eb0e"
                        ]
                    }
                }
            ),
            400: "Неверные данные"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        # Автоматически привязываем компанию к текущему пользователю
        serializer.save(user=self.request.user)


class SearchCompanyViewSet(viewsets.ViewSet):
    """
    Вьюсет для поиска компаний через DaData.
    """
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="Поиск компаний по частичному ИНН через DaData.",
        manual_parameters=[
            openapi.Parameter(
                'query',
                openapi.IN_QUERY,
                description="Частичный ИНН для поиска",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Response(
                description="Список найденных компаний",
                examples={
                    "application/json": {
                        "companies": [
                            {
                                "name": "Example LLC",
                                "inn": "123456789012",
                                "kpp": "123456789",
                                "address": "123 Main St",
                                "ogrn": "1234567890123"
                            }
                        ]
                    }
                }
            ),
            400: "Параметр 'query' обязателен",
            404: "Компании не найдены",
            500: "Ошибка сервера"
        }
    )
    def list(self, request):
        """
        Поиск компаний по частичному ИНН через DaData.
        """
        query = request.query_params.get('query')
        if not query:
            return Response(
                {"error": "Параметр 'query' обязателен"},
                status=400
            )

        TOKEN_DADATA = os.getenv('TOKEN_DADATA')
        if not TOKEN_DADATA:
            return Response(
                {"error": "API ключ DaData не настроен"},
                status=500
            )

        dadata = Dadata(TOKEN_DADATA)

        try:
            result = dadata.suggest("party", query)
            if result:
                companies = [{
                    "name": company["value"],
                    "inn": company["data"]["inn"],
                    "kpp": company["data"].get("kpp", ""),
                    "address": company["data"]["address"].get("value", ""),
                    "ogrn": company["data"].get("ogrn", ""),
                } for company in result]
                return Response({"companies": companies})
            else:
                return Response({"error": "Компании не найдены"}, status=404)
        except Exception as e:
            print(f"Ошибка при запросе к DaData: {e}")
            return Response({"error": str(e)}, status=500)
