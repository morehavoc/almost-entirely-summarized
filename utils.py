# utils.py
import logging
import datetime
import re
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def validate_url(url):
    """Validate if a string is a proper URL."""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

    return bool(url_pattern.match(url))

def get_current_date_string():
    """Return current date as YYYY-MM-DD string."""
    return datetime.datetime.now().strftime("%Y-%m-%d")

def generate_output_filename():
    """Generate an output filename with the current date."""
    return f"summary_{get_current_date_string()}.md"

def parse_date(date_string):
    """Parse a date string in various formats."""
    try:
        # Try ISO format first
        return datetime.datetime.fromisoformat(date_string)
    except ValueError:
        # Try with dateutil parser
        try:
            from dateutil import parser
            return parser.parse(date_string)
        except:
            logger.error(f"Invalid date format: {date_string}")
            return None
