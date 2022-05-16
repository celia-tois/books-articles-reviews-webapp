"""litreview URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.contrib.auth.views import LoginView, LogoutView
from django.conf.urls.static import static

import authentication.views
import app.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', LoginView.as_view(template_name='authentication/login.html', redirect_authenticated_user=True), name='login'),
    path('signup/', authentication.views.signup, name='signup'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('flux/', app.views.flux, name='flux'),
    path('subscriptions/', app.views.follow_users, name='subscriptions'),
    path('subscriptions/<int:id>/unfollow/', app.views.unfollow_user, name='unfollow_user'),
    path('create-ticket/', app.views.create_ticket, name='create_ticket'),
    path('<int:id>/create-review/', app.views.create_review, name='create_review'),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
