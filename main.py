import json, os

CONFIG_PATH = "config.json"

from yt_dlp import YoutubeDL

def load_text_file_data(path: str) -> str:
    file = open(path, "r")
    
    data: str = file.read()
    
    file.close()
    
    return data

def load_config() -> object:
    file_data: str = load_text_file_data(CONFIG_PATH)
    
    config = json.loads(file_data)
    
    return config

config: object = load_config()

def get_installed_song_names() -> list:
    folder_path: str = config["MUSIC_PATH"]
    
    files = os.listdir(folder_path)
    
    music_names: list = [filename[0:-5] for filename in files]
    
    return music_names

def get_playlist_song_data() -> list:
    url: str = config["PLAYLIST_URL"]
    
    ydl_opts: object = {
        'quiet': True,
        'extract_flat': True,
        'skip_download': True,
    }

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        
        if 'entries' not in info:
            return []

        data: list = [{"name":entry["title"], "url":entry["url"]} for entry in info['entries']]
        
        print("Accessed playlist from url " + url + ".")
        
        return data
    
def get_missing_songs(already_installed: list, playlist: list) -> list:
    hashed: dict = {}
    
    missing: list = []
    
    for song_name in already_installed:
        hashed[song_name] = True
        
    for song_data in playlist:
        song_name: str = song_data["name"]
        
        if (hashed.get(song_name) != None):
            continue
        
        missing.append(song_data)
        
    return missing 

def install_song(path: str, url: str) -> None:
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio',
        'extract_audio': True,
        'outtmpl': (path + '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',
        }],
    }

    with YoutubeDL(ydl_opts) as ydl:
        code: int = ydl.download([url])
        
        if (code == 0):
            print("Installed song from url " + url + ".")
            return
        
    print("Failed to download song from url " + url + "?")

def install_songs(to_install: list):
    path: str = config["MUSIC_PATH"]
    
    for song in to_install:
        url: str = song["url"]
        
        install_song(path, url)

already_installed: list = get_installed_song_names()

playlist: list = get_playlist_song_data()

missing: list = get_missing_songs(already_installed, playlist)

install_songs(missing)