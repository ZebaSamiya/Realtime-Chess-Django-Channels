# Chess_App/views.py

import chess
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.http import HttpResponse, JsonResponse
from .forms import LoginForm, JoinForm, MoveForm, ChallengeForm
from django.contrib.auth.decorators import login_required
from .models import ChessGame, Invite, PlayerGame
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from journal.models import JournalEntry
from .models import Invite
import json
from django.views.decorators.csrf import csrf_exempt
from .utils import fen_to_dict
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@csrf_exempt
def user_login(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data["username"]
            password = login_form.cleaned_data["password"]
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    auth_login(request, user)
                    return redirect('home')
                else:
                    return HttpResponse("Your account is not active.")
            else:
                return render(request, 'Chess_App/login.html', {"login_form": login_form, "error": "Invalid login credentials."})
        else:
            return render(request, 'Chess_App/login.html', {"login_form": login_form})
    else:
        login_form = LoginForm()
        return render(request, 'Chess_App/login.html', {"login_form": login_form})

@csrf_exempt
def user_logout(request):
    auth_logout(request)
    return redirect('user_login')

@csrf_exempt
def join(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        join_form = JoinForm(request.POST)
        if join_form.is_valid():
            user = join_form.save(commit=False)
            user.set_password(join_form.cleaned_data['password1'])
            user.save()
            auth_login(request, user)
            return redirect('home')
        else:
            return render(request, 'Chess_App/join.html', {'join_form': join_form})
    else:
        join_form = JoinForm()
        return render(request, 'Chess_App/join.html', {'join_form': join_form})

@csrf_exempt
def about(request):
    return render(request, 'Chess_App/about.html')
@csrf_exempt
def rules(request):
    return render(request, 'Chess_App/rules.html')
@csrf_exempt
def history(request):
    return render(request, 'Chess_App/history.html')
@csrf_exempt
def guest_access(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'Chess_App/guest_access.html')

@csrf_exempt
@login_required
def home(request):
    # Check for an active game
    game = ChessGame.objects.filter(
        Q(white_player=request.user) | Q(black_player=request.user),
        status='in_progress'
    ).first()

    if game:
        form = MoveForm()
        if game.current_turn == 'white':
            current_turn = game.white_player.username
        else:
            current_turn = game.black_player.username
        board_rows = fen_to_dict(game.board_state)
        
        # Determine user's color
        if game.white_player == request.user:
            user_color = 'white'
        else:
            user_color = 'black'
        
        is_user_turn = (game.current_turn == user_color)
        
        journal_entries = JournalEntry.objects.filter(user=request.user, game=game)
    
        return render(request, 'Chess_App/home.html', {
            'chess_form': form,
            'current_turn': current_turn,
            'rows': board_rows,
            'game': game,
            'journal_entries': journal_entries,
            'is_user_turn': is_user_turn,
            'user_color': user_color,
        })
    else:
        challenge_form = ChallengeForm(user=request.user)
        completed_games_qs = ChessGame.objects.filter(
            Q(white_player=request.user) | Q(black_player=request.user),
            status='completed'
        )
        
        player_games = PlayerGame.objects.filter(
            user=request.user,
            is_deleted=False,
            game__status='completed'
        ).select_related('game')

        game_entries = []
        for player_game in player_games:
            game = player_game.game
            if game.white_player == request.user:
                opponent = game.black_player
                user_color = 'white'
            else:
                opponent = game.white_player
                user_color = 'black'

            entry = JournalEntry.objects.filter(user=request.user, game=game).first()

            if game.outcome == 'tie':
                outcome = 'Tie'
            elif (game.outcome == 'white_win' and user_color == 'white') or \
                 (game.outcome == 'black_win' and user_color == 'black'):
                outcome = 'Win'
            else:
                outcome = 'Loss'

            game_entries.append({
                'game': game,
                'opponent': opponent,
                'moves': game.moves,
                'outcome': outcome,
                'entry': entry,
            })

        pending_invites = Invite.objects.filter(invitee=request.user, accepted=False)

        return render(request, 'Chess_App/new_game_screen.html', {
            'challenge_form': challenge_form,
            'game_entries': game_entries,
            'pending_invites': pending_invites,
        })
    


@csrf_exempt
@login_required
def new_game_screen(request):
    # Fetch completed games from PlayerGame where is_deleted=False
    player_games = PlayerGame.objects.filter(
        user=request.user,
        is_deleted=False,
        game__status='completed'
    ).select_related('game')

    game_entries = []
    for player_game in player_games:
        game = player_game.game
        opponent = game.black_player if game.white_player == request.user else game.white_player
        journal_entry = JournalEntry.objects.filter(user=request.user, game=game).first()

        if game.outcome == 'tie':
            outcome = 'Tie'
        elif (game.outcome == 'white_win' and game.white_player == request.user) or \
             (game.outcome == 'black_win' and game.black_player == request.user):
            outcome = 'Win'
        else:
            outcome = 'Loss'

        game_entries.append({
            'game': game,
            'opponent': opponent,
            'moves': game.moves,
            'outcome': outcome,
            'entry': journal_entry,
        })

    # **Ensure that only invites where the current user is the invitee are fetched**
    pending_invites = Invite.objects.filter(invitee=request.user, accepted=False)

    context = {
        'game_entries': game_entries,
        'challenge_form': ChallengeForm(user=request.user),
        'pending_invites': pending_invites,
    }
    return render(request, 'Chess_App/new_game_screen.html', context)


@csrf_exempt
@login_required
def challenge_player(request):
    if request.method == 'POST':
        form = ChallengeForm(request.POST, user=request.user)
        if form.is_valid():
            opponent = form.cleaned_data['opponent']
            
            if opponent == request.user:
                messages.error(request, 'You cannot challenge yourself.')
                return redirect('home')
            
            active_game = ChessGame.objects.filter(
                Q(white_player=request.user) | Q(black_player=request.user) |
                Q(white_player=opponent) | Q(black_player=opponent),
                status='in_progress'
            ).exists()
            if active_game:
                messages.error(request, 'Either you or the opponent already has an active game.')
                return redirect('home')
            
            game = ChessGame.objects.create(
                white_player=request.user,
                black_player=opponent,
                board_state=chess.Board().fen(),
                current_turn='white',
                status='in_progress'
            )
            # Create PlayerGame instances for both players
            PlayerGame.objects.create(user=request.user, game=game)
            PlayerGame.objects.create(user=opponent, game=game)

            invite = Invite.objects.create(inviter=request.user, invitee=opponent)

            # Send notification to the opponent via WebSocket
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f"user_{opponent.id}",
                {
                    'type': 'send_notification',
                    'message': f"{request.user.username} has sent you a game invite.",
                    'invite_id': invite.id,
                    'inviter_username': request.user.username,
                }
            )

            messages.success(request, f'Invitation sent to {opponent.username}')
            return redirect('home')
        else:
            messages.error(request, 'Invalid form submission.')
            return redirect('home')
    else:
        return redirect('home')


# @csrf_exempt
# @login_required
# def make_move(request):
#     if request.method == 'POST':
#         action = request.POST.get('action')  # Get the action from the form
#         game = ChessGame.objects.filter(
#             Q(white_player=request.user) | Q(black_player=request.user),
#             status='in_progress'
#         ).first()
#         if not game:
#             messages.error(request, 'No active game found.')
#             return redirect('home')

#         if action == 'resign':
#             # Handle resignation
#             if game.white_player == request.user:
#                 game.outcome = 'black_win'
#             else:
#                 game.outcome = 'white_win'

#             game.status = 'completed'
#             game.save()

#             messages.success(request, 'You have resigned. The game is now completed.')
#             return redirect('home')

#         elif action == 'move':
#             # Handle move submission
#             form = MoveForm(request.POST)
#             if form.is_valid():
#                 move_input = form.cleaned_data['move']
#                 is_user_turn = (game.current_turn == 'white' and request.user == game.white_player) or \
#                                (game.current_turn == 'black' and request.user == game.black_player)
#                 if not is_user_turn:
#                     messages.error(request, 'It is not your turn.')
#                     return redirect('home')

#                 # Load the board state
#                 board = chess.Board()
#                 if game.board_state != 'start':
#                     board.set_fen(game.board_state)
#                 try:
#                     move = chess.Move.from_uci(move_input)
#                     if move in board.legal_moves:
#                         board.push(move)
#                         game.board_state = board.fen()
#                         game.current_turn = 'black' if game.current_turn == 'white' else 'white'
#                         game.moves += 1
#                         if board.is_game_over():
#                             game.status = 'completed'
#                             if board.is_checkmate():
#                                 if board.turn == chess.WHITE:
#                                     game.outcome = 'black_win'
#                                 else:
#                                     game.outcome = 'white_win'
#                             else:
#                                 game.outcome = 'tie'
#                         game.save()
#                         return redirect('home')
#                     else:
#                         messages.error(request, 'Invalid move.')
#                 except ValueError:
#                     messages.error(request, 'Invalid move format.')
#             else:
#                 messages.error(request, 'Invalid form input.')
#         else:
#             messages.error(request, 'Unknown action.')
#     return redirect('home')

# @csrf_exempt
# @login_required
# def poll_game_state(request):
#     game = ChessGame.objects.filter(
#         Q(white_player=request.user) | Q(black_player=request.user),
#         status='in_progress'
#     ).first()

#     if game:
#         board_rows = fen_to_dict(game.board_state)
#         if game.current_turn == 'white':
#             current_player = game.white_player.username
#         else:
#             current_player = game.black_player.username
#         return JsonResponse({
#             'game': {
#                 'id': str(game.id),
#                 'board': board_rows,
#                 'current_turn': current_player,
#                 'moves': game.moves,
#                 'status': game.status,
#                 'outcome': game.outcome,
#             }
#         })
#     else:
#         available_users = User.objects.exclude(id=request.user.id).filter(is_active=True)
#         users_data = [{'id': user.id, 'username': user.username} for user in available_users]
#         return JsonResponse({'available_users': users_data})

# @csrf_exempt
# def fen_to_dict(fen_string):
#     piece_to_html = {
#         'K': '&#9812;', 'Q': '&#9813;', 'R': '&#9814;', 'B': '&#9815;', 'N': '&#9816;', 'P': '&#9817;',
#         'k': '&#9818;', 'q': '&#9819;', 'r': '&#9820;', 'b': '&#9821;', 'n': '&#9822;', 'p': '&#9823;',
#     }
#     if fen_string == 'start':
#         fen_string = chess.STARTING_FEN
#     position_part = fen_string.split(' ')[0]
#     ranks = position_part.split('/')
#     rows_list = []
#     for rank_index, rank_str in enumerate(ranks):
#         rank_number = 8 - rank_index
#         rank_dict = {}
#         file_index = 0
#         for c in rank_str:
#             if c.isdigit():
#                 for _ in range(int(c)):
#                     file_letter = chr(ord('a') + file_index)
#                     position = f"{file_letter}{rank_number}"
#                     rank_dict[position] = '&nbsp;'
#                     file_index += 1
#             else:
#                 file_letter = chr(ord('a') + file_index)
#                 position = f"{file_letter}{rank_number}"
#                 rank_dict[position] = piece_to_html.get(c, '&nbsp;')
#                 file_index += 1
#         rows_list.append(rank_dict)
#     return rows_list


@csrf_exempt
@login_required
def delete_game(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id)
    if request.user != game.white_player and request.user != game.black_player:
        messages.error(request, "You are not authorized to delete this game.")
        return redirect('home')

    if request.method == 'POST':
        # Set is_deleted=True for this user's PlayerGame instance
        try:
            player_game = PlayerGame.objects.get(user=request.user, game=game)
            player_game.is_deleted = True
            player_game.save()
            messages.success(request, "Game deleted successfully.")
        except PlayerGame.DoesNotExist:
            messages.error(request, "Game not found in your records.")
        return redirect('home')
    else:
        messages.error(request, "Invalid request method.")
        return redirect('home')


# Chess_App/views.py

@csrf_exempt
@login_required
def send_invite(request):
    if request.method == 'POST':
        opponent_id = request.POST.get('opponent')
        try:
            opponent = User.objects.get(id=opponent_id)
        except User.DoesNotExist:
            return JsonResponse({'success': False, 'error': "Invalid opponent selection."})

        if opponent == request.user:
            return JsonResponse({'success': False, 'error': "You cannot invite yourself."})

        existing_invite = Invite.objects.filter(inviter=request.user, invitee=opponent, accepted=False).exists()
        if existing_invite:
            return JsonResponse({'success': False, 'error': "An invite already exists."})

        invite = Invite.objects.create(inviter=request.user, invitee=opponent)

        # Send notification to the invitee about the new invite
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{opponent.id}",
            {
                'type': 'send_notification',
                'message': f"{request.user.username} has sent you a game invite.",
                'invite_id': invite.id,  # Add invite ID
                'inviter_username': request.user.username,  # Add inviter's username
            }
        )

        return JsonResponse({
            'success': True,
            'message': f'Invitation sent to {opponent.username}',
            'invite_id': invite.id,
            'inviter_username': request.user.username
        })
    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)



