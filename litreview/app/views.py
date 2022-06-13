from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Value, CharField
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from itertools import chain
from . import forms, models

User = get_user_model()


@login_required
def flux(request):
    user_logged_in = User.objects.get(username=request.user)
    users_to_display = [user_logged_in]
    for subscription in models.UserFollows.objects.filter(user=request.user):
        user = User.objects.get(username=subscription.followed_user)
        users_to_display.append(user)
    tickets = models.Ticket.objects.filter(user__in=users_to_display)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = models.Review.objects.filter(user__in=users_to_display)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    posts = sorted(chain(reviews, tickets), key=lambda post: post.time_created, reverse=True)

    for post in range(len(posts)):
        if posts[post].content_type == 'TICKET':
            check_if_ticket_has_review(posts, post)
        else:
            handle_rating_stars(posts, post)

    context = {
        'posts': posts,
        'user_logged_in': user_logged_in,
    }
    return render(request, 'app/flux.html', context=context)


def check_if_ticket_has_review(posts, post):
    ticket_in_review = models.Review.objects.filter(ticket=posts[post])
    if len(ticket_in_review) == 1:
        has_review = True
    else:
        has_review = False
    posts[post] = {"ticket": posts[post],
                   "has_review": has_review}


def handle_rating_stars(posts, post):
    rating = posts[post].rating
    full_stars = [star for star in range(rating)]
    empty_stars = [star for star in range(5 - rating)]
    posts[post] = {"review": posts[post],
                   "rating": {"full_stars": full_stars, "empty_stars": empty_stars}}


@login_required
def display_posts(request):
    user_logged_in = User.objects.get(username=request.user)
    tickets = models.Ticket.objects.filter(user=user_logged_in)
    reviews = []
    for review in models.Review.objects.filter(user=user_logged_in):
        rating = review.rating
        full_stars = [star for star in range(rating)]
        empty_stars = [star for star in range(5 - rating)]
        reviews.append({
            'review': review,
            'rating': {'full_stars': full_stars, 'empty_stars': empty_stars}
        })
    context = {
        'tickets': tickets,
        'reviews': reviews,
        'user_logged_in': user_logged_in,
    }
    return render(request, 'app/posts.html', context=context)


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
def edit_ticket(request, id):
    ticket = get_object_or_404(models.Ticket, id=id)
    form = forms.TicketForm(instance=ticket)
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES, instance=ticket)
        if form.is_valid():
            form.save()
            return redirect('posts')
    return render(request, 'app/edit_ticket.html', context={'form': form, 'ticket': ticket})


@login_required
def delete_ticket(request, id):
    ticket = get_object_or_404(models.Ticket, id=id)
    if request.method == 'POST':
        ticket.delete()
        return redirect('posts')
    return render(request, 'app/delete_ticket.html', context={'ticket': ticket})


@login_required
def create_review(request, id):
    user_logged_in = User.objects.get(username=request.user)
    ticket = models.Ticket.objects.get(id=id)
    form = forms.ReviewForm()
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.ticket = ticket
            review.save()
            return redirect('flux')
    rating_range = [number for number in range(6)]
    context = {
        'form': form,
        'ticket': ticket,
        'user_logged_in': user_logged_in,
        'rating_range': rating_range
    }
    return render(request, 'app/create_review.html', context=context)


@login_required
def edit_review(request, id):
    review = get_object_or_404(models.Review, id=id)
    form = forms.ReviewForm(instance=review)
    if request.method == 'POST':
        form = forms.ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('posts')
    rating_range = [number for number in range(6)]
    context = {
        'form': form,
        'ticket': review.ticket,
        'rating_range': rating_range
    }
    return render(request, 'app/edit_review.html', context=context)


@login_required
def delete_review(request, id):
    review = get_object_or_404(models.Review, id=id)
    if request.method == 'POST':
        review.delete()
        return redirect('posts')
    return render(request, 'app/delete_review.html', context={'review': review})