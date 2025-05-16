import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import time
import os
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

# Import functions from test_enhanced.py
from test_enhanced import (
    generate_keywords, setup_master_log_directory, process_keyword,
    generate_aggregated_report, calculate_business_idea_scores,
    generate_executive_summary, VALIDATION_THRESHOLDS, SCORE_WEIGHTS,
    MIN_RELEVANCE_THRESHOLD, save_to_file
)

# Set page configuration
st.set_page_config(
    page_title="Business Idea Validator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #424242;
        margin-bottom: 1rem;
    }
    .card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        color: #000000;
    }
    .status-validated {
        color: #2E7D32;
        font-weight: 700;
        font-size: 1.2rem;
    }
    .status-partially {
        color: #F9A825;
        font-weight: 700;
        font-size: 1.2rem;
    }
    .status-not {
        color: #C62828;
        font-weight: 700;
        font-size: 1.2rem;
    }
    .metric-label {
        font-weight: 600;
        color: #616161;
    }
    .score-high {
        color: #2E7D32;
        font-weight: 700;
    }
    .score-medium {
        color: #F9A825;
        font-weight: 700;
    }
    .score-low {
        color: #C62828;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for visualization
def create_gauge_chart(value, title, min_val=0, max_val=10, threshold_ranges=None):
    if threshold_ranges is None:
        threshold_ranges = [(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [min_val, max_val], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [range_min, range_max], 'color': color} 
                for range_min, range_max, color in threshold_ranges
            ],
        }
    ))
    
    fig.update_layout(
        height=250,
        margin=dict(l=10, r=10, t=50, b=10),
        font={'color': "#444", 'family': "Arial"}
    )
    
    return fig

def create_radar_chart(scores, categories):
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        name='Business Idea Scores',
        line_color='rgba(30, 136, 229, 0.8)',
        fillcolor='rgba(30, 136, 229, 0.3)'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        height=400,
        margin=dict(l=70, r=70, t=20, b=70),
    )
    
    return fig

def create_horizontal_bar_chart(items, title, color_scale="Viridis"):
    if not items:
        return None
    
    # Extract text and relevance from items
    texts = []
    relevance_scores = []
    
    for item in items:
        if isinstance(item, dict) and "text" in item and "relevance" in item:
            texts.append(item["text"])
            relevance_scores.append(item["relevance"])
    
    if not texts:  # If no valid items were found
        return None
    
    # Create DataFrame
    df = pd.DataFrame({
        'Text': texts,
        'Relevance': relevance_scores
    })
    
    # Sort by relevance
    df = df.sort_values('Relevance', ascending=True)
    
    # Create horizontal bar chart
    fig = px.bar(
        df, 
        x='Relevance', 
        y='Text', 
        orientation='h',
        title=title,
        color='Relevance',
        color_continuous_scale=color_scale,
        range_color=[0, 10]
    )
    
    fig.update_layout(
        height=max(300, len(texts) * 30),  # Dynamic height based on number of items
        margin=dict(l=10, r=10, t=50, b=10),
        yaxis={'categoryorder': 'total ascending'}
    )
    
    return fig

def get_status_class(status):
    if "Strongly Validated" in status or "Validated" in status:
        return "status-validated"
    elif "Partially Validated" in status:
        return "status-partially"
    else:
        return "status-not"

def get_score_class(score, max_score=10):
    percentage = (score / max_score) * 100
    if percentage >= 70:
        return "score-high"
    elif percentage >= 40:
        return "score-medium"
    else:
        return "score-low"

def format_item_with_relevance(item):
    if isinstance(item, dict) and "text" in item and "relevance" in item:
        relevance_class = get_score_class(item["relevance"])
        return f"{item['text']} <span class='{relevance_class}'>({item['relevance']}/10)</span>"
    elif isinstance(item, str):
        return item
    return ""

# Initialize session state
if 'validation_complete' not in st.session_state:
    st.session_state.validation_complete = False
if 'validation_in_progress' not in st.session_state:
    st.session_state.validation_in_progress = False
if 'business_idea' not in st.session_state:
    st.session_state.business_idea = ""
if 'keywords' not in st.session_state:
    st.session_state.keywords = []
if 'current_keyword' not in st.session_state:
    st.session_state.current_keyword = ""
if 'keyword_results' not in st.session_state:
    st.session_state.keyword_results = {}
