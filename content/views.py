from django.shortcuts import render

# Create your views here.
def song_list_view(request):
    # Logic to retrieve and display songs
    return render(request, 'content/song_list.html')

def song_detail_view(request):
    # Logic to retrieve and display a specific song by its ID
    return render(request, 'content/song_detail.html')

def instrument_list_view(request):
    # Logic to retrieve and display instruments
    return render(request, 'content/instrument_list.html')

