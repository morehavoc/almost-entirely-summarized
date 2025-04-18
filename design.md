# Updated Software Architecture Design Document: AI Blog Post Summarizer with Embeddings

## 1. Overview

This document outlines the updated architecture for an application that summarizes blog posts using Anthropic's Claude AI and vector embeddings. Building on the previous version, this enhanced system will process Esri blog posts, generate generic summaries, create vector embeddings for each summary, and enable topic-specific retrieval based on similarity matching rather than static interest scores.

## 2. System Architecture

### 2.1 High-Level Components

```
┌───────────────┐    ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
│  Blog Source  │───▶│ Post Processor │───▶│  Data Store   │◀───┤ Query         │
│  Input        │    │ & Summarizer   │    │ with          │    │ Processor     │
└───────────────┘    └───────────────┘    │ Embeddings    │    └───────┬───────┘
                           │              └───────────────┘            │
                           │                      │                    │
                           ▼                      ▼                    ▼
                     ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
                     │ Embedding     │    │ Similarity     │    │ Summary       │
                     │ Generator     │───▶│ Matcher        │◀───│ Generator     │
                     └───────────────┘    └───────────────┘    └───────────────┘
```

### 2.2 Components Description

1. **Blog Source Input**: Handles the loading of blog URLs from a text file or other input sources.
2. **Post Processor & Summarizer**: Fetches blog content, processes it, and generates generic summaries using Claude.
3. **Embedding Generator**: Creates vector embeddings for blog summaries using Voyage embedding service.
4. **Data Store with Embeddings**: Persists information about processed blogs, their summaries, and embeddings.
5. **Query Processor**: Handles user input queries about specific topics of interest.
6. **Similarity Matcher**: Compares query embeddings with stored blog summary embeddings to find relevant content.
7. **Summary Generator**: Creates a comprehensive summary of the most relevant blog posts based on similarity matching.

## 3. Technical Specifications

### 3.1 Dependencies

- Python 3.8+
- Anthropic Claude API for AI summarization
- Voyage API for embedding generation
- Requests library for HTTP requests
- BeautifulSoup for HTML parsing
- NumPy for vector operations
- Scikit-learn for similarity calculations
- JSON for data storage

### 3.2 Data Models

```python
# Blog Post Record
{
    "url": "string",             # Original blog URL
    "title": "string",           # Blog post title
    "date": "ISO-8601 string",   # Publication date
    "content": "string",         # Full or truncated blog content
    "summary": "string",         # AI-generated summary
    "embedding": [float],        # Vector embedding of the summary
    "embeddingModel": "string",  # Version of the embedding model used
    "processedDate": "ISO-8601 string"  # When the post was processed
}
```

## 4. Component Details

### 4.1 Blog Source Input

No changes from the previous version.

### 4.2 Post Processor & Summarizer

Updated to:
- Use exclusively Anthropic's Claude for summarization
- Generate generic, comprehensive summaries of blog posts without biasing toward specific interests
- Remove interest scoring from the AI prompt

**Updated Claude Prompt:**
```
SYSTEM:

You are a professional writer who specializes in technical content summarization, particularly for GIS and geospatial technology. You excel at distilling complex content into clear, objective summaries. Always think before you write, think out loud using the <THINKING> xml tags. 

The content you are reading will always be contained in the <POST> xml tags.

Return only your summary in <SUMMARY> xml tags.

USER:
Here is the blog post content:
<POST>
${blogContent}
</POST>

Provide a comprehensive, objective summary that captures the key technical information, announcements, features, and updates described in this post.
```

### 4.3 Embedding Generator

This new component will:
- Connect to the Voyage embedding service API
- Generate vector embeddings for each blog summary
- Handle API authentication and rate limiting
- Ensure consistent embedding model is used across all content

### 4.4 Data Store with Embeddings

Enhanced to:
- Store embedding vectors alongside blog data
- Record the embedding model version used
- Support efficient vector querying and similarity calculations

### 4.5 Query Processor

