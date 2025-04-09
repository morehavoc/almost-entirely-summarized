import anthropic
import re
import json
from utils import logger

class AIInterface:
    def __init__(self, api_key, model="claude-3-opus-20240229"):
        self.model = model
        self.client = anthropic.Anthropic(api_key=api_key)

    def summarize_blog(self, blog_content, title, url):
        """Send blog content to Claude for summarization and scoring"""
        try:
            prompt = f"""
            You are an expert summarizer for technical blog posts. I'll provide you with a blog post from Esri about GIS and mapping technology. 
            Your task is to:

            1. Create a concise but informative summary (150-250 words) that captures the key points
            2. Assign an interest score from 1-10 based on these criteria:
               - Technical innovations and new features (high value)
               - Developer tools and APIs (high value)
               - Platform architecture changes (high value)
               - Performance improvements (medium value)
               - Security updates (medium value)
               - ArcGIS Indoors (medium value)
               - Web App Builder to Experience Builder (medium value)
               - Digital Twins, AI Assistants in AGOL (high value)
               - Application End-of-life announcements (high value)
               - New product announcements (high value)
               - Bug fixes and patches (low value)

            Here's the blog post:
            Title: {title}
            URL: {url}
            Content: {blog_content[:100000]}  # Truncate if too long

            Return your response in the following format:
            <summary>
            Your concise summary here
            </summary>
            <score>X</score>
            <rationale>
            Brief explanation of why you assigned this interest score
            </rationale>
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
            return {"summary": "Error generating summary", "interestScore": 1, "rationale": str(e)}

    def generate_comprehensive_summary(self, top_posts):
        """Generate a comprehensive summary of multiple blog posts"""
        try:
            posts_json = json.dumps([{
                'title': post.get('title', 'No Title'),
                'url': post.get('url', ''),
                'summary': post.get('summary', ''),
                'interestScore': post.get('interestScore', 0),
                'date': post.get('date', '')
            } for post in top_posts], indent=2)

            prompt_standard = f"""
            You are an expert tech content curator specializing in GIS technology. I'll provide you with information about the most interesting recent Esri blog posts.

            Your task is to create a comprehensive summary titled "Recent Esri Blog Highlights" that synthesizes the key information from these posts.

            Structure your response as follows:

            1. Introduction (1 paragraph)
            2. Key themes and trends observed across these posts (1-2 paragraphs)
            3. Highlights from each post, organized by theme rather than by individual post
            4. Conclusion with the most significant developments mentioned

            Format the output as a professional Markdown document with:
            - Clear section headings
            - Proper links to the original articles when mentioning them
            - Bullet points where appropriate
            - Emphasis on the most important points

            Here are the blog posts:
            {posts_json}

            Create a coherent, valuable summary that would be useful for GIS professionals and developers who want to stay updated with Esri technology.
            """

            prompt = f"""
You're a whip-smart tech content curator who can transform dull GIS technology updates into a cosmic journey of wit and wonder with an unusual affliction that causes you to see the universe as Douglas Adams might. When given information about recent Esri blog posts, you'll craft a summary that would make Douglas Adams proud - full of unexpected metaphors, existential asides, and that distinctive blend of absurdist humor that makes readers snort coffee through their noses.

            Your response should follow this structure:

            1. An introduction that presents GIS technology as if it were a peculiar alien artifact discovered in the vast improbability of space
            2. Key themes across the posts, explained as if they were entries in the Hitchhiker's Guide to the Galaxy
            3. Post highlights organized by theme, each with at least one preposterous comparison or metaphor
            4. A conclusion that ties everything together while suggesting the universe is simultaneously meaningless and profound
            
            Format requirements:

            - Section headings that sound like chapters from a cosmic travel guide
            - Links to original articles (possibly described as "sub-etha transmissions") (be sure to include the links directly in the result)
            - Bullet points described as "mostly harmless" facts
            - Important concepts emphasized with the narrative gravity of impending planetary destruction
            - It should be outputed in Markdown format
            
            Remember to maintain Adams' distinctive voice throughout - sardonic, philosophical, and delightfully meandering with perfectly timed punchlines and absurd observations about the nature of technology and existence.

            Here are the blog posts:
            {posts_json}
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
        """Parse XML tags from AI response to extract summary and score"""
        try:
            summary_match = re.search(r'<summary>(.*?)</summary>', response, re.DOTALL)
            score_match = re.search(r'<score>(\d+)</score>', response)
            rationale_match = re.search(r'<rationale>(.*?)</rationale>', response, re.DOTALL)

            summary = summary_match.group(1).strip() if summary_match else "No summary provided"
            score = int(score_match.group(1)) if score_match else 1
            rationale = rationale_match.group(1).strip() if rationale_match else "No rationale provided"

            return {
                "summary": summary,
                "interestScore": score,
                "rationale": rationale
            }
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return {
                "summary": "Error parsing summary",
                "interestScore": 1,
                "rationale": f"Error: {str(e)}"
            }
