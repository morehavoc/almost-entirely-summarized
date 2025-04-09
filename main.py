import os
import argparse
from blog_sources import BlogSourceHandler
from content_processor import BlogContentProcessor
from ai_interface import AIInterface
from data_store import DataStore
from summary_generator import SummaryGenerator
import config
from utils import logger

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='AI Blog Post Summarizer')
    parser.add_argument('--limit', type=int, default=config.MAX_POSTS_IN_SUMMARY,
                        help='Maximum number of posts to include in summary')
    parser.add_argument('--force-refresh', action='store_true',
                        help='Process all URLs even if already processed')
    args = parser.parse_args()

    # Initialize components
    try:
        logger.info("Initializing application components")

        if not config.ANTHROPIC_API_KEY:
            logger.error("Anthropic API key not found. Please set ANTHROPIC_API_KEY in your environment or .env file.")
            return

        ai_interface = AIInterface(config.ANTHROPIC_API_KEY, config.ANTHROPIC_MODEL)
        data_store = DataStore(config.STORAGE_FILE)
        blog_source = BlogSourceHandler(config.URL_FILE)
        content_processor = BlogContentProcessor(ai_interface)
        summary_generator = SummaryGenerator(ai_interface, data_store, config.OUTPUT_DIR)

        # Load URLs
        urls = blog_source.load_urls()
        if not urls:
            logger.warning(f"No URLs found in {config.URL_FILE}. Please add URLs to the file.")
            return

        # Process each URL
        for url in urls:
            # Skip if already processed (unless force refresh is on)
            if data_store.is_url_processed(url) and not args.force_refresh:
                logger.info(f"Skipping already processed URL: {url}")
                continue

            # Process the blog
            blog_data = content_processor.process_blog(url)
            if blog_data:
                data_store.save_blog_data(blog_data)

        # Generate and save comprehensive summary
        logger.info("Generating comprehensive summary")
        summary = summary_generator.generate_summary(args.limit)
        output_file = summary_generator.save_summary(summary)

        if output_file:
            logger.info(f"Summary generated successfully and saved to {output_file}")
            print(f"\nSummary generated successfully!\nOutput file: {output_file}")
        else:
            logger.error("Failed to save summary")

    except Exception as e:
        logger.error(f"An error occurred in the main process: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
