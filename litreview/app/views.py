from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from . import forms, models
from django.contrib.auth.models import User

User = get_user_model()


@login_required
def flux(request):
    user_logged_in = User.objects.get(username=request.user)
    users_to_display = [user_logged_in]
    for subscription in models.UserFollows.objects.filter(user=request.user):
        user = User.objects.get(username=subscription.followed_user)
        users_to_display.append(user)
    tickets = models.Ticket.objects.filter(user=users_to_display[0])
    print(tickets)
    return render(request, 'app/flux.html', context={'tickets': tickets, 'user_logged_in': user_logged_in})


@login_required
def follow_users(request):
    users = User.objects.all()
    subscriptions = [subscription.followed_user for subscription in models.UserFollows.objects.filter(user=request.user)]
    followers = [follower.user for follower in models.UserFollows.objects.filter(followed_user=request.user)]
    if request.method == 'POST':
        try:
            user_to_follow = User.objects.get(username=request.POST['username'])
            if user_to_follow != request.user and user_to_follow not in subscriptions:
                user_followed = models.UserFollows(user=request.user, followed_user=user_to_follow)
                user_followed.save()
                return redirect('subscriptions')
        except:
            print("Impossible de s'abonner à cet utilisateur")
    context = {
        'users': users,
        'subscriptions': subscriptions,
        'followers': followers,
    }
    return render(request, 'app/follow_users.html', context=context)


@login_required
def unfollow_user(request, id):
    user_selected = User.objects.get(id=id)
    for user in models.UserFollows.objects.filter(user=request.user):
        if user.followed_user == user_selected:
            user_to_unfollow = user
            username_of_user_to_unfollow = user_to_unfollow.followed_user.username
            if request.method == 'POST':
                user_to_unfollow.delete()
                return redirect('subscriptions')
    return render(request, 'app/unfollow_user.html', context={'username_of_user_to_unfollow': username_of_user_to_unfollow})


@login_required
def create_ticket(request):
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    return render(request, 'app/create_ticket.html', context={'form': form})


@login_required
def create_review(request):
    return render(request, 'app/create_review.html')