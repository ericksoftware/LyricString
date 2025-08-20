from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm, UserPreferencesForm
from .models import CustomUser, UserPreferences
from django.db import IntegrityError
from django.http import JsonResponse
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
from datetime import datetime, timedelta
from content.models import Song, Artist, Genre, Instrument

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, "You have successfully logged in!")
            return redirect('song_list')
        else:
            messages.error(request, "Invalid username or password.")
    
    return render(request, 'users/login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out.")
    return redirect('login')

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                # Use get_or_create instead of create to prevent duplicates
                UserPreferences.objects.get_or_create(user=user)
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    login(request, user)
                    return JsonResponse({
                        'success': True,
                        'redirect_url': reverse('profile')
                    })
                else:
                    login(request, user)
                    messages.success(request, "Registration successful!")
                    return redirect('profile')
            
            except IntegrityError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'success': False,
                        'message': 'Registration failed. Please try again.'
                    }, status=400)
                else:
                    messages.error(request, "Registration failed. Please try again.")
                    return redirect('register')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'errors': form.errors.get_json_data()
            }, status=400)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)
    else:
        return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    user = request.user
    liked_songs = Song.objects.filter(liked_by=user)
    saved_songs = Song.objects.filter(saved_by=user)
    
    preferences = user.preferences  # Using the property we defined
    
    context = {
        'user': user,
        'liked_songs': liked_songs,
        'saved_songs': saved_songs,
        'preferences': preferences
    }
    return render(request, 'users/profile.html', context)

@login_required
def profile_edit_view(request):
    user = request.user
    preferences = user.preferences  # Using the property we defined
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        pref_form = UserPreferencesForm(request.POST, instance=preferences)
        
        if user_form.is_valid() and pref_form.is_valid():
            user_form.save()
            pref_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        user_form = UserProfileForm(instance=user)
        pref_form = UserPreferencesForm(instance=preferences)
    
    context = {
        'user_form': user_form,
        'pref_form': pref_form
    }
    return render(request, 'users/profile_edit.html', context)

@staff_member_required
def admin_dashboard(request):
    # User statistics
    total_users = CustomUser.objects.count()
    new_users_today = CustomUser.objects.filter(
        date_joined__date=datetime.today()
    ).count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    
    # Content statistics
    total_songs = Song.objects.count()
    total_artists = Artist.objects.count()
    total_genres = Genre.objects.count()
    total_instruments = Instrument.objects.count()
    
    # Recent activity
    recent_users = CustomUser.objects.order_by('-date_joined')[:5]
    recent_songs = Song.objects.order_by('-created_at')[:5]
    
    # User growth (last 7 days)
    user_growth = []
    for i in range(7):
        date = datetime.today() - timedelta(days=i)
        count = CustomUser.objects.filter(
            date_joined__date=date
        ).count()
        user_growth.append({
            'date': date.strftime('%Y-%m-%d'),
            'count': count
        })
    user_growth.reverse()
    
    # Popular genres
    popular_genres = Genre.objects.annotate(
        song_count=Count('song')
    ).order_by('-song_count')[:5]
    
    context = {
        'total_users': total_users,
        'new_users_today': new_users_today,
        'active_users': active_users,
        'total_songs': total_songs,
        'total_artists': total_artists,
        'total_genres': total_genres,
        'total_instruments': total_instruments,
        'recent_users': recent_users,
        'recent_songs': recent_songs,
        'user_growth': user_growth,
        'popular_genres': popular_genres,
    }
    return render(request, 'users/admin_dashboard.html', context)

