import streamlit as st
import json
import datetime
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import time
import pandas as pd
from typing import List, Dict, Any
import asyncio
import threading

# Import your existing validation functions (assuming they're in a separate module)
# You would need to modularize your original script
try:
    from business_validator import (
        generate_keywords, 
        process_keyword, 
        generate_aggregated_report,
        calculate_business_idea_scores,
        generate_executive_summary,
        setup_master_log_directory
    )
except ImportError:
    # Mock functions for demonstration
    st.error("Please ensure your validation module is properly imported")

# Page configuration
st.set_page_config(
    page_title="AI Business Idea Validator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .score-card {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
    }
    .pain-point-card {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .excitement-card {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .competitor-card {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
    }
    .section-header {
        background-color: #1f2937;
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 2rem 0 1rem 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class BusinessIdeaValidator:
    def __init__(self):
        if 'validation_results' not in st.session_state:
            st.session_state.validation_results = None
        if 'is_validating' not in st.session_state:
            st.session_state.is_validating = False

    def render_header(self):
        """Render the app header"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <h1 style="color: #1f2937; font-size: 3rem; margin-bottom: 1rem;">🚀 AI Business Idea Validator</h1>
            <p style="font-size: 1.2rem; color: #6b7280;">Validate your business ideas with AI-powered market research before you launch</p>
        </div>
        """, unsafe_allow_html=True)

    def render_input_section(self):
        """Render the business idea input section"""
        st.markdown('<div class="section-header"><h2>Enter Your Business Idea</h2></div>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            business_idea = st.text_area(
                "Describe your business idea",
                height=150,
                placeholder="e.g., A mobile app that connects local pet owners with trusted pet sitters in their neighborhood..."
            )
            
            if st.button("🔍 Validate My Idea", type="primary", use_container_width=True):
                if business_idea:
                    self.validate_idea(business_idea)
                else:
                    st.error("Please enter a business idea to validate")

    def validate_idea(self, business_idea: str):
        """Run the validation process"""
        st.session_state.is_validating = True
        
        # Create a progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        try:
            # Step 1: Generate keywords
            status_text.text("🔑 Generating relevant keywords...")
            progress_bar.progress(20)
            time.sleep(1)  # Simulate processing
            
            # Step 2: Scrape and analyze data
            status_text.text("🌐 Scraping and analyzing market data...")
            progress_bar.progress(50)
            time.sleep(2)  # Simulate processing
            
            # Step 3: Generate report
            status_text.text("📊 Generating validation report...")
            progress_bar.progress(80)
            time.sleep(1)  # Simulate processing
            
            # Step 4: Complete
            status_text.text("✅ Validation complete!")
            progress_bar.progress(100)
            time.sleep(0.5)
            
            # For demonstration, use the provided sample data
            # In real implementation, you would call your validation functions here
            sample_results = self.load_sample_results()
            sample_results['metadata']['business_idea'] = business_idea
            
            st.session_state.validation_results = sample_results
            st.session_state.is_validating = False
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
            
            st.rerun()
            
        except Exception as e:
            st.error(f"An error occurred during validation: {str(e)}")
            st.session_state.is_validating = False
            progress_bar.empty()
            status_text.empty()

    def load_sample_results(self) -> Dict[str, Any]:
        """Load the sample results for demonstration"""
        # This would be replaced with actual validation results
        return {
            "scores": {
                "market_pain_score": 4.2,
                "market_interest_score": 4.2,
                "competition_score": 8,
                "keyword_relevance_score": 10,
                "coherence_score": 8.3,
                "overall_viability_score": 58.1,
                "raw_counts": {
                    "pain_points": 13,
                    "excitement_signals": 14,
                    "competitors": 10,
                    "red_flags": 10
                },
                "avg_relevance": {
                    "pain_points": 8.6,
                    "excitement_signals": 8.6
                }
            },
            "executive_summary": {
                "business_idea": "a tool to validate business ideas with AI and data before launch",
                "validation_status": "Partially Validated",
                "overall_score": 58.1,
                "top_pain_points": [
                    {"text": "Risk of launching without validating the idea leading to failed launches", "relevance": 10},
                    {"text": "Lack of existing products for validating business ideas with AI and data", "relevance": 10},
                    {"text": "High cost and time consumption in validating business ideas", "relevance": 9},
                    {"text": "Need for quick validation of business ideas", "relevance": 9},
                    {"text": "Failed launches due to inadequate validation", "relevance": 9}
                ],
                "top_excitement_signals": [
                    {"text": "Interest in AI tools that can quickly validate business ideas", "relevance": 10},
                    {"text": "Validating a startup idea in 20 seconds for free", "relevance": 10},
                    {"text": "Ability to validate a startup idea in 20 seconds for free", "relevance": 10},
                    {"text": "AI and data-driven validation before launching", "relevance": 10},
                    {"text": "Desire for affordable validation tools", "relevance": 9}
                ],
                "top_competitors": [
                    "Amazon",
                    "I built a startup idea validator",
                    "AI that turns concepts into projects",
                    "GitHub",
                    "Fastest way to test multiple business ideas with AI-generated landing pages"
                ],
                "key_insights": [
                    "Healthy competitive landscape, indicating a validated market.",
                    "Keywords were highly relevant, providing good market insights."
                ],
                "recommendation": "This business idea shows moderate market validation. Consider refining the concept based on the identified pain points and excitement signals."
            },
            "metadata": {
                "business_idea": "",
                "timestamp": datetime.datetime.now().isoformat(),
                "keywords": ["business idea validation", "AI validation tools"],
                "sources": ["Reddit", "ProductHunt"],
                "pages_per_source": 3
            }
        }

    def render_results(self):
        """Render the validation results"""
        if not st.session_state.validation_results:
            return
            
        results = st.session_state.validation_results
        scores = results['scores']
        summary = results['executive_summary']
        
        # Header with overall score
        st.markdown('<div class="section-header"><h2>📊 Validation Results</h2></div>', unsafe_allow_html=True)
        
        # Overall score card
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            status_color = self.get_status_color(summary['validation_status'])
            st.markdown(f"""
            <div class="score-card" style="background: {status_color};">
                <h2>{summary['validation_status']}</h2>
                <h1>{summary['overall_score']}/100</h1>
                <h3>{summary['business_idea']}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Score metrics
        self.render_score_metrics(scores)
        
        # Key findings
        self.render_key_findings(summary)
        
        # Detailed insights
        self.render_detailed_insights(summary, scores)
        
        # Recommendations
        self.render_recommendations(summary)
        
        # Data sources and methodology
        self.render_methodology(results['metadata'])

    def get_status_color(self, status: str) -> str:
        """Get color based on validation status"""
        colors = {
            "Strongly Validated": "linear-gradient(45deg, #4caf50 0%, #8bc34a 100%)",
            "Validated": "linear-gradient(45deg, #2196f3 0%, #03a9f4 100%)",
            "Partially Validated": "linear-gradient(45deg, #ff9800 0%, #ffc107 100%)",
            "Weakly Validated": "linear-gradient(45deg, #f44336 0%, #e91e63 100%)",
            "Not Validated": "linear-gradient(45deg, #9c27b0 0%, #673ab7 100%)"
        }
        return colors.get(status, "linear-gradient(45deg, #667eea 0%, #764ba2 100%)")

    def render_score_metrics(self, scores: Dict[str, Any]):
        """Render score metrics with gauges"""
        st.markdown('<div class="section-header"><h3>🎯 Score Breakdown</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Market Pain Score
            fig1 = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = scores['market_pain_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Market Pain Score"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#f44336"},
                    'steps': [
                        {'range': [0, 3], 'color': "#ffcdd2"},
                        {'range': [3, 6], 'color': "#ef9a9a"},
                        {'range': [6, 8], 'color': "#e57373"},
                        {'range': [8, 10], 'color': "#f44336"}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 7}
                }
            ))
            fig1.update_layout(height=250)
            st.plotly_chart(fig1, use_container_width=True)
            
            # Competition Score
            fig3 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = scores['competition_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Competition Score"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#ff9800"},
                    'steps': [
                        {'range': [0, 3], 'color': "#ffecb3"},
                        {'range': [3, 6], 'color': "#ffe082"},
                        {'range': [6, 8], 'color': "#ffb74d"},
                        {'range': [8, 10], 'color': "#ff9800"}
                    ]
                }
            ))
            fig3.update_layout(height=250)
            st.plotly_chart(fig3, use_container_width=True)
        
        with col2:
            # Market Interest Score
            fig2 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = scores['market_interest_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Market Interest Score"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#4caf50"},
                    'steps': [
                        {'range': [0, 3], 'color': "#c8e6c9"},
                        {'range': [3, 6], 'color': "#a5d6a7"},
                        {'range': [6, 8], 'color': "#81c784"},
                        {'range': [8, 10], 'color': "#4caf50"}
                    ]
                }
            ))
            fig2.update_layout(height=250)
            st.plotly_chart(fig2, use_container_width=True)
            
            # Keyword Relevance Score
            fig4 = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = scores['keyword_relevance_score'],
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Keyword Relevance Score"},
                gauge = {
                    'axis': {'range': [None, 10]},
                    'bar': {'color': "#9c27b0"},
                    'steps': [
                        {'range': [0, 3], 'color': "#e1bee7"},
                        {'range': [3, 6], 'color': "#ce93d8"},
                        {'range': [6, 8], 'color': "#ba68c8"},
                        {'range': [8, 10], 'color': "#9c27b0"}
                    ]
                }
            ))
            fig4.update_layout(height=250)
            st.plotly_chart(fig4, use_container_width=True)

    def render_key_findings(self, summary: Dict[str, Any]):
        """Render key findings section"""
        st.markdown('<div class="section-header"><h3>🔍 Key Findings</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 😣 Top Pain Points")
            for i, pain_point in enumerate(summary['top_pain_points'][:5], 1):
                st.markdown(f"""
                <div class="pain-point-card">
                    <strong>#{i}</strong> {pain_point['text']}
                    <br><small>Relevance: {pain_point['relevance']}/10</small>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🎉 Top Excitement Signals")
            for i, excitement in enumerate(summary['top_excitement_signals'][:5], 1):
                st.markdown(f"""
                <div class="excitement-card">
                    <strong>#{i}</strong> {excitement['text']}
                    <br><small>Relevance: {excitement['relevance']}/10</small>
                </div>
                """, unsafe_allow_html=True)

    def render_detailed_insights(self, summary: Dict[str, Any], scores: Dict[str, Any]):
        """Render detailed insights"""
        st.markdown('<div class="section-header"><h3>💡 Detailed Insights</h3></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🏢 Competitors Identified")
            for competitor in summary['top_competitors']:
                st.markdown(f"""
                <div class="competitor-card">
                    {competitor}
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 📊 Market Analysis")
            for insight in summary['key_insights']:
                st.markdown(f"• {insight}")
            
            # Raw counts visualization
            counts = scores['raw_counts']
            fig = go.Figure(data=[
                go.Bar(name='Count', x=['Pain Points', 'Excitement Signals', 'Competitors', 'Red Flags'],
                       y=[counts['pain_points'], counts['excitement_signals'], 
                          counts['competitors'], counts['red_flags']],
                       marker_color=['#f44336', '#4caf50', '#ff9800', '#e91e63'])
            ])
            fig.update_layout(title="Market Research Findings", yaxis_title="Count", height=300)
            st.plotly_chart(fig, use_container_width=True)

    def render_recommendations(self, summary: Dict[str, Any]):
        """Render recommendations section"""
        st.markdown('<div class="section-header"><h3>💼 Recommendations</h3></div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="background-color: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 4px solid #007bff;">
            <h4>Our Recommendation:</h4>
            <p style="font-size: 1.1rem; line-height: 1.6;">{summary['recommendation']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Next steps
        st.markdown("#### 🚀 Suggested Next Steps")
        if summary['validation_status'] in ['Strongly Validated', 'Validated']:
            st.markdown("""
            1. **Proceed with MVP development**
            2. **Focus on the highest-relevance pain points**
            3. **Analyze competitor strategies**
            4. **Create a minimum viable product**
            5. **Test with early adopters**
            """)
        elif summary['validation_status'] == 'Partially Validated':
            st.markdown("""
            1. **Refine your business concept**
            2. **Address the identified pain points**
            3. **Research the competition more thoroughly**
            4. **Consider pivoting to higher-relevance areas**
            5. **Conduct additional market research**
            """)
        else:
            st.markdown("""
            1. **Reassess your business idea**
            2. **Consider significant pivots**
            3. **Explore alternative market segments**
            4. **Gather more market feedback**
            5. **Evaluate completely different approaches**
            """)

    def render_methodology(self, metadata: Dict[str, Any]):
        """Render data sources and methodology"""
        with st.expander("🔬 Methodology & Data Sources", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Data Sources")
                st.markdown(f"• **Sources**: {', '.join(metadata['sources'])}")
                st.markdown(f"• **Pages per source**: {metadata['pages_per_source']}")
                st.markdown(f"• **Keywords used**: {', '.join(metadata['keywords'])}")
                st.markdown(f"• **Analysis date**: {metadata['timestamp'][:10]}")
            
            with col2:
                st.markdown("#### Scoring Methodology")
                st.markdown("""
                **Weighted Scoring System:**
                • Pain Points: 35%
                • Excitement Signals: 30%
                • Competition Analysis: 20%
                • Keyword Relevance: 15%
                
                **Validation Thresholds:**
                • Strongly Validated: 85+
                • Validated: 70-84
                • Partially Validated: 55-69
                • Weakly Validated: 40-54
                • Not Validated: <40
                """)

    def render_sidebar(self):
        """Render sidebar with additional information"""
        with st.sidebar:
            st.markdown("### 🚀 About This Tool")
            st.markdown("""
            This AI-powered business idea validator helps entrepreneurs:
            
            ✅ **Identify market pain points**  
            ✅ **Discover excitement signals**  
            ✅ **Analyze competition**  
            ✅ **Generate validation scores**  
            ✅ **Get actionable insights**  
            """)
            
            st.markdown("### 📊 How It Works")
            st.markdown("""
            1. **Keyword Generation**: AI creates relevant search terms
            2. **Data Scraping**: Analyzes Reddit, ProductHunt, etc.
            3. **AI Analysis**: Extracts pain points and excitement
            4. **Scoring Algorithm**: Calculates validation scores
            5. **Executive Summary**: Provides clear recommendations
            """)
            
            if st.session_state.validation_results:
                st.markdown("### 💾 Export Results")
                if st.button("📥 Download JSON Report"):
                    json_str = json.dumps(st.session_state.validation_results, indent=2)
                    st.download_button(
                        label="Download Report",
                        data=json_str,
                        file_name=f"validation_report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
            
            st.markdown("### 🔧 Settings")
            st.markdown("*API Configuration*")
            openai_key = st.text_input("OpenAI API Key", type="password", help="Required for AI analysis")
            scraper_key = st.text_input("ScraperAPI Key", type="password", help="Required for web scraping")
            
            if openai_key and scraper_key:
                st.success("✅ API keys configured")
            else:
                st.warning("⚠️ Please configure API keys for full functionality")

def main():
    """Main function to run the Streamlit app"""
    validator = BusinessIdeaValidator()
    
    # Render sidebar
    validator.render_sidebar()
    
    # Render main content
    validator.render_header()
    
    if not st.session_state.validation_results and not st.session_state.is_validating:
        validator.render_input_section()
    
    if st.session_state.is_validating:
        st.info("🔄 Validation in progress...")
    
    if st.session_state.validation_results:
        validator.render_results()
        
        # Reset button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔄 Validate Another Idea", type="secondary", use_container_width=True):
                st.session_state.validation_results = None
                st.rerun()

if __name__ == "__main__":
    main()