import os
from utils import logger, validate_url

class BlogSourceHandler:
    def __init__(self, source_file):
        self.source_file = source_file
        if not os.path.exists(source_file):
            with open(source_file, 'w') as f:
                f.write("# Add blog URLs here, one per line\n")
                f.write("https://www.esri.com/arcgis-blog/example1/\n")
                f.write("https://www.esri.com/arcgis-blog/example2/\n")
            logger.info(f"Created sample URL file at {source_file}")

    def load_urls(self):
        """Load and validate URLs from the source file"""
        urls = []
        try:
            with open(self.source_file, 'r') as file:
                for line in file:
                    line = line.strip()
                    # Skip empty lines and comments
                    if not line or line.startswith('#'):
                        continue

                    if validate_url(line):
                        urls.append(line)
                    else:
                        logger.warning(f"Invalid URL format: {line}")

            logger.info(f"Loaded {len(urls)} URLs from {self.source_file}")
            return urls
        except Exception as e:
            logger.error(f"Error loading URLs: {e}")
            return []
