from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# from allauth.account.forms import ChangePasswordForm
from allauth.socialaccount.models import SocialAccount, SocialApp
from allauth.socialaccount.providers import registry

from .forms import EditProfileForm


@login_required
def user_profile(request):
    user = request.user
    if request.method == "GET":
        first_name= user.first_name
        last_name= user.last_name
        email= user.email
        image= user.image
        is_staff = user.is_staff
        is_authenticated = user.is_authenticated
        username = user.username
        has_usable_password = user.has_usable_password()
        # projects = []
        organisation = user.organisation
        bio= user.bio
        # phone_number = request.user.phone_number

        connected_accounts_queryset = SocialAccount.objects.filter(user=request.user)
        
        # # Create a set of connected provider IDs for fast lookup
        connected_providers_ids = set(acc.provider for acc in connected_accounts_queryset)

        # # Get all registered provider classes
        all_providers = registry.get_class_list()
        
        # Filter out providers the user is already connected to
        available_providers_classes = [
            provider 
            for provider in all_providers 
            if provider.id not in connected_providers_ids
        ]
        
        # Transform the remaining provider classes into a list of simple dictionaries
        # containing only the 'id' and 'name'.
        available_providers_list = [
            {'id': provider.id, 'name': provider.name,}
            for provider in available_providers_classes
        ]

        user_data = {"is_staff": is_staff, "is_authenticated": is_authenticated, "first_name": first_name, "last_name": last_name, "image":image, "email": email, "bio": bio, "organisation": organisation, "username": username, "has_usable_password": has_usable_password}

        # return render(request, "users/user_profile.html",)
        return render(request, "users/user_profile.html", {"user": user_data, "get_providers": registry.get_class_list(), "connected_accounts": connected_providers_ids, "available_providers": available_providers_list})
    


@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully.')
            return redirect('users:user_profile')
    else:
        form = EditProfileForm(instance=user)

    return render(request, 'users/edit_profile.html', {'form': form})


