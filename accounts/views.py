from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm

# Create your views here.

@login_required
def home_view(request):
    """
    Renders the beautiful user dashboard, only accessible to authenticated users.
    """
    return render(request, 'accounts/home.html', {
        'user': request.user
    })


def register_view(request):
    """
    Handles user registration. Logs in and redirects to home upon successful sign up.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.username}! Your account has been successfully created.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = UserRegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def login_view(request):
    """
    Handles user login. Redirects to previous page or home upon successful authentication.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form
    })


def logout_view(request):
    """
    Logs out the user and redirects them to the login page.
    """
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('login')
