# Chess_App/consumers.py

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from channels.db import database_sync_to_async
from .utils import fen_to_dict
import chess
from .models import ChessGame, Invite, PlayerGame  
from asgiref.sync import async_to_sync  

logger = logging.getLogger(__name__)


class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_id = self.scope['url_route']['kwargs']['game_id']
        self.room_group_name = f'game_{self.game_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        logger.info(f"WebSocket connection accepted for game_id: {self.game_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"WebSocket connection closed for game_id: {self.game_id}")

    async def receive(self, text_data):
        logger.info(f"Received data: {text_data} from game_id: {self.game_id}")
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')

        if message_type == 'move':
            move = text_data_json.get('move')
            user = self.scope['user']


            result = await self.process_move(user, move)

            if result['success']:
                await self.send_game_update()
            else:
                # Send error message to the user
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result['error']
                }))
                logger.error(f"Error processing move: {result['error']}")

        elif message_type == 'resign':
            user = self.scope['user']
            logger.info(f"Processing resignation by user: {user.username}")
            result = await self.process_resign(user)
            if result['success']:
                await self.send_game_update()
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': result['error']
                }))
                logger.error(f"Error processing resignation: {result['error']}")

    @database_sync_to_async
    def process_move(self, user, move_input):
        try:
            game = ChessGame.objects.get(id=self.game_id)
        except ChessGame.DoesNotExist:
            return {'success': False, 'error': 'Game does not exist.'}

        is_user_turn = (game.current_turn == 'white' and user == game.white_player) or \
                       (game.current_turn == 'black' and user == game.black_player)
        if not is_user_turn:
            return {'success': False, 'error': 'It is not your turn.'}

        board = chess.Board()
        if game.board_state != 'start':
            board.set_fen(game.board_state)

        try:
            move = chess.Move.from_uci(move_input)
            if move in board.legal_moves:
                board.push(move)
                game.board_state = board.fen()
                game.current_turn = 'black' if game.current_turn == 'white' else 'white'
                game.moves += 1
                if board.is_game_over():
                    game.status = 'completed'
                    if board.is_checkmate():
                        if board.turn == chess.WHITE:
                            game.outcome = 'black_win'
                            game.winner = game.black_player
                        else:
                            game.outcome = 'white_win'
                            game.winner = game.white_player
                    else:
                        game.outcome = 'tie'
                        game.winner = None  # Tie has no winner
                game.save()
                logger.info(f"Move processed successfully for game_id: {self.game_id}")
                return {'success': True}
            else:
                logger.warning(f"Invalid move attempted: {move_input} for game_id: {self.game_id}")
                return {'success': False, 'error': 'Invalid move.'}
        except ValueError:
            logger.warning(f"Invalid move format: {move_input} for game_id: {self.game_id}")
            return {'success': False, 'error': 'Invalid move format.'}

    @database_sync_to_async
    def process_resign(self, user):
        try:
            game = ChessGame.objects.get(id=self.game_id)
        except ChessGame.DoesNotExist:
            return {'success': False, 'error': 'Game does not exist.'}

        if game.status != 'in_progress':
            return {'success': False, 'error': 'Game is not in progress.'}

        if game.white_player == user:
            game.outcome = 'black_win'
            game.winner = game.black_player
        elif game.black_player == user:
            game.outcome = 'white_win'
            game.winner = game.white_player
        else:
            return {'success': False, 'error': 'You are not a player in this game.'}

        game.status = 'completed'
        game.save()
        logger.info(f"User {user.username} resigned from game_id: {self.game_id}")

        return {'success': True}

    @database_sync_to_async
    def get_game_state(self):
        game = ChessGame.objects.get(id=self.game_id)
        board_rows = fen_to_dict(game.board_state)
        current_player = game.white_player.username if game.current_turn == 'white' else game.black_player.username

        game_state = {
            'id': str(game.id),
            'board': board_rows,
            'current_turn': current_player,
            'moves': game.moves,
            'status': game.status,
            'outcome': game.outcome,
        }

        if game.status == 'completed':
            if game.outcome == 'white_win':
                winner = game.white_player.username
            elif game.outcome == 'black_win':
                winner = game.black_player.username
            else:
                winner = None
            game_state['winner'] = winner

        return game_state
    

    async def send_game_update(self):
        game_state = await self.get_game_state()
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_update',
                'game': game_state
            }
        )
        logger.info(f"Sent game update for game_id: {self.game_id}")

    async def game_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'game_update',
            'game': event['game']
        }))
        logger.info(f"Broadcasted game update to group {self.room_group_name}")