This new component will:
- Accept user queries about specific topics of interest
- Process and clean query text
- Generate embeddings for user queries using the same model as the stored data

### 4.6 Similarity Matcher

This new component will:
- Calculate similarity scores (cosine similarity) between query embeddings and blog summary embeddings
- Rank blog posts by relevance to the query
- Select the top N most relevant posts for summarization

### 4.7 Summary Generator

Updated to:
- Accept relevant blog posts based on similarity matching rather than interest scores
- Generate comprehensive summaries using Claude that focus on the specific topics from the user query
- Include references to the original blog posts

## 5. Implementation Details

### 5.1 File Structure

```
project/
├── main.py                  # Entry point for the application
├── blog_sources.py          # Handles loading and validating blog URLs
├── content_processor.py     # Fetches and processes blog content
├── claude_interface.py      # Interacts with Claude API for summarization
├── embedding_service.py     # Handles embedding generation with Voyage API
├── vector_store.py          # Data storage with vector operations
├── similarity_engine.py     # Calculates similarities between embeddings
├── query_processor.py       # Processes user topic queries
├── summary_generator.py     # Creates comprehensive summaries
├── config.py                # Configuration settings
├── utils.py                 # Utility functions
├── data/
│   ├── urls.txt             # Input file with blog URLs
│   └── blog_data.json       # Persistent storage of processed blogs with embeddings
└── output/
    └── summary_YYYY-MM-DD_TOPIC.md # Generated summary output with topic identifier
```

### 5.2 Key Functions and Classes

#### 5.2.1 Claude Interface Module

```python
class ClaudeInterface:
    def __init__(self, api_key, model="claude-3-opus-20240229"):
        self.api_key = api_key
        self.model = model
        self.client = Anthropic(api_key=api_key)

    def summarize_blog(self, blog_content):
        """Send blog content to Claude for summarization"""
        prompt = f"""
        SYSTEM:
        You are a professional writer who specializes in technical content summarization, particularly for GIS and geospatial technology. You excel at distilling complex content into clear, objective summaries. Always think before you write, think out loud using the <THINKING> xml tags. 

        The content you are reading will always be contained in the <POST> xml tags.

        Return only your summary in <SUMMARY> xml tags.

        USER:
        Here is the blog post content:
        <POST>
        {blog_content}
        </POST>

        Provide a comprehensive, objective summary that captures the key technical information, announcements, features, and updates described in this post.
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )

        return self._parse_claude_response(response.content[0].text)

    def generate_comprehensive_summary(self, relevant_posts, query_text):
        """Generate a comprehensive summary of multiple blog posts relevant to the query"""
        posts_content = "\n\n".join([
            f"URL: {post['url']}\nSummary: {post['summary']}"
            for post in relevant_posts
        ])

        prompt = f"""
        SYSTEM:
        You are a professional technical writer specializing in GIS and Esri technology. You write clear, engaging blog posts that highlight the most critical developments in the Esri ecosystem. Your audience is technical professionals who use Esri products. You work for Dymaptic, a small consulting firm specializing in GIS solutions. We always write blogs in the tone of your local GIS professional who is excited to help you out! Always think before you write; think out loud using the <THINKING> XML tags. Ensure you include a brief introduction about overall trends or themes you notice in the posts. Include a good hook at the beginning to grab the reader's attention. Always provide links to the posts you are summarizing.

        USER:
        Write a blog post summarizing these {len(relevant_posts)} most relevant Esri blog posts related to: "{query_text}". For each post, explain why it's significant and what readers should know about it. Start with a brief introduction about overall trends or themes you notice.

        Here are the posts to summarize:

        {posts_content}
        """

        response = self.client.messages.create(
            model=self.model,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )

        return response.content[0].text

    def _parse_claude_response(self, response):
        """Parse XML tags from Claude response to extract summary"""
        summary_match = re.search(r'<SUMMARY>(.*?)</SUMMARY>', response, re.DOTALL)
        if summary_match:
            return summary_match.group(1).strip()
        return response  # Fallback if no tags found
```

