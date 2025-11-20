from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

# Routers must be checked before using in react 
router = DefaultRouter()
app_name = "chat"

urlpatterns = [
    path("", base_view, name="chat_page"),

    # api routes 
    path("api/user/", UserViewAPI.as_view(), name="user_chat"),
    path("api/staff/", AdminChatViewAPI.as_view(), name="staff_chat"),
    path("api/staff/contacts", AdminContactsViewAPI.as_view(), name="contacts_for_staff"), # new needs to be checked  
    path("api/staff/<int:chat_id>/", SelectedChatAPI.as_view(), name="staff_chat"),

    # get / read / update / delete message(s) 

    # POST for READ messages
    # PATCH for UPDATE single message
    # DELETE for DELETE multiple/single message(s)
    # GET for getting message 
    path("api/messages/<int:chat_id>", MessagesAPI.as_view(), name="messages"),

    # dev routes
    path("api/dev/user/", dev_user_info),
    path("api/dev/login/", dev_login),
]


