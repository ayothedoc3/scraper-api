"""
Combined analysis functionality that synthesizes insights from multiple sources.
"""

import logging
import os
import json
from typing import List, Dict, Any

from business_validator.models import CombinedAnalysis, HNPostAnalysis, RedditPostAnalysis, PlatformInsight

def generate_final_analysis(
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis],
    business_idea: str,
    keywords: List[str] = None
) -> CombinedAnalysis:
    """Generate final combined analysis from multiple sources.
    
    Args:
        hn_analyses: List of HackerNews post analyses
        reddit_analyses: List of Reddit post analyses
        business_idea: The business idea being validated
        keywords: List of keywords used for search
        
    Returns:
        CombinedAnalysis object with synthesized insights
    """
    logging.info("Generating final combined analysis...")
    
    # Get API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key or google_api_key == "your_google_api_key_here":
        logging.warning("Google API key not found, using fallback analysis")
        return create_fallback_analysis(hn_analyses, reddit_analyses, business_idea, keywords)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the data for analysis
        hn_summary = _summarize_hn_analyses(hn_analyses)
        reddit_summary = _summarize_reddit_analyses(reddit_analyses)
        
        prompt = f"""Business Idea: "{business_idea}"
Keywords Used: {keywords if keywords else 'Not provided'}

HackerNews Analysis Summary:
{hn_summary}

Reddit Analysis Summary:
{reddit_summary}

Based on these analyses from multiple sources, provide a comprehensive business validation assessment. Return a JSON object with the following structure:
{{
    "overall_score": 0-100,
    "market_validation_summary": "comprehensive summary of market validation findings",
    "key_pain_points": ["pain point 1", "pain point 2", ...],
    "existing_solutions": ["solution 1", "solution 2", ...],
    "market_opportunities": ["opportunity 1", "opportunity 2", ...],
    "platform_insights": [
        {{"platform": "HackerNews", "insights": "insights from HN data"}},
        {{"platform": "Reddit", "insights": "insights from Reddit data"}}
    ],
    "recommendations": ["recommendation 1", "recommendation 2", ...]
}}

Instructions:
1. Overall score (0-100): Rate the market validation strength
2. Market validation summary: Synthesize key findings
3. Key pain points: Extract the most important pain points identified
4. Existing solutions: List current solutions in the market
5. Market opportunities: Identify gaps and opportunities
6. Platform insights: Separate insights from HN vs Reddit
7. Recommendations: Actionable next steps

Focus on providing actionable business intelligence."""
        
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
            
            # Convert platform insights to PlatformInsight objects
            platform_insights = []
            for insight_data in analysis_data.get('platform_insights', []):
                platform_insights.append(PlatformInsight(
                    platform=insight_data.get('platform', ''),
                    insights=insight_data.get('insights', '')
                ))
            
            # Validate the parsed data matches our model
            return CombinedAnalysis(
                overall_score=analysis_data.get('overall_score', 0),
                market_validation_summary=analysis_data.get('market_validation_summary', ''),
                key_pain_points=analysis_data.get('key_pain_points', []),
                existing_solutions=analysis_data.get('existing_solutions', []),
                market_opportunities=analysis_data.get('market_opportunities', []),
                platform_insights=platform_insights,
                recommendations=analysis_data.get('recommendations', [])
            )
        
        except (json.JSONDecodeError, ValueError, TypeError) as e:
            logging.warning(f"JSON parsing failed: {e}")
            logging.warning(f"Raw response: {response.text}")
            return create_fallback_analysis(hn_analyses, reddit_analyses, business_idea, keywords)
        
    except Exception as e:
        logging.error(f"Error generating final analysis with Gemini API: {e}")
        return create_fallback_analysis(hn_analyses, reddit_analyses, business_idea, keywords)

def _summarize_hn_analyses(analyses: List[HNPostAnalysis]) -> str:
    """Create a summary of HackerNews analyses."""
    if not analyses:
        return "No HackerNews analyses available."
    
    relevant_count = sum(1 for a in analyses if a.relevant)
    total_count = len(analyses)
    
    all_pain_points = []
    all_solutions = []
    all_signals = []
    
    for analysis in analyses:
        if analysis.relevant:
            all_pain_points.extend(analysis.pain_points)
            all_solutions.extend(analysis.solutions_mentioned)
            all_signals.extend(analysis.market_signals)
    
    return f"""
    Total posts analyzed: {total_count}
    Relevant posts: {relevant_count}
    Common pain points: {', '.join(set(all_pain_points[:5]))}
    Solutions mentioned: {', '.join(set(all_solutions[:5]))}
    Market signals: {', '.join(set(all_signals[:5]))}
    """

