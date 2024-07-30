import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp
import os
import re
import subprocess

# Spotify API credentials
SPOTIPY_CLIENT_ID = 'bc9f17029cfa4c5ca6a6d969ce36217c'
SPOTIPY_CLIENT_SECRET = 'e2f342ad7d42433d9b1f54ba9c998b35'

# Set up Spotify client
client_credentials_manager = SpotifyClientCredentials(client_id=SPOTIPY_CLIENT_ID, client_secret=SPOTIPY_CLIENT_SECRET)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except FileNotFoundError:
        return False

def extract_playlist_id(url):
    match = re.search(r'playlist/([a-zA-Z0-9]+)', url)
    return match.group(1) if match else None

def get_playlist_tracks(playlist_id):
    results = sp.playlist_tracks(playlist_id)
    tracks = results['items']
    while results['next']:
        results = sp.next(results)
        tracks.extend(results['items'])
    return tracks

def download_track(track_info, output_folder):
    track_name = track_info['track']['name']
    artist_name = track_info['track']['artists'][0]['name']
    search_query = f"{track_name} {artist_name} audio"
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_folder, f'{track_name} - {artist_name}.%(ext)s'),
        'default_search': 'ytsearch',
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([search_query])
            print(f"Downloaded: {track_name} - {artist_name}")
        except Exception as e:
            print(f"Failed to download: {track_name} - {artist_name}. Error: {str(e)}")

def main():
    if not check_ffmpeg():
        print("Error: FFmpeg is not installed or not in the system PATH.")
        print("Please install FFmpeg and make sure it's accessible from the command line.")
        print("Installation instructions:")
        print("- Windows: https://www.gyan.dev/ffmpeg/builds/ (download and add to PATH)")
        print("- macOS: Use Homebrew: 'brew install ffmpeg'")
        print("- Linux: Use your package manager, e.g., 'sudo apt-get install ffmpeg'")
        return

    playlist_url = input("Enter your Spotify playlist URL: ")
    output_folder = input("Enter the folder path to save MP3 files: ")
    
    playlist_id = extract_playlist_id(playlist_url)
    if not playlist_id:
        print("Invalid Spotify playlist URL.")
        return
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    tracks = get_playlist_tracks(playlist_id)
    
    print(f"Found {len(tracks)} tracks. Starting download...")
    
    for track in tracks:
        download_track(track, output_folder)
    
    print("Download complete!")

if __name__ == "__main__":
    main() 

