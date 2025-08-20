from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings

User = get_user_model()

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    icon_class = models.CharField(max_length=50, default='fas fa-music')
    
    def __str__(self):
        return self.name

class Instrument(models.Model):
    name = models.CharField(max_length=50)
    category = models.CharField(max_length=50, choices=[
        ('strings', 'Strings'),
        ('percussion', 'Percussion'),
        ('wind', 'Wind'),
        ('keyboard', 'Keyboard'),
        ('electronic', 'Electronic')
    ])
    description = models.TextField()
    icon_class = models.CharField(max_length=50, default='fas fa-music')
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    
    def __str__(self):
        return self.name

class Artist(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    genres = models.ManyToManyField(Genre)
    
    def __str__(self):
        return self.name

class Song(models.Model):
    title = models.CharField(max_length=100)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    duration = models.DurationField()
    key = models.CharField(max_length=20)
    bpm = models.PositiveIntegerField()
    year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    instruments = models.ManyToManyField(Instrument, through='SongInstrument')
    description = models.TextField()
    cover_image = models.ImageField(upload_to='song_covers/', blank=True)
    audio_file = models.FileField(upload_to='song_audio/')
    created_at = models.DateTimeField(auto_now_add=True)
    liked_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_songs')
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_songs')
    
    def __str__(self):
        return f"{self.title} - {self.artist}"

class SongInstrument(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    difficulty = models.CharField(max_length=10, choices=[
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ], default='medium')
    
    class Meta:
        unique_together = ('song', 'instrument')

class ChordProgression(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='chords')
    chord_name = models.CharField(max_length=20)
    chord_type = models.CharField(max_length=20)
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']

class LyricsSection(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='lyrics')
    section_type = models.CharField(max_length=20, choices=[
        ('verse', 'Verse'),
        ('chorus', 'Chorus'),
        ('bridge', 'Bridge'),
        ('intro', 'Intro'),
        ('outro', 'Outro')
    ])
    content = models.TextField()
    order = models.PositiveIntegerField()
    
    class Meta:
        ordering = ['order']

class Tab(models.Model):
    song = models.ForeignKey(Song, on_delete=models.CASCADE, related_name='tabs')
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    content = models.TextField()