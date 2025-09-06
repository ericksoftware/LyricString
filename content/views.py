# views.py
from django.shortcuts import render, get_object_or_404
from .models import Song, Instrument, Artist, Genre, LyricsSection, ChordProgression, Tab

def song_list_view(request):
    # Get all songs with related artists and genres
    songs = Song.objects.select_related('artist').prefetch_related('genres').all()
    
    # Get all genres for the filter tags
    genres = Genre.objects.all()
    
    context = {
        'songs': songs,
        'genres': genres,
        'total_songs': Song.objects.count(),
        'total_artists': Artist.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_instruments': Instrument.objects.count(),
    }
    return render(request, 'content/song_list.html', context)

def song_detail_view(request, song_id):
    # Get the song with all related data
    song = get_object_or_404(
        Song.objects.select_related('artist')
                    .prefetch_related('genres', 
                                     'songinstrument_set__instrument',
                                     'chords',
                                     'lyrics',
                                     'tabs__instrument'),
        pk=song_id
    )
    
    # Organize lyrics by section type
    lyrics_by_section = {}
    for section in song.lyrics.all():
        if section.section_type not in lyrics_by_section:
            lyrics_by_section[section.section_type] = []
        lyrics_by_section[section.section_type].append(section)
    
    # Get ALL tabs for the song
    all_tabs = song.tabs.all()
    
    # Create a dictionary to store tabs by instrument name
    tabs_by_instrument = {}
    for tab in all_tabs:
        tabs_by_instrument[tab.instrument.name] = tab.content
    
    context = {
        'song': song,
        'lyrics_by_section': lyrics_by_section,
        'chords': song.chords.all(),
        'tabs_by_instrument': tabs_by_instrument,  # Add this
        'all_tabs': all_tabs,  # And this for debugging
    }
    return render(request, 'content/song_detail.html', context)

def instrument_list_view(request):
    # Get all instruments
    instruments = Instrument.objects.all()
    
    context = {
        'instruments': instruments,
        'total_instruments': Instrument.objects.count(),
        'total_lessons': 2847,  # This would come from a Lesson model if you had one
        'total_tutorials': 456,  # Same as above
    }
    return render(request, 'content/instrument_list.html', context)

def instrument_songs_view(request, instrument_id):
    # Get the specific instrument
    instrument = get_object_or_404(Instrument, pk=instrument_id)
    
    # Get songs that use this instrument
    songs = Song.objects.filter(
        songinstrument__instrument=instrument
    ).select_related('artist').prefetch_related('genres').distinct()
    
    # Get all genres for the filter tags
    genres = Genre.objects.all()
    
    context = {
        'instrument': instrument,
        'songs': songs,
        'genres': genres,
        'total_songs': songs.count(),
        'total_artists': Artist.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_instruments': Instrument.objects.count(),
    }
    return render(request, 'content/instrument_songs.html', context)

def genre_list_view(request):
    # Get all genres
    genres = Genre.objects.all()
    
    # Add additional data for each genre
    for genre in genres:
        # Set icon classes based on genre name
        genre_name_lower = genre.name.lower()
        if 'rock' in genre_name_lower:
            genre.icon_class = 'fas fa-guitar'
        elif 'pop' in genre_name_lower:
            genre.icon_class = 'fas fa-microphone'
        elif 'jazz' in genre_name_lower:
            genre.icon_class = 'fas fa-music'
        elif 'classical' in genre_name_lower:
            genre.icon_class = 'fas fa-violin'
        elif 'hip' in genre_name_lower or 'rap' in genre_name_lower:
            genre.icon_class = 'fas fa-drum'
        elif 'electronic' in genre_name_lower or 'dance' in genre_name_lower:
            genre.icon_class = 'fas fa-synth'
        elif 'country' in genre_name_lower:
            genre.icon_class = 'fas fa-hat-cowboy'
        elif 'blues' in genre_name_lower:
            genre.icon_class = 'fas fa-guitar-electric'
        elif 'folk' in genre_name_lower:
            genre.icon_class = 'fas fa-guitar-acoustic'
        elif 'reggae' in genre_name_lower:
            genre.icon_class = 'fas fa-drum-steelpan'
        elif 'metal' in genre_name_lower:
            genre.icon_class = 'fas fa-guitar-electric'
        else:
            genre.icon_class = 'fas fa-music'
        
        # Get song count for this genre
        genre.song_count = genre.song_set.count()
        
        # Get artist count for this genre
        genre.artist_count = Artist.objects.filter(genres=genre).count()
        
        # Set popularity level based on song count
        if genre.song_count > 50:
            genre.popularity_level = 'high'
        elif genre.song_count > 20:
            genre.popularity_level = 'medium'
        else:
            genre.popularity_level = 'low'
    
    context = {
        'genres': genres,
        'total_genres': Genre.objects.count(),
        'total_songs': Song.objects.count(),
        'total_artists': Artist.objects.count(),
        'total_albums': 500,  # This would come from an Album model if you had one
    }
    return render(request, 'content/genre_list.html', context)

def genre_songs_view(request, genre_id):
    # Get the specific genre
    genre = get_object_or_404(Genre, pk=genre_id)
    
    # Get songs of this genre
    songs = Song.objects.filter(
        genres=genre
    ).select_related('artist').prefetch_related('genres').distinct()
    
    # Get all genres for the filter tags
    all_genres = Genre.objects.all()
    
    context = {
        'genre': genre,
        'songs': songs,
        'genres': all_genres,
        'total_songs': songs.count(),
        'total_artists': Artist.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_instruments': Instrument.objects.count(),
    }
    return render(request, 'content/genre_songs.html', context)