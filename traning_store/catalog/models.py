from django.db import models
from traning_store.constant import TITLE_LEN

class Country(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    code = models.CharField('Код',
                                        max_length=TITLE_LEN)

    class Meta:
        verbose_name = 'Страна'
        verbose_name_plural = 'Страны'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.code}'
    
class Brend(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    country_brand = models.OneToOneField(
        # На какую модель ссылаемся
        Country,
        # Поведение при удалении:
        # если оригинальное имя будет удалено,
        # то и сам фильм будет удалён. 
        on_delete=models.CASCADE
    ) 
    class Meta:
        verbose_name = 'Бренд'
        verbose_name_plural = 'Бренды'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}, {self.country_brand}'
    

class Appointment(models.Model):
    name = models.CharField('Название', max_length=TITLE_LEN)
    class Meta:
        verbose_name = 'Назначение'
        verbose_name_plural = 'Назначения'
        ordering = ('name',)

    def __str__(self):
        return f'{self.name}'