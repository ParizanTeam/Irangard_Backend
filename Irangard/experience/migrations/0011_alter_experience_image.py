# Generated by Django 3.2.8 on 2022-05-06 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experience', '0010_auto_20220506_1714'),
    ]

    operations = [
        migrations.AlterField(
            model_name='experience',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='images/experiences'),
        ),
    ]
