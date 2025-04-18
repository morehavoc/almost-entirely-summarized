import os
import argparse
from blog_sources import BlogSourceHandler
from content_processor import BlogContentProcessor
from ai_interface import AIInterface
from embedding_service import EmbeddingService
from data_store import DataStore
from query_processor import QueryProcessor
from similarity_engine import SimilarityEngine
from summary_generator import SummaryGenerator
import config
from utils import logger

def process_blogs(force_refresh=False):
    """Process blogs from the URL file"""
    logger.info("Starting blog processing")

    # Initialize components
    ai_interface = AIInterface(config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL)
    embedding_service = EmbeddingService(config.VOYAGE_API_KEY, config.VOYAGE_MODEL)
    data_store = DataStore(config.STORAGE_FILE)
    blog_source = BlogSourceHandler(config.URL_FILE)
    content_processor = BlogContentProcessor(ai_interface, embedding_service)

    # Load URLs
    urls = blog_source.load_urls()
    if not urls:
        logger.warning(f"No URLs found in {config.URL_FILE}. Please add URLs to the file.")
        return False

    processed_count = 0

    # Process each URL
    for url in urls:
        # Skip if already processed (unless force refresh is on)
        if data_store.is_url_processed(url) and not force_refresh:
            logger.info(f"Skipping already processed URL: {url}")
            continue

        # Process the blog
        try:
            blog_data = content_processor.process_blog(url)
            if blog_data:
                data_store.save_blog_data(blog_data)
                processed_count += 1
        except Exception as e:
            logger.error(f"Error processing blog {url}: {str(e)}")

    logger.info(f"Processed {processed_count} blog posts")
    return processed_count > 0

def generate_topic_summary(query_text, top_n=10):
    """Generate a summary of blogs relevant to the given topic"""
    logger.info(f"Generating topic summary for query: {query_text}")

    # Initialize components
    ai_interface = AIInterface(config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL)
    embedding_service = EmbeddingService(config.VOYAGE_API_KEY, config.VOYAGE_MODEL)
    data_store = DataStore(config.STORAGE_FILE)
    query_processor = QueryProcessor(embedding_service)
    similarity_engine = SimilarityEngine(data_store)
    summary_generator = SummaryGenerator(ai_interface, config.OUTPUT_DIR)

    try:
        # Process the query and get its embedding
        query_data = query_processor.process_query(query_text)

        # Find similar posts
        relevant_posts = similarity_engine.find_similar_posts(
            query_data["embedding"], 
            top_n=top_n
        )

        if not relevant_posts:
            logger.warning("No relevant posts found for the query")
            return {"error": "No relevant posts found for the query"}

        # Generate comprehensive summary
        summary = summary_generator.generate_summary(relevant_posts, query_text)

        # Save summary to file
        output_file = summary_generator.save_summary(summary, query_text)

        if output_file:
            return {
                "success": True,
                "output_file": output_file,
                "summary": summary,
                "relevant_posts": [
                    {"url": post.get("url"), "title": post.get("title"), "similarity": post.get("similarity_score")} 
                    for post in relevant_posts
                ]
            }
        else:
            return {"error": "Failed to save summary"}

    except Exception as e:
        logger.error(f"Error generating topic summary: {str(e)}")
        return {"error": str(e)}

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='AI Blog Post Summarizer with Embeddings')
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Process blogs command
    process_parser = subparsers.add_parser("process", help="Process blogs from URL file")
    process_parser.add_argument("--force-refresh", action="store_true",
                        help="Process all URLs even if already processed")

    # Generate summary command
    summary_parser = subparsers.add_parser("summarize", help="Generate topic summary")
    summary_parser.add_argument("query", help="Topic query for finding relevant posts")
    summary_parser.add_argument("--top", type=int, default=config.MAX_POSTS_IN_SUMMARY, 
                         help="Number of top posts to include")

    args = parser.parse_args()

    # Check for API keys
    if not config.ANTHROPIC_API_KEY:
        logger.error("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment or .env file.")
        return

    if not config.VOYAGE_API_KEY:
        logger.error("Voyage API key not found. Please set VOYAGE_API_KEY in your environment or .env file.")
        return

    # Execute command
    if args.command == "process":
        process_blogs(args.force_refresh)
    elif args.command == "summarize":
        result = generate_topic_summary(args.query, top_n=args.top)

        if "success" in result:
            print(f"\nSummary generated successfully!\nOutput file: {result['output_file']}")

            print("\nTop relevant posts:")
            for i, post in enumerate(result["relevant_posts"][:5], 1):
                print(f"{i}. {post['title']} (Similarity: {post['similarity']:.4f})")
                print(f"   {post['url']}")
        else:
            print(f"Error: {result.get('error', 'Unknown error')}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
