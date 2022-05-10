from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from . import forms, models
from django.contrib.auth.models import User

User = get_user_model()


@login_required
def home(request):
    return render(request, 'app/home.html')


@login_required
def follow_users(request):
    users = User.objects.all()
    subscriptions = [subscription.followed_user for subscription in models.UserFollows.objects.filter(user=request.user)]
    followers = [follower.user for follower in models.UserFollows.objects.filter(followed_user=request.user)]
    if request.method == 'POST':
        try:
            user_to_follow = User.objects.get(username=request.POST['username'])
            if user_to_follow is not request.user and user_to_follow not in subscriptions:
                user_followed = models.UserFollows(user=request.user, followed_user=user_to_follow)
                user_followed.save()
        except:
            print("Impossible de s'abonner à cet utilisateur")
    context = {
        'users': users,
        'subscriptions': subscriptions,
        'followers': followers,
    }
    return render(request, 'app/follow_users_form.html', context=context)
