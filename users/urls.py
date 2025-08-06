# urls.py
from django.urls import path
from users import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),
    path('profile_edit/', views.profile_edit_view, name='profile_edit'),
]