def _summarize_reddit_analyses(analyses: List[RedditPostAnalysis]) -> str:
    """Create a summary of Reddit analyses."""
    if not analyses:
        return "No Reddit analyses available."
    
    relevant_count = sum(1 for a in analyses if a.relevant)
    total_count = len(analyses)
    
    all_pain_points = []
    all_solutions = []
    all_signals = []
    subreddits = []
    
    for analysis in analyses:
        if analysis.relevant:
            all_pain_points.extend(analysis.pain_points)
            all_solutions.extend(analysis.solutions_mentioned)
            all_signals.extend(analysis.market_signals)
            if analysis.subreddit_context:
                subreddits.append(analysis.subreddit_context)
    
    return f"""
    Total posts analyzed: {total_count}
    Relevant posts: {relevant_count}
    Common pain points: {', '.join(set(all_pain_points[:5]))}
    Solutions mentioned: {', '.join(set(all_solutions[:5]))}
    Market signals: {', '.join(set(all_signals[:5]))}
    Subreddit contexts: {', '.join(set(subreddits[:3]))}
    """

def create_fallback_analysis(
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis],
    business_idea: str,
    keywords: List[str] = None
) -> CombinedAnalysis:
    """Create a basic fallback analysis when LLM is not available."""
    
    if hn_analyses is None:
        hn_analyses = []
    if reddit_analyses is None:
        reddit_analyses = []
    
    # Basic aggregation
    total_relevant = sum(1 for a in hn_analyses if a.relevant) + sum(1 for a in reddit_analyses if a.relevant)
    total_posts = len(hn_analyses) + len(reddit_analyses)
    
    # Simple validation score based on relevance ratio
    overall_score = min(100, max(0, int((total_relevant / max(total_posts, 1)) * 100)))
    
    # Aggregate pain points and solutions
    all_pain_points = []
    all_solutions = []
    all_signals = []
    
    for analysis in hn_analyses + reddit_analyses:
        if hasattr(analysis, 'relevant') and analysis.relevant:
            all_pain_points.extend(analysis.pain_points)
            all_solutions.extend(analysis.solutions_mentioned)
            if hasattr(analysis, 'market_signals'):
                all_signals.extend(analysis.market_signals)
    
    # Create platform insights
    platform_insights = [
        PlatformInsight(
            platform="HackerNews",
            insights=f"Analyzed {len(hn_analyses)} posts, {sum(1 for a in hn_analyses if a.relevant)} relevant"
        ),
        PlatformInsight(
            platform="Reddit", 
            insights=f"Analyzed {len(reddit_analyses)} posts, {sum(1 for a in reddit_analyses if a.relevant)} relevant"
        )
    ]
    
    return CombinedAnalysis(
        overall_score=overall_score,
        market_validation_summary=f"Basic analysis of {total_posts} posts found {total_relevant} relevant discussions. Limited analysis due to API constraints.",
        key_pain_points=list(set(all_pain_points[:5])) if all_pain_points else ["Limited data available"],
        existing_solutions=list(set(all_solutions[:5])) if all_solutions else ["Limited data available"],
        market_opportunities=["Requires detailed analysis with full API access"],
        platform_insights=platform_insights,
        recommendations=["Obtain full API access for comprehensive analysis", "Gather more data from additional sources"]
    )

def create_minimal_analysis(business_idea: str, data_dir: str = None) -> CombinedAnalysis:
    """Create minimal analysis when no data is available."""
    return CombinedAnalysis(
        overall_score=0,
        market_validation_summary="No data available for analysis. Validation process was incomplete.",
        key_pain_points=["No data available for analysis"],
        existing_solutions=["No data available for analysis"],
        market_opportunities=["No data available for analysis"],
        platform_insights=[
            PlatformInsight(platform="HackerNews", insights="No data collected"),
            PlatformInsight(platform="Reddit", insights="No data collected")
        ],
        recommendations=["Retry validation process", "Check API keys and network connectivity", "Review logs for errors"]
    )
