import requests
from django.shortcuts import render
from django.conf import settings
from bs4 import BeautifulSoup

GENIUS_BASE_URL = "https://api.genius.com"
GENIUS_API_KEY = getattr(settings, 'GENIUS_API_KEY', None)

def search_view(request):
    return render(request, 'finder/search.html')

def results_view(request):
    title = request.GET.get('title', '').strip()
    if not title:
        return render(request, 'finder/search.html', {'error': 'Please enter a song title'})

    headers = {"Authorization": f"Bearer {GENIUS_API_KEY}"}
    search_url = f"{GENIUS_BASE_URL}/search"
    response = requests.get(search_url, headers=headers, params={'q': title})

    if response.status_code != 200:
        return render(request, 'finder/results.html', {'title': title, 'lyrics': None, 'error': 'API Error: Try again later'})

    data = response.json()
    hits = data.get('response', {}).get('hits', [])

    if not hits:
        return render(request, 'finder/results.html', {'title': title, 'lyrics': None, 'error': 'No results found'})

    # Take top result
    song = hits[0]['result']
    song_title = song['title']
    artist = song['primary_artist']['name']
    song_url = song['url']

    # Extract lyrics from Genius HTML page
    page = requests.get(song_url)
    soup = BeautifulSoup(page.text, 'html.parser')
    lyrics_div = soup.find("div", {"data-lyrics-container": "true"})
    if not lyrics_div:
        lyrics_div = soup.find("div", class_="Lyrics__Container-sc-1ynbvzw-6")
    lyrics = lyrics_div.get_text(separator="\n") if lyrics_div else "Lyrics not found."

    return render(request, 'finder/results.html', {
        'title': song_title,
        'artist': artist,
        'lyrics': lyrics
    })
