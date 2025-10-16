import os
import time
import schedule
from datetime import datetime
from openai import AzureOpenAI
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Azure OpenAI API credentials
AZURE_OPENAI_API_KEY =  os.environ.get("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.environ.get("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_VERSION = os.environ.get("AZURE_OPENAI_API_VERSION")

# Google Sheets credentials
GOOGLE_SHEETS_CREDENTIALS_FILE = "google_credentials.json"  # Path to your Google credentials JSON
SPREADSHEET_ID = "1wC_LoTybaf5dQM2rY1aisuI9UFSmibNpHNFZAEfLdW4"
SHEET_NAME = "blog"  # This corresponds to the sheet with gid=1308846749

# Initialize Azure OpenAI client
client = AzureOpenAI(
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION,
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def initialize_google_sheets():
    """Initialize and return Google Sheets client"""
    # For OAuth flow instead of service account
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    import json
    
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = None
    
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Load client ID and secret from credentials file
            with open(GOOGLE_SHEETS_CREDENTIALS_FILE, 'r') as f:
                creds_data = json.load(f)
            
            client_config = {
                'installed': {
                    'client_id': creds_data['web']['client_id'],
                    'client_secret': creds_data['web']['client_secret'],
                    'redirect_uris': ['http://localhost', 'urn:ietf:wg:oauth:2.0:oob'],
                    'auth_uri': creds_data['web']['auth_uri'],
                    'token_uri': creds_data['web']['token_uri']
                }
            }
            
            flow = InstalledAppFlow.from_client_config(
                client_config, SCOPES)
            creds = flow.run_local_server(port=64576)
            
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    gc = gspread.authorize(creds)
    return gc

def append_to_google_sheet(data):
    """Append data to Google Sheet"""
    gc = initialize_google_sheets()
    spreadsheet = gc.open_by_key(SPREADSHEET_ID)
    worksheet = spreadsheet.worksheet(SHEET_NAME)
    worksheet.append_row([data])
    print(f"Data appended to Google Sheet: {SPREADSHEET_ID}, Sheet: {SHEET_NAME}")

def generate_ai_response(prompt, system_message="", model="gpt-4.1-nano"):
    """Generate response using Azure OpenAI"""
    messages = []
    
    if system_message:
        messages.append({"role": "system", "content": system_message})
    
    messages.append({"role": "user", "content": prompt})
    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

def ai_agent():
    """Generate blog topic ideas for Sparrow API testing platform"""
    system_message = """You are an AI agent specializing in generating blog topic ideas specifically for the Sparrow API testing platform. Your role is to analyze the latest trends, user needs, and industry developments related to API testing and the Sparrow platform. When provided with information about the target audience or content objectives, you will suggest a range of blog topics tailored to Sparrow's features, use cases, best practices, and integration tips. For each topic, include a clear title, a brief description outlining the blog's focus, and a note on how it benefits Sparrow users or those interested in API testing. Your recommendations should be relevant, actionable, and designed to help users maximize their experience with the Sparrow API testing platform."""
    
    prompt = "Generate a blog topic idea for the Sparrow API testing platform."
    return generate_ai_response(prompt, system_message)

def outline_writer(topic):
    """Generate a structured outline for the blog post"""
    system_message = "# Overview\nYou are an expert outline writer. Your job is to generate a structured outline for a blog post with section titles and key points."
    
    prompt = f"Here is the topic to write a blog about: {topic}"
    return generate_ai_response(prompt, system_message)

def outline_evaluation(outline):
    """Evaluate and revise the outline"""
    system_message = """# Overview
You are an expert blog evaluator. Revise this outline and ensure it covers the following key criteria: 
(1) Engaging Introduction 
(2) Clear Section Breakdown
(3) Logical Flow
(4) Conclusion with Key Takeaways

## Output
Only output the revised outline."""
    
    prompt = f"Here is the outline: \n\n{outline}"
    return generate_ai_response(prompt, system_message)

def blog_writer(revised_outline):
    """Generate a detailed blog post using the outline"""
    system_message = "# Overview\nYou are an expert blog writer. Generate a detailed blog post using the outline with well-structured paragraphs and engaging content."
    
    prompt = f"Here is the revised outline: {revised_outline}"
    return generate_ai_response(prompt, system_message)

def run_workflow():
    """Execute the complete workflow"""
    print(f"Starting workflow at {datetime.now()}")
    
    # Step 1: Generate blog topic
    topic = ai_agent()
    print(f"Generated topic: {topic[:100]}...")
    
    # Step 2: Create outline
    outline = outline_writer(topic)
    print(f"Created outline: {outline[:100]}...")
    
    # Step 3: Evaluate and revise outline
    revised_outline = outline_evaluation(outline)
    print(f"Revised outline: {revised_outline[:100]}...")
    
    # Step 4: Write blog post
    blog_post = blog_writer(revised_outline)
    print(f"Generated blog post: {blog_post[:100]}...")
    
    # Step 5: Append to Google Sheet
    append_to_google_sheet(blog_post)
    
    print(f"Workflow completed at {datetime.now()}")

def schedule_workflow():
    """Schedule the workflow to run every 5 hours"""
    schedule.every(5).hours.do(run_workflow)
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    print("Starting Sparrow API blog generation workflow")
    print("Press Ctrl+C to exit")
    
    try:
        # Run once immediately
        run_workflow()
        
        # Then schedule for every 5 hours
        schedule_workflow()
    except KeyboardInterrupt:
        print("Workflow stopped by user")
    except Exception as e:
        print(f"Error in workflow: {str(e)}")