from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import get_user_model

# Get the custom user model if one is used, otherwise the default
User = get_user_model()

# additional security layer
class AdminObscurityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        try:
            admin_url = reverse("admin:index")
            # remove "index/" from "admin:index" reverse result, e.g. "/admin/"
            self.admin_prefix = admin_url.rsplit("index/", 1)[0]
        except Exception:
            self.admin_prefix = "/admin/"

    def __call__(self, request):
        # check if request targets admin path
        if request.path.startswith(self.admin_prefix):
            user = getattr(request, "user", None)

            # Allow only authenticated staff or superusers
            if not user or not user.is_authenticated or not (user.is_staff or user.is_superuser):
                raise Http404()

        return self.get_response(request)
    

    
class ProfileCompletionMiddleware(MiddlewareMixin):
    """
    Middleware to check if the authenticated user has completed their profile
    (first name and last name) and redirects them to a profile completion
    page if not.
    """
    def process_request(self, request):
        # 1. Check if the user is authenticated
        if request.user.is_authenticated:
            user = request.user

            # 2. Define the path the user should be redirected to
            # This is the URL where the user can enter their f_name and l_name
            # Ensure this URL is defined in your project's urls.py
            # Example: A view/form where they update their profile
            PROFILE_UPDATE_URL = reverse('account_complete_profile')

            # 3. Define URLs to be excluded from the check
            # Users shouldn't be redirected if they are already on the update page or logging out
            EXCLUDE_URLS = [
                PROFILE_UPDATE_URL,
                reverse(getattr(settings, 'ACCOUNT_LOGOUT_URL', 'account_logout')),
                reverse('account_logout'), # account_logout is the default allauth name
                'admin/', # Optionally exclude admin pages
                # Add any other necessary exclusions like static/media file paths
            ]

            # 4. Check if the user is missing f_name or l_name
            # Assumes your User model has 'first_name' and 'last_name' fields.
            # You might need to adjust the field names based on your custom User model.
            if not user.first_name or not user.last_name:

                # 5. Check if the current path should be excluded
                current_path = request.path

                # Check if the current path is NOT the update page or an excluded URL
                if not any(current_path.startswith(url) for url in EXCLUDE_URLS):
                    # Redirect the user to the profile update page
                    return redirect(PROFILE_UPDATE_URL)

        # Allow the request to continue normally
        return None