import os
from datetime import datetime
from utils import logger, generate_output_filename

class SummaryGenerator:
    def __init__(self, ai_interface, data_store, output_dir):
        self.ai_interface = ai_interface
        self.data_store = data_store
        self.output_dir = output_dir

    def generate_summary(self, limit=10):
        """Generate a comprehensive summary of top posts"""
        logger.info(f"Generating comprehensive summary of top {limit} posts")

        top_posts = self.data_store.get_top_posts(limit)

        if not top_posts:
            logger.warning("No posts found for summary generation")
            return "No posts available for summary generation."

        logger.info(f"Found {len(top_posts)} posts for summary generation")
        comprehensive_summary = self.ai_interface.generate_comprehensive_summary(top_posts)

        return comprehensive_summary

    def save_summary(self, summary, output_file=None):
        """Save the generated summary to a file"""
        if not output_file:
            output_file = os.path.join(self.output_dir, generate_output_filename())

        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)

            logger.info(f"Summary saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return None
