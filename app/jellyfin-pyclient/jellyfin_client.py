import requests
import logging
import sys
import datetime
import os
from collections import defaultdict
from urllib.parse import urljoin
from typing import Optional, List, Dict, Set

import dotenv

dotenv.load_dotenv()

CONFIG = {
    'SERVER_URL': os.getenv('SERVER_URL'),
    'API_KEY': os.getenv('API_KEY'),
    'USER_ID': os.getenv('USER_ID'),
    'MEDIA_TYPE': os.getenv('MEDIA_TYPE'),
    'BASE_PATH': os.getenv('BASE_PATH'),
    'SINGLE_PATH': os.getenv('SINGLE_PATH'),
    'START_LEVEL': os.getenv('START_LEVEL'),
    'LEVELS': os.getenv('LEVELS'),
    'MIN_DURATION': os.getenv('MIN_DURATION'),
    'MAX_DURATION': os.getenv('MAX_DURATION'),
    'DRY_RUN': os.getenv('DRY_RUN'),
    'LOG_LEVEL': os.getenv('LOG_LEVEL')
}

def setup_logging(log_level):
    """Configure logging with the specified level"""
    logging.basicConfig(
        level=log_level,
        stream=sys.stdout,
        format='time=%(asctime)s level=%(levelname)s msg=%(message)s'
    )
    logging.Formatter.formatTime = (
        lambda self, record, datefmt=None:
        datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
        .astimezone().isoformat(sep="T", timespec="milliseconds")
    )

def is_valid_media_path(path: str) -> bool:
    """Check if path is valid"""
    return os.path.isdir(path)

