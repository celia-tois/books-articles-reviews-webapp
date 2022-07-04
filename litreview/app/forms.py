from django import forms
from app.models import Ticket, Review


class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        exclude = ('user',)


class ReviewForm(forms.ModelForm):
    image = forms.ImageField(widget=forms.FileInput)

    class Meta:
        model = Review
        exclude = ('user', 'ticket')
