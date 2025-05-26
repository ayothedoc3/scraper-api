"""
Keyword generation functionality for business idea validation.
"""

import logging
import os
from typing import List

from business_validator.models import KeywordModel

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Initialize LLM with error handling
llm_instance = None

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
        logging.info("Google Gemini LLM initialized successfully")
    else:
        logging.warning("Google API key not found or not set properly")
        
except Exception as e:
    logging.warning(f"Could not initialize Google Gemini LLM: {e}")

def generate_keywords(business_idea: str, num_keywords: int = 3) -> List[str]:
    """Generate search keywords for the business idea.
    
    Args:
        business_idea: The business idea to generate keywords for
        num_keywords: The number of keywords to generate
        
    Returns:
        List of generated keywords
    """
    logging.info(f"Generating keywords for business idea: {business_idea}")
    
    if llm_instance is None:
        logging.warning("LLM not available, using fallback keyword generation")
        # Fallback to basic keywords if LLM is not available
        words = business_idea.lower().split()
        fallback_keywords = []
        
        # Generate simple keywords from the business idea
        if len(words) >= 2:
            fallback_keywords.append(" ".join(words[:2]))
        if len(words) >= 3:
            fallback_keywords.append(" ".join(words[1:3]))
        if len(words) >= 1:
            fallback_keywords.append(words[0])
            
        # Ensure we have at least num_keywords
        while len(fallback_keywords) < num_keywords and len(words) > len(fallback_keywords):
            fallback_keywords.append(words[len(fallback_keywords)])
            
        return fallback_keywords[:num_keywords]
    
    try:
        # Set up the parser
        parser = PydanticOutputParser(pydantic_object=KeywordModel)
        
        # Create the prompt template
        prompt = PromptTemplate(
            template="""For the business idea: "{business_idea}"

Generate {num_keywords} specific search keywords that would help validate this idea.
These should be phrases people might use when discussing pain points, needs, or solutions related to this idea.

Keep keywords concise (2-4 words) and focused on the core problem/solution.

{format_instructions}""",
            input_variables=["business_idea", "num_keywords"],
            partial_variables={"format_instructions": parser.get_format_instructions()}
        )
        
        # Create the chain
        chain = prompt | llm_instance | parser
        
        # Generate keywords
        response = chain.invoke({
            "business_idea": business_idea,
            "num_keywords": num_keywords
        })
        
        logging.info(f"Generated keywords: {response.keywords}")
        return response.keywords
        
    except Exception as e:
        logging.error(f"Error generating keywords with LLM: {e}")
        # Fallback to basic keywords if generation fails
        words = business_idea.lower().split()
        fallback_keywords = []
        
        if len(words) >= 2:
            fallback_keywords.append(" ".join(words[:2]))
        if len(words) >= 1:
            fallback_keywords.append(words[0])
            
        return fallback_keywords[:num_keywords] if fallback_keywords else [business_idea]
