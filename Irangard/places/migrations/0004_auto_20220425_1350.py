# Generated by Django 3.2.8 on 2022-04-25 09:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('places', '0003_auto_20220423_1608'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contact',
            name='x_location',
            field=models.DecimalField(decimal_places=10, max_digits=15),
        ),
        migrations.AlterField(
            model_name='contact',
            name='y_location',
            field=models.DecimalField(decimal_places=10, max_digits=15),
        ),
    ]
