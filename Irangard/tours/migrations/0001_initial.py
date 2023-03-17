# Generated by Django 3.2.8 on 2023-03-03 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Tour',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('image', models.ImageField(blank=True, null=True, upload_to='images/tours')),
                ('cost', models.IntegerField(default=0)),
                ('capacity', models.IntegerField(default=0)),
                ('remaining', models.IntegerField(default=0)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('total_revenue', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('date_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('bookers', models.ManyToManyField(blank=True, related_name='tours', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tours', to='accounts.specialuser')),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.IntegerField(default=0)),
                ('date', models.DateTimeField()),
                ('sender', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='transactions', to=settings.AUTH_USER_MODEL)),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='transactions', to='tours.tour')),
            ],
        ),
        migrations.CreateModel(
            name='DiscountCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('off_percentage', models.IntegerField(default=0)),
                ('expire_date', models.DateTimeField()),
                ('code', models.CharField(max_length=255)),
                ('tour', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='discount_codes', to='tours.tour')),
            ],
        ),
    ]
