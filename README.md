# Business Idea Validator Streamlit App

A professional Streamlit application that provides a user-friendly interface for validating business ideas. This app analyzes online discussions to identify pain points, excitement signals, and competitors related to your business idea.

## Features

- Input your business idea and get it validated
- Visualize validation scores with interactive charts
- View detailed analysis of pain points, excitement signals, and competitors
- Get professional executive summary with recommendations
- Download reports in JSON format

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

1. Clone this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3. Enter your business idea in the text area and click "Validate Business Idea"

4. Wait for the validation process to complete

5. Review the results and download reports if needed

## How It Works

The Business Idea Validator:

1. Takes your business idea as input
2. Generates relevant keywords
3. Searches online platforms (Reddit, ProductHunt) for discussions related to these keywords
4. Analyzes the content using AI to extract:
   - Pain points
   - Excitement signals
   - Competitors
   - Notable quotes
   - Red flags
5. Calculates scores based on the findings
6. Generates an executive summary with recommendations

## Configuration

The app uses the following configuration from `test_enhanced.py`:

- API keys for ScraperAPI and OpenAI
- Scoring weights for different factors
- Validation thresholds
- Number of pages to fetch per site
- Number of keywords to generate

## License

This project is licensed under the MIT License - see the LICENSE file for details.
