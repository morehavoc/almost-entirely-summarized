import re
from utils import logger

class QueryProcessor:
    """Process user queries and generate embeddings for them"""

    def __init__(self, embedding_service):
        self.embedding_service = embedding_service

    def process_query(self, query_text):
        """Process user query and generate embedding"""
        try:
            logger.info(f"Processing query: {query_text}")
            clean_query = self.clean_query(query_text)
            embedding, model = self.embedding_service.generate_embedding(clean_query)

            return {
                "original_query": query_text,
                "clean_query": clean_query,
                "embedding": embedding,
                "model": model
            }
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            raise

    def clean_query(self, query_text):
        """Clean and normalize query text"""
        # Simple cleaning - remove extra whitespace
        query = re.sub(r'\s+', ' ', query_text.strip())
        return query
