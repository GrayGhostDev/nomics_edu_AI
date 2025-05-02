import os
import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time

class CacheManager:
    def __init__(self, cache_dir: str = "cache", ttl_hours: int = 24):
        """Initialize cache manager with specified directory and TTL"""
        self.cache_dir = cache_dir
        self.ttl = timedelta(hours=ttl_hours)
        os.makedirs(cache_dir, exist_ok=True)
        
    def _generate_cache_key(self, data: Dict[str, Any], template_content: str) -> str:
        """Generate a unique cache key based on input data and template"""
        # Create a dictionary with all relevant data
        cache_data = {
            "game_data": data,
            "template": template_content,
            "timestamp": datetime.now().strftime("%Y%m%d")  # Include date to refresh cache daily
        }
        
        # Convert to sorted JSON string to ensure consistent ordering
        cache_str = json.dumps(cache_data, sort_keys=True)
        
        # Generate MD5 hash
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get the file path for a cache key"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, data: Dict[str, Any], template_content: str) -> Optional[str]:
        """Get cached response if available and not expired"""
        cache_key = self._generate_cache_key(data, template_content)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache has expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                os.remove(cache_path)  # Clean up expired cache
                return None
                
            return cache_data['response']
            
        except Exception as e:
            print(f"Error reading cache: {str(e)}")
            return None
    
    def set(self, data: Dict[str, Any], template_content: str, response: str):
        """Cache a response"""
        cache_key = self._generate_cache_key(data, template_content)
        cache_path = self._get_cache_path(cache_key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'response': response,
            'metadata': {
                'subject': data['request']['subject'],
                'grade_level': data['request']['grade_level'],
                'difficulty': data['request']['difficulty'],
                'template_hash': hashlib.md5(template_content.encode()).hexdigest()
            }
        }
        
        try:
            with open(cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Error writing cache: {str(e)}")
    
    def clear_expired(self):
        """Clear all expired cache entries"""
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
                
            cache_path = os.path.join(self.cache_dir, filename)
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    os.remove(cache_path)
                    
            except Exception as e:
                print(f"Error clearing cache {filename}: {str(e)}")
    
    def clear_all(self):
        """Clear all cache entries"""
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                os.remove(os.path.join(self.cache_dir, filename))
                
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_entries = 0
        expired_entries = 0
        total_size = 0
        subjects = set()
        
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith('.json'):
                continue
                
            cache_path = os.path.join(self.cache_dir, filename)
            try:
                with open(cache_path, 'r') as f:
                    cache_data = json.load(f)
                    
                total_entries += 1
                total_size += os.path.getsize(cache_path)
                subjects.add(cache_data['metadata']['subject'])
                
                cached_time = datetime.fromisoformat(cache_data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    expired_entries += 1
                    
            except Exception:
                continue
                
        return {
            'total_entries': total_entries,
            'expired_entries': expired_entries,
            'active_entries': total_entries - expired_entries,
            'total_size_mb': total_size / (1024 * 1024),
            'subjects': list(subjects)
        } 