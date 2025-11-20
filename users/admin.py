from django.contrib import admin, messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import Group
# from django.contrib.auth import get_user_model
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from allauth.account.models import EmailAddress

# from .models import CustomUser

User = get_user_model()
# admin.site.unregister(User) # This should work now if you have a custom user model configured
admin.site.unregister(Group)

# def verify_selected_emails(modeladmin, request, queryset):
#     verified_count = 0
#     for user in queryset:
#         if user.email:
#             email_addr, created = EmailAddress.objects.get_or_create(
#                 user=user,
#                 email=user.email,
#                 defaults={'verified': True, 'primary': True}
#             )
#             if not email_addr.verified:
#                 email_addr.verified = True
#                 email_addr.primary = True
#                 email_addr.save()
#                 verified_count += 1
#     messages.success(request, f'Verified emails for {verified_count} users')


# verify_selected_emails.short_description = "Verify email for selected users"

@admin.register(User)
class CustomUserAdmin(ModelAdmin, BaseUserAdmin):
    # actions = [verify_selected_emails] + ModelAdmin.actions
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    model = User
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('email', 'username')
    ordering = ('email',)
    fieldsets = (
            (None, {"fields": ("username", "password")}),
            (
                "Personal info",
                {
                    "fields": (
                        "first_name",  # <-- Added/Ensured
                        "last_name",   # <-- Added/Ensured
                        "email",
                        "image"
                    )
                },
            ),
            (
                "Permissions",
                {
                    "fields": (
                        "is_active",
                        "is_staff",
                        "is_superuser",
                        "groups",
                        "user_permissions",
                    ),
                },
            ),
            ("Important dates", {"fields": ("last_login", "date_joined")}),
        )


    # 2. REQUIRED: FIELDSETS FOR ADDING A NEW USER (Must include password fields)
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", 
                "email", # Added email for creation
                "first_name", 
                "last_name", 
                "image", 
                "is_staff", # Often added during creation
                "is_superuser", # Often added during creation
                "password1", # Required by UserCreationForm
                "password2", # Required by UserCreationForm
            ),
        }),
    )
    
    # Use the existing BaseUserAdmin search/filter settings
    # search_fields = BaseUserAdmin.search_fields
    # ordering = BaseUserAdmin.ordering
    # filter_horizontal = BaseUserAdmin.filter_horizontal
    # list_filter = BaseUserAdmin.list_filter

@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass