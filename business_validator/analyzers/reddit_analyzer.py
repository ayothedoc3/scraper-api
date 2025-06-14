"""
Reddit post analysis functionality.
"""

import logging
import os
import json
from typing import Dict, List

from business_validator.models import RedditPostAnalysis

def analyze_reddit_post(post: dict, comments: List[dict], business_idea: str) -> RedditPostAnalysis:
    """Analyze a single Reddit post for business validation.
    
    Args:
        post: Dictionary containing post information
        comments: List of comment dictionaries
        business_idea: The business idea being validated
        
    Returns:
        RedditPostAnalysis object with analysis results
    """
    logging.info(f"Analyzing Reddit post: {post['title'][:50]}...")
    
    # Get API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key or google_api_key == "your_google_api_key_here":
        logging.warning("Google API key not found, returning default analysis")
        return RedditPostAnalysis(
            relevant=False,
            pain_points=["API key not available"],
            solutions_mentioned=["API key not available"],
            market_signals=["API key not available"],
            sentiment="neutral",
            engagement_score=0,
            subreddit_context="API key not available"
        )
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare comments text
        comments_text = ""
        if comments:
            top_comments = comments[:5]  # Limit to top 5 comments
            comments_text = "\n".join([f"- {comment.get('body', '')[:200]}" for comment in top_comments])
        
        prompt = f"""Business Idea: "{business_idea}"

Reddit Post:
Title: {post['title']}
Subreddit: {post.get('subreddit', 'unknown')}
Score: {post.get('score', 0)}
Comments: {post.get('num_comments', 0)}
Content: {post.get('selftext', '')[:500]}

Top Comments:
{comments_text}

Analyze this Reddit post for business validation signals. Return a JSON object with the following structure:
{{
    "relevant": true/false,
    "pain_points": ["pain point 1", "pain point 2", ...],
    "solutions_mentioned": ["solution 1", "solution 2", ...],
    "market_signals": ["signal 1", "signal 2", ...],
    "sentiment": "positive/negative/neutral",
    "engagement_score": 0-10,
    "subreddit_context": "description of what this subreddit tells us about the audience"
}}

Instructions:
1. Is this post relevant to validating the business idea?
2. Extract key pain points mentioned or implied
3. Identify solutions discussed or mentioned
4. Highlight market signals (demand, competition, trends)
5. Determine overall sentiment
6. Rate engagement based on score and comments
7. Analyze what the subreddit context tells us about the target audience

Focus on extracting actionable insights for business validation."""
        
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        try:
            # First, try to extract JSON from code block or text
            json_match = response.text.strip()
            if json_match.startswith('```json'):
                json_match = json_match[7:-3].strip()
            elif json_match.startswith('```'):
                json_match = json_match[3:-3].strip()
            
            analysis_data = json.loads(json_match)
            
            # Validate the parsed data matches our model
            return RedditPostAnalysis(
                relevant=analysis_data.get('relevant', False),
                pain_points=analysis_data.get('pain_points', []),
                solutions_mentioned=analysis_data.get('solutions_mentioned', []),
                market_signals=analysis_data.get('market_signals', []),
                sentiment=analysis_data.get('sentiment', 'neutral'),
                engagement_score=analysis_data.get('engagement_score', 0),
                subreddit_context=analysis_data.get('subreddit_context', '')
            )
        
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logging.warning(f"JSON parsing failed: {e}")
            # Fallback to text parsing if JSON fails
            logging.warning(f"Raw response: {response.text}")
            return RedditPostAnalysis(
                relevant=False,
                pain_points=["Analysis parsing failed"],
                solutions_mentioned=["Analysis parsing failed"],
                market_signals=["Analysis parsing failed"],
                sentiment="neutral",
                engagement_score=0,
                subreddit_context="Analysis parsing failed"
            )
        
    except Exception as e:
        logging.error(f"Error analyzing Reddit post with Gemini API: {e}")
        return RedditPostAnalysis(
            relevant=False,
            pain_points=["Analysis failed"],
            solutions_mentioned=["Analysis failed"],
            market_signals=["Analysis failed"],
            sentiment="neutral",
            engagement_score=0,
            subreddit_context="Analysis failed"
        )
