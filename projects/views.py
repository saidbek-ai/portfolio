from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Project
# from .forms import ProjectForm 

# Create your views here.
def projects_list(request):
    query = request.GET.get('q')
    if query:
        projects = Project.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        ).only("title", "slug", "cover_image", "demo_url", "source_code")
    else:
        projects = Project.objects.all().only("title", "slug", "cover_image", "demo_url", "source_code")

    return render(request, 'projects/projects_list.html', {
        'projects': projects,
        'query': query,
    })



def project_detail(request, slug):
    project = get_object_or_404(Project, slug=slug)
    return render(request, 'projects/project_detail.html', {'project': project,})



# @login_required
# @staff_member_required
# def create_project(request):
#     if request.method == 'POST':
#         form = ProjectForm(request.POST, request.FILES)
#         if form.is_valid():
#             project = form.save(commit=False)
#             project.creator = request.user
#             project.save()
#             return redirect('projects:projects_list')
#     else:
#         form = ProjectForm()
#     return render(request, 'projects/create.html', {'form': form})
