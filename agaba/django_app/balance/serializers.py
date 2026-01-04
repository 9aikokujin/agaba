from django.db.models import Q
from rest_framework import serializers

from .models import (
    Balance, Replenishment, Withdrawal,
    OrderOperation,
    AllOperation, AccountPDF
)
from account.models import Company


class BalanceSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Balance."""
    class Meta:
        model = Balance
        fields = ['user', 'cash_account', 'date_update']
        read_only_fields = ['user', 'date_update']


class ReplenishmentSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=False, allow_null=True)
    inn = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    legal_address = serializers.CharField(required=False, allow_null=True)
    kpp = serializers.CharField(required=False, allow_null=True)
    ogrn = serializers.CharField(required=False, allow_null=True)
    is_hidden = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Replenishment
        fields = [
            'amount_replenishment',
            'payment_type',
            'company_id',
            'inn',
            'name',
            'legal_address',
            'kpp',
            'ogrn',
            'is_hidden'
        ]

    def validate(self, data):
        if not data.get('company_id') and not all(
            [
                data.get('inn'), data.get('name'),
                data.get('legal_address'),
                data.get('kpp'), data.get('ogrn')
            ]
        ):
            raise serializers.ValidationError(
                """Необходимо указать либо company_id,
                 либо все данные для создания новой компании."""
            )
        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None) or validated_data.get('user')
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication required to create a replenishment."
            )
        validated_data.pop('user', None)

        is_hidden = validated_data.pop('is_hidden', None)
        company_data = {
            'inn': validated_data.pop('inn', None),
            'name': validated_data.pop('name', None),
            'legal_address': validated_data.pop('legal_address', None),
            'kpp': validated_data.pop('kpp', None),
            'ogrn': validated_data.pop('ogrn', None),
        }
        if is_hidden is not None:
            company_data['is_hidden'] = is_hidden

        company_id = validated_data.pop('company_id', None)
        if company_id:
            company = Company.objects.filter(
                id=company_id
            ).filter(
                Q(user=user) | Q(custom_users_company=user)
            ).first()
            if not company:
                raise serializers.ValidationError(
                    "Company does not belong to the current user."
                )
        else:
            company = Company.objects.create(user=user, **company_data)

        replenishment = Replenishment.objects.create(
            user=user,
            company=company,
            **validated_data
        )
        return replenishment


class WithdrawalSerializer(serializers.ModelSerializer):
    company_id = serializers.IntegerField(required=False, allow_null=True)
    inn = serializers.CharField(required=False, allow_null=True)
    name = serializers.CharField(required=False, allow_null=True)
    legal_address = serializers.CharField(required=False, allow_null=True)
    kpp = serializers.CharField(required=False, allow_null=True)
    ogrn = serializers.CharField(required=False, allow_null=True)
    is_hidden = serializers.BooleanField(required=False, write_only=True)

    class Meta:
        model = Withdrawal
        fields = [
            'amount_withdrawal',
            'type_operation',
            'company_id',
            'inn',
            'name',
            'legal_address',
            'kpp',
            'ogrn',
            'is_hidden',
            'bik',
            'ks',
            'rs',
            'number_account',
        ]

    def validate(self, data):
        if not data.get('company_id') and not all(
            [
                data.get('inn'), data.get('name'),
                data.get('legal_address'),
                data.get('kpp'), data.get('ogrn')
            ]
        ):
            raise serializers.ValidationError(
                "Provide company_id or full company details."
            )

        missing_bank_fields = [
            field for field in ('bik', 'ks', 'rs') if not data.get(field)
        ]
        if missing_bank_fields:
            raise serializers.ValidationError(
                "bik, ks and rs are required."
            )

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None) or validated_data.get('user')
        if not user or not user.is_authenticated:
            raise serializers.ValidationError(
                "Authentication required to create a withdrawal."
            )
        validated_data.pop('user', None)

        is_hidden = validated_data.pop('is_hidden', None)
        company_data = {
            'inn': validated_data.pop('inn', None),
            'name': validated_data.pop('name', None),
            'legal_address': validated_data.pop('legal_address', None),
            'kpp': validated_data.pop('kpp', None),
            'ogrn': validated_data.pop('ogrn', None),
        }
        if is_hidden is not None:
            company_data['is_hidden'] = is_hidden

        company_id = validated_data.pop('company_id', None)
        if company_id:
            company = Company.objects.filter(
                id=company_id
            ).filter(
                Q(user=user) | Q(custom_users_company=user)
            ).first()
            if not company:
                raise serializers.ValidationError(
                    "Company does not belong to the current user."
                )
        else:
            company = Company.objects.create(user=user, **company_data)

        withdrawal = Withdrawal.objects.create(
            user=user,
            company=company,
            **validated_data
        )
        return withdrawal


class OrderOperationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели OrderOperation."""
    class Meta:
        model = OrderOperation
        fields = [
            'order_operation_id', 'user', 'order_id',
            'type_operation', 'date_created'
        ]
        read_only_fields = ['order_operation_id', 'date_created']


class AllOperationSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AllOperation."""
    class Meta:
        model = AllOperation
        fields = [
            'operation_id', 'user', 'amount',
            'type_operation', 'status_operation',
            'payment_type', 'replenishment', 'withdrawal',
            'order_operation', 'details', 'date_created'
        ]
        read_only_fields = ['operation_id', 'date_created']


class AccountPDFSerializer(serializers.ModelSerializer):
    """Сериализатор для модели AccountPDF."""
    class Meta:
        model = AccountPDF
        fields = ['user', 'path_invoice', 'company', 'download_link']
        read_only_fields = ['download_link']
