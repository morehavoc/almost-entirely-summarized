# embedding_service.py
import requests
from utils import logger

class EmbeddingService:
    """Service to generate embeddings from text using Voyage AI"""

    def __init__(self, api_key, model="voyage-01"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.voyageai.com/v1/embeddings"

    def generate_embedding(self, text):
        """Generate embedding vector for the given text"""
        try:
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }

            payload = {
                "model": self.model,
                "input": text,
                "input_type": "document"
            }

            logger.info(f"Generating embedding using model {self.model}")
            response = requests.post(self.base_url, headers=headers, json=payload)

            if response.status_code == 200:
                result = response.json()
                logger.info("Successfully generated embedding")

                # Debug the API response structure
                logger.info(f"Response keys: {result.keys()}")

                # Check different possible response formats
                if "data" in result and len(result["data"]) > 0 and "embedding" in result["data"][0]:
                    # Format: {"data": [{"embedding": [...]}]}
                    return result["data"][0]["embedding"], self.model
                elif "embedding" in result:
                    # Format: {"embedding": [...]}
                    return result["embedding"], self.model
                elif "embeddings" in result:
                    # Format: {"embeddings": [[...]]}
                    if isinstance(result["embeddings"], list):
                        if len(result["embeddings"]) > 0:
                            # If embeddings is a list of embeddings
                            return result["embeddings"][0], self.model
                        else:
                            raise Exception("Empty embeddings list in response")
                else:
                    # Log the full response for debugging
                    logger.error(f"Unexpected response format: {result}")
                    raise Exception(f"Unexpected response format: {list(result.keys())}")
            else:
                logger.error(f"Error generating embedding: {response.text}")
                raise Exception(f"Error generating embedding: {response.text}")
        except Exception as e:
            logger.error(f"Exception generating embedding: {str(e)}")
            # Return a default embedding as fallback (all zeros)
            # This is not ideal but allows the process to continue
            return [0.0] * 1024, self.model  # Voyage models typically use 1024 dimensions
