from django import forms
from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from taggit.forms import TagWidget
from markdownx.widgets import AdminMarkdownxWidget
from unfold.admin import ModelAdmin
from .models import Blog
from .forms import BlogAdminForm

# Register your models here.
# class BlogAdminForm(forms.ModelForm):
#     class Meta:
#         model = Blog
#         fields = "__all__"
#         widgets = {
#             "content": AdminMarkdownxWidget(
#                 attrs={
#                     # "style": "margin: 2rem;"
#                     "class": "m-24"
#                 }
#             )
#         }

@admin.register(Blog)
class BlogAdmin(ModelAdmin, MarkdownxModelAdmin):

    form = BlogAdminForm
    list_display = ("title", "author", "published", "created_at",)
    list_editable = ("published",)
    list_filter = ("created_at",)
    readonly_fields= ("slug", "created_at", "updated_at", "excerpt", "author")
    search_fields = ("title", "tags__name",)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        return super().save_model(request, obj, form, change)


    # prepopulated_fields = {"slug": ("title",), "excerpt": ("content",)}