"""
Simplified keyword generation functionality for business idea validation.
"""

import logging
import os
import json
from typing import List

def generate_keywords_simple(business_idea: str, num_keywords: int = 3) -> List[str]:
    """Generate search keywords for the business idea using Google Gemini API directly.
    
    Args:
        business_idea: The business idea to generate keywords for
        num_keywords: The number of keywords to generate
        
    Returns:
        List of generated keywords
    """
    logging.info(f"Generating keywords for business idea: {business_idea}")
    
    # Get API key from environment
    google_api_key = os.getenv("GOOGLE_API_KEY")
    
    if not google_api_key or google_api_key == "your_google_api_key_here":
        logging.warning("Google API key not found, using fallback keyword generation")
        return generate_fallback_keywords(business_idea, num_keywords)
    
    try:
        import google.generativeai as genai
        
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = f"""For the business idea: "{business_idea}"

Generate {num_keywords} specific search keywords that would help validate this idea.
These should be phrases people might use when discussing pain points, needs, or solutions related to this idea.

Keep keywords concise (2-4 words) and focused on the core problem/solution.

Return a JSON array of keywords, without any additional text."""
        
        response = model.generate_content(prompt)
        
        # Try to parse the response as JSON
        try:
            # First, try to extract JSON from code block or text
            json_match = response.text.strip()
            if json_match.startswith('```json'):
                json_match = json_match[7:-3].strip()
            elif json_match.startswith('```'):
                json_match = json_match[3:-3].strip()
            
            keywords = json.loads(json_match)
            
            # Ensure it's a list of strings
            if isinstance(keywords, list) and all(isinstance(k, str) for k in keywords):
                cleaned_keywords = [k.strip() for k in keywords if k.strip()]
                
                if cleaned_keywords:
                    logging.info(f"Generated keywords: {cleaned_keywords}")
                    return cleaned_keywords[:num_keywords]
        except (json.JSONDecodeError, ValueError):
            # If JSON parsing fails, try parsing the text directly
            keywords = [line.strip() for line in response.text.strip().split('\n') if line.strip()]
            keywords = [k for k in keywords if k and not k.startswith('-') and not k.startswith('*')]
            
            # Clean up keywords and limit to requested number
            cleaned_keywords = []
            for keyword in keywords[:num_keywords]:
                # Remove numbering and clean up
                keyword = keyword.strip()
                if keyword.startswith(('1.', '2.', '3.', '4.', '5.')):
                    keyword = keyword[2:].strip()
                if keyword.startswith(('1)', '2)', '3)', '4)', '5)')):
                    keyword = keyword[2:].strip()
                if keyword:
                    cleaned_keywords.append(keyword)
            
            if cleaned_keywords:
                logging.info(f"Generated keywords: {cleaned_keywords}")
                return cleaned_keywords[:num_keywords]
        
        logging.warning("No valid keywords generated, using fallback")
        return generate_fallback_keywords(business_idea, num_keywords)
        
    except Exception as e:
        logging.error(f"Error generating keywords with Gemini API: {e}")
        return generate_fallback_keywords(business_idea, num_keywords)

def generate_fallback_keywords(business_idea: str, num_keywords: int = 3) -> List[str]:
    """Generate fallback keywords when AI is not available."""
    words = business_idea.lower().split()
    fallback_keywords = []
    
    # Generate simple keywords from the business idea
    if len(words) >= 2:
        fallback_keywords.append(" ".join(words[:2]))
    if len(words) >= 3:
        fallback_keywords.append(" ".join(words[1:3]))
    if len(words) >= 1:
        fallback_keywords.append(words[0])
        
    # Add more single words if needed
    for word in words:
        if len(word) > 3 and word not in [k.split()[-1] for k in fallback_keywords]:
            fallback_keywords.append(word)
            if len(fallback_keywords) >= num_keywords:
                break
    
    # Ensure we have at least num_keywords
    while len(fallback_keywords) < num_keywords and len(words) > len(fallback_keywords):
        if len(fallback_keywords) < len(words):
            fallback_keywords.append(words[len(fallback_keywords)])
    
    return fallback_keywords[:num_keywords]

# For backward compatibility
def generate_keywords(business_idea: str, num_keywords: int = 3) -> List[str]:
    """Main function for generating keywords."""
    return generate_keywords_simple(business_idea, num_keywords)
