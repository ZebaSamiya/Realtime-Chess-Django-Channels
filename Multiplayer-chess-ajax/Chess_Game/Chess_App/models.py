from django.db import models
import uuid
from django.contrib.auth.models import User
import chess

class ChessGame(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    OUTCOME_CHOICES = [
        ('white_win', 'White Wins'),
        ('black_win', 'Black Wins'),
        ('tie', 'Tie'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    white_player = models.ForeignKey(User, related_name='white_games', on_delete=models.CASCADE)
    black_player = models.ForeignKey(User, related_name='black_games', on_delete=models.CASCADE)
    board_state = models.CharField(max_length=255, default='start')
    current_turn = models.CharField(max_length=5, choices=[('white', 'White'), ('black', 'Black')], default='white')
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default='in_progress')
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES, blank=True, null=True)
    moves = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    winner = models.ForeignKey(User, related_name='won_games', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Game {self.id} between {self.white_player.username} and {self.black_player.username}"


class Invite(models.Model):
    inviter = models.ForeignKey(User, related_name='sent_invites', on_delete=models.CASCADE)
    invitee = models.ForeignKey(User, related_name='received_invites', on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Invite from {self.inviter} to {self.invitee}"
