import logging
import os
import sys
import dotenv
from collections import defaultdict
import requests

dotenv.load_dotenv()

class Immich:
    def __init__(self):
        self.api_key = os.getenv("IMMICH_API_KEY")
        self.base_url = os.getenv("IMMICH_BASE_URL")
        self.root_path = os.getenv("IMMICH_ROOT_PATH")
        self.album_levels = os.getenv("IMMICH_ALBUM_LEVELS")
        self.separator = os.getenv("IMMICH_SEPARATOR")
        self.chunk_size = os.getenv("IMMICH_CHUNK_SIZE")
        self.library_id = os.getenv("IMMICH_LIBRARY_ID")
        
        self.requests_kwargs = {
            'headers': {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        }
        
        logging.basicConfig(
            level=logging.INFO,
            format='time=%(asctime)s level=%(levelname)s msg=%(message)s',
            stream=sys.stdout
        )
        
    def get_all_albums(self):
        albums = requests.get(
            url=f"{self.base_url}/albums",
            headers=self.requests_kwargs['headers']
        ).json()
        return albums

    def create_album(self, album_name):
        data = {
            'albumName': album_name,
            'description': album_name
        }
        response = requests.post(
            url=f"{self.base_url}/albums",
            headers=self.requests_kwargs['headers'],
            json=data
        )
        if response.status_code not in [200, 201]:
            raise Exception(f"Failed to create album: {response.text}")
        return response.json()['id']

    def add_assets_to_album(self, album_id, asset_ids):
        for i in range(0, len(asset_ids), self.chunk_size):
            chunk = asset_ids[i:i + self.chunk_size]
            data = {'ids': chunk}
            response = requests.put(
                url=f"{self.base_url}/albums/{album_id}/assets",
                headers=self.requests_kwargs['headers'],
                json=data
            )
            if response.status_code not in [200, 201]:
                logging.error(f"Failed to add assets to album: {response.text}")
                continue
                
            results = response.json()
            added_count = sum(1 for r in results if r['success'])
            if added_count > 0:
                logging.info(f"{added_count} new assets added to album {album_id}")

    def fetch_assets(self):
        assets = []
        page = 1
        page_size = 1000
        
        while True:
            body = {
                'isNotInAlbum': 'true',
                'size': page_size,
                'page': str(page)
            }
            response = requests.post(
                url=f"{self.base_url}/search/metadata",
                headers=self.requests_kwargs['headers'],
                json=body
            )
            response.raise_for_status()
            
            items = response.json()['assets']['items']
            assets.extend(items)
            
            if len(items) < page_size:
                break
            page += 1
            
        return assets

    def scan_library(self):
        r = requests.post(
            url=self.base_url + f"/libraries/{self.library_id}/scan",
            headers=self.requests_kwargs['headers']
        )
        logging.info(f"Scan request sent: {r.text}")
       
        return r
    
    def create_album_name(self, path_chunks):
        if self.album_levels < 0:
            start = self.album_levels
        else:
            start = 0
            levels = min(len(path_chunks), self.album_levels)
        
        selected_chunks = path_chunks[start:] if self.album_levels < 0 else path_chunks[:levels]
        return self.separator.join(selected_chunks)

    def organize_albums(self, path: str = None):
        if not path:
            root_path = self.root_path.rstrip('/') + '/'

        logging.info("Fetching all assets...")
        assets = self.fetch_assets()
        logging.info(f"Found {len(assets)} assets")

        logging.info("Organizing assets into albums...")
        album_to_assets = defaultdict(list)
        for asset in assets:
            if root_path not in asset['originalPath']:
                continue
                
            path_chunks = asset['originalPath'].replace(root_path, '').split('/')
            if len(path_chunks) <= 1:
                continue
                
            path_chunks = path_chunks[:-1]
            album_name = self.create_album_name(path_chunks)
            if album_name:
                album_to_assets[album_name].append(asset['id'])

        logging.info(f"Identified {len(album_to_assets)} albums")
        logging.info(f"Album list: {list(album_to_assets.keys())}")

        existing_albums = {album['albumName']: album['id'] for album in self.get_all_albums()}
        
        albums_created = 0
        for album_name in album_to_assets:
            if album_name not in existing_albums:
                album_id = self.create_album(album_name)
                existing_albums[album_name] = album_id
                logging.info(f"Created album: {album_name}")
                albums_created += 1
        
        logging.info(f"Created {albums_created} new albums")

        logging.info("Adding assets to albums...")
        for album_name, asset_ids in album_to_assets.items():
            album_id = existing_albums[album_name]
            self.add_assets_to_album(album_id, asset_ids)

        logging.info("Done!")