from django.db import models
from django.conf import settings 
from django.utils.text import slugify, Truncator
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
import uuid
import bleach


# Create your models here.
class Project(models.Model):
    title = models.CharField()
    description = MarkdownxField()
    cover_image = models.ImageField(upload_to="project_images/")
    demo_url = models.URLField(blank=True)
    source_code = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    slug = models.SlugField(unique=True, max_length=200)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    class Meta:
        ordering = ["-created_at"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # store original content for change detection
        self.__original_content = self.description
    

    # generating slug automatically 
    def save(self, *args, **kwargs):
        # Generate slug
        if not self.slug:
            words = self.title.lower().split()[:8]
            base_slug = slugify(" ".join(words))[:36]
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            self.slug = unique_slug

        super().save(*args, **kwargs)

    @property
    def rendered_description(self):
        html = markdownify(self.description)
        # sanitize with bleach
        allowed_tags = [
            "div", "span", "p", "strong", "em", "ul", "ol", "li", "a", "blockquote",
            "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6",
            "br", "hr", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "col", "colgroup",
        ]
        allowed_attrs = {
            "a": ["href", "title"],
            "img": ["src", "alt", "title"],  # if you allow images
            "div": ["class"],
            "span": ["class"],
            "code": ["class"],
            "pre": ["class"],
        }    

        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs)

    def __str__(self):
        return self.title