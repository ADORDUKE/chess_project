# Импортируем необходимый модуль из Django REST Framework
from rest_framework import serializers

# Импортируем нашу модель Game из текущего каталога
from .models import Game

# Создаем класс сериализатора для модели Game
class GameSerializer(serializers.ModelSerializer):
    """
    Сериализатор преобразует данные игры:
    - Из модели Django → в JSON (для API)
    - Из JSON → в модель Django (при создании/обновлении)
    """

    # Вложенный класс Meta определяет настройки сериализатора
    class Meta:
        model = Game # Указываем, какую модель используем

         # Перечисляем все поля модели, которые нужно сериализовать
        fields = ['id', 'fen', 'white_player', 'black_player', 'current_turn', 'status']

# Для новичка важно понять, что сериализатор - это "мост" между сложными данными Django и простым JSON для фронтенда.