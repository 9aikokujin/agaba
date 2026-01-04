# До подключение СМС выводим OTP под формой
# ВАЖНО, за пользователем закреплено максимум 5 компаний.
from datetime import timezone
import random
import string
from django.core.cache import cache

from rest_framework import serializers
from .models import CustomUser, Company
from balance.serializers import BalanceSerializer


class BaseVerificationSerializer(serializers.Serializer):
    """Базовый сериализатор для верификации."""
    username = serializers.CharField(max_length=150, required=True)
    otp_number = serializers.CharField(max_length=5, required=True)

    def validate(self, attrs):
        """Валидируем данные из кеша и формы."""
        username = attrs['username']
        otp_number = attrs['otp_number']

        registration_data = cache.get(f"registration:{username}")
        if not registration_data:
            raise serializers.ValidationError(
                "Данные регистрации не найдены или истекли."
            )

        if registration_data['otp'] != otp_number:
            raise serializers.ValidationError("Неверный OTP или он истек.")

        return attrs

    def create_user(self, username, role=None):
        """
        Создает пользователя и удаляет данные из Redis.
        """
        registration_data = cache.get(f"registration:{username}")
        if not role:
            role = 'buyer'
        user, created = CustomUser.objects.get_or_create(
            username=username,
            defaults={'role': role}
        )

        cache.delete(f"registration:{username}")

        return user


class CompanySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Company."""
    class Meta:
        model = Company
        fields = [
            'id', 'user', 'inn', 'name',
            'legal_address', 'kpp', 'ogrn', 'edo',
            'is_hidden', 'logistic_org',
            'created', 'updated', 'is_reliable', 'rating'
        ]
        read_only_fields = [
            'id', 'created', 'updated',
            'is_reliable', 'rating'
        ]


class CustomUserSerializer(serializers.ModelSerializer):
    balance = BalanceSerializer(read_only=True)
    """Сериализатор для модели CustomUser."""

    class Meta:
        model = CustomUser
        fields = [
            'id', 'username', 'email', 'role',
            'first_name', 'last_name',
            'image', 'balance', 'companies'
        ]
        read_only_fields = ['id', 'is_mobile_verified', 'role', 'balance']


class AvatarUpdateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для обновления аватара пользователя.
    """
    image = serializers.ImageField(required=True)

    class Meta:
        model = CustomUser
        fields = ['image']


class RegistrationOTPSerializer(serializers.Serializer):
    """Первый этап регистрации и генерация OTP."""
    role = serializers.ChoiceField(choices=['seller'], required=False)
    username = serializers.CharField(max_length=150, required=True)

    inn = serializers.CharField(max_length=12, required=False)
    name = serializers.CharField(max_length=255, required=False)
    legal_address = serializers.CharField(max_length=255, required=False)
    kpp = serializers.CharField(max_length=9, required=False)
    ogrn = serializers.CharField(max_length=13, required=False)
    edo = serializers.CharField(max_length=255, required=False)
    is_hidden = serializers.BooleanField(required=False, default=False)
    logistic_org = serializers.BooleanField(required=False, default=False)
    bank_account = serializers.CharField(max_length=20, required=False)
    bik = serializers.CharField(max_length=9, required=False)

    def validate(self, attrs):
        role = attrs.get('role')

        if role == 'seller':
            required_fields = [
                'inn', 'name', 'legal_address', 'kpp', 'ogrn',
                'edo', 'bank_account', 'bik'
            ]
            for field in required_fields:
                if not attrs.get(field):
                    raise serializers.ValidationError(
                        f"Поле '{field}' обязательно для роли 'seller'."
                    )

        return attrs

    def create(self, validated_data):
        """
        Генерирует OTP и сохраняет данные в Redis.
        """
        username = validated_data['username']
        role = validated_data.get('role')

        otp = ''.join(random.choices(string.digits, k=5))

        cache_data = {
            'otp': otp,
        }

        if role == 'seller':
            cache_data['role'] = 'seller'
            cache_data['company_data'] = {
                'inn': validated_data.get('inn'),
                'name': validated_data.get('name'),
                'legal_address': validated_data.get('legal_address'),
                'kpp': validated_data.get('kpp'),
                'ogrn': validated_data.get('ogrn'),
                'edo': validated_data.get('edo'),
                'is_hidden': validated_data.get('is_hidden'),
                'logistic_org': validated_data.get('logistic_org'),
                'bank_account': validated_data.get('bank_account'),
                'bik': validated_data.get('bik'),
            }
        else:
            # Указываем роль buyer только если seller не передан
            cache_data['role'] = 'buyer'

        cache.set(
            f"registration:{username}", cache_data, timeout=300  # 5 минут
        )

        return {
            'username': username,
            'otp_number': otp
        }


class BuyerVerificationSerializer(BaseVerificationSerializer):
    """Верификация покупателя."""

    def save(self, **kwargs):
        username = self.validated_data['username']

        user = self.create_user(username)
        return user


class SellerVerificationSerializer(BaseVerificationSerializer):
    """Верификация продавца."""

    def save(self, **kwargs):
        username = self.validated_data['username']
        role = 'seller'

        registration_data = cache.get(f"registration:{username}")
        if not registration_data or 'company_data' not in registration_data:
            raise serializers.ValidationError(
                "Данные компании не найдены или валидны."
            )

        company_data = registration_data['company_data']

        user = self.create_user(username, role)

        company = Company.objects.create(
            user=user,
            inn=company_data['inn'],
            name=company_data['name'],
            legal_address=company_data['legal_address'],
            kpp=company_data['kpp'],
            ogrn=company_data['ogrn'],
            edo=company_data['edo'],
            is_hidden=company_data['is_hidden'],
            logistic_org=company_data['logistic_org'],
            bank_account=company_data['bank_account'],
            bik=company_data['bik']
        )

        user.companies.add(company)

        cache.delete(f"registration:{username}")

        return user, company


class UserShortSerializer(serializers.ModelSerializer):
    """Короткое отображение пользователя"""

    full_name = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'full_name', 'avatar']
        read_only_fields = fields

    def get_full_name(self, obj):
        """Возвращает полное имя пользователя, если доступно."""
        return obj.get_full_name() or obj.username

    def get_avatar(self, obj):
        """Возвращает URL аватара пользователя."""
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def to_representation(self, instance):
        """Фильтруем поля в зависимости от контекста."""
        data = super().to_representation(instance)
        request = self.context.get('request')

        if not (request and (
            request.user.is_staff or request.user == instance
        )):
            data.pop('email', None)

        if 'last_seen' in self.fields:
            data[
                'is_online'
            ] = instance.last_seen and instance.last_seen > timezone.now(
            ) - timezone.timedelta(minutes=5)

        return data


class StatusSerializer(serializers.Serializer):
    status = serializers.CharField()
