from django.db import models
from django.contrib.auth.models import User
from Chess_App.models import ChessGame

class JournalEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(ChessGame, on_delete=models.CASCADE)
    game_date = models.DateTimeField(auto_now_add=True) 
    description = models.TextField()

    def __str__(self):
        return f"Journal Entry for {self.user.username} on {self.game_date}"