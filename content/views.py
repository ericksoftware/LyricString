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
    
    # Get tabs grouped by instrument
    tabs_by_instrument = {}
    for tab in song.tabs.all():
        if tab.instrument.name not in tabs_by_instrument:
            tabs_by_instrument[tab.instrument.name] = tab.content
    
    context = {
        'song': song,
        'lyrics_by_section': lyrics_by_section,
        'chords': song.chords.all(),
        'tabs_by_instrument': tabs_by_instrument,
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