# accept_invite view
@csrf_exempt
@login_required
def accept_invite(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id, invitee=request.user, accepted=False)
    except Invite.DoesNotExist:
        messages.error(request, "The invitation does not exist or has already been processed.")
        return redirect('home')

    if request.method == 'POST':
        invite.accepted = True
        invite.save()

        game = ChessGame.objects.create(
            white_player=invite.inviter,
            black_player=invite.invitee,
            board_state=chess.Board().fen(),
            current_turn='white',
            status='in_progress'
        )

        # Create PlayerGame instances for both players
        PlayerGame.objects.create(user=invite.inviter, game=game)
        PlayerGame.objects.create(user=invite.invitee, game=game)

        # Send notification to inviter that invitee accepted
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{invite.inviter.id}",
            {
                'type': 'send_notification',
                'message': f"{request.user.username} has accepted your game invite.",
                'game_id': str(game.id)
            }
        )

        # Send notification to invitee (self) that game has started
        async_to_sync(channel_layer.group_send)(
            f"user_{invite.invitee.id}",
            {
                'type': 'send_notification',
                'message': f"Game started with {invite.inviter.username}.",
                'game_id': str(game.id)
            }
        )

        messages.success(request, f'Game started with {invite.inviter.username}')
        return redirect('home')
    else:
        return redirect('home')


