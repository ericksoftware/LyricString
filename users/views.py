from django.shortcuts import render, redirect, get_object_or_404
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
from content.models import Song, Artist, Genre, Instrument, LyricsSection, ChordProgression, Tab
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from content.models import Genre
import json

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
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out.")
        return redirect('song_list')
    
    # If it's a GET request, show the confirmation page
    return render(request, 'users/logout.html')

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
    
    # Get all artists, genres, and instruments for the add song form
    artists = Artist.objects.all()
    genres = Genre.objects.all()
    instruments = Instrument.objects.all()
    
    # Get all songs for the edit modal
    all_songs = Song.objects.select_related('artist').prefetch_related('genres').all()
    
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
        'artists': artists,
        'genres': genres,
        'instruments': instruments,
        'all_songs': all_songs,
    }
    return render(request, 'users/admin_dashboard.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["GET"])
def get_song_data(request, song_id):
    """API endpoint to get song data for editing"""
    try:
        song = get_object_or_404(Song, id=song_id)
        
        # Convert duration to minutes:seconds format
        total_seconds = int(song.duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        duration_formatted = f"{minutes}:{seconds:02d}"
        
        # Get lyrics as a single string
        lyrics = "\n\n".join([f"[{section.section_type}]\n{section.content}" 
                             for section in song.lyrics.all().order_by('order')])
        
        # Get chords as a single string
        chords = "\n".join([f"{chord.chord_name} ({chord.chord_type})" 
                           for chord in song.chords.all().order_by('order')])
        
        # Get chord progression as a single string
        chord_progression = " - ".join([chord.chord_name 
                                       for chord in song.chords.all().order_by('order')])
        
        # Get tabs as a single string (combine all instrument tabs)
        tabs = "\n\n".join([f"[{tab.instrument.name}]\n{tab.content}" 
                           for tab in song.tabs.all()])
        
        data = {
            'id': song.id,
            'title': song.title,
            'artist_id': song.artist.id,
            'year': song.year,
            'key': song.key,
            'bpm': song.bpm,
            'duration': duration_formatted,
            'genres': [genre.id for genre in song.genres.all()],
            'instruments': [instrument.id for instrument in song.instruments.all()],
            'description': song.description,
            'cover_image_url': song.cover_image.url if song.cover_image else None,
            'audio_file_url': song.audio_file.url if song.audio_file else None,
            'cover_image_name': song.cover_image.name.split('/')[-1] if song.cover_image else None,
            'audio_file_name': song.audio_file.name.split('/')[-1] if song.audio_file else None,
            # Add the song content fields
            'lyrics': lyrics,
            'chords': chords,
            'chord_progression': chord_progression,
            'tabs': tabs,
        }
        
        return JsonResponse({'success': True, 'song': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def update_song(request):
    """API endpoint to update song data"""
    try:
        song_id = request.POST.get('song_id')
        song = get_object_or_404(Song, id=song_id)
        
        # Update basic fields
        song.title = request.POST.get('title')
        song.artist_id = request.POST.get('artist')
        
        # Handle year
        year = request.POST.get('year')
        if year and year.isdigit():
            song.year = int(year)
        else:
            song.year = None
        
        song.key = request.POST.get('key')
        
        # Handle BPM
        bpm = request.POST.get('bpm')
        if bpm and bpm.isdigit():
            song.bpm = int(bpm)
        else:
            song.bpm = None
        
        song.description = request.POST.get('description')
        
        # Handle duration
        duration_str = request.POST.get('duration')
        if duration_str:
            try:
                if ':' in duration_str:
                    minutes, seconds = map(int, duration_str.split(':'))
                    song.duration = timedelta(minutes=minutes, seconds=seconds)
                else:
                    # Handle case where it might be just seconds
                    seconds = int(duration_str)
                    song.duration = timedelta(seconds=seconds)
            except (ValueError, AttributeError):
                return JsonResponse({'success': False, 'error': 'Invalid duration format. Use MM:SS or seconds'})
        
        # Handle file uploads
        if 'cover_image' in request.FILES:
            song.cover_image = request.FILES['cover_image']
        if 'audio_file' in request.FILES:
            song.audio_file = request.FILES['audio_file']
        
        song.save()
        
        # Update genres
        genre_ids = request.POST.getlist('genres')
        song.genres.set(Genre.objects.filter(id__in=genre_ids))
        
        # Update instruments
        instrument_ids = request.POST.getlist('instruments')
        song.instruments.set(Instrument.objects.filter(id__in=instrument_ids))
        
        # Update song content (lyrics, chords, tabs)
        lyrics_content = request.POST.get('lyrics', '').strip()
        chords_content = request.POST.get('chords', '').strip()
        tabs_content = request.POST.get('tabs', '').strip()
        
        # DEBUG: Print received content
        print(f"Lyrics content received: {repr(lyrics_content[:100])}")
        print(f"Chords content received: {repr(chords_content[:100])}")
        print(f"Tabs content received: {repr(tabs_content[:100])}")
        
        # Process lyrics - save exactly as received
        if lyrics_content:
            # Clear existing lyrics
            LyricsSection.objects.filter(song=song).delete()
            
            # Create a single lyrics section with all content
            if lyrics_content.strip():
                LyricsSection.objects.create(
                    song=song,
                    section_type='verse',  # Default type
                    content=lyrics_content.strip(),
                    order=1
                )
                print(f"Created lyrics section with content length: {len(lyrics_content)}")
        
        # Process chords - save exactly as received but parse if possible
        if chords_content:
            # Clear existing chords
            ChordProgression.objects.filter(song=song).delete()
            
            # Try to parse chords, but if parsing fails, create a single chord entry with all content
            chords = chords_content.strip().split('\n')
            order = 1
            chords_created = 0
            
            for chord_line in chords:
                chord_line = chord_line.strip()
                if chord_line:
                    try:
                        # Try to parse chord format
                        chord_name = chord_line
                        chord_type = "major"  # default
                        
                        if '(' in chord_line and ')' in chord_line:
                            chord_name = chord_line.split('(')[0].strip()
                            chord_type = chord_line.split('(')[1].split(')')[0].strip()
                        elif ' ' in chord_line:
                            parts = chord_line.split(' ', 1)
                            chord_name = parts[0].strip()
                            chord_type = parts[1].strip()
                        
                        chord_name = chord_name.split('(')[0].strip()
                        
                        ChordProgression.objects.create(
                            song=song,
                            chord_name=chord_name,
                            chord_type=chord_type,
                            order=order
                        )
                        order += 1
                        chords_created += 1
                        
                    except Exception as e:
                        # If parsing fails for any line, break and create a single entry with all content
                        print(f"Chord parsing failed, creating single entry: {e}")
                        break
            
            # If no chords were created through parsing, create a single entry with all content
            if chords_created == 0 and chords_content.strip():
                ChordProgression.objects.create(
                    song=song,
                    chord_name="Song Chords",
                    chord_type=chords_content.strip(),
                    order=1
                )
                print("Created single chord entry with all content")
        
        # Process tabs - save exactly as received
        if tabs_content:
            # Clear existing tabs
            Tab.objects.filter(song=song).delete()
            
            # Create a single tab entry with all content
            if tabs_content.strip():
                # Use a default instrument (Guitar)
                try:
                    instrument = Instrument.objects.get(name__iexact='guitar')
                except Instrument.DoesNotExist:
                    instrument = Instrument.objects.create(
                        name='Guitar',
                        category='strings',
                        description='Standard guitar',
                        icon_class='fas fa-music',
                        difficulty='medium'
                    )
                
                Tab.objects.create(
                    song=song,
                    instrument=instrument,
                    content=tabs_content.strip()
                )
                print(f"Created tab with content length: {len(tabs_content)}")
        
        # Verification
        lyrics_count = LyricsSection.objects.filter(song=song).count()
        chords_count = ChordProgression.objects.filter(song=song).count()
        tabs_count = Tab.objects.filter(song=song).count()
        
        print(f"Final counts - Lyrics: {lyrics_count}, Chords: {chords_count}, Tabs: {tabs_count}")
        
        return JsonResponse({
            'success': True, 
            'message': 'Song updated successfully!',
            'counts': {
                'lyrics': lyrics_count,
                'chords': chords_count,
                'tabs': tabs_count
            }
        })
    except Exception as e:
        import traceback
        print(f"Error in update_song: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_song(request, song_id):
    """API endpoint to delete a song"""
    try:
        song = get_object_or_404(Song, id=song_id)
        song_title = song.title
        song.delete()
        return JsonResponse({'success': True, 'message': f'Song "{song_title}" deleted successfully!'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_song(request):
    """API endpoint to add a new song"""
    try:
        # Create new song
        song = Song()
        song.title = request.POST.get('title')
        song.artist_id = request.POST.get('artist')
        
        # Handle year - convert to integer if provided
        year = request.POST.get('year')
        if year and year.isdigit():
            song.year = int(year)
        else:
            song.year = None
        
        song.key = request.POST.get('key')
        
        # Handle BPM - convert to integer if provided
        bpm = request.POST.get('bpm')
        if bpm and bpm.isdigit():
            song.bpm = int(bpm)
        else:
            song.bpm = None
        
        song.description = request.POST.get('description')
        
        # Handle duration
        duration_str = request.POST.get('duration')
        if duration_str:
            try:
                if ':' in duration_str:
                    minutes, seconds = map(int, duration_str.split(':'))
                    song.duration = timedelta(minutes=minutes, seconds=seconds)
                else:
                    seconds = int(duration_str)
                    song.duration = timedelta(seconds=seconds)
            except (ValueError, AttributeError):
                return JsonResponse({'success': False, 'error': 'Invalid duration format. Use MM:SS or seconds'})
        
        # Handle file uploads
        if 'cover_image' in request.FILES:
            song.cover_image = request.FILES['cover_image']
        if 'audio_file' in request.FILES:
            song.audio_file = request.FILES['audio_file']
        
        song.save()
        
        # Add genres
        genre_ids = request.POST.getlist('genres')
        if genre_ids:
            song.genres.set(Genre.objects.filter(id__in=genre_ids))
        
        # Add instruments
        instrument_ids = request.POST.getlist('instruments')
        if instrument_ids:
            song.instruments.set(Instrument.objects.filter(id__in=instrument_ids))
        
        # Add song content (lyrics, chords, tabs)
        lyrics_content = request.POST.get('lyrics', '').strip()
        chords_content = request.POST.get('chords', '').strip()
        tabs_content = request.POST.get('tabs', '').strip()
        
        # DEBUG: Print received content
        print(f"Lyrics content received: {repr(lyrics_content[:100])}")
        print(f"Chords content received: {repr(chords_content[:100])}")
        print(f"Tabs content received: {repr(tabs_content[:100])}")
        
        # Process lyrics - save exactly as received
        if lyrics_content:
            # Create a single lyrics section with all content
            if lyrics_content.strip():
                LyricsSection.objects.create(
                    song=song,
                    section_type='verse',  # Default type
                    content=lyrics_content.strip(),
                    order=1
                )
                print(f"Created lyrics section with content length: {len(lyrics_content)}")
        
        # Process chords - save exactly as received but parse if possible
        if chords_content:
            # Try to parse chords, but if parsing fails, create a single chord entry with all content
            chords = chords_content.strip().split('\n')
            order = 1
            chords_created = 0
            
            for chord_line in chords:
                chord_line = chord_line.strip()
                if chord_line:
                    try:
                        # Try to parse chord format
                        chord_name = chord_line
                        chord_type = "major"  # default
                        
                        if '(' in chord_line and ')' in chord_line:
                            chord_name = chord_line.split('(')[0].strip()
                            chord_type = chord_line.split('(')[1].split(')')[0].strip()
                        elif ' ' in chord_line:
                            parts = chord_line.split(' ', 1)
                            chord_name = parts[0].strip()
                            chord_type = parts[1].strip()
                        
                        chord_name = chord_name.split('(')[0].strip()
                        
                        ChordProgression.objects.create(
                            song=song,
                            chord_name=chord_name,
                            chord_type=chord_type,
                            order=order
                        )
                        order += 1
                        chords_created += 1
                        
                    except Exception as e:
                        # If parsing fails for any line, break and create a single entry with all content
                        print(f"Chord parsing failed, creating single entry: {e}")
                        break
            
            # If no chords were created through parsing, create a single entry with all content
            if chords_created == 0 and chords_content.strip():
                ChordProgression.objects.create(
                    song=song,
                    chord_name="Song Chords",
                    chord_type=chords_content.strip(),
                    order=1
                )
                print("Created single chord entry with all content")
        
        # Process tabs - save exactly as received
        if tabs_content:
            # Create a single tab entry with all content
            if tabs_content.strip():
                # Use a default instrument (Guitar)
                try:
                    instrument = Instrument.objects.get(name__iexact='guitar')
                except Instrument.DoesNotExist:
                    instrument = Instrument.objects.create(
                        name='Guitar',
                        category='strings',
                        description='Standard guitar',
                        icon_class='fas fa-music',
                        difficulty='medium'
                    )
                
                Tab.objects.create(
                    song=song,
                    instrument=instrument,
                    content=tabs_content.strip()
                )
                print(f"Created tab with content length: {len(tabs_content)}")
        
        # Verification
        lyrics_count = LyricsSection.objects.filter(song=song).count()
        chords_count = ChordProgression.objects.filter(song=song).count()
        tabs_count = Tab.objects.filter(song=song).count()
        
        print(f"Final counts - Lyrics: {lyrics_count}, Chords: {chords_count}, Tabs: {tabs_count}")
        
        return JsonResponse({
            'success': True, 
            'message': 'Song added successfully!', 
            'song_id': song.id,
            'counts': {
                'lyrics': lyrics_count,
                'chords': chords_count,
                'tabs': tabs_count
            }
        })
    except Exception as e:
        import traceback
        print(f"Error in add_song: {str(e)}")
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'error': str(e)})

@staff_member_required
def admin_add_song_view(request):
    """View for the add song page"""
    # Get all artists, genres, and instruments for the form
    artists = Artist.objects.all()
    genres = Genre.objects.all()
    instruments = Instrument.objects.all()
    
    context = {
        'artists': artists,
        'genres': genres,
        'instruments': instruments,
    }
    return render(request, 'users/admin_add_song.html', context)

@staff_member_required
def admin_edit_song_view(request):
    """View for the edit song list page"""
    # Get all songs with pagination
    all_songs = Song.objects.select_related('artist').prefetch_related('genres').order_by('-created_at')
    
    # Pagination - 10 songs per page
    paginator = Paginator(all_songs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get all artists and genres for filters
    artists = Artist.objects.all()
    genres = Genre.objects.all()
    
    context = {
        'all_songs': page_obj,
        'artists': artists,
        'genres': genres,
    }
    return render(request, 'users/admin_edit_song.html', context)

@staff_member_required
def admin_edit_song_detail_view(request, song_id):
    """View for the edit song detail page"""
    # Get the song to edit
    song = get_object_or_404(
        Song.objects.select_related('artist')
                    .prefetch_related('genres', 'instruments', 'lyrics', 'chords', 'tabs__instrument'),
        pk=song_id
    )
    
    # Get all artists, genres, and instruments for the form
    artists = Artist.objects.all()
    genres = Genre.objects.all()
    instruments = Instrument.objects.all()
    
    context = {
        'song': song,
        'artists': artists,
        'genres': genres,
        'instruments': instruments,
    }
    return render(request, 'users/admin_edit_song_detail.html', context)

@staff_member_required
def manage_artists_view(request):
    """View for managing artists"""
    artists = Artist.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(artists, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'artists': page_obj,
    }
    return render(request, 'users/manage_artists.html', context)

@staff_member_required
def add_artist_view(request):
    """View for adding a new artist"""
    genres = Genre.objects.all()
    context = {
        'genres': genres,
        'is_edit': False
    }
    return render(request, 'users/add_edit_artist.html', context)

@staff_member_required
def edit_artist_view(request, artist_id):
    """View for editing an existing artist"""
    artist = get_object_or_404(Artist, id=artist_id)
    genres = Genre.objects.all()
    
    context = {
        'artist': artist,
        'genres': genres,
        'is_edit': True
    }
    return render(request, 'users/add_edit_artist.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_artist_api(request):
    """API endpoint to add a new artist"""
    try:
        name = request.POST.get('name')
        bio = request.POST.get('bio', '')
        genre_ids = request.POST.getlist('genres')
        
        # Create the artist
        artist = Artist.objects.create(
            name=name,
            bio=bio
        )
        
        # Add genres
        if genre_ids:
            artist.genres.set(Genre.objects.filter(id__in=genre_ids))
        
        return JsonResponse({
            'success': True, 
            'message': 'Artist added successfully!',
            'artist_id': artist.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def update_artist_api(request, artist_id):
    """API endpoint to update an artist"""
    try:
        artist = get_object_or_404(Artist, id=artist_id)
        
        name = request.POST.get('name')
        bio = request.POST.get('bio', '')
        genre_ids = request.POST.getlist('genres')
        
        # Update the artist
        artist.name = name
        artist.bio = bio
        artist.save()
        
        # Update genres
        if genre_ids:
            artist.genres.set(Genre.objects.filter(id__in=genre_ids))
        
        return JsonResponse({
            'success': True, 
            'message': 'Artist updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_artist_api(request, artist_id):
    """API endpoint to delete an artist"""
    try:
        artist = get_object_or_404(Artist, id=artist_id)
        artist_name = artist.name
        artist.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Artist "{artist_name}" deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })
    
@staff_member_required
def manage_users_view(request):
    """View for managing users"""
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Pagination
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'all_users': page_obj,
    }
    return render(request, 'users/manage_users.html', context)

@staff_member_required
def add_user_view(request):
    """View for adding a new user"""
    return render(request, 'users/add_user.html')

@staff_member_required
def edit_user_view(request, user_id):
    """View for editing an existing user"""
    user = get_object_or_404(CustomUser, id=user_id)
    
    context = {
        'user': user,
    }
    return render(request, 'users/edit_user.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_user_api(request):
    """API endpoint to add a new user"""
    try:
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        website = request.POST.get('website', '')
        social_media = request.POST.get('social_media', '')
        skill_level = request.POST.get('skill_level', 'beginner')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Create the user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Set additional fields
        user.bio = bio
        user.location = location
        user.website = website
        user.social_media = social_media
        user.skill_level = skill_level
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'User added successfully!',
            'user_id': user.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def update_user_api(request, user_id):
    """API endpoint to update a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        bio = request.POST.get('bio', '')
        location = request.POST.get('location', '')
        website = request.POST.get('website', '')
        social_media = request.POST.get('social_media', '')
        skill_level = request.POST.get('skill_level', 'beginner')
        is_active = request.POST.get('is_active') == 'on'
        is_staff = request.POST.get('is_staff') == 'on'
        is_superuser = request.POST.get('is_superuser') == 'on'
        
        # Update the user
        user.username = username
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.bio = bio
        user.location = location
        user.website = website
        user.social_media = social_media
        user.skill_level = skill_level
        user.is_active = is_active
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        
        # Update password if provided
        if password:
            user.set_password(password)
        
        # Handle profile picture
        if 'profile_picture' in request.FILES:
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'User updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_user_api(request, user_id):
    """API endpoint to delete a user"""
    try:
        user = get_object_or_404(CustomUser, id=user_id)
        
        # Prevent deletion of the currently logged-in user
        if request.user.id == user_id:
            return JsonResponse({
                'success': False, 
                'error': 'You cannot delete your own account while logged in.'
            })
        
        user.delete()
        
        return JsonResponse({
            'success': True, 
            'message': 'User deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })
    
@staff_member_required
def manage_genres_view(request):
    """View for managing genres"""
    genres = Genre.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(genres, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'genres': page_obj,
    }
    return render(request, 'users/manage_genres.html', context)

@staff_member_required
def add_genre_view(request):
    """View for adding a new genre"""
    return render(request, 'users/add_edit_genre.html', {'is_edit': False})

@staff_member_required
def edit_genre_view(request, genre_id):
    """View for editing an existing genre"""
    genre = get_object_or_404(Genre, id=genre_id)
    
    context = {
        'genre': genre,
        'is_edit': True
    }
    return render(request, 'users/add_edit_genre.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_genre_api(request):
    """API endpoint to add a new genre"""
    try:
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon_class = request.POST.get('icon_class', 'fas fa-music')
        
        # Create the genre
        genre = Genre.objects.create(
            name=name,
            description=description,
            icon_class=icon_class
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Genre added successfully!',
            'genre_id': genre.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def update_genre_api(request, genre_id):
    """API endpoint to update a genre"""
    try:
        genre = get_object_or_404(Genre, id=genre_id)
        
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        icon_class = request.POST.get('icon_class', 'fas fa-music')
        
        # Update the genre
        genre.name = name
        genre.description = description
        genre.icon_class = icon_class
        genre.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Genre updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_genre_api(request, genre_id):
    """API endpoint to delete a genre"""
    try:
        genre = get_object_or_404(Genre, id=genre_id)
        genre_name = genre.name
        genre.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Genre "{genre_name}" deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
def manage_instruments_view(request):
    """View for managing instruments"""
    instruments = Instrument.objects.all().order_by('name')
    
    # Pagination
    paginator = Paginator(instruments, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'instruments': page_obj,
    }
    return render(request, 'users/manage_instruments.html', context)

@staff_member_required
def add_instrument_view(request):
    """View for adding a new instrument"""
    return render(request, 'users/add_edit_instrument.html', {'is_edit': False})

@staff_member_required
def edit_instrument_view(request, instrument_id):
    """View for editing an existing instrument"""
    instrument = get_object_or_404(Instrument, id=instrument_id)
    
    context = {
        'instrument': instrument,
        'is_edit': True
    }
    return render(request, 'users/add_edit_instrument.html', context)

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def add_instrument_api(request):
    """API endpoint to add a new instrument"""
    try:
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        icon_class = request.POST.get('icon_class', 'fas fa-music')
        difficulty = request.POST.get('difficulty', 'medium')
        
        # Create the instrument
        instrument = Instrument.objects.create(
            name=name,
            category=category,
            description=description,
            icon_class=icon_class,
            difficulty=difficulty
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Instrument added successfully!',
            'instrument_id': instrument.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["POST"])
def update_instrument_api(request, instrument_id):
    """API endpoint to update an instrument"""
    try:
        instrument = get_object_or_404(Instrument, id=instrument_id)
        
        name = request.POST.get('name')
        category = request.POST.get('category')
        description = request.POST.get('description', '')
        icon_class = request.POST.get('icon_class', 'fas fa-music')
        difficulty = request.POST.get('difficulty', 'medium')
        
        # Update the instrument
        instrument.name = name
        instrument.category = category
        instrument.description = description
        instrument.icon_class = icon_class
        instrument.difficulty = difficulty
        instrument.save()
        
        return JsonResponse({
            'success': True, 
            'message': 'Instrument updated successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })

@staff_member_required
@csrf_exempt
@require_http_methods(["DELETE"])
def delete_instrument_api(request, instrument_id):
    """API endpoint to delete an instrument"""
    try:
        instrument = get_object_or_404(Instrument, id=instrument_id)
        instrument_name = instrument.name
        instrument.delete()
        
        return JsonResponse({
            'success': True, 
            'message': f'Instrument "{instrument_name}" deleted successfully!'
        })
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': str(e)
        })
    
def terms_view(request):
    """View for Terms of Service page"""
    return render(request, 'terms.html')

def privacy_view(request):
    """View for Privacy Policy page"""
    return render(request, 'privacy.html')