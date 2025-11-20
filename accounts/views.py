from allauth.socialaccount.views import ConnectionsView
from django.http import Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CompleteProfileForm

User = get_user_model()

class ProtectedConnectionsView(ConnectionsView):
    def post(self, request, *args, **kwargs):
        # Completely block disconnect requests
        raise Http404("Page not found")
    
    def get(self, request):
        raise Http404("Page not found")


def email_modifications_disabled(request):
    raise Http404("Page not found")

@login_required
def complete_profile(request):
    user = request.user
    # prevents users to go by url if they have first_name and last_name
    if user.first_name or user.last_name:
        raise Http404("Page not found!")

    if request.method == "POST":
        form = CompleteProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Signup completed successfully.")
            return redirect("home")
        else:
            messages.error(request, "Please correct errors:")
    else:
        form = CompleteProfileForm(instance=user)

    return render(request, "account/complete_profile.html", {"form": form})

