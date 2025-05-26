# Business Idea Validator Streamlit App

A professional Streamlit application that provides a user-friendly interface for validating business ideas. This app analyzes online discussions to identify pain points, excitement signals, and competitors related to your business idea.

## Features

-   Input your business idea and get it validated
-   Visualize validation scores with interactive charts
-   View detailed analysis of pain points, excitement signals, and competitors
-   Get a professional executive summary with recommendations
-   Download reports in JSON format
-   Supports data scraping and analysis from Reddit and Hacker News
-   Comprehensive logging for monitoring and debugging
-   Configuration options for API keys, scoring weights, and validation thresholds

## Requirements

-   Python 3.8+
-   Dependencies listed in `requirements.txt`

## Installation

1.  Clone this repository
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the Streamlit app:

    ```bash
    streamlit run business_validator_ui.py
    ```

2.  Open your web browser and navigate to the URL displayed in the terminal (typically http://localhost:8501)

3.  Enter your business idea in the text area and click "Validate Business Idea"

4.  Wait for the validation process to complete

5.  Review the results and download reports if needed

## How It Works

The Business Idea Validator:

1.  Takes your business idea as input
2.  Generates relevant keywords using the `keyword_generator.py` module
3.  Scrapes online platforms (Reddit, Hacker News) for discussions related to these keywords using the `reddit.py` and `hackernews.py` modules
4.  Analyzes the content using AI (OpenAI) to extract:
    -   Pain points
    -   Excitement signals
    -   Competitors
    -   Notable quotes
    -   Red flags
5.  Calculates scores based on the findings using the `validator.py` module
6.  Generates an executive summary with recommendations
7.  Stores validation data in the `validation_data/` directory
8.  Logs application events and errors in the `logs/` directory

## Architecture

The app consists of the following main components:

-   `business_validator_ui.py`: The main Streamlit application file, providing the user interface.
-   `validator.py`: Contains the core validation logic and scoring algorithms.
-   `analyzers/`: Contains modules for analyzing data from different sources:
    -   `reddit_analyzer.py`: Analyzes data from Reddit.
    -   `hackernews_analyzer.py`: Analyzes data from Hacker News.
    -   `combined_analyzer.py`: Combines the results from different analyzers.
    -   `keyword_generator.py`: Generates relevant keywords for the business idea.
-   `scrapers/`: Contains modules for scraping data from different sources:
    -   `reddit.py`: Scrapes data from Reddit.
    -   `hackernews.py`: Scrapes data from Hacker News.
-   `models.py`: Defines the data models used in the app.
-   `config.py`: Contains configuration settings for the app, such as API keys and scoring weights.
-   `utils/`: Contains utility modules:
    -   `environment.py`: Manages environment variables.
    -   `reporting.py`: Provides reporting functions.

## Configuration

The app uses the following configuration options, which can be set in the `config.py` file or as environment variables:

-   API keys for ScraperAPI and OpenAI
-   Scoring weights for different factors
-   Validation thresholds
-   Number of pages to fetch per site
-   Number of keywords to generate

## Logging

The app uses the `logging` module to log events and errors. Log files are stored in the `logs/` directory.

## Data Storage

The app stores validation data in JSON format in the `validation_data/` directory. Each validation run creates a new subdirectory with the data for that run.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
