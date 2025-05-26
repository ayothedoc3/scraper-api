"""
Reddit post analysis functionality.
"""

import logging
import os
from typing import Dict

from business_validator.models import RedditPostAnalysis

# Use the same LLM instance as in keyword_generator
try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.output_parsers import PydanticOutputParser
    from langchain_core.prompts import PromptTemplate
    
    # Get API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if google_api_key and google_api_key != "your_google_api_key_here":
        llm_instance = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=google_api_key,
            temperature=0.7
        )
    else:
        llm_instance = None
        
except Exception as e:
    llm_instance = None
    logging.warning(f"Could not initialize Google Gemini LLM in reddit_analyzer: {e}")

def analyze_reddit_post(post: dict, business_idea: str) -> RedditPostAnalysis:
    """Analyze a single Reddit post for business validation.
    
    Args:
        post: Dictionary containing post information
        business_idea: The business idea being validated
        
    Returns:
        RedditPostAnalysis object with analysis results
    """
    logging.info(f"Analyzing Reddit post: {post['title'][:50]}...")
    
    if llm_instance is None:
        logging.warning("LLM not available, returning default analysis")
        return RedditPostAnalysis(
            relevant=False,
            pain_points=["LLM not available for analysis"],
            solutions_mentioned=["LLM not available for analysis"],
            market_signals=["LLM not available for analysis"],
            sentiment="neutral",
            engagement_score=0,
            subreddit_context=""
        )
    
    try:
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=RedditPostAnalysis)
        
        # Create the prompt template
        prompt = PromptTemplate(
            template="""Business Idea: "{business_idea}"

Reddit Post:
Title: {title}
Subreddit: {subreddit}
Score: {score}
Comments: {num_comments}
Content: {selftext}

Analyze this Reddit post for business validation signals:

1. Is this post relevant to validating the business idea? (true/false)
2. What pain points are mentioned or implied?
3. What solutions are discussed or mentioned?
4. What market signals does this show? (demand, competition, trends, etc.)
5. What's the overall sentiment? (positive/negative/neutral)
6. Rate the engagement score 1-10 based on score and comments relative to typical Reddit posts
7. What context does the subreddit provide about the target audience?

Focus on extracting actionable insights for business validation.

{format_instructions}""",
            input_variables=["business_idea", "title", "subreddit", "score", "num_comments", "selftext"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create the chain
        chain = prompt | llm_instance | parser
        
        # Analyze the post
        analysis = chain.invoke({
            "business_idea": business_idea,
            "title": post['title'],
            "subreddit": post.get('subreddit', 'unknown'),
            "score": post.get('score', 0),
            "num_comments": post.get('num_comments', 0),
            "selftext": post.get('selftext', '')[:500]  # Limit content length
        })
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing Reddit post: {e}")
        # Return a default analysis if generation fails
        return RedditPostAnalysis(
            relevant=False,
            pain_points=["Analysis failed"],
            solutions_mentioned=["Analysis failed"],
            market_signals=["Analysis failed"],
            sentiment="neutral",
            engagement_score=0,
            subreddit_context="Analysis failed"
        )
