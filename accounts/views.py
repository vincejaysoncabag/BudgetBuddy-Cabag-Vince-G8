from django.contrib import messages
from django.contrib.auth import logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .decorators import role_required
from .forms import ChangePasswordForm, EmailLoginForm, ProfileForm, RegisterForm
from .models import User


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Account created. Log in to get started.")
            return redirect("login")
        messages.error(request, "Please fix the errors below.")
    return render(request, "accounts/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = EmailLoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name}.")
        return super().form_valid(form)


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


@login_required
def dashboard_redirect(request):
    """Send each user to the dashboard for their role."""
    if request.user.role == User.Role.ADMIN:
        return redirect("admin_dashboard")
    return redirect("user_dashboard")


@role_required(User.Role.USER)
def user_dashboard(request):
    return render(request, "accounts/user_dashboard.html")


@role_required(User.Role.ADMIN)
def admin_dashboard(request):
    users = User.objects.filter(role=User.Role.USER).order_by("-date_joined")
    context = {"total_users": users.count(), "recent_users": users[:10]}
    return render(request, "accounts/admin_dashboard.html", context)


@login_required
def profile_view(request):
    # Always operates on request.user, so users can only see/edit their own profile.
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
        messages.error(request, "Profile not saved. Please fix the errors below.")
    return render(request, "accounts/profile.html", {"form": form})


@login_required
def change_password_view(request):
    form = ChangePasswordForm(request.user, request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password changed.")
            return redirect("profile")
        messages.error(request, "Password not changed. Please fix the errors below.")
    return render(request, "accounts/change_password.html", {"form": form})
