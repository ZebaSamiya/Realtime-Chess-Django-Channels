# Chess_App/urls.py

from django.urls import include, path
from .views import (
    home, about, history, rules, join, user_login, user_logout, guest_access,
    challenge_player, make_move, poll_game_state, challenge_player, send_invite, check_invite, accept_invite, decline_invite, check_for_started_game, delete_game
)

urlpatterns = [
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('history/', history, name='history'),
    path('rules/', rules, name='rules'),
    path('join/', join, name='join'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('challenge/', challenge_player, name='challenge_player'),
    path('move/', make_move, name='make_move'),
    path('poll/', poll_game_state, name='poll_game_state'),
    path('journal/', include('journal.urls')), 
    path('guest_access/', guest_access, name='guest_access'),
    path('challenge_player/', challenge_player, name='challenge_player'),
    path('invite-player/', send_invite, name='send_invite'),
    path('check-invite/', check_invite, name='check_invite'),
    path('accept-invite/<int:invite_id>/', accept_invite, name='accept_invite'),
    path('decline-invite/<int:invite_id>/', decline_invite, name='decline_invite'),
    path('check-for-started-game/', check_for_started_game, name='check_for_started_game'),
    path('delete_game/<uuid:game_id>/', delete_game, name='delete_game'),
    
]

