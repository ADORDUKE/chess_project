from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()    # Получаем модель пользователя Django

class Game(models.Model):
    # Варианты выбора для цвета
    # Создаём константы для удобства (WHITE/WHITE вместо 'white'/'white')
    WHITE = 'white'
    BLACK = 'black'
    # COLOR_CHOICES - список вариантов для полей с выбором
    COLOR_CHOICES = [
        (WHITE, 'White'),   # ('значение в базе', 'читаемое имя')
        (BLACK, 'Black'),
    ]

    # Позиция на доске в FEN-формате (стандартный шахматный формат)
    # fen - текстовое представление шахматной доски
    fen = models.CharField(
        max_length=100, 
        default='rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
        )
    
    # Игрок за белых (связь с моделью User)
    white_player = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL,  # Если пользователь удалится, игра останется
        null=True,                  # Может быть пустым (пока нет игрока)
        related_name='white_games'  # Как обращаться из пользователя к его играм
        )
    
    # Игрок за чёрных (аналогично)
    black_player = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='black_games'
        )
    
     # Чей сейчас ход (выбор из COLOR_CHOICES)
    current_turn = models.CharField(
        max_length=5, 
        choices=COLOR_CHOICES, 
        default=WHITE
        )
    
     # Статус игры (ожидание, игра, завершена)
    status = models.CharField(max_length=20, default='waiting')

    # Даты создания и обновления (автоматически заполняются)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Game {self.id} - {self.white_player} vs {self.black_player}"
