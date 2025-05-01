#   generics - готовые классы для типовых операций (список, создание, детализация)
#   Response - специальный класс для возврата ответов API
#   APIView - базовый класс для создания своих API-представлений
#   Game, GameSerializer - наши модель и сериализатор
#   uuid - генератор уникальных ID


# Импортируем необходимые компоненты из Django REST Framework
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

# Импортируем нашу модель Game и сериализатор
from .models import Game
from .serializers import GameSerializer

# Импортируем модуль uuid для генерации уникальных идентификаторов
import uuid

class GameListCreateView(generics.ListCreateAPIView):
    """
    Обрабатывает:
    - GET /api/games/ - список всех игр
    - POST /api/games/ - создание новой игры
    """
    queryset = Game.objects.all()   # Какие данные выбирать из БД
    serializer_class = GameSerializer  # Как преобразовывать данные

    # 1. При GET-запросе вернёт JSON со всеми играми
    # 2. При POST-запросе создаст новую игру
    # 3. Автоматически поддерживает пагинацию, фильтрацию

    def create(self, request, *args, **kwargs):
        game = Game.objects.create()
        return Response({
            'id': game.id,
            'fen': game.fen,
            'status': game.status
        })
    

class GameDetailView(APIView):
    """
    Обрабатывает:
    - GET /api/games/<id>/ - информация об одной игре
    """
    def get(self, request, pk):
        try:
            # Пытаемся найти игру по ID
            game = Game.objects.get(pk=pk)

            # Преобразуем данные игры через сериализатор
            serializer = GameSerializer(game)

             # Возвращаем JSON с данными
            return Response(serializer.data)
        
        except Game.DoesNotExist:
            # Если игра не найдена - возвращаем 404 ошибку
            return Response({
                'error': 'Game not found'
            }, status=404)
    
    # 1. Принимает pk (ID игры) из URL
    # 2. Пытается найти игру в базе
    # 3. Если находит - возвращает данные в JSON
    # 4. Если нет - возвращает ошибку 404L