class JellyfinCollectionManager:
    def __init__(self):
        self.server_url = CONFIG['SERVER_URL'].rstrip('/') + '/'
        self.api_key = CONFIG['API_KEY']
        self.session = requests.Session()
        self.session.headers.update({
            'X-MediaBrowser-Token': self.api_key,
            'Content-Type': 'application/json'
        })
        self.dry_run = CONFIG['DRY_RUN']

    def get_physical_paths(self) -> List[str]:
        """Get all physical paths from Jellyfin"""
        url = urljoin(self.server_url, 'Library/PhysicalPaths')
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def get_library_id(self) -> Optional[str]:
        """Get library ID"""
        params = {'userId': CONFIG['USER_ID']}
        url = urljoin(self.server_url, 'UserViews')
        response = self.session.get(url, params=params)
        response.raise_for_status()
        
        libraries = response.json()
        for library in libraries.get('Items', []):
            return library['Id']
        return None

    def get_collections(self) -> List[Dict]:
        """Fetch all existing collections"""
        library_id = self.get_library_id()
        if not library_id:
            logging.warning("Library not found")
            return []
            
        url = urljoin(self.server_url, 'Items')
        params = {
            'ParentId': library_id,
            'IncludeItemTypes': 'Playlist',
            'Recursive': True
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return response.json().get('Items', [])
    
    def get_logs(self):
        url = urljoin(self.server_url, 'System/Logs')
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()

    def create_collection(self, name: str, media_type: str = 'Mixed') -> str:
        """Create a new collection"""
        if self.dry_run:
            logging.info(f"[DRY RUN] Would create collection: {name} ({media_type})")
            return f"dry-run-id-{name}"
            
        url = urljoin(self.server_url, 'Collections')
        params = {
            'name': name,
            'isLocked': False
        }
        
        response = self.session.post(url, params=params)
        response.raise_for_status()
        return response.json().get('Id')

    def get_playlists(self) -> Dict[str, str]:
        """Get all existing playlists"""
        url = urljoin(self.server_url, 'Items')
        params = {
            'userId': CONFIG['USER_ID'],
            'includeItemTypes': 'Playlist',
            'recursive': True,
            'fields': 'Path'
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        return {item['Name']: item['Id'] for item in response.json().get('Items', [])}
        
    def clear_playlist(self, playlist_id: str):
        """Clear all items from a playlist"""
        if self.dry_run:
            logging.info(f"[DRY RUN] Would clear playlist {playlist_id}")
            return
            
        url = urljoin(self.server_url, f'Playlists/{playlist_id}')
        params = {'userId': CONFIG['USER_ID']}
        
        try:
            response = self.session.get(url, params=params)
            response.raise_for_status()
            item_ids = response.json().get('ItemIds', [])
            
            if not item_ids:
                return
                
            delete_url = urljoin(self.server_url, f'Playlists/{playlist_id}/Items')
            # delete_params = {
            #     'entryIds': ','.join(item_ids),
            # }
            
            response = self.session.delete(delete_url)
            response.raise_for_status()
        except Exception as e:
            logging.error(f"Failed to clear playlist {playlist_id}: {e}")

    def add_to_playlist(self, playlist_id: str, item_ids: List[str]):
        """Add items to a playlist"""
        if self.dry_run:
            logging.info(f"[DRY RUN] Would add {len(item_ids)} items to playlist {playlist_id}")
            return
            
        def split_list(items: List[str], size: int):
            for i in range(0, len(items), size):
                yield items[i:i + size]
                
        for group in split_list(item_ids, 15):
            url = urljoin(self.server_url, f'Playlists/{playlist_id}/Items')
            params = {
                'ids': ','.join(group),
                'userId': CONFIG['USER_ID']
            }
            
            response = self.session.post(url, params=params)
            response.raise_for_status()
            # logging.info(f"Added group of {len(group)} items to playlist {playlist_id}")

    def add_to_collection(self, collection_id: str, item_ids: List[str]):
            """Add items to a collection in batches"""
            if self.dry_run:
                logging.info(f"[DRY RUN] Would add {len(item_ids)} items to collection {collection_id}")
                return
                
            def split_list(items: List[str], size: int):
                for i in range(0, len(items), size):
                    yield items[i:i + size]
                    
            for group in split_list(item_ids, 15):
                url = urljoin(self.server_url, f'Collections/{collection_id}/Items')
                params = {'ids': ','.join(group)}
                
                response = self.session.post(url, params=params)
                response.raise_for_status()
                logging.info(f"Added group of {len(group)} items to collection {collection_id}")

    def list_valid_paths(self):
        """List all valid physical paths"""
        paths = self.get_physical_paths()
        valid_paths = []
        
        print("\nScanning physical paths in Jellyfin:")
        for path in sorted(paths):
            if single_path := CONFIG.get('SINGLE_PATH'):
                if single_path in path and is_valid_media_path(path):
                    valid_paths.append(path)
                    print(f"✓ {path}")
            elif is_valid_media_path(path):
                valid_paths.append(path)
                print(f"✓ {path}")
            else:
                print(f"✗ {path} (invalid)")
                
        return valid_paths
    def create_playlist(self, name: str) -> str:
            """Create a new playlist"""
            if self.dry_run:
                logging.info(f"[DRY RUN] Would create playlist: {name}")
                return f"dry-run-id-{name}"
                
            url = urljoin(self.server_url, 'Playlists')
            params = {
                'Name': name,
                'userId': CONFIG['USER_ID']
            }
            
            response = self.session.post(url, params=params)
            response.raise_for_status()
            return response.json().get('Id')

    def get_items(self, physical_path: str, media_type: Optional[str] = None, 
                 min_duration: Optional[int] = None, max_duration: Optional[int] = None) -> List[Dict]:
        """Fetch items from a specific physical path"""
        url = urljoin(self.server_url, 'Items')
        params = {
            'PhysicalPath': physical_path,
            'Recursive': True,
            'Fields': 'Path,ParentId,RunTimeTicks',
            'IncludeItemTypes': media_type if media_type != 'Mixed' else 'Photo,Video',
        }
        
        response = self.session.get(url, params=params)
        response.raise_for_status()
        items = response.json()['Items']

        if media_type == 'Video' and (min_duration is not None or max_duration is not None):
            filtered_items = []
            for item in items:
                if 'RunTimeTicks' not in item:
                    continue
                duration_minutes = (item['RunTimeTicks'] / 10000000) / 60
                
                if min_duration is not None and duration_minutes < min_duration:
                    continue
                if max_duration is not None and duration_minutes > max_duration:
                    continue
                    
                filtered_items.append(item)
            return filtered_items

        return items

    def remove_playlist(self, playlist_id: str):
        """Remove a playlist by ID"""
        if self.dry_run:
            logging.info(f"[DRY RUN] Would remove playlist {playlist_id}")
            return
            
        url = urljoin(self.server_url, f'Items/{playlist_id}')
        response = self.session.delete(url)
        response.raise_for_status()
        return response.status_code

def process_library(manager: JellyfinCollectionManager, physical_path: str):
    base_path = os.path.normpath(physical_path)
    logging.info(f"Processing path: {base_path}")

    items = manager.get_items(
        physical_path,
        media_type=CONFIG['MEDIA_TYPE'],
        min_duration=CONFIG['MIN_DURATION'],
        max_duration=CONFIG['MAX_DURATION']
    )
    logging.info(f"Found {len(items)} total items in path")

    playlists = defaultdict(list)
    skipped_items = defaultdict(int)
    
    for item in items:
        if 'Path' not in item:
            skipped_items['no_path'] += 1
            continue
            
        item_path = os.path.normpath(item['Path'])
        if not item_path.startswith(base_path):
            skipped_items['outside_base'] += 1
            continue

        parent_dir = os.path.dirname(item_path)
        if parent_dir == base_path:
            skipped_items['in_base_dir'] += 1
            continue
            
        rel_path = os.path.relpath(parent_dir, base_path)
        path_parts = rel_path.split(os.sep)
        
        if CONFIG['LOG_LEVEL'] == 'DEBUG':
            logging.debug(f"Item: {item_path}")
            logging.debug(f"  Depth: {len(path_parts)} parts: {path_parts}")
            
        if len(path_parts) > CONFIG['LEVELS']:
            skipped_items['too_deep'] += 1
            continue
        if len(path_parts) < CONFIG['START_LEVEL']:
            skipped_items['too_shallow'] += 1
            continue
            
        playlist_name = rel_path
        playlists[playlist_name].append(item['Id'])

    for reason, count in skipped_items.items():
        if count > 0:
            logging.info(f"Skipped {count} items: {reason}")

    logging.info(f"Identified {len(playlists)} potential playlists")
    
    if CONFIG['DRY_RUN']:
        total_items = 0
        for name, item_ids in playlists.items():
            total_items += len(item_ids)
            logging.info(f"Playlist '{name}' would contain {len(item_ids)} items")
            if CONFIG['LOG_LEVEL'] == 'DEBUG':
                logging.debug(f"Items in playlist {name}:")
                for item in items:
                    if item['Id'] in item_ids:
                        logging.debug(f"  - {item['Path']}")
        logging.info(f"Total items across all playlists: {total_items}")
        return

    existing_playlists = manager.get_playlists()
    
    base_collection_name = os.path.basename(physical_path)
    collection_id = manager.create_collection(base_collection_name)
    
    playlist_ids = []
    for name, item_ids in playlists.items():
        if name in existing_playlists:
            playlist_id = existing_playlists[name]
            logging.info(f"Clearing existing playlist: {name}")
            manager.clear_playlist(playlist_id)
        else:
            logging.info(f"Creating new playlist: {name}")
            playlist_id = manager.create_playlist(name)
            
        manager.add_to_playlist(playlist_id, item_ids)
        playlist_ids.append(playlist_id)
    
    manager.add_to_collection(collection_id, playlist_ids)

def main():
    setup_logging(CONFIG['LOG_LEVEL'])
    manager = JellyfinCollectionManager()

    if CONFIG['DRY_RUN']:
        logging.info("=== DRY RUN MODE - No changes will be made ===")

    valid_paths = manager.list_valid_paths()
    if not valid_paths:
        logging.error("No valid media paths found")
        return

    for path in valid_paths:
        process_library(manager, path)

    if CONFIG['DRY_RUN']:
        logging.info("=== DRY RUN completed - no changes were made ===")
    else:
        logging.info("Done!")

if __name__ == '__main__':
    main()