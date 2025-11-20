from django.urls import path, include
from .views import complete_profile, email_modifications_disabled, ProtectedConnectionsView


urlpatterns = [
    path('complete_profile/', complete_profile, name='account_complete_profile'),
    path('social/connections/', ProtectedConnectionsView.as_view(), name="socialaccount_connections"),
    path('email/', email_modifications_disabled, name="account_email"),
    path('', include('allauth.urls')),   
]