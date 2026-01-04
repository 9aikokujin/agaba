from datetime import timedelta
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.contrib.auth.hashers import make_password, check_password
from django.utils.crypto import get_random_string
# from website.utils import pluralize_ru


class CustomUser(AbstractUser):
    """Модель для хранения пользователей."""

    ROLE_CHOICES = [
        ('buyer', 'Покупатель'),
        ('seller', 'Продавец'),
        ('admin', 'Админ'),
        ('superadmin', 'Суперадмин'),
        ('manager', 'Менеджер по заказам'),
        ('broker', 'Брокер'),
        ('moderator', 'Модератор'),
        ('buh', 'Бухгалтер'),
    ]
    last_seen = models.DateTimeField(
        null=True, blank=True,
        verbose_name="Последняя активность"
    )
    # mobile_number = models.CharField(
    #     max_length=15, unique=True, blank=True, null=True
    # )
    is_mobile_verified = models.BooleanField(default=False)
    email = models.EmailField(blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='buyer',
        verbose_name='Роль пользователя'
    )
    image = models.ImageField(
        upload_to='user_images/',
        null=True, blank=True
    )
    companies = models.ManyToManyField(
        'Company',
        related_name='custom_users_company',
        blank=True,
        verbose_name='Компании',
        help_text='Компании, связанные с пользователем (максимум 5).'
    )
    otp_hash = models.CharField(
        max_length=128,
        blank=True,
        null=True
    )
    otp_expiration = models.DateTimeField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def clean(self):
        super().clean()

        # Валидация email
        if self.email and CustomUser.objects.filter(
            email=self.email
        ).exclude(id=self.id).exists():
            raise ValidationError(
                {'email': 'Пользователь с таким email уже существует.'}
            )

    def generate_otp(self, digits=5):
        """Генерирует OTP и сохраняет его в базе данных."""
        otp = get_random_string(length=digits, allowed_chars='0123456789')
        self.otp_hash = make_password(otp)
        self.otp_expiration = now() + timedelta(seconds=60)
        self.save()
        return otp

    def verify_otp(self, otp):
        """Проверяет OTP."""
        if self.otp_expiration and self.otp_expiration > now():
            if check_password(otp, self.otp_hash):
                self.is_mobile_verified = True
                self.otp_hash = None
                self.otp_expiration = None
                self.save()
                return True
        return False

    def __str__(self):
        """Возвращает строку представления объекта."""
        return self.username


class Company(models.Model):
    """Модель для хранения информации о компаниях."""

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='company',
        verbose_name='Пользователь'
    )
    inn = models.CharField(
        max_length=12,
        unique=True,
        verbose_name='ИНН'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Название компании'
    )
    legal_address = models.CharField(
        max_length=254,
        blank=True,  # Пока тру, для отдалки
        null=True,  # Пока тру, для отдалки
        verbose_name='Юредический адрес'
    )
    kpp = models.CharField(
        max_length=9,
        blank=True, null=True,
        verbose_name='КПП'
    )  # КПП тру, может его и не быть у ИП
    ogrn = models.CharField(
        max_length=15, blank=True,
        null=True, verbose_name='ОГРН')  # Пока тру, для отдалки
    edo = models.CharField(
        max_length=100, blank=True,
        null=True, verbose_name='ЕДО')  # Пока тру, для отдалки
    is_hidden = models.BooleanField(
        default=True,
        verbose_name='Скрыта'
    )
    logistic_org = models.BooleanField(
        default=False,
        verbose_name='Логистическая организация'
    )
    bank_account = models.CharField(
        max_length=50, blank=True,
        null=True, verbose_name='Номер банковского счета'
    )
    bik = models.CharField(
        max_length=50, blank=True,
        null=True, verbose_name='БИК'
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'
        ordering = ['-id']

    @property
    def is_reliable(self):
        """Проверяет надежность компании."""
        # Реализовать логику проверки надежности компании!!
        # Статус "Надежный продавец" получает
        # продавец который провел хоть одну сделку.
        return True

    @property
    def rating(self):
        """Вычисляет рейтинг компании."""
        # Рейтинг компании рассчитывается по отзывам пользователей о компании. (из Фигмы)
        # Здесь должна быть логика получения рейтинга из базы данных.
        # rating = random.random()*5
        rating = 4.5  # Пример, заменить на реальную логику

        # определяем цвет в зависимости от рейтинга
        # здесь нужно вернуть класс CSS, который
        # будет использоваться для отображения цвета
        if rating >= 4:
            color = "--colorc3eb0e" # Из Фигмы.
        elif rating >= 3:
            color = "--colorfff459" # Из Фигмы.
        else:
            color = "--colorff4c00" # Из Фигмы.

        return round(rating, 1), color

    # @property
    # def duration_since_creation(self):
    #     """
    #     Возвращает продолжительность с момента создания компании
    #     в формате 'X лет Y месяцев'.
    #     """
    #     delta = timezone.now() - self.created
    #     days = delta.days
    #     years = days // 365
    #     months = (days % 365) // 30

    #     year_str = ""
    #     if years > 0:
    #         word = pluralize_ru(years, "год").replace("годов", "лет")
    #         year_str = f"{years} {word} "

    #     month_str = ""
    #     if months > 0:
    #         word = pluralize_ru(months, "месяц")
    #         month_str = f"{months} {word} "

    #     duration = (year_str + month_str).strip()
    #     return f"{duration} на AGABA" if duration else "На AGABA менее месяца"

    # @property
    # def number_of_sales(self):
    #     """Возвращает количество продаж компании."""
    #     # Здесь должна быть логика получения количества продаж из базы данных.
    #     quantity = random.randint(1, 10)  # Пример статического значения, заменить на реальную логику
    #     word = pluralize_ru(quantity, "продажа")
    #     return f"{quantity} {word}"

    # @property
    # def number_of_reviews(self):
    #     """Возвращает количество отзывов компании."""
    #     # Здесь должна быть логика получения количества отзывов из базы данных.
    #     quantity = random.randint(1, 10)  # Пример статического значения, заменить на реальную логику
    #     word = pluralize_ru(quantity, "отзыв")
    #     return f"{quantity} {word}"

    # def __str__(self):
    #     return f'Компания "{self.name}" добавлена к пользователю "{self.user.username}".'
