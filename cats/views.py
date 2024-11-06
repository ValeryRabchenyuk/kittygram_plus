from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import mixins


from .models import Cat, Owner
from .serializers import CatSerializer, OwnerSerializer


class CatViewSet(viewsets.ModelViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer
    # Пишем метод, а в декораторе разрешим работу со списком объектов
    # и переопределим URL на более презентабельный
    @action(detail=False, url_path='recent-white-cats')
    def recent_white_cats(self, request):
        """
        Нестандартные через декоратор   @action.
        По умолчанию отслеживает только GET-запрос, можно разрешить и другие:    @action(methods=['get', 'delete', ...]
        Параметр detail  = True (разрешена работа с одним объектом) или False (работаем с коллекцией):
	    url_path='...' изменяет URL эндпоинта по умолчанию.
        """
        # Нужно получить записи о пяти котиках белого цвета
        cats = Cat.objects.filter(color='White')[:5]
        # Передадим queryset cats сериализатору 
        # и разрешим работу со списком объектов
        serializer = self.get_serializer(cats, many=True)
        return Response(serializer.data) 


class CreateRetrieveViewSet(mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                            viewsets.GenericViewSet):
    """
    Собственный базовый класс вьюсета: он будет создавать экземпляр объекта и получать экземпляр объекта.
    В DRF есть пять предустановленных классов миксинов ↑ :
    CreateModelMixin; 
    ListModelMixin; 
    RetrieveModelMixin; 
    UpdateModelMixin; 
    DestroyModelMixin 
    """
    # В теле класса код не нужен
    pass 


class LightCatViewSet(CreateRetrieveViewSet):
    queryset = Cat.objects.all()
    serializer_class = CatSerializer 


class OwnerViewSet(viewsets.ModelViewSet):
    queryset = Owner.objects.all()
    serializer_class = OwnerSerializer