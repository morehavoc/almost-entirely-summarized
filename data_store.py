import json
import os
import numpy as np
from datetime import datetime
from utils import logger

class DataStore:
    def __init__(self, storage_file):
        self.storage_file = storage_file
        self.ensure_storage_file()

    def ensure_storage_file(self):
        """Ensure the storage file exists"""
        if not os.path.exists(self.storage_file):
            directory = os.path.dirname(self.storage_file)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)
            with open(self.storage_file, 'w') as f:
                json.dump([], f)
            logger.info(f"Created new storage file: {self.storage_file}")

    def save_blog_data(self, blog_data):
        """Save processed blog data with embeddings to storage"""
        try:
            existing_data = self.load_all_data()

            # Check if URL already exists and update if it does
            for i, post in enumerate(existing_data):
                if post.get('url') == blog_data.get('url'):
                    # Update existing entry
                    existing_data[i] = blog_data
                    logger.info(f"Updated existing entry for URL: {blog_data.get('url')}")
                    break
            else:
                # URL not found, add new entry
                existing_data.append(blog_data)
                logger.info(f"Added new entry for URL: {blog_data.get('url')}")

            # Save updated data
            with open(self.storage_file, 'w') as f:
                json.dump(existing_data, f, indent=2)

            return True
        except Exception as e:
            logger.error(f"Error saving blog data: {e}")
            return False

    def load_all_data(self):
        """Load all stored blog data including embeddings"""
        try:
            if os.path.exists(self.storage_file) and os.path.getsize(self.storage_file) > 0:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading data: {e}")
            return []

    def is_url_processed(self, url):
        """Check if a URL has already been processed"""
        data = self.load_all_data()
        for post in data:
            if post.get('url') == url:
                return True
        return False

    def get_embeddings_as_matrix(self):
        """Return a matrix of all embeddings for efficient similarity calculation"""
        try:
            data = self.load_all_data()
            embeddings = [post.get("embedding", []) for post in data if "embedding" in post]
            if embeddings:
                return np.array(embeddings)
            return np.array([])
        except Exception as e:
            logger.error(f"Error creating embedding matrix: {e}")
            return np.array([])
