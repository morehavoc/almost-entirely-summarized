import numpy as np
from utils import logger

class SimilarityEngine:
    """Engine to calculate similarity between embeddings and find relevant posts"""

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def find_similar_posts(self, query_embedding, top_n=10):
        """Find the top N most similar posts to the query embedding"""
        try:
            # Load all blog data
            all_posts = self.vector_store.load_all_data()

            if not all_posts:
                logger.warning("No posts found in vector store")
                return []

            # Calculate similarities for posts that have embeddings
            similarities = []
            for i, post in enumerate(all_posts):
                if "embedding" in post:
                    similarity = self.calculate_cosine_similarity(
                        query_embedding, 
                        post["embedding"]
                    )
                    similarities.append((i, similarity))

            if not similarities:
                logger.warning("No posts with embeddings found")
                return []

            # Sort by similarity (highest first)
            similarities.sort(key=lambda x: x[1], reverse=True)

            # Get top N posts
            top_indices = [idx for idx, _ in similarities[:top_n]]
            top_posts = [all_posts[idx] for idx in top_indices]

            # Add similarity scores to posts
            for i, (idx, score) in enumerate(similarities[:top_n]):
                top_posts[i]["similarity_score"] = score

            logger.info(f"Found {len(top_posts)} relevant posts")
            return top_posts
        except Exception as e:
            logger.error(f"Error finding similar posts: {str(e)}")
            return []

    def calculate_cosine_similarity(self, query_embedding, post_embedding):
        """Calculate cosine similarity between query and post embedding"""
        try:
            # Convert to numpy arrays if not already
            query_vec = np.array(query_embedding)
            post_vec = np.array(post_embedding)

            # Calculate cosine similarity
            dot_product = np.dot(query_vec, post_vec)
            norm_query = np.linalg.norm(query_vec)
            norm_post = np.linalg.norm(post_vec)

            similarity = dot_product / (norm_query * norm_post)
            return similarity
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
