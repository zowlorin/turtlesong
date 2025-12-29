import json, os, re, tqdm

from mutagen.mp4 import MP4
from yt_dlp import YoutubeDL

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(CURRENT_PATH, "config.json")

def sanitize_filename(filename: str) -> str:
    return re.sub(r'[<>:"/\\|?*]', ' ', filename)

def load_text_file_data(path: str) -> str:
    file = open(path, "r")
    
    data: str = file.read()
    
    file.close()
    
    return data

def load_config() -> object:
    file_data: str = load_text_file_data(CONFIG_PATH)
    
    config = json.loads(file_data)
    
    return config


class SongManager():
    def __init__(self, url: str, path: str):
        self.url = url
        self.path = path

        self.installed: set = set()

        self.updateInstalled()

    def getCommentedFileURL(self, filename: str) -> str | None:
        path = self.path + filename

        try:
            audio = MP4(path)

            comments = audio.tags.get("\xa9cmt", [])

            url = comments[0]

            return url
        
        except:
            return None
    
    def updateInstalled(self) -> None:
        folder_path: str = config["MUSIC_PATH"]
    
        files = os.listdir(folder_path)

        self.installed.clear()

        for filename in files:
            path = folder_path + filename
            
            url = self.getCommentedFileURL(path)

            if not url:
                continue

            self.installed.add(url)

    def requestPlaylist(self) -> list:
        opts: object = {
            'quiet': True,
            'extract_flat': True,
            'skip_download': True,
        }

        with YoutubeDL(opts) as ydl:
            try:
                info = ydl.extract_info(self.url, download=False)
                
                if 'entries' not in info:
                    return []

                data: list = [{"name":sanitize_filename(entry["title"]), "url":entry["url"]} for entry in info['entries']]
                
                return data
            
            except:
                return []

    def findMissing(self) -> None:
        playlist = self.requestPlaylist()
        
        missing: list = []
        
        for data in playlist:
            url = data["url"]
            
            if (url in self.installed):
                continue
            
            missing.append(data)
            
        return missing 
    
    def installSong(path: str, name: str, url: str) -> None:
        name = sanitize_filename(name)
        
        opts = {
            'quiet': True,
            'no_warnings': True,

            'format': 'bestaudio',
            'extract_audio': True,
            
            'outtmpl': (path + name + '.%(ext)s'),
            'postprocessors': [
                {
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'm4a',
                },
                {
                    'key': 'FFmpegMetadata',
                    'add_metadata': True,
                },
            ],
            'embed_metadata': True,
        }

        with YoutubeDL(opts) as ydl:
            try:
                code: int = ydl.download([url])
            
                if (code == 1):
                    print("Failed to download song from url " + url + "?")
                    
                    return
                
            except:
                print("Error while downloading song from url " + url + "?")

    def updateSongs(self):
        path: str = config["MUSIC_PATH"]

        missing = self.findMissing()

        if not len(missing):
            print("Everything up-to-date")
            return
        
        print(f"Found {len(missing)} missing song{"s" if len(missing) > 1 else ""}")
    
        for i in tqdm(range(len(missing))):
            song = missing[i]

            url: str = song["url"]

            name: str = song["name"]
            
            self.installSong(path, name, url)

        
        print(f"Installed all {len(missing)} missing song{"s" if len(missing) > 1 else ""}")


if __name__ == "__main__":
    config: object = load_config()
    manager = SongManager(config["PLAYLIST_URL"], config["MUSIC_PATH"])