# Generated by Django 4.2.16 on 2024-11-14 18:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0008_product_available_product_created_product_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='gallery',
            name='main',
            field=models.BooleanField(default=False),
        ),
    ]
