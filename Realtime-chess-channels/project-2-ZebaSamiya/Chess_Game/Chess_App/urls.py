# Chess_App/urls.py

from django.urls import include, path
from .views import (
    home, about, history, rules, join, user_login, user_logout, guest_access,
    challenge_player, accept_invite, decline_invite, delete_game, new_game_screen
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
    path('journal/', include('journal.urls')), 
    path('guest_access/', guest_access, name='guest_access'),
    path('new_game_screen/', new_game_screen, name='new_game_screen'),
    path('accept-invite/<int:invite_id>/', accept_invite, name='accept_invite'),
    path('decline-invite/<int:invite_id>/', decline_invite, name='decline_invite'),
    path('delete_game/<uuid:game_id>/', delete_game, name='delete_game'),
]
