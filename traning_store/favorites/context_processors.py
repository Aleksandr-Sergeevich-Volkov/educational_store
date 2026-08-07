# favorites/context_processors.py
from .utils import SessionFavorites


def favorites_context(request):
    """
    Контекстный процессор для избранного
    Доступен во всех шаблонах
    """
    session_fav = SessionFavorites(request)

    return {
        "favorites_count": session_fav.count(),
        "favorite_ids": session_fav.get_ids(),
    }