# decline_invite view
@csrf_exempt
@login_required
def decline_invite(request, invite_id):
    try:
        invite = Invite.objects.get(id=invite_id, invitee=request.user, accepted=False)
    except Invite.DoesNotExist:
        messages.error(request, "The invitation does not exist or has already been processed.")
        return redirect('new_game_screen')

    if request.method == 'POST':
        invite.delete()

        # Send notification to inviter that invitee declined
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{invite.inviter.id}",
            {
                'type': 'send_notification',
                'message': f"{request.user.username} has declined your game invite."
            }
        )

        messages.success(request, 'Invitation declined.')
        return redirect('new_game_screen')
    else:
        return redirect('new_game_screen')


    
@csrf_exempt
@login_required
def check_invite(request):
    invite = Invite.objects.filter(invitee=request.user, accepted=False).first()
    if invite:
        return JsonResponse({
            'invite': True,
            'inviter': invite.inviter.username,
            'invite_id': invite.id
        })
    return JsonResponse({'invite': False})


@csrf_exempt
@login_required
def check_for_started_game(request):
    active_game = ChessGame.objects.filter(
        Q(white_player=request.user) | Q(black_player=request.user),
        status='in_progress'
    ).order_by('-id').first()
    
    if active_game:
        return JsonResponse({'game_started': True})
    else:
        return JsonResponse({'game_started': False})