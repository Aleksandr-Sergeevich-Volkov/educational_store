from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def user_context_processor(request):
    return {
        'is_authenticated': request.user.is_authenticated,
        'username': request.user.username if request.user.is_authenticated else 'войдите или зарегистрируйтесь',
    }
