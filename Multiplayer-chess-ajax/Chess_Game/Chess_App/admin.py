from django.contrib import admin
from Chess_App.models import ChessGame

@admin.register(ChessGame)
class ChessGameAdmin(admin.ModelAdmin):
    list_display = ('id', 'white_player', 'black_player', 'status', 'outcome', 'moves', 'created_at', 'updated_at')
    list_filter = ('status', 'outcome', 'current_turn')
    search_fields = ('white_player__username', 'black_player__username', 'id')
