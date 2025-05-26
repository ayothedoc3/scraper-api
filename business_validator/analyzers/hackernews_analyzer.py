"""
HackerNews post analysis functionality.
"""

import logging
import os
from typing import Dict

from business_validator.models import HNPostAnalysis

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
    logging.warning(f"Could not initialize Google Gemini LLM in hackernews_analyzer: {e}")

def analyze_hn_post(post: dict, business_idea: str) -> HNPostAnalysis:
    """Analyze a single HackerNews post for business validation.
    
    Args:
        post: Dictionary containing post information
        business_idea: The business idea being validated
        
    Returns:
        HNPostAnalysis object with analysis results
    """
    logging.info(f"Analyzing HN post: {post['title'][:50]}...")
    
    if llm_instance is None:
        logging.warning("LLM not available, returning default analysis")
        return HNPostAnalysis(
            relevant=False,
            pain_points=["LLM not available for analysis"],
            solutions_mentioned=["LLM not available for analysis"],
            market_signals=["LLM not available for analysis"],
            sentiment="neutral",
            engagement_score=0
        )
    
    try:
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=HNPostAnalysis)
        
        # Create the prompt template
        prompt = PromptTemplate(
            template="""Business Idea: "{business_idea}"

HackerNews Post:
Title: {title}
Points: {points}
Comments: {comments}
URL: {url}

Analyze this post for business validation signals:

1. Is this post relevant to validating the business idea? (true/false)
2. What pain points are mentioned or implied?
3. What solutions are discussed or mentioned?
4. What market signals does this show? (demand, competition, trends, etc.)
5. What's the overall sentiment? (positive/negative/neutral)
6. Rate the engagement score 1-10 based on points and comments relative to typical HN posts

Focus on extracting actionable insights for business validation.

{format_instructions}""",
            input_variables=["business_idea", "title", "points", "comments", "url"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create the chain
        chain = prompt | llm_instance | parser
        
        # Analyze the post
        analysis = chain.invoke({
            "business_idea": business_idea,
            "title": post['title'],
            "points": post['points'],
            "comments": post['comments'],
            "url": post['url']
        })
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error analyzing HN post: {e}")
        # Return a default analysis if generation fails
        return HNPostAnalysis(
            relevant=False,
            pain_points=["Analysis failed"],
            solutions_mentioned=["Analysis failed"],
            market_signals=["Analysis failed"],
            sentiment="neutral",
            engagement_score=0
        )