#### 5.2.2 Embedding Service Module

```python
class EmbeddingService:
    def __init__(self, api_key, model="voyage-01"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.voyageai.com/v1/embeddings"

    def generate_embedding(self, text):
        """Generate embedding vector for the given text"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "input": text,
            "input_type": "document"
        }

        response = requests.post(self.base_url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            return result["embeddings"][0], self.model
        else:
            raise Exception(f"Error generating embedding: {response.text}")

    def batch_generate_embeddings(self, texts, batch_size=50):
        """Generate embeddings for multiple texts in batches"""
        results = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "input": batch,
                "input_type": "document"
            }

            response = requests.post(self.base_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                results.extend(result["embeddings"])
            else:
                raise Exception(f"Error generating batch embeddings: {response.text}")

        return results

    def get_model_info(self):
        """Return information about the current embedding model"""
        return {
            "model": self.model,
            "dimensions": 1024  # Typical for Voyage models, adjust as needed
        }
```

#### 5.2.3 Content Processor Module

```python
class BlogContentProcessor:
    def __init__(self, claude_interface, embedding_service):
        self.claude_interface = claude_interface
        self.embedding_service = embedding_service

    def fetch_content(self, url):
        """Fetch blog content from a given URL"""
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception(f"Failed to fetch content from {url}")

    def extract_text(self, html_content):
        """Extract text content from HTML"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # Extract main content (adjust selectors based on blog structure)
        main_content = soup.find('article') or soup.find('main') or soup.find('div', class_='content')

        if main_content:
            text = main_content.get_text(separator='\n')
        else:
            text = soup.get_text(separator='\n')

        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        text = '\n'.join(line for line in lines if line)

        return text

    def extract_metadata(self, html_content):
        """Extract title, date, and other metadata"""
        soup = BeautifulSoup(html_content, 'html.parser')

        # Extract title
        title = None
        title_tag = soup.find('title')
        if title_tag:
            title = title_tag.text.strip()

        # Extract date (adjust selectors based on blog structure)
        date = None
        date_tag = soup.find('time') or soup.find('span', class_='date')
        if date_tag:
            date_str = date_tag.get('datetime') or date_tag.text
            try:
                # Attempt to parse the date
                date = parser.parse(date_str).isoformat()
            except:
                date = date_str

        return {
            "title": title,
            "date": date
        }

    def process_blog(self, url):
        """Process a blog post completely, returning structured data with summary and embedding"""
        html_content = self.fetch_content(url)
        text_content = self.extract_text(html_content)
        metadata = self.extract_metadata(html_content)

        # Generate summary using Claude
        summary = self.claude_interface.summarize_blog(text_content)

        # Generate embedding for the summary
        embedding, model = self.embedding_service.generate_embedding(summary)

        return {
            "url": url,
            "title": metadata["title"],
            "date": metadata["date"],
            "content": text_content[:5000],  # Store truncated content to save space
            "summary": summary,
            "embedding": embedding,
            "embeddingModel": model,
            "processedDate": datetime.now().isoformat()
        }
```

#### 5.2.4 Vector Store Module

```python
class VectorStore:
    def __init__(self, storage_file):
        self.storage_file = storage_file
        self._ensure_storage_exists()

    def _ensure_storage_exists(self):
        """Create storage file if it doesn't exist"""
        if not os.path.exists(self.storage_file):
            with open(self.storage_file, 'w') as f:
                json.dump([], f)

    def save_blog_data(self, blog_data):
        """Save processed blog data with embeddings to storage"""
        current_data = self.load_all_data()

        # Check if URL already exists and update if it does
        url_exists = False
        for i, post in enumerate(current_data):
            if post["url"] == blog_data["url"]:
                current_data[i] = blog_data
                url_exists = True
                break

        if not url_exists:
            current_data.append(blog_data)

        with open(self.storage_file, 'w') as f:
            json.dump(current_data, f, indent=2)

    def load_all_data(self):
        """Load all stored blog data including embeddings"""
        try:
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def is_url_processed(self, url):
        """Check if a URL has already been processed"""
        current_data = self.load_all_data()
        return any(post["url"] == url for post in current_data)

    def get_embeddings_as_matrix(self):
        """Return a matrix of all embeddings for efficient similarity calculation"""
        data = self.load_all_data()
        embeddings = [post["embedding"] for post in data if "embedding" in post]
        return np.array(embeddings)
```

