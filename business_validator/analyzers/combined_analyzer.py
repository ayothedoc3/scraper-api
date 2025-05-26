"""
Combined analysis functionality that synthesizes insights from multiple sources.
"""

import logging
import os
from typing import List, Dict, Any

from business_validator.models import CombinedAnalysis, HNPostAnalysis, RedditPostAnalysis

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
    logging.warning(f"Could not initialize Google Gemini LLM in combined_analyzer: {e}")

def combine_analyses(
    business_idea: str,
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis]
) -> CombinedAnalysis:
    """Combine and synthesize analyses from multiple sources.
    
    Args:
        business_idea: The business idea being validated
        hn_analyses: List of HackerNews post analyses
        reddit_analyses: List of Reddit post analyses
        
    Returns:
        CombinedAnalysis object with synthesized insights
    """
    logging.info("Combining analyses from multiple sources...")
    
    if llm_instance is None:
        logging.warning("LLM not available, returning basic combined analysis")
        return _create_fallback_analysis(business_idea, hn_analyses, reddit_analyses)
    
    try:
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=CombinedAnalysis)
        
        # Prepare the data for analysis
        hn_summary = _summarize_hn_analyses(hn_analyses)
        reddit_summary = _summarize_reddit_analyses(reddit_analyses)
        
        # Create the prompt template
        prompt = PromptTemplate(
            template="""Business Idea: "{business_idea}"

HackerNews Analysis Summary:
{hn_summary}

Reddit Analysis Summary:
{reddit_summary}

Based on these analyses from multiple sources, provide a comprehensive business validation assessment:

1. Overall validation score (1-10, where 10 means highly validated)
2. Key pain points identified across all sources
3. Existing solutions mentioned across all sources
4. Market demand signals observed
5. Competition level assessment
6. Target audience insights
7. Key recommendations for next steps
8. Risk factors to consider

Synthesize insights from both HackerNews and Reddit to provide actionable business intelligence.

{format_instructions}""",
            input_variables=["business_idea", "hn_summary", "reddit_summary"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create the chain
        chain = prompt | llm_instance | parser
        
        # Generate combined analysis
        analysis = chain.invoke({
            "business_idea": business_idea,
            "hn_summary": hn_summary,
            "reddit_summary": reddit_summary
        })
        
        return analysis
        
    except Exception as e:
        logging.error(f"Error combining analyses: {e}")
        return _create_fallback_analysis(business_idea, hn_analyses, reddit_analyses)

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

def _create_fallback_analysis(
    business_idea: str,
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis]
) -> CombinedAnalysis:
    """Create a basic fallback analysis when LLM is not available."""
    
    # Basic aggregation
    total_relevant = sum(1 for a in hn_analyses if a.relevant) + sum(1 for a in reddit_analyses if a.relevant)
    total_posts = len(hn_analyses) + len(reddit_analyses)
    
    # Simple validation score based on relevance ratio
    validation_score = min(10, max(1, int((total_relevant / max(total_posts, 1)) * 10)))
    
    # Aggregate pain points and solutions
    all_pain_points = []
    all_solutions = []
    
    for analysis in hn_analyses + reddit_analyses:
        if hasattr(analysis, 'relevant') and analysis.relevant:
            all_pain_points.extend(analysis.pain_points)
            all_solutions.extend(analysis.solutions_mentioned)
    
    return CombinedAnalysis(
        validation_score=validation_score,
        key_pain_points=list(set(all_pain_points[:5])),
        existing_solutions=list(set(all_solutions[:5])),
        market_demand_signals=["Basic analysis - LLM not available"],
        competition_level="Unknown - LLM not available",
        target_audience_insights=["Basic analysis - LLM not available"],
        recommendations=["Get proper LLM access for detailed analysis"],
        risk_factors=["Limited analysis due to LLM unavailability"]
    )

def generate_final_analysis(
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis],
    business_idea: str,
    keywords: List[str] = None
) -> CombinedAnalysis:
    """Generate final analysis - alias for combine_analyses for backward compatibility."""
    return combine_analyses(business_idea, hn_analyses, reddit_analyses)

def create_fallback_analysis(
    hn_analyses: List[HNPostAnalysis],
    reddit_analyses: List[RedditPostAnalysis],
    business_idea: str,
    keywords: List[str] = None
) -> CombinedAnalysis:
    """Create fallback analysis - public interface for _create_fallback_analysis."""
    if hn_analyses is None:
        hn_analyses = []
    if reddit_analyses is None:
        reddit_analyses = []
    return _create_fallback_analysis(business_idea, hn_analyses, reddit_analyses)

def create_minimal_analysis(business_idea: str) -> CombinedAnalysis:
    """Create minimal analysis when no data is available."""
    return CombinedAnalysis(
        validation_score=1,
        key_pain_points=["No data available for analysis"],
        existing_solutions=["No data available for analysis"],
        market_demand_signals=["No data available for analysis"],
        competition_level="Unknown - no data available",
        target_audience_insights=["No data available for analysis"],
        recommendations=["Gather more data for proper analysis"],
        risk_factors=["Insufficient data for validation"]
    )
