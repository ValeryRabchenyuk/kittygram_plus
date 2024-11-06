from django.urls import include, path

from rest_framework.routers import DefaultRouter
# from rest_framework.authtoken import views        # перешли на JWT


from cats.views import CatViewSet, LightCatViewSet, OwnerViewSet


router = DefaultRouter()
router.register('cats', CatViewSet)
router.register('owners', OwnerViewSet)
router.register(r'mycats', LightCatViewSet) 

urlpatterns = [
    path('', include(router.urls)),
    # path('api-token-auth/', views.obtain_auth_token),   # перешли на JWT
        # Djoser создаст набор необходимых эндпоинтов.
        # базовые, для управления пользователями в Django:
    path('auth/', include('djoser.urls')),
        # JWT-эндпоинты, для управления JWT-токенами:
    path('auth/', include('djoser.urls.jwt')),
]

"""
При регистрации эндпоинтов для вьюсета в качестве URL-префикса используется не обычная строка, а регулярное выражение. 
За счёт этого URL-префикс может обрабатывать множество вариантов URL.

При регистрации эндпоинтов с таким URL-префиксом
router.register(r'profile/(?P<username>[\w.@+-]+)/', AnyViewSet)
..вьюсет AnyViewSet будет получать на обработку все запросы с адресов и подобных:
/profile/toh@/
/profile/nik.nik/
/profile/leo/

«просто строка» типа 'cats' — это частный случай регулярного выражения, Django интерпретировал её как regExp.
Префикс r перед строкой определяет raw-строку.
Такую строку система будет читать как простую последовательность символов,
игнорируя escape-последовательности.
"""