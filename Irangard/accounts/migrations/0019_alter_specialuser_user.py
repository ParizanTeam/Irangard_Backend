# Generated by Django 3.2.8 on 2022-05-25 18:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0018_auto_20220522_2003'),
    ]

    operations = [
        migrations.AlterField(
            model_name='specialuser',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='special_user', serialize=False, to=settings.AUTH_USER_MODEL),
        ),
    ]
