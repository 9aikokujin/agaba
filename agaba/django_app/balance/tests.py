from django.test import TestCase
from .models import Replenishment, Withdrawal, Balance
from account.models import CustomUser


class OperationsTestCase(TestCase):
    """Тесты для операций по заказам."""
    def setUp(self):
        # Создаем юзера
        self.user = CustomUser.objects.create(username='testuser')
        # Создаем объект заказа
        self.replenishment = Replenishment.objects.create(
            user_id=self.user,
            amount_replenishment=100,
            type_operation='account'
        )
        # Создаем объект вывода
        self.withdrawal = Withdrawal.objects.create(
            user_id=self.user,
            amount_withdrawal=50,
            type_operation='account'
        )

    def test_replenishment_success(self):
        """Тест успешного пополнения баланса."""
        self.replenishment.mark_as_success()
        balance = Balance.objects.get(user_id=self.user)
        self.assertEqual(balance.cash_account, 100)

    def test_withdrawal_success(self):
        """Тест успешного вывода средств."""
        balance = Balance.objects.create(user_id=self.user, cash_account=100)
        self.withdrawal.mark_as_success()
        balance.refresh_from_db()
        self.assertEqual(balance.cash_account, 50)

    def test_withdrawal_failure_insufficient_funds(self):
        """Тест неудачного вывода средств при недостатке средств."""
        balance = Balance.objects.create(user_id=self.user, cash_account=20)
        with self.assertRaises(ValueError):
            self.withdrawal.mark_as_success()