if 'final_report' not in st.session_state:
    st.session_state.final_report = None
if 'scores' not in st.session_state:
    st.session_state.scores = None
if 'executive_summary' not in st.session_state:
    st.session_state.executive_summary = None
if 'master_log_dir' not in st.session_state:
    st.session_state.master_log_dir = None

# Main app header
st.markdown("<h1 class='main-header'>Business Idea Validator</h1>", unsafe_allow_html=True)
st.markdown(
    "This tool helps validate your business idea by analyzing online discussions, "
    "identifying pain points, excitement signals, and competitors."
)

# Sidebar
with st.sidebar:
    st.markdown("<h2 class='sub-header'>About</h2>", unsafe_allow_html=True)
    st.markdown(
        "The Business Idea Validator analyzes online discussions to validate your business idea. "
        "It searches platforms like Reddit and ProductHunt to identify pain points, excitement signals, "
        "and competitors related to your idea."
    )
    
    st.markdown("<h2 class='sub-header'>How it works</h2>", unsafe_allow_html=True)
    st.markdown(
        "1. Enter your business idea\n"
        "2. The tool generates relevant keywords\n"
        "3. It searches online platforms for each keyword\n"
        "4. AI analyzes the content to extract insights\n"
        "5. Results are compiled into an executive summary with scores"
    )
    
    if st.session_state.validation_complete:
        st.markdown("<h2 class='sub-header'>Download Results</h2>", unsafe_allow_html=True)
        if st.session_state.master_log_dir:
            summary_path = Path(st.session_state.master_log_dir) / "executive_summary.json"
            report_path = Path(st.session_state.master_log_dir) / "final_report.json"
            
            if summary_path.exists():
                with open(summary_path, 'r') as f:
                    summary_data = json.load(f)
                st.download_button(
                    label="Download Executive Summary",
                    data=json.dumps(summary_data, indent=2),
                    file_name="executive_summary.json",
                    mime="application/json"
                )
            
            if report_path.exists():
                with open(report_path, 'r') as f:
                    report_data = json.load(f)
                st.download_button(
                    label="Download Full Report",
                    data=json.dumps(report_data, indent=2),
                    file_name="full_report.json",
                    mime="application/json"
                )

# Input form (only show if validation is not in progress or complete)
if not st.session_state.validation_in_progress and not st.session_state.validation_complete:
    st.markdown("<h2 class='sub-header'>Enter Your Business Idea</h2>", unsafe_allow_html=True)
    
    with st.form("idea_form"):
        business_idea = st.text_area(
            "Describe your business idea in detail",
            height=100,
            placeholder="e.g., A mobile app that helps people find and book last-minute fitness classes"
        )
        
        submitted = st.form_submit_button("Validate Business Idea")
        
        if submitted and business_idea:
            st.session_state.business_idea = business_idea
            st.session_state.validation_in_progress = True
            st.rerun()

