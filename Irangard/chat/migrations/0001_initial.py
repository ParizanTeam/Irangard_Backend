# Generated by Django 3.2.8 on 2023-03-03 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('room_name', models.CharField(max_length=250)),
                ('sender_type', models.CharField(choices=[('SERVER', 'Server'), ('CLIENT', 'Client')], max_length=6, null=True)),
                ('sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='send_chats', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
