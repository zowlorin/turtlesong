import json, os, re

CONFIG_PATH = "config.json"

from yt_dlp import YoutubeDL

def load_text_file_data(path: str) -> str:
    file = open(path, "r")
    
    data: str = file.read()
    
    file.close()
    
    return data

import re

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', ' ', filename)

def load_config() -> object:
    file_data: str = load_text_file_data(CONFIG_PATH)
    
    config = json.loads(file_data)
    
    return config

config: object = load_config()

def get_installed_song_names() -> list:
    folder_path: str = config["MUSIC_PATH"]
    
    files = os.listdir(folder_path)
    
    music_names: list = [filename[0:-4] for filename in files]
    
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

        data: list = [{"name":sanitize_filename(entry["title"]), "url":entry["url"]} for entry in info['entries']]
        
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

def install_song(path: str, name: str, url: str) -> None:
    name = sanitize_filename(name)
    
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio',
        'extract_audio': True,
        'outtmpl': (path + name + '.%(ext)s'),
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
        name: str = song["name"]
        
        install_song(path, name, url)
        
def install_missing_songs():
    already_installed: list = get_installed_song_names()

    playlist: list = get_playlist_song_data()

    missing: list = get_missing_songs(already_installed, playlist)
    
    if not len(missing):
        print("Everything up-to-date.")
        return
    
    install_songs(missing)
    
    print("Installed all {} missing songs.".format(len(missing)))
    
if __name__ == "__main__":
    install_missing_songs()