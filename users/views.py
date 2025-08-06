from django.shortcuts import render

# Create your views here.
def login_view(request):
    # Logic for user login
    return render(request, 'users/login.html')

def register_view(request):
    # Logic for user registration
    return render(request, 'users/register.html')

def profile_view(request):
    # Logic for displaying user profile
    return render(request, 'users/profile.html')

def profile_edit_view(request):
    # Logic for editing user profile
    return render(request, 'users/profile_edit.html')

