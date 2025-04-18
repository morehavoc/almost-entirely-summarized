import anthropic
import re
from utils import logger

class AIInterface:
    def __init__(self, api_key, model="claude-3-opus-20240229"):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def summarize_blog(self, blog_content, title, url):
        """Send blog content to Claude for generic summarization"""
        try:
            prompt = f"""
            SYSTEM:
            You are a professional writer who specializes in technical content summarization, particularly for GIS and geospatial technology. You excel at distilling complex content into clear, objective summaries. Always think before you write, think out loud using the <THINKING> xml tags. 

            The content you are reading will always be contained in the <POST> xml tags.

            Return only your summary in <SUMMARY> xml tags.

            USER:
            Here is the blog post content:
            <POST>
            Title: {title}
            URL: {url}

            {blog_content[:100000]}
            </POST>

            Provide a comprehensive, objective summary that captures the key technical information, announcements, features, and updates described in this post.
            """

            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.0,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return self._parse_ai_response(response.content[0].text)
        except Exception as e:
            logger.error(f"Error in AI summarization: {e}")
            return "Error generating summary: " + str(e)

    def generate_comprehensive_summary(self, relevant_posts, query_text):
        """Generate a comprehensive summary of multiple blog posts relevant to the query"""
        try:
            posts_content = "\n\n".join([
                f"URL: {post.get('url', 'No URL')}\n"
                f"Title: {post.get('title', 'No Title')}\n"
                f"Date: {post.get('date', 'No Date')}\n"
                f"Similarity: {post.get('similarity_score', 0):.4f}\n"
                f"Summary: {post.get('summary', 'No Summary')}"
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
                max_tokens=2000,
                temperature=0.2,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text
        except Exception as e:
            logger.error(f"Error generating comprehensive summary: {e}")
            return f"Error generating comprehensive summary: {e}"

    def _parse_ai_response(self, response):
        """Parse XML tags from AI response to extract summary"""
        try:
            summary_match = re.search(r'<SUMMARY>(.*?)</SUMMARY>', response, re.DOTALL)
            if summary_match:
                return summary_match.group(1).strip()
            return response  # Fallback if no tags found
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return response
