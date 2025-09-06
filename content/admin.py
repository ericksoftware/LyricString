# admin.py
from django.contrib import admin
from .models import Genre, Instrument, Artist, Song, SongInstrument, ChordProgression, LyricsSection, Tab

# Inline admin classes for related objects
class SongInstrumentInline(admin.TabularInline):
    model = SongInstrument
    extra = 1
    fields = ('instrument', 'difficulty')

class ChordProgressionInline(admin.TabularInline):
    model = ChordProgression
    extra = 1
    fields = ('chord_name', 'chord_type', 'order')

class LyricsSectionInline(admin.TabularInline):
    model = LyricsSection
    extra = 1
    fields = ('section_type', 'content', 'order')

class TabInline(admin.TabularInline):
    model = Tab
    extra = 1
    fields = ('instrument', 'content')

# Main admin classes
@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon_class')
    search_fields = ('name',)
    prepopulated_fields = {'icon_class': ('name',)}

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'difficulty', 'icon_class')
    list_filter = ('category', 'difficulty')
    search_fields = ('name', 'category')
    list_editable = ('difficulty', 'icon_class')

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_genres')
    search_fields = ('name',)
    filter_horizontal = ('genres',)
    
    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    get_genres.short_description = 'Genres'

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('title', 'artist', 'year', 'key', 'bpm', 'duration_formatted')
    list_filter = ('year', 'genres', 'key')
    search_fields = ('title', 'artist__name')
    filter_horizontal = ('genres',)  # Removed 'instruments' from here
    inlines = [SongInstrumentInline, ChordProgressionInline, LyricsSectionInline, TabInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'artist', 'description')
        }),
        ('Technical Details', {
            'fields': ('duration', 'key', 'bpm', 'year')
        }),
        ('Media', {
            'fields': ('cover_image', 'audio_file')
        }),
        ('Categorization', {
            'fields': ('genres',)  # Removed 'instruments' from here
        }),
    )
    
    def duration_formatted(self, obj):
        """Format duration as minutes:seconds"""
        total_seconds = int(obj.duration.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    duration_formatted.short_description = 'Duration'

@admin.register(SongInstrument)
class SongInstrumentAdmin(admin.ModelAdmin):
    list_display = ('song', 'instrument', 'difficulty')
    list_filter = ('instrument', 'difficulty')
    search_fields = ('song__title', 'instrument__name')

@admin.register(ChordProgression)
class ChordProgressionAdmin(admin.ModelAdmin):
    list_display = ('song', 'chord_name', 'chord_type', 'order')
    list_filter = ('chord_type',)
    search_fields = ('song__title', 'chord_name')
    list_editable = ('order',)

@admin.register(LyricsSection)
class LyricsSectionAdmin(admin.ModelAdmin):
    list_display = ('song', 'section_type', 'order', 'content_preview')
    list_filter = ('section_type',)
    search_fields = ('song__title', 'content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'

@admin.register(Tab)
class TabAdmin(admin.ModelAdmin):
    list_display = ('song', 'instrument', 'content_preview')
    list_filter = ('instrument',)
    search_fields = ('song__title', 'instrument__name', 'content')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Tab Content Preview'