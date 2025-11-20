from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from unfold.admin import ModelAdmin
from .models import Project 


@admin.register(Project)
class CustomAdminClass(ModelAdmin, MarkdownxModelAdmin):
    list_display = ("title", "author", "created_at", "updated_at")
    readonly_fields= ("slug", "created_at", "updated_at", "author")

    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        return super().save_model(request, obj, form, change)
    