# Validation process
if st.session_state.validation_in_progress and not st.session_state.validation_complete:
    st.markdown("<h2 class='sub-header'>Validation in Progress</h2>", unsafe_allow_html=True)
    
    # Create progress bar
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Set up master log directory
        status_text.text("Setting up log directory...")
        master_log_dir = setup_master_log_directory(st.session_state.business_idea)
        st.session_state.master_log_dir = str(master_log_dir)
        progress_bar.progress(5)
        
        # Step 2: Generate keywords
        status_text.text("Generating keywords...")
        keywords = generate_keywords(st.session_state.business_idea)
        st.session_state.keywords = keywords
        
        # Display generated keywords
        st.markdown("<h3>Generated Keywords:</h3>", unsafe_allow_html=True)
        st.write(", ".join(keywords))
        progress_bar.progress(15)
        
        # Step 3: Process each keyword
        all_keyword_results = {}
        total_keywords = len(keywords)
        
        for i, keyword in enumerate(keywords):
            st.session_state.current_keyword = keyword
            status_text.text(f"Processing keyword {i+1}/{total_keywords}: {keyword}")
            
            # Create a placeholder for this keyword's status
            keyword_status = st.empty()
            keyword_status.info(f"Searching and analyzing content for: {keyword}")
            
            # Process the keyword
            keyword_results = process_keyword(keyword, master_log_dir)
            all_keyword_results[keyword] = keyword_results
            st.session_state.keyword_results[keyword] = keyword_results
            
            # Update keyword status
            keyword_status.success(f"Completed analysis for: {keyword}")
            
            # Update progress
            progress_value = 15 + (i + 1) * (55 / total_keywords)
            progress_bar.progress(int(progress_value))
        
        # Step 4: Generate aggregated report
        status_text.text("Generating aggregated report...")
        final_report = generate_aggregated_report(
            st.session_state.business_idea, 
            keywords, 
            all_keyword_results, 
            master_log_dir
        )
        st.session_state.final_report = final_report
        progress_bar.progress(75)
        
        # Step 5: Calculate scores
        status_text.text("Calculating business idea scores...")
        scores = calculate_business_idea_scores(final_report)
        st.session_state.scores = scores
        progress_bar.progress(85)
        
        # Step 6: Generate executive summary
        status_text.text("Generating executive summary...")
        executive_summary = generate_executive_summary(final_report, scores)
        st.session_state.executive_summary = executive_summary
        progress_bar.progress(95)
        
        # Save summary and scores to file
        summary_with_scores = {
            "scores": scores,
            "executive_summary": executive_summary
        }
        summary_path = Path(master_log_dir) / "executive_summary.json"
        save_to_file(summary_with_scores, summary_path, is_json=True)
        
        # Complete
        status_text.text("Validation complete!")
        progress_bar.progress(100)
        
        # Set validation as complete
        st.session_state.validation_complete = True
        st.session_state.validation_in_progress = False
        
        # Rerun to show results
        time.sleep(1)
        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred during validation: {str(e)}")
        st.session_state.validation_in_progress = False

