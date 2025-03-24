# journal/views.py

from django.shortcuts import render, redirect, get_object_or_404
from .models import JournalEntry
from Chess_App.models import ChessGame
from .forms import JournalEntryForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages


@login_required
def journal_entries(request):
    completed_games = ChessGame.objects.filter(
        Q(white_player=request.user) | Q(black_player=request.user),
        status='completed'
    ).order_by('-id')

    game_entries = []
    for game in completed_games:
        opponent = game.black_player if game.white_player == request.user else game.white_player
        entry = JournalEntry.objects.filter(user=request.user, game=game).first()
        
        if game.outcome == 'white_win':
            outcome = 'Win' if game.white_player == request.user else 'Loss'
        elif game.outcome == 'black_win':
            outcome = 'Win' if game.black_player == request.user else 'Loss'
        elif game.outcome == 'tie':
            outcome = 'Tie'
        else:
            outcome = 'Loss' 
        
        game_entries.append({
            'game': game,
            'opponent': opponent,
            'moves': game.moves,
            'outcome': outcome,
            'entry': entry,
        })

    return render(request, 'journal/journal.html', {'game_entries': game_entries})


@login_required
def add_journal_entry(request, game_id):
    game = get_object_or_404(ChessGame, id=game_id, status='completed')
    
    existing_entry = JournalEntry.objects.filter(user=request.user, game=game).first()
    if existing_entry:
        messages.error(request, 'A journal entry for this game already exists.')
        return redirect('journal_entries')
    
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            new_entry = form.save(commit=False)
            new_entry.user = request.user
            new_entry.game = game
            new_entry.save()
            messages.success(request, 'Journal entry added successfully.')
            return redirect('journal_entries')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add_journal_entry.html', {'form': form, 'game': game})


@login_required
def edit_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, id=id, user=request.user)
    game = entry.game

    if request.method == 'POST':
        form = JournalEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Journal entry updated successfully.")
            return redirect('journal_entries')
    else:
        form = JournalEntryForm(instance=entry)

    return render(request, 'journal/edit_journal_entry.html', {'form': form, 'game': game, 'entry': entry})


@login_required
def delete_journal_entry(request, id):
    entry = get_object_or_404(JournalEntry, id=id, user=request.user)
    if request.method == 'POST':
        entry.delete()
        messages.success(request, "Journal entry deleted successfully.")
        return redirect('journal_entries')
    return render(request, 'journal/delete_journal_entry.html', {'entry': entry})


def journal_dashboard(request):
    return redirect('journal_entries')