#### 5.2.5 Query Processor Module

```python
class QueryProcessor:
    def __init__(self, embedding_service):
        self.embedding_service = embedding_service

    def process_query(self, query_text):
        """Process user query and generate embedding"""
        clean_query = self.clean_query(query_text)
        embedding, model = self.embedding_service.generate_embedding(clean_query)

        return {
            "original_query": query_text,
            "clean_query": clean_query,
            "embedding": embedding,
            "model": model
        }

    def clean_query(self, query_text):
        """Clean and normalize query text"""
        # Simple cleaning - remove extra whitespace
        query = re.sub(r'\s+', ' ', query_text.strip())
        return query
```

#### 5.2.6 Similarity Engine Module

```python
class SimilarityEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store

    def find_similar_posts(self, query_embedding, top_n=10):
        """Find the top N most similar posts to the query embedding"""
        # Load all blog data
        all_posts = self.vector_store.load_all_data()

        # Calculate similarities for posts that have embeddings
        similarities = []
        for i, post in enumerate(all_posts):
            if "embedding" in post:
                similarity = self.calculate_cosine_similarity(
                    query_embedding, 
                    post["embedding"]
                )
                similarities.append((i, similarity))

        # Sort by similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Get top N posts
        top_indices = [idx for idx, _ in similarities[:top_n]]
        top_posts = [all_posts[idx] for idx in top_indices]

        # Add similarity scores to posts
        for i, (idx, score) in enumerate(similarities[:top_n]):
            top_posts[i]["similarity_score"] = score

        return top_posts

    def calculate_cosine_similarity(self, query_embedding, post_embedding):
        """Calculate cosine similarity between query and post embedding"""
        # Convert to numpy arrays if not already
        query_vec = np.array(query_embedding)
        post_vec = np.array(post_embedding)

        # Calculate cosine similarity
        dot_product = np.dot(query_vec, post_vec)
        norm_query = np.linalg.norm(query_vec)
        norm_post = np.linalg.norm(post_vec)

        similarity = dot_product / (norm_query * norm_post)
        return similarity
```

#### 5.2.7 Summary Generator Module

```python
class SummaryGenerator:
    def __init__(self, claude_interface):
        self.claude_interface = claude_interface

    def generate_summary(self, relevant_posts, query_text):
        """Generate a comprehensive summary focused on the query topic"""
        summary = self.claude_interface.generate_comprehensive_summary(relevant_posts, query_text)
        return summary

    def save_summary(self, summary, query_topic, output_file=None):
        """Save the generated summary to a file with topic identifier"""
        if output_file is None:
            # Create a filename based on date and simplified topic
            date_str = datetime.now().strftime("%Y-%m-%d")
            topic_slug = re.sub(r'[^\w\s-]', '', query_topic.lower())
            topic_slug = re.sub(r'[\s-]+', '-', topic_slug).strip('-')
            output_file = f"output/summary_{date_str}_{topic_slug[:30]}.md"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w') as f:
            f.write(summary)

        return output_file
```

#### 5.2.8 Main Application Module

