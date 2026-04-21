from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import UserProfile
from .forms import ProfileForm


def profile_view(request, slug):
    profile = get_object_or_404(UserProfile, slug=slug)
    return render(request, "users/profile.html", {"profile": profile})


@login_required
def profile_edit(request):
    profile = request.user.userprofile

    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect("profile", slug=profile.slug)
    else:
        form = ProfileForm(instance=profile)

    return render(request, "users/profile_edit.html", {"form": form})
