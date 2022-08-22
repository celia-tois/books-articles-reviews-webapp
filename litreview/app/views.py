from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Value, CharField
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from itertools import chain
from . import forms, models
from django.contrib.auth.models import User


@login_required(login_url='login')
def flux(request):
    """
    Display the :model:`models.Ticket` and :model:`models.Review` posted by
    the user logged in and the users followed by the user logged in.

    **Context**

    ``posts``
        List of dicts: :model:`myapp.Ticket` and has_review (bool) /
        :model:`models.Review` and rating (dict).
    ``user_logged_in``
        An instance of :model:`User`

    **Template:**

    :template:`app/flux.html`

    """
    user_logged_in = User.objects.get(username=request.user)
    users_to_display = [user_logged_in]
    for subscription in models.UserFollows.objects.filter(user=request.user):
        user = User.objects.get(username=subscription.followed_user)
        users_to_display.append(user)
    tickets = models.Ticket.objects.filter(user__in=users_to_display)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = models.Review.objects.filter(user__in=users_to_display)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    posts = sorted(chain(reviews, tickets),
                   key=lambda post: post.time_created, reverse=True)

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
    """
    Create a dict containing the :model:`myapp.Ticket` and has_review (bool).
    :arg: posts: List of :model:`myapp.Ticket`.
    :arg: post: Integer indicating the location of the post in the list of
    posts.
    """
    ticket_in_review = models.Review.objects.filter(ticket=posts[post])
    if len(ticket_in_review) == 1:
        has_review = True
    else:
        has_review = False
    posts[post] = {"ticket": posts[post],
                   "has_review": has_review}


def handle_rating_stars(posts, post):
    """
    Create a dict containing the :model:`myapp.Review` and rating (dict).
    :arg: posts: List of :model:`myapp.Ticket`.
    :arg: post: Integer indicating the location of the post in the list
    of posts.
    """
    rating = posts[post].rating
    full_stars = [star for star in range(rating)]
    empty_stars = [star for star in range(5 - rating)]
    posts[post] = {"review": posts[post],
                   "rating": {"full_stars": full_stars,
                              "empty_stars": empty_stars}}


@login_required(login_url='login')
def display_posts(request):
    """
    Display the :model:`models.Ticket` and :model:`models.Review` posted by
    the user logged in.

    **Context**

    ``posts``
        List of dicts: :model:`myapp.Ticket` / :model:`models.Review` and
        rating (dict).
    ``user_logged_in``
        An instance of User.

    **Template:**

    :template:`app/posts.html`

    """
    user_logged_in = User.objects.get(username=request.user)
    tickets = models.Ticket.objects.filter(user=user_logged_in)
    tickets = tickets.annotate(content_type=Value('TICKET', CharField()))

    reviews = models.Review.objects.filter(user=user_logged_in)
    reviews = reviews.annotate(content_type=Value('REVIEW', CharField()))

    posts = sorted(chain(reviews, tickets),
                   key=lambda post: post.time_created, reverse=True)

    for post in range(len(posts)):
        if posts[post].content_type == 'TICKET':
            posts[post] = {"ticket": posts[post]}
        else:
            handle_rating_stars(posts, post)

    context = {
        'posts': posts,
        'user_logged_in': user_logged_in,
    }
    return render(request, 'app/posts.html', context=context)


@login_required(login_url='login')
def follow_users(request):
    """
    Display the list of :model:`User` followed by the user logged in
    and the users following the user logged in.

    **Context**

    ``users``
        List of :model:`User`.
    ``subscriptions``
        List of :model:`models.UserFollows`.
    ``followers``
        List of :model:`models.UserFollows`.

    **Template:**

    :template:`app/follow_users.html`

    """
    users = User.objects.all()
    subscriptions = [subscription.followed_user for subscription
                     in models.UserFollows.objects.filter(user=request.user)]
    followers = [follower.user for follower in
                 models.UserFollows.objects.filter(followed_user=request.user)]
    if request.method == 'POST':
        try:
            user_to_follow = User.objects\
                .get(username=request.POST['username'])
            if user_to_follow != request.user and \
                    user_to_follow not in subscriptions:
                user_followed = models.UserFollows(
                    user=request.user, followed_user=user_to_follow)
                user_followed.save()
                return redirect('subscriptions')
        except ObjectDoesNotExist:
            print("Impossible de s'abonner à cet utilisateur")
    context = {
        'users': users,
        'subscriptions': subscriptions,
        'followers': followers,
    }
    return render(request, 'app/follow_users.html', context=context)


@login_required(login_url='login')
def unfollow_user(request, id):
    """
    Display an instance of :model:`User` to unfollow.

    **Context**

    ``username_of_user_to_unfollow``
        Username of the user to unfollow.

    **Template:**

    :template:`app/unfollow_user.html`

    """
    user_selected = User.objects.get(id=id)
    for user in models.UserFollows.objects.filter(user=request.user):
        if user.followed_user == user_selected:
            user_to_unfollow = user
            username_of_user_to_unfollow =\
                user_to_unfollow.followed_user.username
            if request.method == 'POST':
                user_to_unfollow.delete()
                return redirect('subscriptions')
    return render(
        request,
        'app/unfollow_user.html',
        context={'username_of_user_to_unfollow': username_of_user_to_unfollow})


