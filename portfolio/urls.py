"""
URL configuration for portfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from .views import homepage, faq, dynamic_error


urlpatterns = [
    path('', homepage, name="home"),
    path('error/', dynamic_error, name="dynamic_error" ), 
    path('admin/', admin.site.urls),
    path('markdownx/', include('markdownx.urls')),
    path('faq/', faq, name="faq"),
    path('accounts/', include('accounts.urls')),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('projects/', include('projects.urls')),
    path('blogs/', include('blogs.urls')),
    path('chat/', include('chats.urls')),
    path('auth/', include('social_django.urls', namespace='social'))
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