# Results dashboard
if st.session_state.validation_complete:
    # Get data from session state
    business_idea = st.session_state.business_idea
    executive_summary = st.session_state.executive_summary
    scores = st.session_state.scores
    final_report = st.session_state.final_report
    
    # Executive Summary Section
    st.markdown("<h2 class='sub-header'>Executive Summary</h2>", unsafe_allow_html=True)
    
    # Create three columns for the summary header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"<div class='card'><h3>Business Idea</h3><p>{business_idea}</p></div>", unsafe_allow_html=True)
    
    with col2:
        status_class = get_status_class(executive_summary["validation_status"])
        st.markdown(
            f"<div class='card'><h3>Validation Status</h3>"
            f"<p class='{status_class}'>{executive_summary['validation_status']}</p></div>",
            unsafe_allow_html=True
        )
    
    with col3:
        score_class = get_score_class(executive_summary["overall_score"], 100)
        st.markdown(
            f"<div class='card'><h3>Overall Score</h3>"
            f"<p class='{score_class}'>{executive_summary['overall_score']}/100</p></div>",
            unsafe_allow_html=True
        )
    
    # Recommendation
    st.markdown(
        f"<div class='card'><h3>Recommendation</h3><p>{executive_summary['recommendation']}</p></div>",
        unsafe_allow_html=True
    )
    
    # Score Visualization Section
    st.markdown("<h2 class='sub-header'>Score Breakdown</h2>", unsafe_allow_html=True)
    
    # Create gauge charts for each score
    col1, col2 = st.columns(2)
    
    with col1:
        # Market Pain Score
        st.plotly_chart(
            create_gauge_chart(
                scores["market_pain_score"], 
                "Market Pain Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"<p><b>Why:</b> {scores['score_explanations']['market_pain_score']}</p>", unsafe_allow_html=True)
        
        # Competition Score
        st.plotly_chart(
            create_gauge_chart(
                scores["competition_score"], 
                "Competition Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"<p><b>Why:</b> {scores['score_explanations']['competition_score']}</p>", unsafe_allow_html=True)
    
    with col2:
        # Market Interest Score
        st.plotly_chart(
            create_gauge_chart(
                scores["market_interest_score"], 
                "Market Interest Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"<p><b>Why:</b> {scores['score_explanations']['market_interest_score']}</p>", unsafe_allow_html=True)
        
        # Keyword Relevance Score
        st.plotly_chart(
            create_gauge_chart(
                scores["keyword_relevance_score"], 
                "Keyword Relevance Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"<p><b>Why:</b> {scores['score_explanations']['keyword_relevance_score']}</p>", unsafe_allow_html=True)
    
    # Radar Chart for all scores
    st.markdown("<h3>Score Comparison</h3>", unsafe_allow_html=True)
    radar_scores = [
        scores["market_pain_score"],
        scores["market_interest_score"],
        scores["competition_score"],
        scores["keyword_relevance_score"],
        scores["coherence_score"]
    ]
    radar_categories = [
        "Market Pain",
        "Market Interest",
        "Competition",
        "Keyword Relevance",
        "Coherence"
    ]
    st.plotly_chart(create_radar_chart(radar_scores, radar_categories), use_container_width=True)
    
    # Detailed Results Section
    st.markdown("<h2 class='sub-header'>Detailed Results</h2>", unsafe_allow_html=True)
    
    # Create tabs for different result categories
    tab1, tab2, tab3, tab4 = st.tabs(["Pain Points", "Excitement Signals", "Competitors", "Red Flags"])
    
    with tab1:
        st.markdown("<h3>Top Pain Points</h3>", unsafe_allow_html=True)
        
        # Create bar chart for pain points
        pain_points = final_report["aggregated_results"]["pain_points"]
        if pain_points:
            pain_chart = create_horizontal_bar_chart(
                pain_points, 
                "Pain Points by Relevance",
                color_scale="Reds"
            )
            if pain_chart:
                st.plotly_chart(pain_chart, use_container_width=True)
            
            # List pain points with relevance
            for item in pain_points:
                if isinstance(item, dict) and "text" in item and "relevance" in item:
                    if item["relevance"] >= MIN_RELEVANCE_THRESHOLD:
                        st.markdown(
                            f"- {format_item_with_relevance(item)}",
                            unsafe_allow_html=True
                        )
        else:
            st.info("No pain points found.")
    
    with tab2:
        st.markdown("<h3>Top Excitement Signals</h3>", unsafe_allow_html=True)
        
        # Create bar chart for excitement signals
        excitement_signals = final_report["aggregated_results"]["excitement_signals"]
        if excitement_signals:
            excitement_chart = create_horizontal_bar_chart(
                excitement_signals, 
                "Excitement Signals by Relevance",
                color_scale="Greens"
            )
            if excitement_chart:
                st.plotly_chart(excitement_chart, use_container_width=True)
            
            # List excitement signals with relevance
            for item in excitement_signals:
                if isinstance(item, dict) and "text" in item and "relevance" in item:
                    if item["relevance"] >= MIN_RELEVANCE_THRESHOLD:
                        st.markdown(
                            f"- {format_item_with_relevance(item)}",
                            unsafe_allow_html=True
                        )
        else:
            st.info("No excitement signals found.")
    
    with tab3:
        st.markdown("<h3>Competitors</h3>", unsafe_allow_html=True)
        
        competitors = final_report["aggregated_results"]["mentions_of_competitors"]
        if competitors:
            # Create a DataFrame for competitors
            df_competitors = pd.DataFrame({
                'Competitor': competitors
            })
            
            # Display as a table
            st.dataframe(df_competitors, use_container_width=True)
        else:
            st.info("No competitors found.")
    
    with tab4:
        st.markdown("<h3>Red Flags</h3>", unsafe_allow_html=True)
        
        red_flags = final_report["aggregated_results"].get("red_flags", [])
        if red_flags:
            for flag in red_flags:
                st.markdown(f"- {flag}")
        else:
            st.info("No red flags found.")
    
    # Key Insights Section
    st.markdown("<h2 class='sub-header'>Key Insights</h2>", unsafe_allow_html=True)
    
    for insight in executive_summary["key_insights"]:
        st.markdown(f"- {insight}")
    
    # Notable Quotes Section
    if "notable_quotes" in final_report["aggregated_results"] and final_report["aggregated_results"]["notable_quotes"]:
        st.markdown("<h2 class='sub-header'>Notable Quotes</h2>", unsafe_allow_html=True)
        
        quotes = final_report["aggregated_results"]["notable_quotes"]
        for quote in quotes:
            if isinstance(quote, dict) and "text" in quote:
                st.markdown(f"> *\"{quote['text']}\"*")
            elif isinstance(quote, str):
                st.markdown(f"> *\"{quote}\"*")
    
    # Reset button
    if st.button("Validate Another Business Idea"):
        # Reset session state
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    "Business Idea Validator | Powered by AI | "
    "Uses data from Reddit, ProductHunt, and other platforms"
)
