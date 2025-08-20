# urls.py
from django.urls import path
from content import views

urlpatterns = [
    path('', views.song_list_view, name='song_list'),
    path('song/<int:song_id>/', views.song_detail_view, name='song_detail'),
    path('instruments/', views.instrument_list_view, name='instrument_list'),
]