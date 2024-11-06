from rest_framework import serializers

from .models import Cat, Owner, Achievement, AchievementCat, CHOICES

import datetime as dt
import webcolors


class AchievementSerializer(serializers.ModelSerializer):
    """
    Сериализатор, унаследованный от ModelSerializer, по умолчанию использует
    те же названия полей, что и в модели, с которой он работает. 
    Эти же имена служат ключами в ответе API.
    Необходимость изменить имена 
    решают через переопределение поля и применение параметра source=<'оригинальное имя поля в модели'>
    """
    # новое название  ↓                     старое название ↓
    achievement_name = serializers.CharField(source='name')

    class Meta:
        model = Achievement
        fields = ('id', 'name')


class Hex2NameColor(serializers.Field):
    """
    Для создания собственного типа поля сериализатора нужно описать класс для нового типа, 
    который будет унаследован от serializers.Field и описать в нём два метода:
    def to_representation(self, value) (для чтения)
    и def to_internal_value(self, data) (для записи).
    """
    # При чтении данных ничего не меняем - просто возвращаем как есть
    def to_representation(self, value):
        return value
    # При записи код цвета конвертируется в его название
    def to_internal_value(self, data):
        # Доверяй, но проверяй
        try:
            # Если имя цвета существует, то конвертируем код в название
            data = webcolors.hex_to_name(data)
        except ValueError:
            # Иначе возвращаем ошибку
            raise serializers.ValidationError('Для этого цвета нет имени')
        # Возвращаем данные в новом формате
        return data
    

class CatSerializer(serializers.ModelSerializer):
    # many=True не нужен, потому что у коты мб только один хозяин
    # УБРАЛИ    owner = serializers.StringRelatedField(read_only=True)   чтобы можно было записывать данные, а не только читать
    # Переопределяем поле achievements, чтобы получать объекты целиком, а не ссылки на них
    # вложенный сериализатор ↓
    achievements = AchievementSerializer(many=True, required=False)   #  много достижений, поэтому many=True    
                                                                      # Убрали read_only=True
                                                                      # required=False делает поле achievements из модели необязательным, в модели явно не прописано
    age = serializers.SerializerMethodField()
    # color = Hex2NameColor()  # Вот он - наш собственный тип поля
    # Теперь поле примет только значение, упомянутое в списке CHOICES
    color = serializers.ChoiceField(choices=CHOICES)

    class Meta:
        model = Cat
        fields = ('id', 'name', 'color', 'birth_year', 'owner', 'achievements', 'age', 'color')     #  добавили 'achievements'

    def get_age(self, obj):
        """
        SerializerMethodField — это поле для чтения, связанное с определённым методом,
        в котором будет вычислено значение этого поля. 
        Аргументами метода get_<имя_поля> должны быть self и сериализуемый объект 
        """
        return dt.datetime.now().year - obj.birth_year 


    def create(self, validated_data):
            """
            При работе с сериализаторами бывает полезен доступ к тем данным, которые были переданы в сериализатор: 
            например, если нужно проверить, было ли передано в запросе какое-нибудь необязательное поле. 
            Эти данные хранятся в словаре serializer.initial_data
            """
                    # Если в исходном запросе не было поля achievements
            if 'achievements' not in self.initial_data:
                 # То создаём запись о котике без его достижений
                 cat = Cat.objects.create(**validated_data)
                 return cat

        # Иначе делаем следующее:
            # Уберём список достижений из словаря validated_data и сохраним его
            achievements = validated_data.pop('achievements')

            # Создадим нового котика пока без достижений, данных нам достаточно
            cat = Cat.objects.create(**validated_data)

            # Для каждого достижения из списка достижений
            for achievement in achievements:
                # Создадим новую запись или получим существующий экземпляр из БД
                current_achievement, status = Achievement.objects.get_or_create(
                    **achievement)
                # Поместим ссылку на каждое достижение во вспомогательную таблицу
                # Не забыв указать к какому котику оно относится
                AchievementCat.objects.create(
                    achievement=current_achievement, cat=cat)
            return cat 


class OwnerSerializer(serializers.ModelSerializer):
    # переопределяем PrimaryKeyRelatedField на StringRelatedField
    # аргументы:
    #   —   many=True:     Для поля cats в модели Owner установлена связь «один-ко-многим»,
    #                      следовательно, полю cats в сериализаторе надо разрешить обработку списка объектов.
    #   —   read_only=True:     Поля с типом StringRelatedField не поддерживают операции записи, 
    #                           поэтому для них всегда должен быть указан параметр read_only=True.

    cats = serializers.StringRelatedField(many=True, read_only=True)


    class Meta:
        model = Owner
        fields = ('first_name', 'last_name', 'cats')

"""В модели Owner нет поля cats, но эта модель связана с моделью Cat через related_name 'cats'. 
Сериализаторы могут работать с моделями, которые связаны друг с другом: 
можно указать имя cats в качестве поля сериализатора."""


"""
По умолчанию для связанных полей модели сериализатор будет использовать тип PrimaryKeyRelatedField;
этот тип поля в сериализаторе оперирует первичными ключами (id) связанного объекта. 

Нужно переопределить дефолтный PrimaryKeyRelatedField на StringRelatedField,
чтобы вместо id возвращалось строковое представление объекта.

если у указанной модели изменится строковое представление,
то в случае использования StringRelatedField эти изменения отразятся и на ответах API.
"""