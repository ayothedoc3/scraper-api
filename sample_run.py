#!/usr/bin/env python3
"""
Sample script to demonstrate how to run the Business Idea Validator programmatically.
This script shows how to use the core functions from test_enhanced.py directly.
"""

from pathlib import Path
import json
import time

# Import functions from test_enhanced.py
from test_enhanced import (
    generate_keywords, setup_master_log_directory, process_keyword,
    generate_aggregated_report, calculate_business_idea_scores,
    generate_executive_summary, save_to_file
)

def run_validation(business_idea):
    """
    Run the business idea validation process programmatically.
    
    Args:
        business_idea (str): The business idea to validate
        
    Returns:
        dict: The executive summary
    """
    print(f"Validating business idea: {business_idea}")
    
    # Step 1: Set up master log directory
    print("Setting up log directory...")
    master_log_dir = setup_master_log_directory(business_idea)
    print(f"Logs will be saved to: {master_log_dir}")
    
    # Step 2: Generate keywords
    print("Generating keywords...")
    keywords = generate_keywords(business_idea)
    print(f"Generated keywords: {keywords}")
    
    # Step 3: Process each keyword
    all_keyword_results = {}
    for keyword in keywords:
        print(f"Processing keyword: {keyword}")
        keyword_results = process_keyword(keyword, master_log_dir)
        all_keyword_results[keyword] = keyword_results
    
    # Step 4: Generate aggregated report
    print("Generating aggregated report...")
    final_report = generate_aggregated_report(
        business_idea, 
        keywords, 
        all_keyword_results, 
        master_log_dir
    )
    
    # Step 5: Calculate scores
    print("Calculating business idea scores...")
    scores = calculate_business_idea_scores(final_report)
    
    # Step 6: Generate executive summary
    print("Generating executive summary...")
    executive_summary = generate_executive_summary(final_report, scores)
    
    # Save summary and scores to file
    summary_with_scores = {
        "scores": scores,
        "executive_summary": executive_summary
    }
    summary_path = Path(master_log_dir) / "executive_summary.json"
    save_to_file(summary_with_scores, summary_path, is_json=True)
    
    # Print summary
    print("\n" + "="*60)
    print("EXECUTIVE SUMMARY")
    print("="*60)
    print(f"Business Idea: {business_idea}")
    print(f"Validation Status: {executive_summary['validation_status']} ({executive_summary['overall_score']}/100)")
    print(f"Recommendation: {executive_summary['recommendation']}")
    print("="*60)
    
    return executive_summary

def main():
    """Run the sample validation."""
    # Sample business idea
    business_idea = "A mobile app that helps people find and book last-minute fitness classes"
    
    # Run validation
    executive_summary = run_validation(business_idea)
    
    # Print path to results
    print("\nValidation complete!")
    print("To view the full results, check the logs directory.")
    print("To run the Streamlit app for a visual interface, use: python run.py")

if __name__ == "__main__":
    main()
