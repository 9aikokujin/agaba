import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0010_alter_productreview_product'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favorite',
            options={
                'ordering': ['-created_at'],
                'verbose_name': 'Favorite',
                'verbose_name_plural': 'Favorites',
            },
        ),
        migrations.AddField(
            model_name='favorite',
            name='session_key',
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=40,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='favorite',
            name='user',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='favorites',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name='favorite',
            constraint=models.CheckConstraint(
                check=models.Q(
                    user__isnull=False,
                ) | models.Q(
                    session_key__isnull=False,
                ),
                name='favorite_user_or_session',
            ),
        ),
        migrations.AlterField(
            model_name='product',
            name='rating',
            field=models.IntegerField(
                choices=[
                    (0, 0),
                    (1, 1),
                    (2, 2),
                    (3, 3),
                    (4, 4),
                    (5, 5),
                ],
                default=0,
                verbose_name='Рейтинг',
            ),
        ),
    ]
