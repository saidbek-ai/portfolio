from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Blog


def blog_list(request):
    query = request.GET.get("q")
    if query:
        blog_posts = Blog.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query), published=True
        ).prefetch_related("tags").only("title", "slug", "excerpt", "cover_image").order_by("-created_at")
    else:
        blog_posts = Blog.objects.filter(published=True).prefetch_related("tags").only("title", "slug", "excerpt", "cover_image").order_by("-created_at")

    paginator = Paginator(blog_posts, 6)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # print(page_obj)

    return render(request, "blog/blog_list.html", {"page_obj": page_obj})


def blog_detail(request, slug):
    blog = get_object_or_404(Blog, slug=slug, published=True)

    return render(request, 'blog/blog_detail.html', {"blog": blog})