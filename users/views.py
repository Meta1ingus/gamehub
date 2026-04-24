from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

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

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def form_valid(self, form):
        # Log the user in
        response = super().form_valid(form)

        # Check if "remember me" was selected
        remember = self.request.POST.get("remember_me")

        if remember:
            # Keep session for 2 weeks (default)
            self.request.session.set_expiry(1209600)  # 14 days
        else:
            # Expire session when browser closes
            self.request.session.set_expiry(0)

        return response

@login_required
def orders(request):
    return render(request, "orders/orders.html")