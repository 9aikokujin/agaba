from django.db import migrations, models


def fix_modertor_role(apps, schema_editor):
    CustomUser = apps.get_model('account', 'CustomUser')
    CustomUser.objects.filter(role='modertor').update(role='moderator')


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0003_delete_notification'),
        ('balance', '0005_rename_date_modifed_alloperation_date_modified'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='balance',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(
                choices=[
                    ('buyer', 'Покупатель'),
                    ('seller', 'Продавец'),
                    ('admin', 'Админ'),
                    ('superadmin', 'Суперадмин'),
                    ('manager', 'Менеджер по заказам'),
                    ('broker', 'Брокер'),
                    ('moderator', 'Модератор'),
                    ('buh', 'Бухгалтер'),
                ],
                default='buyer',
                max_length=20,
                verbose_name='Роль пользователя',
            ),
        ),
        migrations.RunPython(fix_modertor_role, migrations.RunPython.noop),
    ]
