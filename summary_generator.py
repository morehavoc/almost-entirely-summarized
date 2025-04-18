import os
import re
from datetime import datetime
from utils import logger, generate_output_filename

class SummaryGenerator:
    def __init__(self, ai_interface, output_dir):
        self.ai_interface = ai_interface
        self.output_dir = output_dir

    def generate_summary(self, relevant_posts, query_text):
        """Generate a comprehensive summary focused on the query topic"""
        logger.info(f"Generating comprehensive summary for query: {query_text}")

        if not relevant_posts:
            logger.warning("No relevant posts provided for summary generation")
            return "No relevant posts found for this query."

        logger.info(f"Generating summary from {len(relevant_posts)} relevant posts")
        summary = self.ai_interface.generate_comprehensive_summary(relevant_posts, query_text)

        return summary

    def save_summary(self, summary, query_topic, output_file=None):
        """Save the generated summary to a file with topic identifier"""
        if output_file is None:
            # Create a filename based on date and simplified topic
            date_str = datetime.now().strftime("%Y-%m-%d")
            topic_slug = re.sub(r'[^\w\s-]', '', query_topic.lower())
            topic_slug = re.sub(r'[\s-]+', '-', topic_slug).strip('-')
            output_file = os.path.join(self.output_dir, f"summary_{date_str}_{topic_slug[:30]}.md")

        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(summary)

            logger.info(f"Summary saved to {output_file}")
            return output_file
        except Exception as e:
            logger.error(f"Error saving summary: {e}")
            return None
