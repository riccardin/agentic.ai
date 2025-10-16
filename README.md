# Sparrow API Blog Generation Workflow

This project automates the generation of blog content for the Sparrow API testing platform using Azure OpenAI services and stores the results in Google Sheets.

## Overview

The workflow performs the following steps:
1. Generates blog topic ideas for the Sparrow API testing platform
2. Creates an outline for the selected topic
3. Evaluates and revises the outline
4. Writes a detailed blog post
5. Appends the result to a Google Sheet

## Requirements

- Python 3.7+
- Azure OpenAI API access
- Google Sheets API access with OAuth 2.0 credentials

## Installation

1. Clone this repository or download the files
2. Install the required packages:

```bash
pip install -r requirements.txt


## Configuration
### Azure OpenAI Configuration
Set the following environment variables:

```bash
export AZURE_OPENAI_API_KEY="your_azure_openai_api_key"
export AZURE_OPENAI_ENDPOINT="your_azure_openai_endpoint"
export AZURE_OPENAI_API_VERSION="2023-05-15"
 ```

### Google Sheets Configuration
1. Place your google_credentials.json file in the project directory
2. The first time you run the script, it will open a browser window for authentication
3. After successful authentication, a token.pickle file will be created for future use
4. The script is configured to use the spreadsheet with ID: "1wC_LoTybaf5dQM2rY1aisuI9UFSmibNpHNFZAEfLdW4"
5. The sheet name is set to "blog"
## Usage
Run the script with:

```bash
python n8test_workflow.py
 ```

The script will:

- Run the workflow once immediately
- Schedule it to run every 5 hours
- Output progress to the console
- Append the generated blog post to the configured Google Sheet
To stop the script, press Ctrl+C.

## Files
- n8test_workflow.py : Main script that runs the workflow
- requirements.txt : List of Python package dependencies
- google_credentials.json : Google API credentials file (OAuth 2.0)
- README.md : This documentation file
## Authentication Flow
The script uses OAuth 2.0 for Google Sheets authentication:

1. First run: Opens a browser window for user authentication
2. Creates and stores a token.pickle file with authentication credentials
3. Subsequent runs: Uses the stored token without requiring re-authentication
4. If the token expires, the script will automatically refresh it
## Notes
- The workflow was converted from an n8n workflow (n8Test.json)
- The script uses the "gpt-4.1-nano" model by default for Azure OpenAI
- The scheduling system runs every 5 hours, matching the original n8n workflow