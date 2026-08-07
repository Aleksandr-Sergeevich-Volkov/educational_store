class SessionFavorites:
    SESSION_KEY = "favorites"

    def __init__(self, request):
        self.session = request.session

        # ✅ КАК В КОРЗИНЕ - ПРЯМОЕ ОБРАЩЕНИЕ С СОЗДАНИЕМ
        favorites = self.session.get(self.SESSION_KEY)
        if favorites is None:
            # ✅ СОЗДАЕМ СЕССИЮ КАК В КОРЗИНЕ!
            favorites = self.session[self.SESSION_KEY] = []
            print("🔥 Session created/favorites initialized in __init__")

        self.favorites = favorites
        print(f"📦 Favorites: {self.favorites}")

    def toggle(self, product_id):
        product_id = str(product_id)

        print(f"🔄 Toggle {product_id}, Current: {self.favorites}")

        if product_id in self.favorites:  # ← '3' in ['3'] = True
            self.favorites.remove(product_id)  # ← УДАЛЯЕТ!
            self._save()
            print(f"🗑️ Removed: {product_id}, Result: {self.favorites}")
            return False
        else:
            self.favorites.append(product_id)
            self._save()
            print(f"✅ Added: {product_id}, Result: {self.favorites}")
            return True

    def _save(self):
        print(f"💾 Saving: {self.favorites}")
        self.session[self.SESSION_KEY] = self.favorites
        self.session.modified = True
        print(f"💾 Session after save: {dict(self.session)}")

    def is_favorite(self, product_id):
        return str(product_id) in self.favorites

    def get_ids(self):
        return [int(id) for id in self.favorites]

    def count(self):
        return len(self.favorites)

    def get_products(self):
        from catalog.models import Product

        ids = self.get_ids()
        if ids:
            return Product.objects.filter(id__in=ids)
        return Product.objects.none()

    def clear(self):
        self.favorites = []
        self._save()
