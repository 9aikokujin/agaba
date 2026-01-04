from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from account.models import Company
from products.models import Category, Subcategory, Product, Favorite, Comparison


class AnonymousCollectionTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='seller',
            password='password123',
            role='seller',
        )
        self.company = Company.objects.create(
            user=self.user,
            inn='123456789012',
            name='Test Company',
        )
        self.category = Category.objects.create(
            name='Category',
            slug='category',
        )
        self.subcategory = Subcategory.objects.create(
            category=self.category,
            name='Subcategory',
            slug='subcategory',
        )
        self.product = Product.objects.create(
            brand='Brand',
            name='Product',
            slug='brand-product',
            description='Test description',
            cur_price='100.00',
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            company=self.company,
            condition='new',
            delivery_time=7,
            availability='in_stock',
            location='City',
            min_deposit='10.00',
        )
        self.favorites_url = reverse('favorite-list')
        self.comparisons_url = reverse('comparison-list')

    def test_favorite_requires_session_key_for_anonymous(self):
        response = self.client.post(
            self.favorites_url,
            {'product_id': self.product.id},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_favorite_with_session_key(self):
        session_key = 'anon-session'
        response = self.client.post(
            self.favorites_url,
            {'product_id': self.product.id},
            format='json',
            HTTP_X_SESSION_KEY=session_key,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Favorite.objects.filter(
                session_key=session_key,
                product=self.product,
            ).exists()
        )

    def test_comparison_requires_session_key_for_anonymous(self):
        response = self.client.post(
            self.comparisons_url,
            {'products': [self.product.id]},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_comparison_with_session_key(self):
        session_key = 'anon-compare'
        response = self.client.post(
            self.comparisons_url,
            {'products': [self.product.id]},
            format='json',
            HTTP_X_SESSION_KEY=session_key,
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            Comparison.objects.filter(
                session_key=session_key
            ).exists()
        )


class BalanceCompanyOwnershipTests(APITestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username='owner',
            password='password123',
            role='seller',
        )
        self.other = get_user_model().objects.create_user(
            username='other',
            password='password123',
            role='seller',
        )
        self.company = Company.objects.create(
            user=self.owner,
            inn='123456789013',
            name='Owner Company',
        )
        self.replenishments_url = reverse('replenishment-list')
        self.withdrawals_url = reverse('withdrawal-list')

    def test_replenishment_rejects_foreign_company(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            self.replenishments_url,
            {
                'amount_replenishment': '10.00',
                'payment_type': 'account',
                'company_id': self.company.id,
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_withdrawal_rejects_foreign_company(self):
        self.client.force_authenticate(user=self.other)
        response = self.client.post(
            self.withdrawals_url,
            {
                'amount_withdrawal': '5.00',
                'type_operation': 'account',
                'company_id': self.company.id,
                'bik': '044525225',
                'ks': '30101810400000000225',
                'rs': '40702810900000000000',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
