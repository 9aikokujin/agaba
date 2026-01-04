import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('balance', '0005_rename_date_modifed_alloperation_date_modified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance',
            name='user',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='balance',
                to=settings.AUTH_USER_MODEL,
                unique=True,
                verbose_name='Пользователь',
            ),
        ),
    ]
