# Generated by Django 3.2.16 on 2024-10-02 14:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0001_initial'),
    ]

    operations = [
        #migrations.CreateModel(
        #    name='Model_type',
        #    fields=[
        #        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #        ('name', models.CharField(max_length=128, verbose_name='Название')),
        #    ],
        #    options={
        #        'verbose_name': 'Модель',
        #        'verbose_name_plural': 'Модель',
        #        'ordering': ('name',),
        #    },
        #),
        #migrations.CreateModel(
        #    name='Size',
        #    fields=[
        #        ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #        ('name', models.CharField(max_length=128, verbose_name='Название')),
        #    ],
        #    options={
        #        'verbose_name': 'Размер',
        #        'verbose_name_plural': 'Размер',
        #        'ordering': ('name',),
        #    },
        #),
        migrations.AlterField(
            model_name='product',
            name='Side',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.side'),
        ),
        migrations.AlterField(
            model_name='product',
            name='Wide_hips',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='catalog.wide_hips'),
        ),
        migrations.AddField(
            model_name='product',
            name='Model_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='catalog.model_type'),
        ),
        migrations.AddField(
            model_name='product',
            name='Size',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='catalog.size'),
        ), 
    ]
