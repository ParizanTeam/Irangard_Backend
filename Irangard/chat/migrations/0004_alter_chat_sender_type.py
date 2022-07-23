# Generated by Django 3.2.8 on 2022-07-10 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_chat_sender_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='sender_type',
            field=models.CharField(choices=[('SERVER', 'Server'), ('CLIENT', 'Client')], max_length=6, null=True),
        ),
    ]
