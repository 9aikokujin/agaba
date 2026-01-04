from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase

from account.models import Company
from products.models import Category, Subcategory, Product, PriceHistory


class ProductPriceHistoryTests(TestCase):
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
            cur_price=Decimal('100.00'),
            category=self.category,
            subcategory=self.subcategory,
            author=self.user,
            company=self.company,
            condition='new',
            delivery_time=7,
            availability='in_stock',
            location='City',
            min_deposit=Decimal('10.00'),
        )

    def test_price_history_on_change(self):
        self.assertEqual(
            PriceHistory.objects.filter(product=self.product).count(),
            1,
        )

        self.product.cur_price = Decimal('120.00')
        self.product.save()
        self.product.refresh_from_db()

        self.assertEqual(self.product.prev_price, Decimal('100.00'))
        self.assertEqual(
            PriceHistory.objects.filter(product=self.product).count(),
            2,
        )
