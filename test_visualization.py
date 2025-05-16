#!/usr/bin/env python3
"""
Test script for the visualization components of the Business Idea Validator Streamlit app.
This script creates sample data and displays it using the visualization functions.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import random
from pathlib import Path

# Set page configuration
st.set_page_config(
    page_title="Visualization Test",
    page_icon="🔍",
    layout="wide"
)

# Sample data generation functions
def generate_sample_pain_points(num=10):
    """Generate sample pain points with relevance scores."""
    pain_points = []
    for i in range(num):
        relevance = random.randint(3, 10)
        pain_points.append({
            "text": f"Sample pain point {i+1}: Users struggle with {random.choice(['usability', 'pricing', 'features', 'support', 'reliability'])}",
            "relevance": relevance
        })
    return pain_points

def generate_sample_excitement_signals(num=8):
    """Generate sample excitement signals with relevance scores."""
    signals = []
    for i in range(num):
        relevance = random.randint(3, 10)
        signals.append({
            "text": f"Sample excitement signal {i+1}: Users love the {random.choice(['convenience', 'design', 'speed', 'innovation', 'value'])}",
            "relevance": relevance
        })
    return signals

def generate_sample_competitors(num=5):
    """Generate sample competitors."""
    competitors = [
        "CompetitorX",
        "IndustryLeader",
        "StartupY",
        "TechGiant",
        "LocalBusiness",
        "GlobalCorp",
        "NewEntrant"
    ]
    return random.sample(competitors, min(num, len(competitors)))

def generate_sample_red_flags(num=3):
    """Generate sample red flags."""
    red_flags = [
        "Market seems saturated with similar solutions",
        "Users complain about high costs for similar services",
        "Regulatory challenges in multiple markets",
        "Technology adoption barriers are significant",
        "Large companies dominating the space"
    ]
    return random.sample(red_flags, min(num, len(red_flags)))

def generate_sample_scores():
    """Generate sample scores."""
    return {
        "market_pain_score": round(random.uniform(5.0, 9.0), 1),
        "market_interest_score": round(random.uniform(4.0, 8.5), 1),
        "competition_score": round(random.uniform(3.0, 9.0), 1),
        "keyword_relevance_score": round(random.uniform(5.5, 8.0), 1),
        "coherence_score": round(random.uniform(6.0, 9.5), 1),
        "overall_viability_score": round(random.uniform(60.0, 85.0), 1),
        "score_explanations": {
            "market_pain_score": "Based on 7 pain points with average relevance of 7.5/10.",
            "market_interest_score": "Based on 5 excitement signals with average relevance of 6.8/10.",
            "competition_score": "Based on 4 competitors mentioned. Moderate competition indicates a validated market.",
            "keyword_relevance_score": "Based on average of 6.2 findings per keyword across 5 keywords.",
            "coherence_score": "Measures consistency and coherence of findings. High score indicates consistent and coherent findings.",
            "overall_viability_score": "Calculated from weighted component scores: Pain Points (35%), Excitement (30%), Competition (20%), Keyword Relevance (15%)."
        }
    }

def generate_sample_executive_summary(scores):
    """Generate sample executive summary."""
    # Determine validation status based on overall score
    overall_score = scores["overall_viability_score"]
    if overall_score >= 85:
        validation_status = "Strongly Validated"
        recommendation = "This business idea shows strong market validation. Consider proceeding with development and creating an MVP."
    elif overall_score >= 70:
        validation_status = "Validated"
        recommendation = "This business idea shows good market validation. Consider proceeding with caution, focusing on the identified pain points."
    elif overall_score >= 55:
        validation_status = "Partially Validated"
        recommendation = "This business idea shows moderate market validation. Consider refining the concept based on the identified pain points and excitement signals."
    elif overall_score >= 40:
        validation_status = "Weakly Validated"
        recommendation = "This business idea shows weak market validation. Consider pivoting or significantly refining the concept before proceeding."
    else:
        validation_status = "Not Validated"
        recommendation = "This business idea lacks sufficient market validation. Consider exploring alternative ideas or completely rethinking the approach."
    
    # Generate insights based on scores
    insights = []
    
    if scores["market_pain_score"] >= 7:
        insights.append("Strong pain points identified, indicating a clear market need.")
    elif scores["market_pain_score"] <= 3:
        insights.append("Few significant pain points identified, suggesting limited market need.")
    
    if scores["market_interest_score"] >= 7:
        insights.append("High market interest detected, indicating potential demand.")
    elif scores["market_interest_score"] <= 3:
        insights.append("Low market interest detected, suggesting limited demand.")
    
    if scores["competition_score"] >= 7:
        insights.append("Healthy competitive landscape, indicating a validated market.")
    elif scores["competition_score"] <= 3:
        insights.append("Limited competition may indicate an untapped market or lack of market viability.")
    
    if scores["keyword_relevance_score"] >= 7:
        insights.append("Keywords were highly relevant, providing good market insights.")
    elif scores["keyword_relevance_score"] <= 3:
        insights.append("Keywords had limited relevance, suggesting the need for refined market research.")
    
    return {
        "business_idea": "A mobile app that helps people find and book last-minute fitness classes",
        "validation_status": validation_status,
        "overall_score": overall_score,
        "top_pain_points": generate_sample_pain_points(5),
        "top_excitement_signals": generate_sample_excitement_signals(5),
        "top_competitors": generate_sample_competitors(5),
        "key_insights": insights,
        "recommendation": recommendation
    }

def generate_sample_final_report():
    """Generate sample final report."""
    pain_points = generate_sample_pain_points(15)
    excitement_signals = generate_sample_excitement_signals(12)
    competitors = generate_sample_competitors(7)
    red_flags = generate_sample_red_flags(4)
    
    return {
        "metadata": {
            "business_idea": "A mobile app that helps people find and book last-minute fitness classes",
            "timestamp": "2025-05-12T18:30:00.000Z",
            "keywords": ["fitness app", "last-minute booking", "gym classes", "workout scheduling", "fitness marketplace"],
            "sources": ["Reddit", "ProductHunt"],
            "pages_per_source": 3
        },
        "aggregated_results": {
            "pain_points": pain_points,
            "excitement_signals": excitement_signals,
            "mentions_of_competitors": competitors,
            "notable_quotes": [
                {"text": "I wish there was an easy way to find available fitness classes near me when my schedule suddenly opens up."},
                {"text": "The current booking systems for gyms are so outdated and frustrating to use."},
                {"text": "I'd pay extra for the convenience of booking a class at the last minute without all the hassle."}
            ],
            "red_flags": red_flags,
            "coherence_score": 8.5
        },
        "keyword_results": {
            "fitness app": {
                "pain_points": pain_points[:8],
                "excitement_signals": excitement_signals[:6],
                "mentions_of_competitors": competitors[:3],
                "notable_quotes": [{"text": "I wish there was an easy way to find available fitness classes near me when my schedule suddenly opens up."}],
                "coherence_score": 8.2
            },
            "last-minute booking": {
                "pain_points": pain_points[3:10],
                "excitement_signals": excitement_signals[2:9],
                "mentions_of_competitors": competitors[1:5],
                "notable_quotes": [{"text": "I'd pay extra for the convenience of booking a class at the last minute without all the hassle."}],
                "coherence_score": 7.9
            }
        }
    }

# Visualization functions
def create_gauge_chart(value, title, min_val=0, max_val=10, threshold_ranges=None):
    """Create a gauge chart for a score."""
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
    """Create a radar chart for multiple scores."""
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
    """Create a horizontal bar chart for items with relevance scores."""
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

# Main app
def main():
    """Main function to display the test visualizations."""
    st.title("Business Idea Validator - Visualization Test")
    st.markdown(
        "This is a test page for the visualization components of the Business Idea Validator app. "
        "It displays sample data to demonstrate how the visualizations will look."
    )
    
    # Generate sample data
    scores = generate_sample_scores()
    executive_summary = generate_sample_executive_summary(scores)
    final_report = generate_sample_final_report()
    
    # Display executive summary
    st.header("Executive Summary")
    
    # Create three columns for the summary header
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"**Business Idea:** {executive_summary['business_idea']}")
    
    with col2:
        st.markdown(f"**Validation Status:** {executive_summary['validation_status']}")
    
    with col3:
        st.markdown(f"**Overall Score:** {executive_summary['overall_score']}/100")
    
    # Recommendation
    st.subheader("Recommendation")
    st.markdown(executive_summary['recommendation'])
    
    # Score Visualization Section
    st.header("Score Breakdown")
    
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
        st.markdown(f"**Why:** {scores['score_explanations']['market_pain_score']}")
        
        # Competition Score
        st.plotly_chart(
            create_gauge_chart(
                scores["competition_score"], 
                "Competition Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"**Why:** {scores['score_explanations']['competition_score']}")
    
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
        st.markdown(f"**Why:** {scores['score_explanations']['market_interest_score']}")
        
        # Keyword Relevance Score
        st.plotly_chart(
            create_gauge_chart(
                scores["keyword_relevance_score"], 
                "Keyword Relevance Score",
                threshold_ranges=[(0, 3, "red"), (3, 7, "orange"), (7, 10, "green")]
            ),
            use_container_width=True
        )
        st.markdown(f"**Why:** {scores['score_explanations']['keyword_relevance_score']}")
    
    # Radar Chart for all scores
    st.subheader("Score Comparison")
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
    st.header("Detailed Results")
    
    # Create tabs for different result categories
    tab1, tab2, tab3, tab4 = st.tabs(["Pain Points", "Excitement Signals", "Competitors", "Red Flags"])
    
    with tab1:
        st.subheader("Top Pain Points")
        
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
            for item in pain_points[:5]:  # Show only top 5
                if isinstance(item, dict) and "text" in item and "relevance" in item:
                    st.markdown(f"- {item['text']} (Relevance: {item['relevance']}/10)")
    
    with tab2:
        st.subheader("Top Excitement Signals")
        
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
            for item in excitement_signals[:5]:  # Show only top 5
                if isinstance(item, dict) and "text" in item and "relevance" in item:
                    st.markdown(f"- {item['text']} (Relevance: {item['relevance']}/10)")
    
    with tab3:
        st.subheader("Competitors")
        
        competitors = final_report["aggregated_results"]["mentions_of_competitors"]
        if competitors:
            # Create a DataFrame for competitors
            df_competitors = pd.DataFrame({
                'Competitor': competitors
            })
            
            # Display as a table
            st.dataframe(df_competitors, use_container_width=True)
    
    with tab4:
        st.subheader("Red Flags")
        
        red_flags = final_report["aggregated_results"].get("red_flags", [])
        if red_flags:
            for flag in red_flags:
                st.markdown(f"- {flag}")
    
    # Key Insights Section
    st.header("Key Insights")
    
    for insight in executive_summary["key_insights"]:
        st.markdown(f"- {insight}")
    
    # Notable Quotes Section
    if "notable_quotes" in final_report["aggregated_results"] and final_report["aggregated_results"]["notable_quotes"]:
        st.header("Notable Quotes")
        
        quotes = final_report["aggregated_results"]["notable_quotes"]
        for quote in quotes:
            if isinstance(quote, dict) and "text" in quote:
                st.markdown(f"> *\"{quote['text']}\"*")
            elif isinstance(quote, str):
                st.markdown(f"> *\"{quote}\"*")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "Business Idea Validator - Visualization Test | "
        "This is a demonstration of the visualization components using sample data."
    )

if __name__ == "__main__":
    main()
