# Generated by Django 3.2.8 on 2022-05-07 22:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_auto_20220423_1545'),
    ]

    operations = [
        migrations.CreateModel(
            name='StagedPayments',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_id', models.CharField(max_length=50)),
                ('order_id', models.CharField(max_length=50)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='staged_payments_info', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
