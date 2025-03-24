from django.urls import path
from .views import add_journal_entry, edit_journal_entry, delete_journal_entry, journal_entries, journal_dashboard


urlpatterns = [
    path('', journal_dashboard, name='journal_dashboard'),
    path('entries/', journal_entries, name='journal_entries'),
    path('add/<uuid:game_id>/', add_journal_entry, name='add_journal_entry'),
    path('edit/<int:id>/', edit_journal_entry, name='edit_journal_entry'),
    path('delete/<int:id>/', delete_journal_entry, name='delete_journal_entry'),
]
