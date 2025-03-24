# Chess_App/forms.py

from django import forms
from django.core import validators
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

def validate_uci_move(value):
    """
    Validate that the move is in UCI format (e.g., e2e4 or e7e8q)
    """
    if len(value) not in [4, 5]:
        raise forms.ValidationError("Enter a valid UCI move (e.g., 'e2e4' or 'e7e8q').")
    source, dest = value[:2], value[2:4]
    files = "abcdefgh"
    ranks = "12345678"
    if source[0] not in files or source[1] not in ranks:
        raise forms.ValidationError("Invalid source position.")
    if dest[0] not in files or dest[1] not in ranks:
        raise forms.ValidationError("Invalid destination position.")
    if len(value) == 5 and value[4] not in ['q', 'r', 'b', 'n']:
        raise forms.ValidationError("Invalid promotion piece. Use 'q', 'r', 'b', or 'n'.")

class MoveForm(forms.Form):
    move = forms.CharField(
        max_length=5,
        strip=True,
        widget=forms.TextInput(attrs={'placeholder': 'e2e4', 'style': 'font-size:small'}),
        validators=[validate_uci_move]
    )

class JoinForm(UserCreationForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'size': '30'}), help_text="Enter a valid email address.")

    class Meta:
        model = get_user_model()  # Ensures using the correct user model
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
        help_texts = {
            'username': None,
            'password1': "Enter a strong password.",
            'password2': "Enter the same password as before, for verification."
        }

    def __init__(self, *args, **kwargs):
        super(JoinForm, self).__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'autocomplete': 'new-password'})
        self.fields['password2'].widget.attrs.update({'autocomplete': 'new-password'})

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput())

class ChallengeForm(forms.Form):
    opponent = forms.ModelChoiceField(
        queryset=User.objects.none(),
        empty_label="Select an opponent",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super(ChallengeForm, self).__init__(*args, **kwargs)
        self.fields['opponent'].queryset = User.objects.exclude(id=user.id).filter(is_active=True)

