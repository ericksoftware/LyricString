from django.contrib import admin
from .models import Genre, Instrument, Artist, Song, SongInstrument

# Register your models here.

admin.site.register(Genre)
admin.site.register(Instrument)
admin.site.register(Artist)
admin.site.register(Song)
admin.site.register(SongInstrument)