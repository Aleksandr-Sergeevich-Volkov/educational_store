# Generated by Django 4.2.16 on 2024-12-23 19:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='address_pvz',
            field=models.CharField(default='Химки, Московсая улица, дом 11', max_length=250),
        ),
    ]
