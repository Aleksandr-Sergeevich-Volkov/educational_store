from catalog.models import (Appointment, Brend, Class_compress, Male, Soсk,
                            Type_product)
from django import template

register = template.Library()


@register.filter
def get_filter_display(value, key):
    try:
        # Преобразуем value в int если это строка с числом
        if isinstance(value, str) and value.isdigit():
            value_id = int(value)
        else:
            value_id = value
        if key == 'brand':
            obj = Brend.objects.get(id=value_id)
            return obj.name
        elif key == 'Class_compress':
            obj = Class_compress.objects.get(id=value)
            return obj.name
        elif key == 'Type_product':
            obj = Type_product.objects.get(id=value)
            return obj.name
        elif key == 'Appointment':
            obj = Appointment.objects.get(id=value)
            return obj.name
        elif key == 'Male':
            obj = Male.objects.get(id=value)
            return obj.name
        elif key == 'Sock':
            obj = Soсk.objects.get(id=value)
            return obj.name

    except (ValueError, TypeError) as e:
        # Ошибка преобразования типов
        print(f"Ошибка преобразования в get_filter_display: {e}")
        return value

    except (Brend.DoesNotExist, Class_compress.DoesNotExist,
            Type_product.DoesNotExist, Appointment.DoesNotExist,
            Male.DoesNotExist, Soсk.DoesNotExist) as e:
        # Объект не найден в БД
        print(f"Объект не найден в get_filter_display: key={key}, value={value}, error={e}")
        return value

    except Exception as e:
        # Любые другие ошибки (логируем, но не показываем пользователю)
        print(f"Неожиданная ошибка в get_filter_display: {e}")
        import traceback
        traceback.print_exc()
        return value
