from django.shortcuts import render
from django.http import HttpResponseForbidden, HttpResponseBadRequest
from projects.models import Project
from blogs.models import Blog
# from django.conf import settings
# from django.contrib.auth import get_user_model

def homepage(request):
    latest_projects =  Project.objects.all().order_by("-created_at")[:3]
    latest_blogs =  Blog.objects.all().order_by("-created_at").exclude(published=False)[:3]
    return render(request, "home.html", {'latest_projects': latest_projects, "latest_blogs": latest_blogs})

def faq(request):
    return render(request, "faq.html")


def dynamic_error(request):
    context = {
        "title": request.GET.get("title", "Something went wrong"),
        "message": request.GET.get("message", "An unexpected error occurred."),
        "emoji": request.GET.get("emoji", "⚠️"),
        "color": request.GET.get("color", "#ef4444"),
        "redirect_url": request.GET.get("redirect", "/"),
    }
    return render(request, "error_dynamic.html", context)


def error(request):
    return render(request, '400.html', )