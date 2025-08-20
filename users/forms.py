# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, UserPreferences
from content.models import Genre, Instrument

# users/forms.py
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    username = forms.CharField(required=True)  # Asegúrate de que sea obligatorio
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'bio', 'profile_picture', 
                 'location', 'website', 'social_media', 'skill_level')

class UserPreferencesForm(forms.ModelForm):
    favorite_genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    instruments_played = forms.ModelMultipleChoiceField(
        queryset=Instrument.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    class Meta:
        model = UserPreferences
        fields = ('favorite_genres', 'instruments_played', 'public_profile', 
                 'show_liked_songs', 'show_activity', 'email_notifications')