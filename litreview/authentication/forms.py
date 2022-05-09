from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': ("Nom d'utilisateur")})
        self.fields['password1'].widget.attrs.update({'placeholder': ("Mot de passe")})
        self.fields['password2'].widget.attrs.update({'placeholder': ("Confirmer le mot de passe")})

    class Meta(UserCreationForm.Meta):
        model = get_user_model()
        fields = ('username', )