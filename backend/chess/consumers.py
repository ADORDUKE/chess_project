import json # Для работы с JSON-данными 
import chess # Шахматная библиотека для логики игры
from channels.generic.websocket import AsyncWebsocketConsumer # Базовый класс для WebSocket
from channels.db import database_sync_to_async # Для работы с БД в асинхронном коде
from .models import Game # Наша модель игры


class ChessConsumer(AsyncWebsocketConsumer):
    """
    Обработчик WebSocket-соединений для шахматной игры
    Основные методы:
    - connect: при подключении
    - disconnect: при отключении
    - receive: при получении сообщения

    1. Обрабатывает все события WebSocket для шахматной игры
    2. Работает асинхронно (async/await)
    """
    async def connect(self):
        # Получаем ID игры из URL (например: ws/game/123/)
        self.game_id = self.scope['url_route']['kwargs']['game_id']

        # Создаём имя группы для этой игры (все подключения к одной игре)
        self.game_group_name = f'game_{self.game_id}'

        # Добавляем текущее соединение в группу
        await self.channel_layer.group_add(
            self.game_group_name,
            self.channel_name
        )

        # Принимаем соединение
        await self.accept()

        # Отправляем текущее состояние игры новому участнику
        game = await self.get_game()
        if game:
            await self.send(text_data=json.dumps({
                'type':'game_state',
                'fen': game.fen,
                'current_turn': game.current_turn,
                'status': game.status
            }))

    # 1. Из URL /ws/game/123/ извлекаем game_id=123
    # 2. Создаём группу game_123 для всех участников этой игры
    # 3. Добавляем текущее соединение в группу
    # 4. Отправляем текущее состояние доски (FEN) и чей ход



    async def disconnect(self, close_code):
        # Удаляем соединение из группы при отключении
        await self.channel_layer.group_discard(
            self.game_group_name,
            self.channel_name
        )

    # 1. Когда пользователь закрывает вкладку или теряет соединение
    # 2. Удаляем его из группы игры, чтобы не пытаться отправлять сообщения


    async def receive(self, text_data):
        # Парсим JSON-сообщение от клиента
        data = json.loads(text_data)

        # Обрабатываем разные типы сообщений
        if data['type'] == 'join_game':
            # Игрок присоединяется к игре (белыми или чёрными)
            player_type = data['player_type']
            game = await self.get_game()

            if game:
                if player_type == 'white' and not game.white_player:
                    await self.set_player(player_type, self.scope['user'])
                elif player_type == 'black' and not game.black_player:
                    await self.set_player(player_type, self.scope['user'])
                
                await self.channel_layer.group_send(
                    self.game_group_name,
                    {
                        'type': 'game_message',
                        'message': {
                            'type': 'player_joined',
                            'player_type': player_type,
                            'fen': game.fen,
                            'current_turn': game.current_turn
                        }
                    }
                )
            
            # Обработка хода фигурой
            elif data['type'] == 'make_move':
                move = data['move']
                player_type = data['player_type']
                game = await self.get_game()

                if game and game.current_turn == player_type:
                    board = chess.Board(game.fen)
                    try:
                        chess_move = board.parse_same(move)
                        if chess_move in board.legal_moves:
                            board.push(chess_move)

                            await self.update_game(
                                fen=board.fen(),
                                current_turn='black' if player_type == 'white' else 'white'
                            )

                            await self.channel_layer.group_send(
                                self.game_group_name,
                                {
                                    'type': 'game_message',
                                    'message':{
                                        'type': 'move_made',
                                        'move': move,
                                        'fen': board.fen(),
                                        'current_turn': 'white' if board.turn else 'black'
                                    }
                                }
                            )
                    except:
                        pass
            

    async def game_message(self,event):
        await self.send(text_data=json.dumps(event['message']))
    
    @database_sync_to_async
    def get_game(self):
        try:
            return Game.objects.get(id=self.game_id)
        except Game.DoesNotExist:
            return None
    
    @database_sync_to_async
    def set_player(self, player_type, user):
        game = Game.objects.get(id=self.game_id)
        if player_type == 'white':
            game.white_player = user
        else:
            game.black_player = user
        game.save()
    
    @database_sync_to_async
    def update_game(self, **kwargs):
        Game.objects.filter(id=self.game_id).update(**kwargs)
