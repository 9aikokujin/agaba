from django_filters.rest_framework import DjangoFilterBackend


from django.contrib.auth.models import AnonymousUser
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework import status


from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from account.paginations import (
    CustomUserPagination
)

from balance.models import (
    Balance, Replenishment, Withdrawal,
    OrderOperation,
    AllOperation, AccountPDF
)

from balance.serializers import (
    BalanceSerializer, ReplenishmentSerializer,
    WithdrawalSerializer,
    OrderOperationSerializer,
    AllOperationSerializer, AccountPDFSerializer
)
from ..permissions import (
    IsAdminOrReadOnly, ReadOnly, IsSuperuserOrBuh
)

from django_app.services import send_notification


class BalanceViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Balance."""
    queryset = Balance.objects.all()
    serializer_class = BalanceSerializer
    permission_classes = [IsAdminOrReadOnly]

    http_method_names = ['get']

    def get_queryset(self):
        """
        Пользователь может видеть только свой баланс.
        Если запрос фейковый (для Swagger), возвращаем пустой QuerySet.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Balance.objects.none()

        if isinstance(self.request.user, AnonymousUser):
            return Balance.objects.none()

        return Balance.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        """Запрещает создание нового баланса через API."""
        return Response(
            {"detail": "Создание нового баланса запрещено."},
            status=status.HTTP_403_FORBIDDEN
        )

    @swagger_auto_schema(
        operation_summary="Получить текущий баланс пользователя",
        operation_description="Возвращает информацию о текущем "
        "балансе пользователя.",
        responses={
            200: openapi.Response(
                description="Успешный запрос",
                examples={
                    "application/json": [
                        {
                            "user": 1,
                            "cash_account": "0.00",
                            "date_update": "2025-04-02T11:40:10.283808+03:00"
                        }
                    ]
                }
            ),
            401: openapi.Response(
                description="Неавторизованный доступ",
                examples={
                    "application/json": {
                        "detail": "Учетные данные не были предоставлены."
                    }
                }
            ),
            403: openapi.Response(
                description="Доступ запрещен",
                examples={
                    "application/json": {
                        "detail": "У вас нет прав для "
                        "выполнения этого действия."
                    }
                }
            ),
        }
    )
    def list(self, request, *args, **kwargs):
        """Получение списка балансов пользователя."""
        return super().list(request, *args, **kwargs)


class ReplenishmentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Replenishment."""

    queryset = Replenishment.objects.all()
    serializer_class = ReplenishmentSerializer
    permission_classes = [IsSuperuserOrBuh]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Replenishment.objects.filter(user=self.request.user)
        else:
            return Replenishment.objects.none()

    @swagger_auto_schema(
        operation_description="Создать заявку на пополнение.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "amount_replenishment": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Сумма пополнения"
                ),
                "payment_type": openapi.Schema(
                    type=openapi.TYPE_STRING, enum=[
                        "account", "card", "bonus"
                    ],
                    description="Тип платежа пока только account"
                ),
                "company_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID компании (опционально)"
                ),
                "inn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ИНН компании "
                    "(обязательно, если не указан company_id)"
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Название компании "
                    "(обязательно, если не указан company_id)"
                ),
                "legal_address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Юридический адрес компании "
                    "(обязательно, если не указан company_id)"
                ),
                "kpp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="КПП компании "
                    "(обязательно, если не указан company_id)"
                ),
                "ogrn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ОГРН компании "
                    "(обязательно, если не указан company_id)"
                ),
                "is_hidden": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Флаг скрытия компании "
                    "(обязательно, если не указан company_id)"
                ),
            },
            required=["amount_replenishment", "payment_type"],
        ),
        responses={
            201: openapi.Response(
                description="Заявка на пополнение успешно создана",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "operation_id": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                    },
                ),
            ),
            400: "Ошибка валидации данных",
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Создание заявки на пополнение баланса.
        Если company_id не указан, создается новая компания.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        replenishment = serializer.save(user=self.request.user)

        return Response(
            {
                "message": "Заявка на пополнение успешно создана.",
                "operation_id": replenishment.operation_id,
            },
            status=status.HTTP_201_CREATED,
        )


class WithdrawalViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Withdrawal."""

    queryset = Withdrawal.objects.all()
    serializer_class = WithdrawalSerializer
    permission_classes = [IsSuperuserOrBuh]

    def get_queryset(self):
        """
        Пользователь может видеть только свои заявки.
        Если запрос фейковый (для Swagger), возвращаем пустой QuerySet.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Withdrawal.objects.none()

        if isinstance(self.request.user, AnonymousUser):
            return Withdrawal.objects.none()

        return Withdrawal.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_summary="Создание заявки на вывод средств",
        operation_description=(
            "Создает заявку на вывод средств. "
            "Если company_id не указан, создается новая компания."
        ),
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "amount_withdrawal": openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description="Сумма вывода"
                ),
                "type_operation": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["account", "card"],
                    description="Тип операции вывода"
                ),
                "company_id": openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="ID компании (опционально)"
                ),
                "inn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ИНН компании "
                    "(обязательно, если не указан company_id)"
                ),
                "name": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Название компании "
                    "(обязательно, если не указан company_id)"
                ),
                "legal_address": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Юридический адрес компании "
                    "(обязательно, если не указан company_id)"
                ),
                "kpp": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="КПП компании "
                    "(обязательно, если не указан company_id)"
                ),
                "ogrn": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="ОГРН компании "
                    "(обязательно, если не указан company_id)"
                ),
                "is_hidden": openapi.Schema(
                    type=openapi.TYPE_BOOLEAN,
                    description="Флаг скрытия компании "
                    "(обязательно, если не указан company_id)"
                ),
                "bik": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="БИК (обязательно)"
                ),
                "ks": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Корреспондентский счет (обязательно)"
                ),
                "rs": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description="Расчетный счет (обязательно)"
                ),
            },
            required=[
                "amount_withdrawal", "type_operation",
                "bik", "ks", "rs"
            ],
        ),
        responses={
            201: openapi.Response(
                description="Заявка на вывод средств успешно создана",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "message": openapi.Schema(type=openapi.TYPE_STRING),
                        "withdrawal_operation_id": openapi.Schema(
                            type=openapi.TYPE_STRING
                        ),
                    },
                ),
            ),
            400: "Ошибка валидации данных",
        },
    )
    def create(self, request, *args, **kwargs):
        """
        Создание заявки на вывод средств.
        Если company_id не указан, создается новая компания.
        """
        if getattr(self, 'swagger_fake_view', False):
            return Response(
                {"detail": "Swagger schema generation request."},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        withdrawal = serializer.save(user=self.request.user)

        send_notification(
            user_id=self.request.user.id,
            message_type='withdrawal_created',
            data={
                'operation_id': str(withdrawal.withdrawal_operation_id),
                'amount': str(withdrawal.amount_withdrawal),
                'payment_type': withdrawal.type_operation,
                'status': withdrawal.status_operation,
                'company_name': withdrawal.company.name,
                'timestamp': str(withdrawal.date_created)
            }
        )

        return Response(
            {
                "message": "Заявка на вывод средств успешно создана.",
                "withdrawal_operation_id": withdrawal.withdrawal_operation_id,
            },
            status=status.HTTP_201_CREATED,
        )


class OrderOperationViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели OrderOperation."""
    queryset = OrderOperation.objects.all()
    serializer_class = OrderOperationSerializer
    permission_classes = [ReadOnly]
    http_method_names = ['get']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AllOperationViewSet(viewsets.ModelViewSet):
    """Вьюсет для просмотра всех операций."""
    queryset = AllOperation.objects.all()
    serializer_class = AllOperationSerializer
    pagination_class = CustomUserPagination
    permission_classes = [IsSuperuserOrBuh]
    http_method_names = ['get', 'put', 'patch']
    filter_backends = [DjangoFilterBackend]
    filterset_fields = [
        'user', 'amount', 'type_operation', 'status_operation',
        'payment_type', 'replenishment', 'withdrawal', 'order_operation'
    ]

    def get_queryset(self):
        """
        Пользователь может видеть только свои заявки.
        Если запрос фейковый (для Swagger), возвращаем пустой QuerySet.
        """
        if getattr(self, 'swagger_fake_view', False):
            return AllOperation.objects.none()

        if isinstance(self.request.user, AnonymousUser):
            return AllOperation.objects.none()

        return AllOperation.objects.filter(user=self.request.user)


class AccountPDFViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели AccountPDF."""
    queryset = AccountPDF.objects.all()
    serializer_class = AccountPDFSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get']

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