@login_required(login_url='login')
def create_ticket(request):
    """
    Display a form to create an instance of :model:`models.Ticket`.

    **Context**

    ``form``
        Form to create an instance of :model:`models.Ticket`.

    **Template:**

    :template:`app/create_ticket.html`

    """
    form = forms.TicketForm()
    if request.method == 'POST':
        form = forms.TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            return redirect('flux')
    return render(request, 'app/create_ticket.html', context={'form': form})


@login_required(login_url='login')
def edit_ticket(request, id):
    """
    Display a form to modify an instance of :model:`models.Ticket`.

    **Context**

    ``form``
        Form to modify an instance of :model:`models.Ticket`.
    ``ticket``
        An instance of :model:`models.Ticket` to modify.

    **Template:**

    :template:`app/edit_ticket.html`

    """
    ticket = get_object_or_404(models.Ticket, id=id)
    form = forms.TicketForm(instance=ticket)
    if request.user == ticket.user:
        if request.method == 'POST':
            form = forms.TicketForm(request.POST,
                                    request.FILES,
                                    instance=ticket)
            if form.is_valid():
                form.save()
                return redirect('posts')
        return render(request,
                      'app/edit_ticket.html',
                      context={'form': form, 'ticket': ticket})
    else:
        return redirect('posts')


@login_required(login_url='login')
def delete_ticket(request, id):
    """
    Display an instance of :model:`models.Ticket` to delete.

    **Context**

    ``ticket``
        An instance of :model:`models.Ticket` to delete.

    **Template:**

    :template:`app/delete_ticket.html`

    """
    ticket = get_object_or_404(models.Ticket, id=id)
    if request.user == ticket.user:
        if request.method == 'POST':
            ticket.delete()
            return redirect('posts')
        return render(request,
                      'app/delete_ticket.html',
                      context={'ticket': ticket})
    else:
        return redirect('posts')


@login_required(login_url='login')
def create_review(request, id):
    """
    Display an instance of :model:`models.Ticket` and a form to create an
    instance of :model:`models.Review`.

    **Context**

    ``form``
        Form to create an instance of :model:`models.Review`.
    ``ticket``
        An instance of :model:`models.Ticket` for which the review is created.
    ``user_logged_in``
        An instance of User.
    ``rating_range``
        List of int from zero to five.

    **Template:**

    :template:`app/create_review.html`

    """
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


@login_required(login_url='login')
def create_review_without_ticket(request):
    """
    Display a form to create an instance of:model:`models.Ticket`
    and :model:`models.Review`.

    **Context**

    ``ticket_form``
        Form to create an instance of :model:`models.Ticket`.
    ``review_form``
        Form to create an instance of :model:`models.Review`.
    ``rating_range``
        List of int from zero to five.

    **Template:**

    :template:`app/create_review_without_ticket.html`

    """
    ticket_form = forms.TicketForm()
    review_form = forms.ReviewForm()
    rating_range = [number for number in range(6)]
    if request.method == 'POST':
        ticket_form = forms.TicketForm(request.POST, request.FILES)
        review_form = forms.ReviewForm(request.POST)
        if ticket_form.is_valid() and review_form.is_valid():
            ticket = ticket_form.save(commit=False)
            ticket.user = request.user
            ticket.save()
            review_ticket = models.Ticket.objects.get(id=ticket.id)
            review = review_form.save(commit=False)
            review.user = request.user
            review.ticket = review_ticket
            review.save()
            return redirect('flux')

    context = {'ticket_form': ticket_form,
               'review_form': review_form,
               'rating_range': rating_range}
    return render(request,
                  'app/create_review_without_ticket.html',
                  context=context)


@login_required(login_url='login')
def edit_review(request, id):
    """
    Display a form to modify an instance of :model:`models.Review`.

    **Context**

    ``form``
        Form to modify an instance of :model:`models.Review`.
    ``ticket``
        An instance of :model:`models.Ticket` for which the review was created.
    ``rating_range``
        List of int from zero to five.

    **Template:**

    :template:`app/edit_review.html`

    """
    review = get_object_or_404(models.Review, id=id)
    form = forms.ReviewForm(instance=review)
    if request.user == review.user:
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
    else:
        return redirect('posts')


@login_required(login_url='login')
def delete_review(request, id):
    """
    Display an instance of :model:`models.Review` to delete.

    **Context**

    ``review``
        An instance of :model:`models.Review` to delete.

    **Template:**

    :template:`app/delete_review.html`

    """
    review = get_object_or_404(models.Review, id=id)
    if request.user == review.user:
        if request.method == 'POST':
            review.delete()
            return redirect('posts')
        return render(request,
                      'app/delete_review.html',
                      context={'review': review})
    else:
        return redirect('posts')
