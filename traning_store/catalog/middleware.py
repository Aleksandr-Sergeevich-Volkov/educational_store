from urllib.parse import urlencode

from django.shortcuts import redirect


class CleanURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Только для GET запросов с параметрами
        if request.method == 'GET' and request.GET:
            cleaned_params = {}

            for key, value in request.GET.items():
                # Проверяем, не пустое ли значение
                if self._is_not_empty(value):
                    cleaned_params[key] = value

            # Если были пустые параметры - редирект
            if len(cleaned_params) != len(request.GET):
                path = request.path
                if cleaned_params:
                    query_string = urlencode(cleaned_params, doseq=True)
                    new_url = f"{path}?{query_string}"
                else:
                    new_url = path

                return redirect(new_url)

        return self.get_response(request)

    def _is_not_empty(self, value):
        """Проверяет, не пустое ли значение"""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, list):
            return any(self._is_not_empty(v) for v in value)
        return True