class NotificationConsumer(AsyncWebsocketConsumer):
    online_users = set()

    async def connect(self):
        logger.info(f"Attempting WebSocket connection for user: {self.scope['user']}")
        if self.scope["user"].is_anonymous:
            logger.warning("User is anonymous. Closing WebSocket connection.")
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}"

            NotificationConsumer.online_users.add(self.user.id)

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.channel_layer.group_add(
                'online_users',
                self.channel_name
            )

            await self.accept()
            logger.info(f"User {self.user.username} connected to notifications.")

            await self.send(text_data=json.dumps({
                'type': 'online_users',
                'users': await self.get_online_users()
            }))

            await self.channel_layer.group_send(
                'online_users',
                {
                    'type': 'user_status',
                    'user_id': self.user.id,
                    'username': self.user.username,
                    'status': 'online'
                }
            )

    async def disconnect(self, close_code):
        NotificationConsumer.online_users.discard(self.user.id)

        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

        await self.channel_layer.group_discard(
            'online_users',
            self.channel_name
        )

        await self.channel_layer.group_send(
            'online_users',
            {
                'type': 'user_status',
                'user_id': self.user.id,
                'username': self.user.username,
                'status': 'offline'
            }
        )

        logger.info(f"User {self.user.username} disconnected from notifications.")

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            if message_type == 'send_invite':
                opponent_id = data.get('opponent_id')
                result = await self.process_invite(self.user, opponent_id)
                if result['success']:
                    await self.send(text_data=json.dumps({
                        'type': 'success',
                        'message': 'Invitation sent successfully.'
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type': 'error',
                        'message': result['error']
                    }))
        except Exception as e:
            logger.error(f"Error in receive method: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'An error occurred while processing your request.'
            }))

    @database_sync_to_async
    def process_invite(self, inviter, opponent_id):
        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            return {'success': False, 'error': "Invalid opponent selection."}

        if opponent == inviter:
            return {'success': False, 'error': "You cannot invite yourself."}

        existing_invite = Invite.objects.filter(inviter=inviter, invitee=opponent, accepted=False).exists()
        if existing_invite:
            return {'success': False, 'error': "An invite already exists."}

        invite = Invite.objects.create(inviter=inviter, invitee=opponent)

        async_to_sync(self.channel_layer.group_send)(
            f"user_{opponent.id}",
            {
                'type': 'send_notification',
                'message': f"{inviter.username} has sent you a game invite.",
                'invite_id': invite.id,
                'inviter_username': inviter.username,
            }
        )

        return {'success': True}

    async def send_notification(self, event):
        message = event['message']
        invite_id = event.get('invite_id')
        inviter_username = event.get('inviter_username')
        game_id = event.get('game_id')

        notification = {
            'message': message
        }

        if invite_id:
            notification['invite_id'] = invite_id
        if inviter_username:
            notification['inviter_username'] = inviter_username
        if game_id:
            notification['game_id'] = game_id

        await self.send(text_data=json.dumps(notification))
        logger.info(f"Sent notification to user {self.user.username}: {message}")

    @database_sync_to_async
    def get_online_users(self):
        online_user_ids = NotificationConsumer.online_users - {self.user.id}
        users = User.objects.filter(id__in=online_user_ids).values('id', 'username')
        return list(users)

    async def user_status(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_status',
            'user_id': event['user_id'],
            'username': event['username'],
            'status': event['status']
        }))