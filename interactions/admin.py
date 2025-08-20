from django.contrib import admin
from .models import Like, Save, Playlist, PlaylistSong, Activity

# Register your models here.
admin.site.register(Like)
admin.site.register(Save) 
admin.site.register(Playlist)
admin.site.register(PlaylistSong)
admin.site.register(Activity)