```python
class BlogSummarizer:
    def __init__(self, config):
        # Initialize components
        self.claude = ClaudeInterface(api_key=config["claude_api_key"])
        self.embedding_service = EmbeddingService(api_key=config["voyage_api_key"])
        self.content_processor = BlogContentProcessor(self.claude, self.embedding_service)
        self.vector_store = VectorStore(config["storage_file"])
        self.query_processor = QueryProcessor(self.embedding_service)
        self.similarity_engine = SimilarityEngine(self.vector_store)
        self.summary_generator = SummaryGenerator(self.claude)

    def process_blogs(self, url_file):
        """Process all blogs from the URL file"""
        with open(url_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip()]

        for url in urls:
            try:
                if not self.vector_store.is_url_processed(url):
                    print(f"Processing {url}")
                    blog_data = self.content_processor.process_blog(url)
                    self.vector_store.save_blog_data(blog_data)
                else:
                    print(f"Skipping already processed {url}")
            except Exception as e:
                print(f"Error processing {url}: {str(e)}")

    def generate_topic_summary(self, query_text, top_n=10):
        """Generate a summary of blogs relevant to the given topic"""
        # Process the query and get its embedding
        query_data = self.query_processor.process_query(query_text)

        # Find similar posts
        relevant_posts = self.similarity_engine.find_similar_posts(
            query_data["embedding"], 
            top_n=top_n
        )

        # Generate comprehensive summary
        summary = self.summary_generator.generate_summary(relevant_posts, query_text)

        # Save summary to file
        output_file = self.summary_generator.save_summary(summary, query_text)

        return {
            "summary": summary,
            "output_file": output_file,
            "relevant_posts": relevant_posts
        }
```

## 6. Workflow

### 6.1 Processing Workflow

1. The application reads blog URLs from the input file
2. For each URL that hasn't been processed yet:
   a. Fetch the blog content
   b. Extract text and metadata
   c. Send to Claude for generic summarization
   d. Generate embedding for the summary using Voyage API
   e. Store the processed data with embeddings

### 6.2 Query Workflow

1. User provides a topic query text describing their interests
2. The query processor generates an embedding for the query
3. The similarity engine compares the query embedding with all stored summary embeddings
4. The top N most similar blog posts are selected
5. The summary generator creates a comprehensive summary focused on the query topic using Claude
6. The summary is saved to an output file with a topic identifier

## 7. Error Handling and Logging

- Implement error handling for network requests and API calls
- Add retry mechanisms for embedding generation
- Log all processing activities with appropriate detail levels
- Handle embedding API rate limits

## 8. Command Line Interface

```python
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI-powered blog post summarizer")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Process blogs command
    process_parser = subparsers.add_parser("process", help="Process blogs from URL file")
    process_parser.add_argument("url_file", help="File containing blog URLs")

    # Generate summary command
    summary_parser = subparsers.add_parser("summarize", help="Generate topic summary")
    summary_parser.add_argument("query", help="Topic query for finding relevant posts")
    summary_parser.add_argument("--top", type=int, default=10, help="Number of top posts to include")

    args = parser.parse_args()

    # Load configuration
    config = {
        "claude_api_key": os.environ.get("CLAUDE_API_KEY"),
        "voyage_api_key": os.environ.get("VOYAGE_API_KEY"),
        "storage_file": "data/blog_data.json"
    }

    summarizer = BlogSummarizer(config)

    if args.command == "process":
        summarizer.process_blogs(args.url_file)
    elif args.command == "summarize":
        result = summarizer.generate_topic_summary(args.query, top_n=args.top)
        print(f"Summary generated and saved to {result['output_file']}")
    else:
        parser.print_help()
```

## 9. Configuration

Store API keys as environment variables:
```
export CLAUDE_API_KEY=your_claude_api_key
export VOYAGE_API_KEY=your_voyage_api_key
```

## 10. Future Enhancements

- Support for chunking blog posts into smaller segments for more granular embeddings
- Hybrid retrieval combining keyword and semantic search
- User feedback mechanisms to improve relevance
- Visualization of embedding space to explore content relationships
- Web interface for querying and viewing summaries
- Scheduled updates to process new blog posts automatically

This updated design document provides a comprehensive blueprint for implementing an AI-powered blog summarizer with embedding-based similarity matching, exclusively using Anthropic's Claude for summarization and Voyage for embeddings.