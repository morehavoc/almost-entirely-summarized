import requests
from bs4 import BeautifulSoup
import datetime
from utils import logger, parse_date
import re

class BlogContentProcessor:
    def __init__(self, ai_interface, embedding_service):
        self.ai_interface = ai_interface
        self.embedding_service = embedding_service
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def fetch_content(self, url):
        """Fetch blog content from a given URL"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.error(f"Error fetching content from {url}: {e}")
            return None

    def extract_text(self, html_content):
        """Extract text content from HTML"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Find the main content area - adjust selectors based on the blog structure
            main_content = None

            # Try different potential content containers
            potential_containers = [
                soup.find('article'),
                soup.find('main'),
                soup.find('div', class_='content'),
                soup.find('div', class_='post-content'),
                soup.find('div', class_='entry-content'),
                soup.find('div', class_='blog-content'),
                soup.find('div', class_='post-body'),
                soup.find('div', id='content'),
                soup.find('div', class_=lambda c: c and ('content' in c.lower() or 'article' in c.lower() or 'post' in c.lower())),
            ]

            for container in potential_containers:
                if container and len(container.get_text(strip=True)) > 200:
                    main_content = container
                    break

            if main_content:
                paragraphs = main_content.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
                content = '\n'.join([p.get_text().strip() for p in paragraphs])
            else:
                # Fallback to body content if no main content area is identified
                body = soup.find('body')
                content = body.get_text() if body else soup.get_text()

            # Clean up whitespace
            content = ' '.join(content.split())
            return content
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return "Error extracting content"

    def extract_title(self, soup, url):
        """Extract title with multiple fallback methods"""
        try:
            # Method 1: Standard title tag
            if soup.title and soup.title.string:
                title = soup.title.string.strip()
                # Sometimes titles include site name, try to remove it
                title = re.sub(r'\s*\|\s*.*?$', '', title)
                title = re.sub(r'\s*-\s*.*?$', '', title)
                if title and len(title) > 3:
                    return title

            # Method 2: Open Graph meta tag
            og_title = soup.find('meta', property='og:title')
            if og_title and og_title.get('content'):
                return og_title['content'].strip()

            # Method 3: H1 tag
            h1 = soup.find('h1')
            if h1 and h1.get_text():
                return h1.get_text().strip()

            # Method 4: Article header
            article_header = soup.find(['header', 'div'], class_=lambda c: c and ('header' in c.lower() or 'title' in c.lower()))
            if article_header:
                h_tag = article_header.find(['h1', 'h2'])
                if h_tag and h_tag.get_text():
                    return h_tag.get_text().strip()

            # Method 5: Classes that often contain the title
            title_classes = ['entry-title', 'post-title', 'article-title', 'headline', 'title']
            for cls in title_classes:
                title_elem = soup.find(class_=cls)
                if title_elem and title_elem.get_text():
                    return title_elem.get_text().strip()

            # Method 6: Extract from URL as last resort
            url_path = url.rstrip('/').split('/')[-1]
            url_title = url_path.replace('-', ' ').replace('_', ' ').title()
            if url_title and len(url_title) > 3:
                return f"Article: {url_title}"

            # If all else fails
            return "Untitled Article"

        except Exception as e:
            logger.error(f"Error extracting title: {e}")
            return "Untitled Article"

    def extract_date(self, soup, url):
        """Extract publication date with multiple fallback methods"""
        try:
            # Method 1: Dedicated meta tags
            meta_date_selectors = [
                ('meta', {'property': 'article:published_time'}),
                ('meta', {'property': 'og:published_time'}),
                ('meta', {'name': 'date'}),
                ('meta', {'name': 'publication_date'}),
                ('meta', {'name': 'publish-date'}),
                ('meta', {'itemprop': 'datePublished'})
            ]

            for tag, attrs in meta_date_selectors:
                date_tag = soup.find(tag, attrs)
                if date_tag and date_tag.get('content'):
                    date_str = date_tag['content'].split('T')[0] if 'T' in date_tag['content'] else date_tag['content']
                    if self.is_valid_date(date_str):
                        return date_str

            # Method 2: Time tag
            time_tag = soup.find('time')
            if time_tag:
                if time_tag.get('datetime'):
                    date_str = time_tag['datetime'].split('T')[0] if 'T' in time_tag['datetime'] else time_tag['datetime']
                    if self.is_valid_date(date_str):
                        return date_str
                elif time_tag.get_text():
                    # Try to parse the text content
                    return self.extract_date_from_text(time_tag.get_text())

            # Method 3: Common date classes
            date_classes = ['date', 'post-date', 'entry-date', 'published', 'byline', 'post-meta']
            for cls in date_classes:
                date_elem = soup.find(class_=cls)
                if date_elem and date_elem.get_text():
                    return self.extract_date_from_text(date_elem.get_text())

            # Method 4: Look for date patterns in the content
            text = soup.get_text()
            date_str = self.extract_date_from_text(text)
            if date_str:
                return date_str

            # Default to current date
            return datetime.datetime.now().strftime("%Y-%m-%d")

        except Exception as e:
            logger.error(f"Error extracting date: {e}")
            return datetime.datetime.now().strftime("%Y-%m-%d")

    def is_valid_date(self, date_str):
        """Check if a string is a valid date format"""
        try:
            # Try to parse with multiple formats
            for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d/%m/%Y", "%m-%d-%Y", "%m/%d/%Y"):
                try:
                    datetime.datetime.strptime(date_str, fmt)
                    return True
                except ValueError:
                    continue
            return False
        except:
            return False

    def extract_date_from_text(self, text):
        """Try to extract a date from text content"""
        # Common date patterns
        patterns = [
            # ISO format: 2023-01-25
            r'\b(\d{4}[-/]\d{1,2}[-/]\d{1,2})\b',
            # Month name formats: January 25, 2023 or 25 January 2023
            r'\b(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.,]?\s+\d{1,2}(?:[a-z]{2})?,?\s+\d{4}\b',
            r'\b\d{1,2}(?:[a-z]{2})?\s+(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)[.,]?\s+\d{4}\b',
            # MM/DD/YYYY or DD/MM/YYYY
            r'\b\d{1,2}[/.-]\d{1,2}[/.-]\d{4}\b'
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                date_text = match.group(0)
                # Try to convert to a standard format
                try:
                    # For ISO format matches
                    if '-' in date_text and len(date_text.split('-')[0]) == 4:
                        return date_text.split()[0]  # Take just the date part

                    # Try to parse with dateutil (more forgiving)
                    from dateutil import parser
                    dt = parser.parse(date_text, fuzzy=True)
                    return dt.strftime("%Y-%m-%d")
                except:
                    # If parsing fails, return the raw matched text
                    pass

        # Default to current date if no patterns match
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def extract_metadata(self, html_content, url):
        """Extract title, date, and other metadata"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')

            # Extract title using robust methods
            title = self.extract_title(soup, url)

            # Extract date using robust methods
            date = self.extract_date(soup, url)

            return {
                "title": title,
                "date": date,
                "url": url
            }
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {
                "title": "Error extracting title",
                "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "url": url
            }

    def process_blog(self, url):
        """Process a blog post completely, returning structured data with summary and embedding"""
        logger.info(f"Processing blog: {url}")

        html_content = self.fetch_content(url)
        if not html_content:
            return None

        metadata = self.extract_metadata(html_content, url)
        content = self.extract_text(html_content)

        if not content or len(content) < 100:
            logger.warning(f"Content too short or not found for {url}")
            return None

        # Get AI summary
        summary = self.ai_interface.summarize_blog(content, metadata["title"], url)

        # Generate embedding for the summary
        embedding, model = self.embedding_service.generate_embedding(summary)

        # Combine all data
        result = {
            "url": url,
            "title": metadata["title"],
            "date": metadata["date"],
            "content": content[:5000],  # Store truncated content
            "summary": summary,
            "embedding": embedding,
            "embeddingModel": model,
            "processedDate": datetime.datetime.now().isoformat()
        }

        logger.info(f"Successfully processed blog: {url}")
        return result
