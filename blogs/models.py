import uuid
import bleach
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify, Truncator
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from taggit.managers import TaggableManager 

class Blog(models.Model):
    title = models.CharField(max_length=200)  # Blog post title
    slug = models.SlugField(unique=True, max_length=200)  # SEO-friendly URL
    tags = TaggableManager(blank=True)
    cover_image = models.ImageField(blank=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='blogs'
    )  # Later you can use ForeignKey to User
    content = MarkdownxField()  # Blog content
    excerpt = models.TextField(blank=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)  # Date created
    updated_at = models.DateTimeField(auto_now=True)  # Last updated
    published = models.BooleanField(default=False)  # Publish toggle

    class Meta:
        ordering = ['-created_at']  # Show newest first

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # store original content for change detection
        self.__original_content = self.content

    def save(self, *args, **kwargs):
        # Generate slug
        if not self.slug:
            words = self.title.lower().split()[:8]
            base_slug = slugify(" ".join(words))[:36]
            unique_slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
            self.slug = unique_slug

        # --- EXCERPT GENERATION (Simplified & Efficient) ---
        # Only regenerate the excerpt if the content has actually changed
        # (or if it's a brand new object, where self.pk is None and __original_content is empty)
        is_new = self.pk is None
        content_changed = self.content != self.__original_content

        if is_new or content_changed:
            # 1. Strip all tags (from Markdown content)
            content = Truncator(self.content).words(30, truncate=" ...")

            html = markdownify(content)
            
            plain_text = bleach.clean(html , tags=[], attributes={}, strip=True)
            # 2. Truncate to 30 words
            self.excerpt = Truncator(plain_text).words(30, truncate=" ...")

        super().save(*args, **kwargs)


    @property
    def rendered_content(self):
        html = markdownify(self.content)
        # sanitize with bleach
        allowed_tags = [
            "div","span","p", "strong", "em", "ul", "ol", "li", "a", "blockquote",
            "code", "pre", "h1", "h2", "h3", "h4", "h5", "h6", "br", "hr", "table", "thead", "tbody", "tfoot", "tr", "th", "td", "caption", "col", "colgroup",
        ]
        allowed_attrs = {
            "a": ["href", "title"],
            "img": ["src", "alt", "title"],  # if you allow images
            "div": ["class"],
            "span": ["class"],
            "code": ["class"],
            "pre": ["class"],
        }

        return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs )

    def __str__(self):
        return self.title
